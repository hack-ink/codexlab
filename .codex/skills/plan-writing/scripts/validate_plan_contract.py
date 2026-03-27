#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from plan_contract import parse_contract_text


def require_json_artifact_path(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.suffix != ".json":
        raise ValueError(f"saved plan path must use a .json suffix: {resolved}")
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a persisted or raw plan/1 contract."
    )
    parser.add_argument(
        "--path",
        type=Path,
        help="Optional plan file to validate. If omitted, read input from stdin.",
    )
    return parser.parse_args()


def read_input(args: argparse.Namespace) -> tuple[str, bool]:
    if args.path is None:
        return sys.stdin.read(), False
    path = require_json_artifact_path(args.path)
    return path.read_text(encoding="utf-8"), True


def main() -> int:
    args = parse_args()
    try:
        raw_text, from_saved_file = read_input(args)
    except (OSError, ValueError) as err:
        print(f"plan/1 invalid: {err}", file=sys.stderr)
        return 2
    result = parse_contract_text(raw_text, from_saved_file=from_saved_file)
    if not result.ok:
        for error in result.errors:
            print(f"plan/1 invalid: {error}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
