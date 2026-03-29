---
name: worktree-reconcile
description: Use only when multiple worktree-backed `.worktrees/*` lanes for the same repository conflict and must be reconciled into one surviving lane. Owns surviving-lane selection, reconciliation strategy choice, integration, and verification; does not create/delete worktrees, do review, merge, or tracker closeout.
---

# Worktree Reconcile

## Scope

- This skill is only for `.worktrees/*` lane conflicts inside the same repository.
- This skill does not create or remove worktrees. It returns `cleanup_candidates` for `worktrees` to close later.
- This skill does not request review, repair review threads, merge PRs, or sync trackers.

Typical triggers:

- Two or more `.worktrees/*` lanes touched the same code and now conflict
- One lane should survive and absorb another lane's work
- A donor lane needs rebase, cherry-pick, merge, or re-split into a clearer boundary
- Repeated conflict churn suggests the original split was wrong

## Core rule

- Identify the surviving lane first. Do not try to "merge everything everywhere."
- Reconcile donor lanes into the surviving lane, then continue the workflow from that surviving lane only.
- Preserve uncommitted work before changing strategy.
- If the conflict is really a bad task split, stop and return `needs_resplit` instead of stacking more merge noise.
- Treat generated artifacts, lockfiles, codegen outputs, and build outputs as tooling-owned: when the repo exposes a canonical regeneration path, reconcile the source inputs and rerun that command instead of editing the generated file by hand.
- Verify the integrated surviving lane before handing it back to `review-*` or `pr-land`.

## Hard gates

- All participating paths must live under `.worktrees/*`.
- All participating worktrees must belong to the same repository.
- The surviving lane must be explicit before you start editing.
- If the donor lane contains useful uncommitted work, preserve it before aborting or switching strategies.

## Triage first

Run the smallest commands that establish lane identities and conflict state:

```bash
git -C "$surviving_worktree" rev-parse --show-toplevel
git -C "$surviving_worktree" rev-parse --abbrev-ref HEAD
git -C "$surviving_worktree" status --short
git -C "$surviving_worktree" diff --name-only --diff-filter=U
git -C "$donor_worktree" rev-parse --abbrev-ref HEAD
git -C "$donor_worktree" status --short
```

If a Git operation is already in progress inside the surviving lane, detect it before editing:

```bash
git -C "$surviving_worktree" rev-parse -q --verify MERGE_HEAD
git -C "$surviving_worktree" rev-parse -q --verify CHERRY_PICK_HEAD
git -C "$surviving_worktree" rev-parse -q --verify REBASE_HEAD
```

Read the branch delta before choosing a strategy:

```bash
git -C "$surviving_worktree" log --oneline --left-right --cherry "$target_branch"...HEAD
git -C "$donor_worktree" log --oneline --left-right --cherry "$target_branch"...HEAD
```

## Pick the strategy deliberately

- `rebase` - donor lane should replay onto the surviving lane or newer base with linear history.
- `cherry-pick` - only a subset of donor commits should cross lanes.
- `merge` - both histories should remain intact and the surviving lane accepts merge commits.
- `needs_resplit` - the original task split was wrong, repeated conflicts keep returning, or the cleanest outcome is to separate commits differently before any more review.

Preserve work before switching strategies:

```bash
git -C "$donor_worktree" status --short
git -C "$surviving_worktree" status --short
```

Use official abort flows instead of deleting progress blindly:

```bash
git -C "$surviving_worktree" merge --abort
git -C "$surviving_worktree" rebase --abort
git -C "$surviving_worktree" cherry-pick --abort
```

## Resolve carefully

- Read each conflicted hunk against both sides and the surrounding function or section.
- Prefer keeping intent, not just both text blocks.
- Remove conflict markers completely.
- Re-check with `git -C "$surviving_worktree" diff --name-only --diff-filter=U` until no unresolved files remain.

For repeated conflict-heavy files, compare against each side explicitly:

```bash
git -C "$surviving_worktree" show :1:path/to/file
git -C "$surviving_worktree" show :2:path/to/file
git -C "$surviving_worktree" show :3:path/to/file
```

## Verify before closeout

After resolving:

1. Confirm the surviving lane is clean enough to continue.
2. If any generated artifacts, lockfiles, or codegen outputs were involved, rerun the canonical regeneration/sync command before verification.
3. Run the repo's scoped verification for the touched area.
4. Review the resulting diff to ensure no accidental donor-lane bleed-through remains.

Minimum checks:

```bash
git -C "$surviving_worktree" status --short
git -C "$surviving_worktree" diff --stat
```

Then run the repo-native test, build, or lint command that covers the reconciled files.

## Outputs

- `reconciled` - donor work integrated into the surviving lane and verified.
- `needs_resplit` - the original split is the problem; stop and re-plan the lane boundary.
- `blocked` - insufficient evidence, risky uncommitted work, or unresolved verification failure.
- `cleanup_candidates` - obsolete donor lanes that `worktrees` may clean up after the surviving lane finishes.

## Red flags

- Reconciling two arbitrary branches that are not `.worktrees/*` lanes
- Editing both surviving and donor lanes interchangeably instead of choosing a surviving lane
- Combining unrelated tasks just to make the conflict disappear
- Manually resolving generated files, lockfiles, codegen outputs, or build outputs instead of rerunning the canonical regeneration path
- Claiming the conflict is fixed before the surviving lane passes `git status` and repo-native verification
