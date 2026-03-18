#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "pr-land" / "SKILL.md"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"pr-land skill must contain {needle!r}")


def main() -> int:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: pr-land",
        "`merged`",
        "`not_ready`",
        "`needs_sync`",
        "`blocked`",
        "`delivery/1`",
        "`delivery-prepare`",
        "`delivery-closeout`",
        "do not squash",
    ]:
        assert_contains(text, needle)
    print("OK: pr-land contract captures readiness and delivery-history merge policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
