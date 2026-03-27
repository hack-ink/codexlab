#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / ".codex" / "skills" / "workspace-reconcile" / "SKILL.md"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"workspace-reconcile skill must contain {needle!r}")


def main() -> int:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: workspace-reconcile",
        ".workspaces/*",
        "surviving lane",
        "donor",
        "cleanup_candidates",
        "needs_resplit",
        "canonical regeneration path",
        "does not create or remove workspaces",
    ]:
        assert_contains(text, needle)
    print("OK: workspace-reconcile contract covers surviving-lane-only reconciliation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
