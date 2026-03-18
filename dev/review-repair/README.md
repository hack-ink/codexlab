# review-repair (Dev-only)

This directory contains development-only artifacts for the `review-repair` skill.

## Quick smoke

From the repo root:

```sh
python3 dev/review-repair/run_smoke.py
```

The smoke validates the checked-in GitHub review-repair loop contract, including in-thread replies, conditional resolve, and bounded escalation.
