# research-pro (Dev-only)

This directory contains development-only validation for the `research-pro` skill.
It stays outside the installable skill directory so installations keep only the
skill instructions.

## Quick smoke

From the repo root:

```sh
python3 dev/research-pro/run_smoke.py
```

Optional host probe:

```sh
python3 dev/research-pro/run_smoke.py --check-host-cli
```

By default, this smoke validates the source-repo `research-pro` contract
without depending on a local browser install:

- legacy Node/Playwright wrapper references stay out of `.codex/skills/research-pro/SKILL.md`
- the obsolete `.codex/skills/research-pro/scripts/agent-browser-node.sh` artifact stays removed

With `--check-host-cli`, it also validates the current host's `agent-browser`
entrypoint:

- the local `agent-browser` CLI is present in `PATH`
- the local CLI exposes the flags that `research-pro` depends on
