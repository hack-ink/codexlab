from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "multi-agent"
SCHEMAS_DIR = SKILL_ROOT / "schemas"
E2E_DIR = Path(__file__).resolve().parent


def load_json(path: Path):
    text = path.read_text()
    stripped = text.strip()
    if stripped.startswith("```") or stripped.endswith("```"):
        raise AssertionError(
            f"{path.name}: worker output must be raw JSON only; code fences are not allowed"
        )
    return json.loads(stripped)


def validate_one(schema_path: Path, payload: dict, label: str) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    print(f"OK: {label} against {schema_path.relative_to(SKILL_ROOT)}")


def ssot_parts(ssot_id: str) -> tuple[str, str]:
    if "-" not in ssot_id:
        raise AssertionError("ssot_id must be scenario-hash: <scenario>-<hex>")
    scenario, token = ssot_id.rsplit("-", 1)
    return scenario, token


def assert_ssot_id_policy(ssot_id: str) -> None:
    scenario, token = ssot_parts(ssot_id)
    if not scenario:
        raise AssertionError("ssot_id scenario prefix must be non-empty")
    if not (8 <= len(token) <= 64):
        raise AssertionError("ssot_id token must be hex length 8..64")
    if any(c not in "0123456789abcdef" for c in token):
        raise AssertionError("ssot_id token must be lowercase hex")

    expected = hashlib.sha256(scenario.encode("utf-8")).hexdigest()[: len(token)]
    if token != expected:
        raise AssertionError(
            "ssot_id must use scenario-hash (sha256(scenario) prefix); "
            f"expected {scenario}-{expected}"
        )


def assert_json_only_output(payload: dict, path: Path) -> None:
    if not isinstance(payload, (dict, list)):
        raise AssertionError(f"{path.name}: output must be a JSON object or array")


def is_within(touched: str, allowed_paths: list[str]) -> bool:
    touched = touched.rstrip("/")
    for allowed in allowed_paths:
        normalized = allowed.rstrip("/")
        if touched == normalized:
            return True
        if touched.startswith(normalized + "/"):
            return True
    return False


def overlaps(a: str, b: str) -> bool:
    a = a.rstrip("/")
    b = b.rstrip("/")
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def assert_no_forbidden_roles(payload: dict, *, label: str) -> None:
    agent_type = payload.get("agent_type")
    role = payload.get("role")
    allowed = {"runner", "builder", "inspector"}

    if role is not None and role not in allowed:
        raise AssertionError(f"{label}: unknown role detected: {role}")
    if agent_type is not None and agent_type not in allowed:
        raise AssertionError(f"{label}: unknown agent_type detected: {agent_type}")


def assert_unique_slice_ids(dispatches: list[dict], *, label: str) -> None:
    slice_ids = [d["slice_id"] for d in dispatches]
    if len(slice_ids) != len(set(slice_ids)):
        duplicates = sorted({sid for sid in slice_ids if slice_ids.count(sid) > 1})
        raise AssertionError(f"{label}: duplicate slice_id(s): {', '.join(duplicates)}")


def assert_dependency_targets_exist(dispatches: list[dict], *, label: str) -> None:
    slice_ids = {d["slice_id"] for d in dispatches}
    for d in dispatches:
        for dep in d.get("dependencies", []):
            if dep not in slice_ids:
                raise AssertionError(
                    f"{label}: {d['slice_id']} depends on missing slice_id {dep!r}"
                )


def validate_dispatches(path: Path, expected_count: int) -> list[dict]:
    dispatches = load_json(path)
    if not isinstance(dispatches, list):
        raise AssertionError(f"{path.name} must be a JSON array")
    if len(dispatches) != expected_count:
        raise AssertionError(
            f"{path.name}: expected {expected_count} items, got {len(dispatches)}"
        )

    assert_unique_slice_ids(dispatches, label=path.name)
    assert_dependency_targets_exist(dispatches, label=path.name)

    schema_path = SCHEMAS_DIR / "task-dispatch.schema.json"
    for i, payload in enumerate(dispatches, 1):
        assert_no_forbidden_roles(payload, label=f"{path.name}[{i}]")
        validate_one(schema_path, payload, f"{path.name}[{i}]")
        assert_ssot_id_policy(payload["ssot_id"])

    return dispatches


def assert_handoff_requests(
    payload: dict, *, dispatch_schema: Path, label: str
) -> None:
    for i, request in enumerate(payload.get("handoff_requests", []), 1):
        assert_no_forbidden_roles(request, label=f"{label}.handoff_requests[{i}]")
        validate_one(dispatch_schema, request, f"{label}.handoff_requests[{i}]")
        assert_ssot_id_policy(request["ssot_id"])


def assert_swarm_ticket_invariants(dispatches: list[dict]) -> None:
    if not all(d["slice_id"].startswith("swarm--") for d in dispatches):
        bad = [d["slice_id"] for d in dispatches if not d["slice_id"].startswith("swarm--")]
        raise AssertionError(
            "dispatches.workstreams.json: slice_id must start with `swarm--`: "
            + ", ".join(bad)
        )

    builders = [d for d in dispatches if d["agent_type"] == "builder"]
    runners = [d for d in dispatches if d["agent_type"] == "runner"]
    inspectors = [d for d in dispatches if d["agent_type"] == "inspector"]

    if not builders or not runners or not inspectors:
        raise AssertionError(
            "dispatches.workstreams.json must include runner, builder, and inspector slices"
        )

    for payload in builders:
        if not payload["ownership_paths"]:
            raise AssertionError(
                f"{payload['slice_id']}: builder slice must declare ownership_paths"
            )
        if not payload["allowed_paths"]:
            raise AssertionError(
                f"{payload['slice_id']}: builder slice must declare allowed_paths"
            )


def assert_council_bootstrap_invariants(dispatches: list[dict]) -> None:
    if len(dispatches) != 2:
        raise AssertionError(
            "dispatches.council_bootstrap.json must contain exactly 2 default bootstrap slices"
        )

    ssot_id = dispatches[0]["ssot_id"]
    runners = [d for d in dispatches if d["agent_type"] == "runner"]
    inspectors = [d for d in dispatches if d["agent_type"] == "inspector"]

    if len(runners) != 1 or len(inspectors) != 1:
        raise AssertionError(
            "dispatches.council_bootstrap.json must have 1 runner and 1 inspector"
        )

    for payload in dispatches:
        if payload["ssot_id"] != ssot_id:
            raise AssertionError(
                "dispatches.council_bootstrap.json must use one shared ssot_id"
            )
        if "-council-" not in payload["slice_id"]:
            raise AssertionError(
                "dispatches.council_bootstrap.json slice_id must include `-council-`"
            )
        if payload.get("dependencies"):
            raise AssertionError(
                f"{payload['slice_id']}: default council bootstrap slices must be dependency-free"
            )

    runner = runners[0]
    inspector = inspectors[0]
    if runner["slice_kind"] != "work":
        raise AssertionError("council bootstrap runner slice must be slice_kind=work")
    if inspector["slice_kind"] != "review":
        raise AssertionError("council bootstrap inspector slice must be slice_kind=review")


def validate_results() -> None:
    runner_schema = SCHEMAS_DIR / "worker-result.runner.schema.json"
    builder_schema = SCHEMAS_DIR / "worker-result.builder.schema.json"
    inspector_schema = SCHEMAS_DIR / "review-result.inspector.schema.json"
    dispatch_schema = SCHEMAS_DIR / "task-dispatch.schema.json"

    results = [
        ("result.runner.json", runner_schema),
        ("result.builder.json", builder_schema),
        ("result.inspector.pass.json", inspector_schema),
        ("result.inspector.block.json", inspector_schema),
        ("result.inspector.needs_evidence.json", inspector_schema),
    ]

    for filename, schema_path in results:
        payload = load_json(E2E_DIR / filename)
        assert_no_forbidden_roles(payload, label=filename)
        assert_json_only_output(payload, E2E_DIR / filename)
        validate_one(schema_path, payload, filename)
        assert_ssot_id_policy(payload["ssot_id"])

        if filename in {"result.runner.json", "result.builder.json"}:
            assert_handoff_requests(
                payload,
                dispatch_schema=dispatch_schema,
                label=filename,
            )

    builder = load_json(E2E_DIR / "result.builder.json")
    for touched_path in builder["changeset"]["touched_paths"]:
        if not is_within(touched_path, builder["allowed_paths"]):
            raise AssertionError(
                "result.builder.json: touched path "
                f"{touched_path!r} is outside allowed_paths"
            )


def assert_dispatch_invariants() -> None:
    read_only = validate_dispatches(
        E2E_DIR / "dispatches.read_only.json", expected_count=16
    )
    if any(d["agent_type"] != "runner" for d in read_only):
        raise AssertionError("read_only dispatches must use agent_type=runner only")
    if any(d["ownership_paths"] for d in read_only):
        raise AssertionError("read_only dispatches must have empty ownership_paths")

    write = validate_dispatches(E2E_DIR / "dispatches.write_mixed.json", expected_count=12)
    builders = [d for d in write if d["agent_type"] == "builder"]
    runners = [d for d in write if d["agent_type"] == "runner"]
    if len(builders) != 6 or len(runners) != 6:
        raise AssertionError(
            "write_mixed dispatches must be exactly 6 builder + 6 runner slices"
        )

    ownership_map: list[tuple[str, list[str]]] = []
    for payload in builders:
        if not payload["ownership_paths"]:
            raise AssertionError(
                f"{payload['slice_id']}: builder slice must declare ownership_paths"
            )
        if not payload["allowed_paths"]:
            raise AssertionError(
                f"{payload['slice_id']}: builder slice must declare allowed_paths"
            )
        ownership_map.append((payload["slice_id"], payload["ownership_paths"]))

    for i in range(len(ownership_map)):
        left_id, left_paths = ownership_map[i]
        for j in range(i + 1, len(ownership_map)):
            right_id, right_paths = ownership_map[j]
            for left_path in left_paths:
                for right_path in right_paths:
                    if overlaps(left_path, right_path):
                        raise AssertionError(
                            "Ownership overlap between builder slices "
                            f"{left_id} and {right_id}: {left_path!r} vs {right_path!r}"
                        )

    workstreams = validate_dispatches(
        E2E_DIR / "dispatches.workstreams.json", expected_count=9
    )
    assert_swarm_ticket_invariants(workstreams)

    council_bootstrap = validate_dispatches(
        E2E_DIR / "dispatches.council_bootstrap.json", expected_count=2
    )
    assert_council_bootstrap_invariants(council_bootstrap)


def main() -> None:
    assert_dispatch_invariants()
    validate_results()
    print("OK: fixtures + invariants (swarm-first)")


if __name__ == "__main__":
    main()
