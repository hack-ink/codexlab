#!/usr/bin/env python3
"""Validate or initialize the manual child skill policy."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib


POLICY_VERSION = 4
DEFAULT_CHILD_POLICY = "any-agent"
MAIN_THREAD_ONLY_POLICY = "main-thread-only"
ALLOWED_KEYS = {"version", "main_thread_only"}
SKILLS_REPO_ROOT = Path(__file__).resolve().parents[2]
EMPTY_TEMPLATE_COMMENTS = [
    "# Optional denylist. Omitted skills are allowed by default.",
    "# Add known local skill names only when children must never self-initiate them.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate or initialize the manual child skill policy."
    )
    skill_root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--policy",
        type=Path,
        default=skill_root / "child-skill-policy.toml",
        help="Policy file to read/write.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the canonical policy to --policy instead of printing it.",
    )
    return parser.parse_args()


def normalize_skill_list(raw: object, field_name: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(f"{field_name} must be a TOML array")

    normalized: list[str] = []
    for value in raw:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")
        normalized.append(value)
    return sorted(set(normalized))


def list_known_skills(skills_root: Path = SKILLS_REPO_ROOT) -> set[str]:
    known: set[str] = set()

    for entry in sorted(skills_root.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir() and (entry / "SKILL.md").is_file():
            known.add(entry.name)

    system_root = skills_root / ".system"
    if system_root.is_dir():
        for entry in sorted(system_root.iterdir()):
            if entry.name.startswith("."):
                continue
            if entry.is_dir() and (entry / "SKILL.md").is_file():
                known.add(entry.name)

    return known


def blank_policy() -> dict[str, object]:
    return {"version": POLICY_VERSION, "main_thread_only": []}


def load_policy(policy_path: Path) -> dict[str, object]:
    if not policy_path.exists():
        return blank_policy()

    data = tomllib.loads(policy_path.read_text(encoding="utf-8"))
    version = data.get("version", POLICY_VERSION)
    if not isinstance(version, int):
        raise ValueError(f"Invalid version {version!r} in {policy_path}")
    if version != POLICY_VERSION:
        raise ValueError(
            f"Unsupported policy version {version!r} in {policy_path}; "
            f"expected {POLICY_VERSION}"
        )

    unexpected_keys = sorted(key for key in data if key not in ALLOWED_KEYS)
    if unexpected_keys:
        raise ValueError(
            "child-skill-policy.toml only supports version and main_thread_only in "
            f"version {POLICY_VERSION}; unexpected keys: {', '.join(unexpected_keys)}"
        )

    policy = blank_policy()
    policy["main_thread_only"] = normalize_skill_list(
        data.get("main_thread_only"),
        "main_thread_only",
    )
    known_skills = list_known_skills()
    unknown_skills = sorted(
        skill_name
        for skill_name in policy["main_thread_only"]
        if skill_name not in known_skills
    )
    if unknown_skills:
        raise ValueError(
            "child-skill-policy.toml main_thread_only entries must reference known local skills; "
            f"unknown: {', '.join(unknown_skills)}"
        )
    return policy


def resolve_skill_policy(
    skill_name: str,
    *,
    policy: dict[str, object] | None = None,
) -> str:
    if policy is None:
        return DEFAULT_CHILD_POLICY
    main_thread_only = policy.get("main_thread_only", [])
    if not isinstance(main_thread_only, list):
        raise ValueError("policy.main_thread_only must be a list")
    if skill_name in main_thread_only:
        return MAIN_THREAD_ONLY_POLICY
    return DEFAULT_CHILD_POLICY


def validate_child_skill_use(
    skill_name: str,
    *,
    policy: dict[str, object],
) -> None:
    known_skills = list_known_skills()
    if skill_name not in known_skills:
        raise ValueError(
            "child skill use must reference known local skills; "
            f"unknown: {skill_name!r}"
        )
    effective_policy = resolve_skill_policy(skill_name, policy=policy)
    if effective_policy == MAIN_THREAD_ONLY_POLICY:
        raise ValueError(
            f"child agents must not self-initiate main-thread-only skill {skill_name!r}"
        )


def render_policy(policy: dict[str, object]) -> str:
    main_thread_only = policy["main_thread_only"]
    if not isinstance(main_thread_only, list):
        raise ValueError("policy.main_thread_only must be a list")

    lines = [f"version = {policy['version']}", "", *EMPTY_TEMPLATE_COMMENTS]
    if not main_thread_only:
        lines.append("main_thread_only = []")
        return "\n".join(lines) + "\n"

    lines.append("main_thread_only = [")
    for skill_name in main_thread_only:
        lines.append(f'  "{skill_name}",')
    lines.append("]")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    policy = load_policy(args.policy.resolve())
    rendered = render_policy(policy)
    if args.write:
        args.policy.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
