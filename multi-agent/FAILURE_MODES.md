# Failure Modes (Two-State Multi)

Use this when a run becomes unreliable (stalls, schema failures, ownership deadlocks, or over-splitting).

## 1) Schema-invalid output

1. `send_input(interrupt=true)` requesting a strict schema retry (JSON-only).
2. If retry fails, `close_agent` and re-dispatch a narrowed slice.
3. After repeated failures, mark `blocked` with evidence.

## 2) Stuck/slow worker

1. Interrupt and request a checkpoint: state, last action, next 3 steps, blocked reason.
2. If the worker is a Builder and owned diffs may already have landed, switch to salvage mode before re-dispatch:
   - close the original stuck worker before dispatching any follow-up Builder so salvage continues from a single live owner
   - independently inspect the owned diff and run fresh targeted verification before adopting any landed changes
   - record scheduler-local provenance for the adoption decision, including the interrupted `slice_id`, current `work_package_id`, verification evidence, and whether the package is complete or still partial
   - keep the same parent and same `work_package_id` only while the redispatch stays under the same `ownership_paths`; mint a new work package when ownership changes
   - escalate to human takeover or `blocked` if the landed state cannot be verified safely
3. If no owned diffs landed, close and re-dispatch smaller scope.
4. If the same stall repeats, require an Inspector pre-mortem before continuing.

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
- ticket storm: dispatch count keeps rising while net completed work per ticket stays low
- dispatch overhead dominates runtime (wait-any refill latency is mostly scheduling round-trips)

Fix:

- merge micro-slices into coherent Builder work packages per owned area
- reduce initial Builder package count and expand only after first-wave evidence
- enforce per-worker handoff budget; request merged packages when budget is exceeded
- keep Runner probes broad and few, not a swarm of tiny greps
