# pr-land (Dev-only)

This directory contains development-only artifacts for the `pr-land` skill.

## Quick smoke

From the repo root:

```sh
python3 dev/pr-land/run_smoke.py
```

The smoke validates the checked-in merge-readiness contract, including `delivery/1` history preservation and explicit separation from closeout and cleanup.
