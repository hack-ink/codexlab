---
name: code-housekeeping
description: Use when reviewing a codebase for compatibility shims, dead code, or stale artifacts that may be safe to remove, and the goal is to produce an evidence-backed cleanup report (not to delete code yet).
---

# Code Housekeeping

## Objective

Identify and report likely-removable code and artifacts (compatibility compromises, dead code, and outdated content) with enough evidence for a human to make a cleanup decision safely.

This skill is **report-only** by default: it does not perform cleanup unless the user explicitly asks.

## When to use

- A repository has accumulated "compat"/"legacy"/"workaround" code and nobody knows if it is still needed.
- Refactors/migrations shipped, but follow-up cleanup never happened.
- You suspect dead code (unused modules/functions, large commented-out blocks, suppressed-unused warnings).
- There are stale scripts, configs, docs, or feature flags that no longer match reality.

## Inputs

Ask for (or infer safely, without blocking when possible):

- Supported versions/targets (language versions, OS/arch, minimum dependency versions).
- Build/test entrypoints (what CI runs; how to run unit/integration tests).
- Any "do not touch" areas (vendor code, generated code, public API stability constraints).

## Hard gates (non-negotiable)

- Do **not** delete or refactor code as part of this skill unless the user explicitly approves.
- Do **not** claim something is safe to remove without evidence; use confidence levels.
- Do **not** recommend removal from a single weak signal (for example, one text search with no hits). Prefer at least two independent evidence signals before marking an item as removable; otherwise mark it as **not_cleanup_ready** or **blocked**.
- Do **not** treat tooling-owned generated artifacts as ordinary dead-code candidates. Trace them back to their source of truth and report the canonical regeneration or removal path instead of suggesting manual deletion.
- If supported-version policy is unknown and affects a finding (for example, a Python/Rust/Node minimum version), mark the item as **blocked** and ask the user.
- Prefer build graph, CI, and runtime-liveness evidence over text-search-only claims when those signals are available.
- Prefer reversible, low-risk tooling: static analysis and text search. Avoid actions that mutate state.

## Why this helps

- Reduces maintenance burden and cognitive load by turning "hunches" into a prioritized, evidence-backed candidate list.
- Avoids risky deletions by separating **detection** (this skill) from **cleanup** (a follow-up task with verification).

## How to use

1. **Baseline context**
   - Identify languages/frameworks and build tooling from the repo (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.).
   - If available, identify what CI runs (GitHub Actions, Buildkite, Makefiles, task runners).
   - Define the cleanup question up front: is each item merely a **candidate**, **not_cleanup_ready**, or strong enough to recommend for a later approved deletion batch?

2. **Scan for compatibility compromises**
   - Search for keywords suggesting historical shims:
     - `compat`, `compatibility`, `legacy`, `workaround`, `shim`, `polyfill`, `fallback`, `deprecated`, `TODO(remove)`, `TODO(drop)`.
   - Search for version-gated logic:
     - patterns like `if version`, `>=`, `<`, `min_version`, `supported`, `old api`, `v1`, `v2`, `migration`.
   - For Rust specifically, look for:
     - `#[cfg(...)]` branches that reference old features or toolchains.
     - feature flags that exist only to support older dependencies.
   - For JS/TS specifically, look for:
     - "browser support" shims, Node-version conditionals, and dual CJS/ESM scaffolding.

   Quick search examples (adapt as needed):
   - `rg -n --hidden --glob '!.git' '(compat(ibility)?|legacy|workaround|shim|polyfill|fallback|deprecated)'`
   - `rg -n --hidden --glob '!.git' 'TODO\\((remove|drop)\\)|TODO: (remove|drop)|remove when|drop when'`
   - `rg -n --hidden --glob '!.git' '(min(_)?version|supported(_)?version|requires node|requires python|MSRV|rust-version)'`

3. **Scan for dead code (define candidates clearly)**
   Treat an item as "dead code candidate" if one or more applies:
   - **Commented-out code blocks**: large blocks that appear executable (not prose) and are no longer referenced by issues/docs.
   - **Suppressed unused**: code annotated to silence unused warnings but lacking a current usage reason.
     - Examples: `#[allow(dead_code)]`, `#[allow(unused)]`, `@SuppressWarnings("unused")`, `eslint-disable no-unused-vars`, `# noqa: F401`, etc.
   - **Unreferenced symbols/files**: modules, exports, functions, classes, binaries, or scripts with no references found via search or tooling.
   - **Unreachable paths**: code behind hardcoded false conditions, obsolete feature flags, or environment variables no longer set anywhere.
   - **Stale toggles**: feature flags that are always-on/off in the current configuration set.

   Evidence to collect (prefer at least two independent signals):
   - Text references: `rg`/`git grep` showing "defined here, never referenced elsewhere".
   - Static analysis warnings (if the repo already uses such tools).
   - Build graph references (import graphs, Cargo workspace members, entrypoints).
   - CI or runtime-liveness evidence (test coverage, startup wiring, config references, logs/telemetry, registration points) when available.

   Quick search examples (adapt as needed):
   - Rust suppressed unused: `rg -n --hidden --glob '!.git' '#\\[allow\\((dead_code|unused|unused_imports|unused_variables)\\)\\]'`
   - Python suppressed unused: `rg -n --hidden --glob '!.git' '#\\s*noqa:\\s*(F401|F841)|#\\s*type:\\s*ignore'`
   - JS/TS suppressed unused: `rg -n --hidden --glob '!.git' 'eslint-disable(-next-line)?\\s+no-unused-vars|@ts-ignore|@ts-expect-error'`
   - Large commented blocks (heuristic): `rg -n --hidden --glob '!.git' '^(\\s*//|\\s*#|\\s*/\\*)'`

4. **Scan for outdated/unneeded content**
   - Old docs: references to removed commands, flags, endpoints, or directories.
   - Old scripts: utilities not invoked by CI, Make/tasks, docs, or developers.
   - Stale configs: duplicated configs, deprecated settings, unused env vars.
   - Tooling-owned generated artifacts: report the generator, source-of-truth inputs, and canonical regeneration/removal path instead of treating the generated file itself as ordinary dead code.
   - Time-based stale TODOs: items referencing dates/releases already passed (treat as "needs review", not automatically removable).

5. **Write the report (and stop)**
   - Produce a single report with:
     - A summary of top risks and quickest wins.
     - A table of candidates grouped by category.
     - Evidence per item (paths + exact identifiers + how you concluded it is likely dead/outdated).
     - A recommended order of operations for cleanup, including verification steps to run after each deletion.
   - Ask the user which items to remove (or whether to proceed with a proposed batch).

## Outputs

Return a report with these sections (Markdown is fine):

- **Repo context**: languages, build tools, CI entrypoints, version/target assumptions.
- **Findings**:
  - Compatibility compromises (candidates + why they exist + what they may still support).
  - Dead code candidates (with a short rubric tag like `commented_block`, `suppressed_unused`, `unreferenced`, `unreachable`, `stale_flag`).
  - Outdated/stale artifacts (docs/scripts/config).
- **Evidence per item**:
  - File path(s), symbol names, relevant search terms used, and what you observed.
  - An explicit evidence map (`claim -> evidence -> source/signal`).
- **Cleanup readiness**:
  - `candidate` / `not_cleanup_ready` / `blocked`, with a short explanation.
- **Confidence and risk**:
  - `high` / `medium` / `low` confidence, plus "blast radius" notes (public API? runtime-critical? tests covering it?).
- **Proposed cleanup plan (optional)**:
  - Suggested deletion batches + verification commands for each batch.
  - Explicit statement that deletion is pending user approval.

## Notes

- "No references found" is not proof of dead code in dynamic/plugin systems; downgrade confidence when reflection, dynamic imports, runtime registration, or config-driven loading is common.
- Prefer to treat generated/vendor directories as out-of-scope unless the user asks. If they are in scope, trace them to source-of-truth inputs and canonical tooling flows rather than treating them as ordinary files.
- If the repository already has linters (Clippy/Ruff/ESLint/etc.), use them for evidence; do not add new tooling as part of this skill.

## Quick reference

- Primary tools: `rg`, repo-native linters, build/test entrypoints.
- Keywords: `compat`, `legacy`, `workaround`, `shim`, `polyfill`, `fallback`, `deprecated`, `TODO(remove)`, `TODO(drop)`.
- Rust suppressed-unused: `#[allow(dead_code)]`, `#[allow(unused)]`.
- Python suppressed-unused: `noqa: F401`, `F841`, `type: ignore`.
- JS/TS suppressed-unused: `eslint-disable no-unused-vars`, `@ts-ignore`, `@ts-expect-error`.

## Common mistakes

- Deleting “because no references”: dynamic imports/registries can hide usage; downgrade confidence and ask for verification entrypoints.
- Treating a single grep result as sufficient evidence: cleanup recommendations should rest on at least two independent signals, or remain `not_cleanup_ready`.
- Mixing detection with cleanup: this skill is report-first; deletion is a separate user-approved follow-up.
- Treating generated/tooling-owned artifacts as ordinary dead files instead of reporting their generator and canonical regeneration/removal path.
- Reporting without evidence: every candidate needs concrete pointers (paths/symbols + search output or tooling signal).

## References

- Repo-local conventions: search for existing "housekeeping" or "cleanup" docs before inventing new rules.
