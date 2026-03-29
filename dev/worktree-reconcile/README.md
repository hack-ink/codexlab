# worktree-reconcile (Dev-only)

This directory contains development-only artifacts for the `worktree-reconcile` skill.

## Quick smoke

From the repo root:

```sh
python3 dev/worktree-reconcile/run_smoke.py
```

This smoke validates the checked-in reconciliation contract for surviving-lane ownership, `.worktrees/*` scoping, output vocabulary, and cleanup-candidate handoff.
