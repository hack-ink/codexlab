# Worker Protocol (Swarm-First)

This document defines how depth-1 workers should behave under the Swarm-first contract.

Hard constraints:

- Workers never spawn; only the Broker spawns (`max_depth=1`).
- `runner` and `inspector` never write repo content.
- Worker outputs must be **JSON-only** and schema-valid.

## Swarm-first defaults (all workers)

- Prefer returning **handoff requests** (new tickets) over expanding scope.
- Keep tickets small enough to finish inside `timebox_minutes`.
- Make dependencies explicit and keep write ownership disjoint.
- If blocked, say exactly what evidence/decision is needed to unblock.

## Runner checklist

- Return concrete evidence (`commands`, `files_read`) for every claim.
- Propose follow-up tickets for:
  - parallelizable probes
  - disjoint write ownership partitions for Builder waves
  - targeted Inspector reviews when risk is high

Runner example (including a handoff request):

```json
{
  "schema": "worker-result.runner/1",
  "ssot_id": "scenario-hash-5277daf391c2",
  "task_id": "example-task",
  "slice_id": "split--runner-boundary-map",
  "role": "runner",
  "status": "done",
  "summary": "Identified two disjoint ownership partitions and one shared dependency gate.",
  "evidence": {
    "commands": [
      {
        "cmd": "rg -n \"foo\" src/",
        "exit_code": 1
      },
      {
        "cmd": "ls -la",
        "exit_code": 0
      }
    ],
    "files_read": [
      "README.md"
    ]
  },
  "next_actions": [
    "Partition A: src/app/ (independent)",
    "Partition B: src/lib/ (independent)",
    "Dependency gate: update schema first"
  ],
  "handoff_requests": [
    {
      "schema": "task-dispatch/1",
      "ssot_id": "scenario-hash-5277daf391c2",
      "task_id": "example-task",
      "slice_id": "wave1--builder-ownership-A",
      "agent_type": "builder",
      "slice_kind": "work",
      "timebox_minutes": 12,
      "allowed_paths": [],
      "ownership_paths": [
        "src/app/"
      ],
      "dependencies": [],
      "task_contract": {
        "goal": "Implement changes for partition A only.",
        "acceptance": [
          "Edits remain within src/app/.",
          "Relevant verification evidence is provided."
        ],
        "constraints": [
          "Do not touch src/lib/."
        ],
        "no_touch": []
      },
      "evidence_requirements": [
        "git_diff",
        "verification"
      ]
    }
  ]
}
```

## Builder checklist

- Stay strictly within `ownership_paths`.
- If you discover cross-cutting work:
  - stop expanding scope
  - propose schema-valid handoff requests with disjoint ownership
- Return verification evidence (`verification`) and a tight `git_diff` summary.

## Inspector checklist

- Review for:
  - missing evidence gates
  - ownership/lock collisions across Builder tickets
  - schema-invalid outputs or non-JSON output risks
- Prefer short, decisive verdicts with explicit “what evidence would change my mind”.
