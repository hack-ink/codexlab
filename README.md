<div align="center">

# codexlab

Codex-first repository for reusable workflow assets, runtime guidance, and packaging patterns.

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/hack-ink/codexlab)](https://github.com/hack-ink/codexlab/tags)
[![GitHub last commit](https://img.shields.io/github/last-commit/hack-ink/codexlab?color=red&style=plastic)](https://github.com/hack-ink/codexlab)
[![GitHub code lines](https://tokei.rs/b1/github/hack-ink/codexlab)](https://github.com/hack-ink/codexlab)

</div>

## Feature Highlights

- Designed for Codex runtime and authoring workflows rather than product application code.
- Current repository content is centered on reusable skills and repo-local maintainer harnesses under `dev/`.
- Repository scope is broader than skills alone and includes Codex-facing assets such as `~/.codex/config.toml`, `~/.codex/AGENTS.md`, `~/.codex/skills/`, and plugin-related metadata and packaging.
- Tracks current Codex plugin packaging concepts, including `.codex-plugin/plugin.json`, `.app.json`, `.mcp.json`, and marketplace-oriented distribution flows.
- Keeps machine-first workflow primitives for planning, review, delivery, and workspace lifecycle management explicit and composable.

## Codex Scope

This repository is for Codex-oriented content.

That includes:

- Runtime configuration and policy, such as `~/.codex/config.toml` and `~/.codex/AGENTS.md`.
- Reusable Codex skills that can live in `~/.codex/skills/` or a repo-local skills directory.
- Plugin packaging and distribution patterns for the current Codex plugin model.
- Maintainer tooling, smoke tests, and validation helpers needed to keep those assets aligned.

The current tree mainly ships reusable skills plus maintainer-only validation helpers. The repository name and README now reflect the broader Codex target so it can also house non-skill Codex assets as they are added.

## Current Skill Catalog

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

To add or update Codex-oriented content:

1. Keep the content Codex-focused. Runtime config, agent policy, skills, and plugin assets belong here; unrelated app code does not.
2. For skills, load the system `skill-creator` skill first so naming, frontmatter, and packaging stay aligned with the current authoring contract.
3. Create or update `<skill-name>/SKILL.md` with the required frontmatter (`name`, `description`).
4. Keep installable runtime assets with the skill itself. If `SKILL.md` references a script, template, schema, or helper at runtime, keep it under `<skill-name>/`.
5. Keep repo-local validation assets under `dev/<skill-name>/`. Smoke tests, e2e fixtures, backtests, and maintainer-only validation entrypoints belong there and are not part of the installed skill contract.
6. If you add plugin assets, keep the plugin manifest at `.codex-plugin/plugin.json` and keep plugin-root files such as `.app.json`, `.mcp.json`, `skills/`, and `assets/` at the plugin root.
7. Treat generated artifacts, lockfiles, codegen outputs, and build outputs as tooling-owned. Runtime content should point to canonical regeneration or sync commands instead of instructing manual edits to generated files.
8. Update this `README.md` when the Codex asset catalog changes.

## Repository Layout

- This repository is intentionally scoped to Codex-facing assets.
- The current tracked tree primarily contains reusable skills plus maintainer tooling.
- `~/.codex/config.toml` and `~/.codex/AGENTS.md` are canonical examples of runtime configuration and policy this repository is designed around, even when those files are installed elsewhere.
- `~/.codex/skills/` is the canonical runtime destination for reusable skills maintained from this repository.
- `<skill-name>/SKILL.md` is the required skill definition entrypoint.
- `<skill-name>/...` stores installable runtime assets referenced by `SKILL.md`, such as scripts, templates, schemas, or references.
- `dev/<skill-name>/...` stores repo-local smoke tests and maintainer validation helpers that are not part of the installed runtime payload.
- Codex plugin assets can include `.codex-plugin/plugin.json`, `.app.json`, `.mcp.json`, `skills/`, and `assets/`, with marketplace metadata layered on top when distribution is needed.

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
