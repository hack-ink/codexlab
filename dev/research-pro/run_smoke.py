#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / ".codex" / "skills" / "research-pro" / "SKILL.md"
LEGACY_WRAPPER = (
    REPO_ROOT / ".codex" / "skills" / "research-pro" / "scripts" / "agent-browser-node.sh"
)
REQUIRED_HELP_NEEDLES = [
    "--session <name>",
    "--session-name <name>",
    "--profile <path>",
    "--headed",
]
FORBIDDEN_SKILL_NEEDLES = [
    "agent-browser-node.sh",
    "Node/Playwright",
    "direct Playwright control",
    "custom Playwright automation",
    "JS wrapper",
    "Node daemon",
    "--native",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the research-pro source contract and optional local CLI surface."
    )
    parser.add_argument(
        "--check-host-cli",
        action="store_true",
        help="Also validate the local agent-browser CLI in PATH.",
    )
    return parser.parse_args()


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        cmd_text = " ".join(cmd)
        raise AssertionError(
            f"command failed: {cmd_text}\n"
            f"cwd: {REPO_ROOT}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return proc


def assert_contains(text: str, needle: str, message: str) -> None:
    if needle not in text:
        raise AssertionError(f"{message}: missing {needle!r}")


def assert_not_contains(text: str, needle: str, message: str) -> None:
    if needle in text:
        raise AssertionError(f"{message}: unexpected {needle!r}")


def assert_skill_doc_current() -> None:
    text = read_text(SKILL_PATH)
    assert_contains(
        text,
        "current host's supported `agent-browser` entrypoint",
        "research-pro skill should stay portable across host packaging shapes",
    )
    assert_contains(
        text,
        "Repair that current-host entrypoint before retrying instead of swapping transports mid-run.",
        "research-pro skill should keep a single transport contract",
    )
    for needle in FORBIDDEN_SKILL_NEEDLES:
        assert_not_contains(text, needle, "research-pro skill should not reference legacy fallback paths")
    print("OK: research-pro skill doc matches the portable agent-browser contract")


def assert_legacy_wrapper_removed() -> None:
    if LEGACY_WRAPPER.exists():
        raise AssertionError(f"legacy wrapper should be removed: {LEGACY_WRAPPER}")
    print("OK: legacy Node wrapper is absent")


def assert_agent_browser_cli() -> None:
    binary = shutil.which("agent-browser")
    if binary is None:
        raise AssertionError("agent-browser not found in PATH")

    resolved_binary = Path(binary).resolve()
    version = run(["agent-browser", "--version"]).stdout.strip()
    assert_contains(version, "agent-browser ", "agent-browser --version should print the CLI version")

    help_text = run(["agent-browser", "--help"]).stdout
    for needle in REQUIRED_HELP_NEEDLES:
        assert_contains(help_text, needle, "agent-browser --help should expose the flags research-pro uses")
    print(f"OK: agent-browser CLI exposes required flags ({resolved_binary})")


def main() -> int:
    args = parse_args()
    assert_skill_doc_current()
    assert_legacy_wrapper_removed()
    if args.check_host_cli:
        assert_agent_browser_cli()
    else:
        print("OK: skipped host agent-browser CLI probe")
    print("OK: research-pro smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
