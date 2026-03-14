# git-workspaces (Dev-only)

This directory contains development-only artifacts for the `git-workspaces` skill. It is intentionally kept outside the installable skill directory so installations do not include smoke tests or local policy fixtures.

## Quick smoke

From the repo root:

```sh
python3 dev/git-workspaces/run_smoke.py
```

This smoke entrypoint creates a temporary Git repository and validates the current lifecycle policy end-to-end:

- `.workspaces/<single-segment>` layout with a slash branch name
- ignored local workspace directory
- self-contained Git metadata inside the workspace
- lane commit and merge
- direct workspace-directory teardown after merge
- no accidental shared-Git lane registration for the workspace
