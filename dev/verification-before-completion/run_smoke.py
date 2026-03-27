#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = (
    REPO_ROOT / ".codex" / "skills" / "verification-before-completion" / "SKILL.md"
)


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"verification-before-completion skill must contain {needle!r}")


def main() -> int:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: verification-before-completion",
        "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE",
        "Evidence before claims, always.",
        "Tests pass",
        "Build succeeds",
        "No shortcuts for verification.",
    ]:
        assert_contains(text, needle)
    print("OK: verification-before-completion gate is present in source repo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
