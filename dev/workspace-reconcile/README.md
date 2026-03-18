# workspace-reconcile (Dev-only)

This directory contains development-only artifacts for the `workspace-reconcile` skill.

## Quick smoke

From the repo root:

```sh
python3 dev/workspace-reconcile/run_smoke.py
```

This smoke validates the checked-in reconciliation contract for surviving-lane ownership, `.workspaces/*` scoping, output vocabulary, and cleanup-candidate handoff.
