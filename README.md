<div align="center">

# hack.ink AI-agent skills

Reusable Codex skills for hack.ink workflows, with machine-first planning, review, delivery, and workspace orchestration.

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/hack-ink/codexlab)](https://github.com/hack-ink/codexlab/tags)
[![GitHub last commit](https://img.shields.io/github/last-commit/hack-ink/codexlab?color=red&style=plastic)](https://github.com/hack-ink/codexlab)
[![GitHub code lines](https://tokei.rs/b1/github/hack-ink/codexlab)](https://github.com/hack-ink/codexlab)

</div>

## Feature Highlights

- Skill-only repository focused on reusable Codex workflow primitives instead of app code.
- Machine-first process skills for `plan/1`, `delivery/1`, review loops, and workspace lifecycle management.
- Repo-local maintainer harnesses under `dev/` for smoke tests and validation without polluting installed skill payloads.
- Small, composable skill units that can be loaded independently as primary workflows or additive overlays.

## Available Skills

| Skill | Purpose | Path |
| --- | --- | --- |
| `delivery-closeout` | Consumes a pushed `delivery/1` payload, syncs delivery state, and mirrors issue outcomes back to GitHub. | `delivery-closeout/SKILL.md` |
| `delivery-prepare` | Produces the shared machine-first `delivery/1` contract before commit or push. | `delivery-prepare/SKILL.md` |
| `dep-roll` | Upgrades pnpm, Poetry, and Cargo dependency graphs to the latest mutually compatible set. | `dep-roll/SKILL.md` |
| `plan-execution` | Executes a persisted `plan/1` without inferring authority from chat. | `plan-execution/SKILL.md` |
| `plan-writing` | Creates or revises persisted `plan/1` files under `docs/plans/`. | `plan-writing/SKILL.md` |
| `pr-land` | Handles PR readiness checks, sync decisions, and merge execution without swallowing downstream closeout. | `pr-land/SKILL.md` |
| `python-policy` | Defines Python runtime boundaries and project-configured quality gates. | `python-policy/SKILL.md` |
| `research` | Runs evidence-backed investigation and recommendation workflows with web research when needed. | `research/SKILL.md` |
| `research-pro` | Consults ChatGPT Pro via chatgpt.com Projects for architecture and research-heavy decisions. | `research-pro/SKILL.md` |
| `review-loop` | Shared bounded review -> fix -> verify -> re-review engine for concrete diffs and repaired heads. | `review-loop/SKILL.md` |
| `review-prepare` | Wraps `review-loop` for pre-PR self-review and branch readiness checks. | `review-prepare/SKILL.md` |
| `review-repair` | Wraps `review-loop` for external review feedback, reply handling, and verified thread resolution. | `review-repair/SKILL.md` |
| `rust-policy` | Defines Rust scope, tooling, formatting, ownership, and safety expectations. | `rust-policy/SKILL.md` |
| `scout-skeptic` | Additive checkpoint guidance for non-trivial tasks that still need evidence gathering or theory challenge after a short probe. | `scout-skeptic/SKILL.md` |
| `scrapling` | Provides fallback scraping guidance when lightweight fetch paths are blocked or incomplete. | `scrapling/SKILL.md` |
| `skill-routing` | Establishes skill discovery, selection order, and primary-vs-overlay loading discipline. | `skill-routing/SKILL.md` |
| `verification-before-completion` | Enforces evidence-first completion checks before claiming readiness or success. | `verification-before-completion/SKILL.md` |
| `workspace-reconcile` | Reconciles conflicting `.workspaces/*` lanes into one surviving implementation lane. | `workspace-reconcile/SKILL.md` |
| `workspaces` | Creates, reuses, and closes clone-backed `.workspaces/*` lanes for non-read-only work. | `workspaces/SKILL.md` |

## Contributing

To add or update a skill:

1. Load the system `skill-creator` skill first so naming, frontmatter, and packaging stay aligned with the current authoring contract.
2. Create or update `<skill-name>/SKILL.md` with the required frontmatter (`name`, `description`).
3. Keep installable runtime assets with the skill itself. If `SKILL.md` references a script, template, schema, or helper at runtime, keep it under `<skill-name>/`.
4. Keep repo-local validation assets under `dev/<skill-name>/`. Smoke tests, e2e fixtures, backtests, and maintainer-only validation entrypoints belong there and are not part of the installed skill contract.
5. Treat generated artifacts, lockfiles, codegen outputs, and build outputs as tooling-owned. Skills should point to canonical regeneration or sync commands instead of instructing manual edits to generated files.
6. Keep instructions concise, testable, and narrowly scoped.
7. Update this `README.md` when the skill catalog changes.

## Repository Layout

- This repository intentionally ships skills only.
- Routing and push policy should live in your Codex home configuration, not in this repo.
- `<skill-name>/SKILL.md` is the required skill definition entrypoint.
- `<skill-name>/...` stores installable runtime assets referenced by `SKILL.md`, such as scripts, templates, schemas, or references.
- `dev/<skill-name>/...` stores repo-local smoke tests and maintainer validation helpers that are not part of the installed skill payload.

## Support Me

If you find this project helpful and would like to support its development, you can buy me a coffee!

Your support is greatly appreciated and motivates me to keep improving this project.

- **Fiat**
  - [Ko-fi](https://ko-fi.com/hack_ink)
  - [Afdian](https://afdian.com/a/hack_ink)
- **Crypto**
  - **Bitcoin**
    - `bc1pedlrf67ss52md29qqkzr2avma6ghyrt4jx9ecp9457qsl75x247sqcp43c`
  - **Ethereum**
    - `0x3e25247CfF03F99a7D83b28F207112234feE73a6`
  - **Polkadot**
    - `156HGo9setPcU2qhFMVWLkcmtCEGySLwNqa3DaEiYSWtte4Y`

Thank you for your support!

## Appreciation

We would like to extend our gratitude to the maintainers, reviewers, and workflow designers who keep agent-driven engineering disciplined, reproducible, and practical.

- The Codex and agent-tooling communities for pushing reusable workflow patterns forward.
- The contributors who keep these skills explicit, testable, and easy to compose across repositories.

## Additional Acknowledgements

- The open-source ecosystem that makes repo-native automation, validation, and documentation tooling reliable enough to encode into repeatable skills.

<div align="right">

### License

<sup>Licensed under [GPL-3.0](LICENSE).</sup>

</div>
