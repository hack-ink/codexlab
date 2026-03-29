#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import re
import sys


def fail(message: str) -> None:
    print(f"VALIDATION_ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    if not run_dir.is_dir():
        fail(f"run dir not found: {run_dir}")

    if run_dir.parent.name != "runs" or run_dir.parent.parent.name != "research" or run_dir.parent.parent.parent.name != "docs":
        fail("run dir must live under docs/research/runs/<run-id>/")
    project_root = run_dir.parent.parent.parent.parent
    index_path = project_root / "docs/research/index.json"
    if not index_path.is_file():
        fail(f"missing research index at {index_path}")

    required = {
        "research-brief.md": run_dir / "research-brief.md",
        "evidence-map.md": run_dir / "evidence-map.md",
        "final-report.md": run_dir / "final-report.md",
        "report.json": run_dir / "report.json",
    }
    for label, path in required.items():
        if not path.is_file():
            fail(f"missing required artifact {label} at {path}")

    option_path = run_dir / "option-analysis.md"
    report = json.loads(required["report.json"].read_text())

    if report.get("schema") != "research-report/1":
        fail("report.json schema must be research-report/1")

    run_id = report.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        fail("report.json run_id missing")

    if run_dir.name != run_id:
        fail(f"run dir name {run_dir.name} does not match run_id {run_id}")

    artifact_paths = report.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        fail("report.json artifact_paths missing")

    expected = {
        "research_brief": str(Path("docs/research/runs") / run_id / "research-brief.md"),
        "evidence_map": str(Path("docs/research/runs") / run_id / "evidence-map.md"),
        "final_report": str(Path("docs/research/runs") / run_id / "final-report.md"),
        "machine_report": str(Path("docs/research/runs") / run_id / "report.json"),
    }
    if option_path.exists():
        expected["option_analysis"] = str(Path("docs/research/runs") / run_id / "option-analysis.md")
    else:
        expected["option_analysis"] = None

    for key, value in expected.items():
        if artifact_paths.get(key) != value:
            fail(f"artifact_paths.{key} expected {value!r}, got {artifact_paths.get(key)!r}")

    final_report = required["final-report.md"].read_text()
    brief = required["research-brief.md"].read_text()

    for label, content in [("brief", brief), ("final report", final_report)]:
        if run_id not in content:
            fail(f"{label} does not mention run_id {run_id}")

    challenge_mode = report.get("challenge_mode")
    if challenge_mode not in {"plugin_skeptic", "local_fallback"}:
        fail("report.json challenge_mode must be plugin_skeptic or local_fallback")
    if f"Challenge mode (`plugin_skeptic` or `local_fallback`): `{challenge_mode}`" not in final_report:
        fail("final-report.md challenge mode does not match report.json")

    confidence = report.get("confidence")
    if confidence not in {"low", "medium", "high"}:
        fail("report.json confidence must be low, medium, or high")
    if f"- Confidence: `{confidence}`" not in final_report:
        fail("final-report.md confidence does not match report.json")

    if report.get("status") not in {"decision-ready", "not-decision-ready"}:
        fail("report.json status must be decision-ready or not-decision-ready")

    worker_usage = report.get("worker_usage")
    if not isinstance(worker_usage, dict):
        fail("report.json worker_usage missing")
    worker_patterns = {
        "scout": r"- Scout \(`not_used`, `plugin_scout`, or `local_fallback`\): `([^`]+)`",
        "analyst": r"- Analyst \(`not_used`, `plugin_analyst`, or `local_fallback`\): `([^`]+)`",
        "skeptic": r"- Skeptic \(`not_used`, `plugin_skeptic`, or `local_fallback`\): `([^`]+)`",
    }
    for key, pattern in worker_patterns.items():
        match = re.search(pattern, final_report)
        if not match:
            fail(f"final-report.md missing worker usage for {key}")
        if worker_usage.get(key) != match.group(1):
            fail(f"worker_usage.{key} mismatch between report.json and final-report.md")

    index = json.loads(index_path.read_text())
    if index.get("schema") != "research-index/1":
        fail("docs/research/index.json schema must be research-index/1")
    runs = index.get("runs")
    if not isinstance(runs, list):
        fail("docs/research/index.json runs must be a list")

    matching_entries = [entry for entry in runs if isinstance(entry, dict) and entry.get("run_id") == run_id]
    if len(matching_entries) != 1:
        fail(f"docs/research/index.json must contain exactly one entry for run_id {run_id}")
    entry = matching_entries[0]

    for key in ["question", "status", "confidence"]:
        if entry.get(key) != report.get(key):
            fail(f"index entry field {key!r} does not match report.json")

    entry_paths = entry.get("artifact_paths")
    if not isinstance(entry_paths, dict):
        fail("index entry artifact_paths missing")
    for key, value in expected.items():
        if entry_paths.get(key) != value:
            fail(f"index entry artifact_paths.{key} expected {value!r}, got {entry_paths.get(key)!r}")

    print("RESEARCH_RUN_VALID")


if __name__ == "__main__":
    main()
