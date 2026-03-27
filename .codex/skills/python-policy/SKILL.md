---
name: python-policy
description: Use when Python work is present and you need the hack-ink Python policy for runtime boundaries and project-configured quality gates.
---

# Python Policy (hack-ink)

## Policy

This skill is the Python policy document for hack-ink repositories. Use it to keep Python changes aligned with the touched project's checked-in tooling and bootstrap path instead of personal defaults.

## Scope

- These rules apply to Python services, libraries, and tooling in this repository when Python code or Python tooling is present.
- Do not apply them to non-Python projects.

## When to use

- You are about to run, modify, or add Python code or Python tooling (Poetry, scripts, CI helpers).
- You need to decide which environment, packaging, format, lint, type-check, or test commands are authoritative for Python work.

## Tooling boundaries

- Follow the formatter, linter, type-check, test, and packaging commands already configured by the project you are touching.
- If the repo does not evidence a tool, do not invent a repo-wide requirement in the name of policy.
- Do not switch environment managers, dependency managers, or quality gates unless the project already requires that change.

## Environment and packaging

- Follow the touched project's checked-in bootstrap and runtime selection rules first.
- Reuse a shared root `.venv` only when the repo or project already documents that layout.
- Allow documented isolated runtimes when required, such as a skill-local private environment.
- Activate or select the intended runtime before running project Python commands.
- If the touched project is Poetry-managed, use the Poetry workflow it documents; do not assume one sync command is universal.

## Execution posture

- Prefer the project's checked-in config, documented bootstrap, and existing CI commands over ad-hoc local conventions.
- If a Python task only needs a narrow script change, keep the workflow narrow too; do not broaden the task into toolchain churn.

## Quick reference

- Tool authority: checked-in project config and existing CI/docs win.
- Runtime choice: follow the documented project or skill bootstrap first.
- Shared env: use repo/root `.venv` only when the repo already standardizes it.
- Isolated envs: allowed when the project or skill explicitly requires them.

## Common mistakes

- Inventing a formatter, linter, type checker, or test runner that the project does not already configure.
- Assuming every Python task should use the repo root `.venv` or one Poetry sync command.
- Ignoring a documented isolated runtime such as a skill-local private environment.
- Running Python or Poetry commands against the wrong runtime, leading to confusing tool resolution and caches.

## Outputs

Return evidence for:

- Which project config or existing command established Python tooling authority.
- The environment source and activation approach used.
- Packaging/bootstrap steps executed, including any documented runtime selection.
