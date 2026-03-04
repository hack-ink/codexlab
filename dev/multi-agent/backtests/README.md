# Swarm Backtests (Deterministic)

This directory contains deterministic broker scheduling backtests for the Swarm-first protocol.

The simulator covers scheduler behaviors that fixture/schema checks cannot prove:

- wait-any replenishment vs wait-all wave scheduling
- write-lock enforcement for overlapping builder ownership
- handoff dedup merge behavior
- retry handling for failed attempts
- observable concurrency

## Run

From the repo root:

```sh
python3 dev/multi-agent/backtests/run_backtests.py
```

Or run the full smoke gate:

```sh
python3 dev/multi-agent/e2e/run_smoke.py
```

## Scenario layout

Each scenario folder contains:

- `scenario.json`: scheduler config, deterministic durations/failures, expectations
- `dispatches.initial.json`: initial ticket board
- `handoff.*.json`: deterministic handoff payload fixtures
- `MANUAL.md`: manual replay/inspection notes
