from __future__ import annotations

from pathlib import Path

from broker_sim import BrokerSimulator, load_json

BACKTESTS_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BACKTESTS_DIR / "scenarios"


def assert_expectations(
    scenario_id: str,
    expectations: dict,
    wait_any: dict,
    wait_all: dict,
) -> None:
    min_parallel = int(expectations.get("min_max_parallel", 1))
    if wait_any["max_parallel"] < min_parallel:
        raise AssertionError(
            f"{scenario_id}: max_parallel={wait_any['max_parallel']} < {min_parallel}"
        )

    min_lock_conflicts = int(expectations.get("min_lock_conflicts", 0))
    if wait_any["lock_conflicts"] < min_lock_conflicts:
        raise AssertionError(
            f"{scenario_id}: lock_conflicts={wait_any['lock_conflicts']} < {min_lock_conflicts}"
        )

    min_dedup_merged = int(expectations.get("min_dedup_merged", 0))
    if wait_any["dedup_merged"] < min_dedup_merged:
        raise AssertionError(
            f"{scenario_id}: dedup_merged={wait_any['dedup_merged']} < {min_dedup_merged}"
        )

    min_retry_count = int(expectations.get("min_retry_count", 0))
    if wait_any["retry_count"] < min_retry_count:
        raise AssertionError(
            f"{scenario_id}: retry_count={wait_any['retry_count']} < {min_retry_count}"
        )

    expected_dispatch_count = expectations.get("expected_dispatch_count")
    if expected_dispatch_count is not None and wait_any["dispatch_count"] != int(
        expected_dispatch_count
    ):
        raise AssertionError(
            f"{scenario_id}: dispatch_count={wait_any['dispatch_count']} != {expected_dispatch_count}"
        )

    speedup_s = wait_all["makespan_s"] - wait_any["makespan_s"]
    min_speedup = int(expectations.get("min_wait_any_speedup_s", 0))
    if speedup_s < min_speedup:
        raise AssertionError(
            f"{scenario_id}: wait-any speedup={speedup_s}s < {min_speedup}s"
        )

    expected_wait_any = expectations.get("expected_wait_any_makespan_s")
    if expected_wait_any is not None and wait_any["makespan_s"] != int(expected_wait_any):
        raise AssertionError(
            f"{scenario_id}: wait_any makespan={wait_any['makespan_s']} != {expected_wait_any}"
        )

    expected_wait_all = expectations.get("expected_wait_all_makespan_s")
    if expected_wait_all is not None and wait_all["makespan_s"] != int(expected_wait_all):
        raise AssertionError(
            f"{scenario_id}: wait_all makespan={wait_all['makespan_s']} != {expected_wait_all}"
        )

    expected_ids = expectations.get("expected_completed_slice_ids")
    if expected_ids is not None:
        expected_set = sorted(set(expected_ids))
        actual_set = sorted(set(wait_any["completed_slice_ids"]))
        if actual_set != expected_set:
            raise AssertionError(
                f"{scenario_id}: completed slices mismatch: expected={expected_set}, got={actual_set}"
            )


def run_scenario(scenario_dir: Path) -> tuple[str, dict, dict]:
    scenario = load_json(scenario_dir / "scenario.json")
    scenario_id = scenario["id"]
    expectations = scenario.get("expectations", {})

    wait_any = BrokerSimulator(scenario_dir, scenario, mode="wait_any").run()
    wait_all = BrokerSimulator(scenario_dir, scenario, mode="wait_all").run()

    assert_expectations(scenario_id, expectations, wait_any, wait_all)

    speedup_s = wait_all["makespan_s"] - wait_any["makespan_s"]
    print(
        "PASS: "
        f"{scenario_id} "
        f"wait_any={wait_any['makespan_s']}s "
        f"wait_all={wait_all['makespan_s']}s "
        f"speedup={speedup_s}s "
        f"parallel={wait_any['max_parallel']} "
        f"retry={wait_any['retry_count']} "
        f"dedup={wait_any['dedup_merged']} "
        f"lock_conflicts={wait_any['lock_conflicts']} "
        f"dispatch={wait_any['dispatch_count']}"
    )
    return scenario_id, wait_any, wait_all


def main() -> None:
    scenario_dirs = sorted(
        path for path in SCENARIOS_DIR.iterdir() if (path / "scenario.json").exists()
    )
    if not scenario_dirs:
        raise AssertionError(f"No scenario.json files found under {SCENARIOS_DIR}")

    results: dict[str, tuple[dict, dict]] = {}
    for scenario_dir in scenario_dirs:
        scenario_id, wait_any, wait_all = run_scenario(scenario_dir)
        results[scenario_id] = (wait_any, wait_all)

    if "swarmbench-02-micro" in results and "swarmbench-02-pack" in results:
        micro_wait_any = results["swarmbench-02-micro"][0]["makespan_s"]
        pack_wait_any = results["swarmbench-02-pack"][0]["makespan_s"]
        if (micro_wait_any - pack_wait_any) < 10:
            raise AssertionError(
                "cross-scenario regression failed: "
                f"micro wait_any={micro_wait_any}s should be at least 10s slower than "
                f"pack wait_any={pack_wait_any}s"
            )

    print(f"OK: backtests ({len(scenario_dirs)} scenarios)")


if __name__ == "__main__":
    main()
