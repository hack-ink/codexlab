# Broker E2E (interactive, Swarm-first)

This is an interactive end-to-end test that exercises the protocol in a real Codex session (as the Broker).

It is intentionally separate from `dev/multi-agent/e2e/run_smoke.py`, which validates schemas + fixtures without spawning agents.

## Goals

- Verify the Broker routing gate (the 90-second rule) is applied consistently.
- Verify the `max_depth=1` broker topology and spawn allowlists are respected in practice.
- Verify ticket-board scheduling uses wait-any replenishment and closes completed children.
- Verify optional Inspector review works for write/mixed runs.

## Preconditions

- Runtime config:
  - `max_depth = 1`
  - `max_threads` is non-trivial (`>= 8` is usually enough for a small window).
- You can access the Codex TUI log: `~/.codex/log/codex-tui.log`.

## Test A - Routing gate (should stay single)

Goal: confirm small, clear tasks do not enter multi-agent mode.

1. Pick a tiny local-only task (example: rename one variable or adjust one doc line).
2. As Broker, record:
   - `t_max_s` (must be `<= 90`)
   - `t_why`
   - `route="single"`
3. Execute the change in `single`.

Pass criteria:

- Broker does not spawn any agents.
- Task completes with `route="single"`.

## Test B - Routing gate (must use `multi`, Swarm-first)

Goal: confirm `route="multi"` uses ticket-board scheduling, not a linear planning bottleneck.

1. Pick a task estimated `> 90` seconds (or high uncertainty) and route as `multi`.
2. Prepare at least 3 lanes:
   - one runner lane (`runner`) for probes/inventory,
   - one builder lane (`builder`) for scoped edits,
   - one inspector lane (`inspector`) for risk/evidence checks.
3. As Broker, record:
   - `t_max_s` (`> 90`) and `t_why`,
   - `route="multi"`.
4. Run the protocol:
   - Broker dispatches JSON-only `task-dispatch/1` tickets for allowed agent types (`runner`, `builder`, `inspector`).
   - Broker schedules with wait-any (`functions.wait`) and replenishes when slots free up.
   - Broker enforces write ownership locks (no overlapping in-flight `ownership_paths` for builder tickets).
   - Workers may return `handoff_requests`; Broker validates and enqueues them before dispatching.

Simple log-check in `~/.codex/log/codex-tui.log`:

- `functions.wait` appears repeatedly during active runs.
- new dispatches appear after completed waits (replenishment loop).
- no spawned worker launches another worker (depth remains 1).

Pass criteria:

- No non-Broker spawns occur (brokered topology).
- `functions.wait` is used with wait-any behavior and the run does not stop while children remain in-flight.
- No direct Broker repo writes occur in `multi`.
- Only allowed agent types are dispatched (`runner`, `builder`, `inspector`).
- Worker outputs are raw JSON (no markdown/code fences) and match their schemas.
- If any worker returns invalid/non-JSON output, Broker runs remediation (`send_input(interrupt=true)`, then close/re-dispatch when needed).

## Test C - Supervision (stall / crash handling)

Goal: confirm Broker does not wait forever and can recover from stalled/failed slices.

1. Pick a task with at least 2 runner slices where one can plausibly stall.
2. Ensure supervision loop follows `multi-agent/PLAYBOOK.md`:
   - bounded wait-any polling,
   - timeout interruption (`send_input(interrupt=true)`),
   - close/re-dispatch or explicit blocked outcome.

Pass criteria:

- Broker continues progress while other runnable work exists.
- If a slice fails or stalls beyond timeout, run retries safely or exits as blocked with explicit evidence.

## Notes

- This test targets real runtime behavior (tool registration, depth caps, thread scheduling).
- Use the TUI log as evidence; this document does not prescribe an automated log verifier.
