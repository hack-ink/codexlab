#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "receiving-code-review" / "SKILL.md"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"receiving-code-review skill must contain {needle!r}")


def main() -> int:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: receiving-code-review",
        "Verify before implementing.",
        "Technical correctness over social comfort.",
        "Push back with technical reasoning",
        "GitHub Thread Replies",
        "not as a top-level PR comment",
    ]:
        assert_contains(text, needle)
    print("OK: receiving-code-review contract is present in source repo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
