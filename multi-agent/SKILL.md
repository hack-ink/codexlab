---
name: multi-agent
description: Use when a task benefits from Swarm-first parallel workers with Broker-only spawning (`max_depth=1`), schema-validated messages, and explicit ownership locks.
---

# Multi-Agent (Swarm-First)

## Path conventions

All paths in this skill are relative to the **skill root** (the directory that contains this `SKILL.md`).

In Codex, locate the skill root using the runtime skills list (it provides the absolute path to this `SKILL.md`), then open `PLAYBOOK.md` in the same directory.

## Objective

Provide a reliable, auditable Swarm-first workflow for multi-agent execution: ticket-board scheduling, explicit ownership, evidence-backed verification, and optional quality review.

## Role terminology

Concept roles are used for protocol clarity:

- **Broker**: the main thread.
- **Runner**: command and investigation worker (`agent_type="runner"`).
- **Builder**: write-capable worker (`agent_type="builder"`).
- **Inspector**: review worker (`agent_type="inspector"`).

## When to use

- The task is non-trivial and benefits from parallel slices (especially mixed read/write work).
- You need strict spawn topology guarantees and schema-validated messages.
- The Broker needs wait-any replenishment instead of a fixed linear pipeline.

## Inputs

- Task goal, scope, and constraints (including no-go areas).
- Routing decision: `single` or `multi` (90s rule).
- Ownership scopes for write slices (must be disjoint in-flight).
- Minimum verification evidence expected before closeout.

## Hard gates (non-negotiable)

- Short-circuit unless `route="multi"` (no spawns in `single`).
- There is no mandatory planning gate or workstream-first ordering.
- Enforce brokered spawning (`max_depth=1`): only the Broker uses collab tools (`spawn_agent`, `wait`, `send_input`, `close_agent`).
- In `multi`, Broker never writes repo content (`apply_patch` or direct edits are prohibited).
- All repo writes are delegated to `agent_type="builder"` slices.
- Enforce ownership locks for write slices (no overlapping `ownership_paths` in-flight).
- Enforce wait-any replenishment (no spawn-wave + wait-all scheduling).
- Close completed children to avoid thread starvation.

## How to use

Read `PLAYBOOK.md` and follow it literally for ticket-board lifecycle, lane caps, and handoff handling.

If `route="multi"` and the task is uncertain, mixed read/write, or likely to exceed a single coherent Builder timebox:

- Open `BROKER_SPLIT.md` before scheduling the first write wave.
- Apply `WORKER_PROTOCOL.md` when drafting dispatch contracts and evaluating handoff requests.
- Use `FAILURE_MODES.md` when stalls, schema-invalid output, deadlocks, or over-splitting occur.

## Outputs

- Schema-valid worker results (`runner`, `builder`, `inspector`) using JSON-only payloads.

## Notes

- This skill uses a Swarm-first protocol: dynamic ticket generation plus brokered handoffs.
- Council defaults are documented in [`COUNCIL.md`](COUNCIL.md) as optional bootstrap templates.
- Schemas are structural; invariants live in the playbook and e2e validator.

## Quick reference

- Playbook: `PLAYBOOK.md`
- Council protocol: `COUNCIL.md`
- Dispatch schema: `schemas/task-dispatch.schema.json` (`schema="task-dispatch/1"`, JSON-only `spawn_agent.message`)
- Worker result schemas:
  - `schemas/worker-result.runner.schema.json` (`schema="worker-result.runner/1"`)
  - `schemas/worker-result.builder.schema.json` (`schema="worker-result.builder/1"`)
- Inspector schema: `schemas/review-result.inspector.schema.json` (`schema="review-result.inspector/1"`)
- `ssot_id` generator: `tools/make_ssot_id.py`
- Council bootstrap helper: `tools/make_council_bootstrap.py`
- Dev-only smoke (skills repo only): `python3 dev/multi-agent/e2e/run_smoke.py`

## Common mistakes

- Non-Broker spawning (impossible under `max_depth=1`, but still a common prompt mistake).
- Dispatch payload not being JSON-only `task-dispatch/1`.
- Worker outputs in markdown/code fences; all worker outputs and dispatches must be raw JSON-only.
- Wait-all behavior instead of wait-any replenishment.
- Returning while any child remains in-flight.
- Forgetting to `close_agent` for completed children.
- Over-splitting into micro-slices where coordination dominates useful work.
