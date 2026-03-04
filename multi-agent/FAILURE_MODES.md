# Failure Modes (Swarm-First)

Use this when a run becomes unreliable (stalls, schema failures, ownership deadlocks, or over-splitting).

## 1) Schema-invalid output

1. `send_input(interrupt=true)` requesting a strict schema retry (JSON-only).
2. If retry fails, `close_agent` and re-dispatch a narrowed slice.
3. After repeated failures, mark `blocked` with evidence.

## 2) Stuck/slow worker

1. Interrupt and request a checkpoint: state, last action, next 3 steps, blocked reason.
2. If still stuck/non-responsive, close and re-dispatch smaller scope.
3. If the same stall repeats, require an Inspector pre-mortem before continuing.

## 3) Ownership lock deadlock

- If all pending Builder tickets conflict with active locks:
  - keep Runner/Inspector lanes busy (evidence gathering, risk checks)
  - wait-any poll until a Builder completes
  - if no progress is possible, mark `blocked` with the conflicting ownership paths

## 4) Over-splitting

Symptoms:

- tickets are <2 minutes but require heavy coordination
- frequent duplicate handoff requests
- repeated lock conflicts due to sloppy ownership partitioning

Fix:

- merge micro-slices into one coherent Builder ticket per owned area
- keep Runner probes broad and few, not a swarm of tiny greps

