# research dev notes

This directory contains development-only validation for the `research` skill.
It stays outside the installable skill directory so installations keep only the
runtime instructions.

## Quick smoke

From the repo root:

```sh
python3 dev/research/run_smoke.py
```

This smoke validates the checked-in escalation guidance:

- the frontmatter exposes escalation from repeated failed local attempts
- the skill requires research before a fourth substantial attempt
- the skill distinguishes substantial attempts from reruns or parameter thrash
- the output template records the escalation trigger when the skill is used as a troubleshooting escalation path
