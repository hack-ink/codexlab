# review-request (Dev-only)

This directory contains development-only artifacts for the `review-request` skill.

## Quick smoke

From the repo root:

```sh
python3 dev/review-request/run_smoke.py
```

The smoke validates the checked-in review-request gate for non-draft pushed PRs with fresh verification evidence.
