#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from plan_contract import parse_contract_text, render_contract_json


def require_json_artifact_path(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.suffix != ".json":
        raise ValueError(f"saved plan path must use a .json suffix: {resolved}")
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize a plan/1 contract into canonical JSON for saved plan artifacts."
    )
    parser.add_argument(
        "--path",
        type=Path,
        help="Optional plan file to read. If omitted, read raw input from stdin.",
    )
    return parser.parse_args()


def read_input(args: argparse.Namespace) -> str:
    if args.path is None:
        return sys.stdin.read()
    path = require_json_artifact_path(args.path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        raw_text = read_input(args)
    except (OSError, ValueError) as err:
        print(f"plan/1 invalid: {err}", file=sys.stderr)
        return 2
    result = parse_contract_text(raw_text, from_saved_file=args.path is not None)
    if not result.ok or result.contract is None:
        for error in result.errors:
            print(f"plan/1 invalid: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(render_contract_json(result.contract))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
