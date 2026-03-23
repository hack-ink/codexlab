#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "research" / "SKILL.md"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"research skill must contain {needle!r}")


def main() -> int:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: research",
        "repeated local attempts on the same problem are failing",
        "Before a fourth substantial attempt on the same error class",
        "workaround, bypass, or brittle patch",
        "Treat a substantial attempt as one that changes a concrete hypothesis",
        "Do not count repeated reruns, extra logging, or near-identical parameter tweaking",
        "If the same error class still persists after 3 substantial attempts",
        "If 10-15 minutes of work produced no new root-cause evidence",
        "If you cannot explain the failure mechanism",
        "**Escalation trigger**",
        "Continuing a workaround loop past the third substantial attempt",
    ]:
        assert_contains(text, needle)
    print("OK: research skill captures escalation before workaround loops")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
