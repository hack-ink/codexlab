# review-prepare (Dev-only)

This directory contains development-only artifacts for the `review-prepare` skill.

## Quick smoke

From the repo root:

```sh
python3 dev/review-prepare/run_smoke.py
```

The smoke validates the checked-in self-review loop contract, including bounded rounds, output vocabulary, and escalation to `research`.
