#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "review-repair" / "SKILL.md"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"review-repair skill must contain {needle!r}")


def main() -> int:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: review-repair",
        "`receiving-code-review`",
        "Reply in the GitHub thread",
        "Resolve a thread only",
        "`needs_re_review`",
        "`awaiting_external`",
        "three consecutive rounds",
        "`research`",
    ]:
        assert_contains(text, needle)
    print("OK: review-repair contract captures verified thread repair and resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
