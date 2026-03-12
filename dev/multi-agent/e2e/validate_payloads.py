from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import textwrap
from typing import Any

from schema_support import (
    REPO_ROOT,
    SKILL_ROOT,
    schema_path_for_id,
    validator_for_id,
    validators_by_id,
)

E2E_DIR = Path(__file__).resolve().parent
DISPATCH_SCHEMA_ID = "ticket-dispatch/1"
RESULT_SCHEMA_ID = "ticket-result/1"
SINGLE_FAST_PATH_MAX_S = 90
ALLOWED_ROLES = {"runner", "builder", "inspector"}
SKILL_ROUTING_HELPER_PATH = (
    REPO_ROOT / "skill-routing" / "scripts" / "build_child_skill_policy.py"
)
SKILL_ROUTING_POLICY_PATH = REPO_ROOT / "skill-routing" / "child-skill-policy.toml"
FORBIDDEN_FIELDS = {
    "agent_type",
    "authorized_skills",
    "evidence_requirements",
    "handoff_requests",
    "recovery",
    "slice_id",
    "slice_kind",
    "ssot_id",
    "task_contract",
    "task_id",
    "work_package_id",
}

DISPATCH_FIXTURES = [E2E_DIR / "dispatches.multi.json"]
RESULT_FIXTURES = [
    E2E_DIR / "result.runner.done.json",
    E2E_DIR / "result.builder.done.json",
    E2E_DIR / "result.builder.blocked.json",
    E2E_DIR / "result.inspector.pass.json",
    E2E_DIR / "result.inspector.needs_evidence.json",
]


def load_skill_policy_helper() -> Any:
    spec = importlib.util.spec_from_file_location(
        "build_child_skill_policy", SKILL_ROUTING_HELPER_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError(
            f"Unable to load shared skill policy helper at {SKILL_ROUTING_HELPER_PATH}"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SKILL_POLICY_HELPER = load_skill_policy_helper()


def load_json(path: Path) -> Any:
    text = path.read_text()
    stripped = text.strip()
    if stripped.startswith("```") or stripped.endswith("```"):
        raise AssertionError(f"{path.name}: payloads must be raw JSON only")
    return json.loads(stripped)


def validate_one(schema_id: str, payload: dict[str, Any], label: str) -> None:
    validator = validator_for_id(schema_id)
    validator.validate(payload)
    schema_path = schema_path_for_id(schema_id)
    print(f"OK: {label} against {schema_path.relative_to(SKILL_ROOT)}")


def ensure_no_forbidden_fields(payload: Any, *, label: str) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_FIELDS:
                raise AssertionError(f"{label}: forbidden legacy field {key!r}")
            ensure_no_forbidden_fields(value, label=f"{label}.{key}")
        return
    if isinstance(payload, list):
        for index, item in enumerate(payload):
            ensure_no_forbidden_fields(item, label=f"{label}[{index}]")


def assert_known_schema_catalog() -> None:
    schema_ids = set(validators_by_id())
    expected = {DISPATCH_SCHEMA_ID, RESULT_SCHEMA_ID}
    if schema_ids != expected:
        raise AssertionError(f"schema catalog mismatch: expected {expected}, got {schema_ids}")
    print(f"OK: schema catalog contains only {sorted(expected)}")


def assert_route_cases() -> None:
    cases = load_json(E2E_DIR / "route_cases.json")
    if not isinstance(cases, list) or not cases:
        raise AssertionError("route_cases.json must be a non-empty list")

    for index, case in enumerate(cases, 1):
        label = f"route_cases[{index}]"
        required = {"label", "tiny_clear_low_risk", "t_max_s", "expected_route"}
        missing = required - set(case)
        if missing:
            raise AssertionError(f"{label}: missing keys {sorted(missing)}")
        expected = "single" if case["tiny_clear_low_risk"] and case["t_max_s"] <= SINGLE_FAST_PATH_MAX_S else "multi"
        if case["expected_route"] != expected:
            raise AssertionError(
                f"{label}: expected_route={case['expected_route']!r} does not match derived {expected!r}"
            )

    print(f"OK: route cases ({len(cases)})")


def assert_dispatch_fixture(path: Path) -> None:
    payload = load_json(path)
    if not isinstance(payload, list) or not payload:
        raise AssertionError(f"{path.name}: expected a non-empty array of dispatches")

    ticket_ids: set[str] = set()
    seen_run_ids: set[str] = set()
    for index, dispatch in enumerate(payload, 1):
        label = f"{path.name}[{index}]"
        if not isinstance(dispatch, dict):
            raise AssertionError(f"{label}: expected object")
        ensure_no_forbidden_fields(dispatch, label=label)
        validate_one(DISPATCH_SCHEMA_ID, dispatch, label)

        role = dispatch["role"]
        if role not in ALLOWED_ROLES:
            raise AssertionError(f"{label}: unexpected role {role!r}")

        ticket_id = dispatch["ticket_id"]
        if ticket_id in ticket_ids:
            raise AssertionError(f"{label}: duplicate ticket_id {ticket_id!r}")
        ticket_ids.add(ticket_id)
        seen_run_ids.add(dispatch["run_id"])

        write_scope = dispatch.get("write_scope", [])
        if role == "builder":
            if not write_scope:
                raise AssertionError(f"{label}: builder dispatch must declare write_scope")
        elif write_scope:
            raise AssertionError(f"{label}: non-builder dispatch must not declare write_scope")

        review_mode = dispatch.get("review_mode")
        if role == "inspector":
            if review_mode is None:
                raise AssertionError(f"{label}: inspector dispatch should declare review_mode in this fixture set")
        elif review_mode is not None:
            raise AssertionError(f"{label}: non-inspector dispatch must not declare review_mode")

    if len(seen_run_ids) != 1:
        raise AssertionError(f"{path.name}: all dispatches must share one run_id, got {seen_run_ids}")
    for index, dispatch in enumerate(payload, 1):
        label = f"{path.name}[{index}]"
        for dependency in dispatch.get("depends_on", []):
            if dependency not in ticket_ids:
                raise AssertionError(f"{label}: unknown dependency {dependency!r}")

    print(f"OK: dispatch fixture ({path.name})")


def load_manual_skill_policy() -> dict[str, Any]:
    if hasattr(SKILL_POLICY_HELPER, "load_policy"):
        return SKILL_POLICY_HELPER.load_policy(SKILL_ROUTING_POLICY_PATH.resolve())
    raise AssertionError("Shared skill policy helper must expose load_policy()")


def assert_child_policy_behavior() -> None:
    manual_policy = {
        "version": getattr(SKILL_POLICY_HELPER, "POLICY_VERSION", 4),
        "main_thread_only": ["multi-agent", "pre-commit"],
    }

    if SKILL_POLICY_HELPER.resolve_skill_policy("multi-agent", policy=manual_policy) != "main-thread-only":
        raise AssertionError("child_policy_behavior: multi-agent must resolve as main-thread-only")
    if SKILL_POLICY_HELPER.resolve_skill_policy("rust-policy", policy=manual_policy) != "any-agent":
        raise AssertionError("child_policy_behavior: omitted skills must resolve as any-agent")

    try:
        SKILL_POLICY_HELPER.validate_child_skill_use("multi-agent", policy=manual_policy)
    except ValueError as exc:
        if "main-thread-only" not in str(exc):
            raise AssertionError(
                f"child_policy_behavior.blocked: expected main-thread-only error, got {exc!r}"
            ) from exc
        print(f"OK: child_policy_behavior.blocked rejected ({exc})")
    else:
        raise AssertionError("child_policy_behavior.blocked: expected rejection")

    SKILL_POLICY_HELPER.validate_child_skill_use("rust-policy", policy=manual_policy)
    print("OK: child_policy_behavior.omitted_allowed")

    loaded_manual_policy = load_manual_skill_policy()
    if SKILL_POLICY_HELPER.resolve_skill_policy("multi-agent", policy=loaded_manual_policy) != "any-agent":
        raise AssertionError("repo manual policy should leave omitted skills allowed by default")
    print("OK: repo child policy keeps omitted skills allowed")


def assert_manual_policy_negative_cases() -> None:
    cases = [
        (
            "unknown_skill_entry",
            """
            version = 4

            main_thread_only = ["not-a-real-skill"]
            """,
            "known local skills",
        ),
        (
            "legacy_default_child_policy",
            """
            version = 4
            default_child_policy = "main-thread-only"
            """,
            "unexpected keys: default_child_policy",
        ),
        (
            "legacy_skills_table",
            """
            version = 4

            [skills]
            "multi-agent" = "main-thread-only"
            """,
            "unexpected keys: skills",
        ),
        (
            "unsupported_version",
            """
            version = 3

            main_thread_only = ["multi-agent"]
            """,
            "Unsupported policy version",
        ),
    ]

    for label, raw_policy, expected_substring in cases:
        with tempfile.TemporaryDirectory() as tmp_dir:
            policy_path = Path(tmp_dir) / "child-skill-policy.toml"
            policy_path.write_text(textwrap.dedent(raw_policy).strip() + "\n", encoding="utf-8")
            try:
                SKILL_POLICY_HELPER.load_policy(policy_path)
            except ValueError as exc:
                message = str(exc)
                if expected_substring not in message:
                    raise AssertionError(
                        f"manual_policy.{label}: expected {expected_substring!r}, got {message!r}"
                    ) from exc
                print(f"OK: manual_policy.{label} rejected ({message})")
                continue
            raise AssertionError(f"manual_policy.{label}: expected rejection")


def assert_result_fixture(path: Path) -> None:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise AssertionError(f"{path.name}: expected object")

    ensure_no_forbidden_fields(payload, label=path.name)
    validate_one(RESULT_SCHEMA_ID, payload, path.name)

    role = payload["role"]
    if role not in ALLOWED_ROLES:
        raise AssertionError(f"{path.name}: unexpected role {role!r}")

    status = payload["status"]
    if status not in {"done", "blocked"}:
        raise AssertionError(f"{path.name}: unexpected status {status!r}")

    if role == "builder" and status == "done" and not payload.get("changed_paths"):
        raise AssertionError(f"{path.name}: builder done result must include changed_paths")
    if status == "blocked" and not payload.get("unblock"):
        raise AssertionError(f"{path.name}: blocked result must include unblock")
    if role == "inspector" and payload.get("verdict") is None:
        raise AssertionError(f"{path.name}: inspector result must include verdict")
    if role != "inspector" and payload.get("verdict") is not None:
        raise AssertionError(f"{path.name}: only inspector results may include verdict")

    print(f"OK: result fixture ({path.name})")


def main() -> None:
    assert_known_schema_catalog()
    assert_route_cases()

    for path in DISPATCH_FIXTURES:
        assert_dispatch_fixture(path)

    assert_child_policy_behavior()
    assert_manual_policy_negative_cases()

    for path in RESULT_FIXTURES:
        assert_result_fixture(path)

    print("OK: e2e payload fixtures align with the reset protocol")


if __name__ == "__main__":
    main()
