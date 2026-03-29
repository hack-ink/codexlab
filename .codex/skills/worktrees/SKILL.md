---
name: worktrees
description: Use for any non-read-only development task that starts or resumes implementation in this repo unless the correct isolated lane is already active. Owns worktree-backed `.worktrees/*` lane setup, reuse, and completed-lane cleanup of the worktree plus local and remote branches; does not own reconciliation, review, merge, or tracker closeout.
---

# Worktrees

## Scope

- This skill is the default entrypoint for non-read-only development tasks unless the correct isolated lane is already active.
- This skill owns lane setup, lane reuse, and completed-lane closeout.
- This skill does not own multi-lane reconciliation, review request/repair, merge execution, or tracker closeout.
- Keep the filesystem convention `.worktrees/*`.

Typical triggers:

- Start a non-read-only implementation task even when the user only asked for a fix, feature, or refactor
- Start a task in a clean branch-specific lane
- Resume implementation in an existing matching lane
- Close out a merged or explicitly abandoned lane
- Clean up a finished lane's worktree and branch state after `delivery-closeout`

## Core rule

- Default to one worktree-backed `.worktrees/<lane>` lane per non-read-only implementation task, branch, and review stream unless the correct lane is already active.
- Prefer reusing an existing matching lane over creating a duplicate.
- Keep `.worktrees/` ignored.
- If a task explicitly needs a persisted `plan/1` artifact, create or update it from inside the active worktree so the plan stays in the same lane as the implementation.
- Do not leave task-local `docs/plans/...` artifacts behind in the primary checkout while implementation lives in a worktree lane.
- Use `git worktree` as the lane backend so each lane gets its own working tree while the repository keeps one shared Git metadata root.
- Never treat a worktree lane as self-contained Git storage. `.git` inside the lane is a pointer file into the primary checkout's Git metadata.
- Run the repository's documented bootstrap and a fast baseline verification after creation.
- Treat closeout as part of task completion. A finished lane is not done until the worktree and branch state are clean.

## Lane model

Treat each `.worktrees/*` checkout as one independent lane:

- One task, branch, and review stream per worktree
- One agent or human owner at a time unless the lane is explicitly shared
- Keep unrelated fixes in separate worktrees even if they touch the same repository

Use separate worktrees by default when:

- Two tasks could land as separate PRs
- One lane may need to be paused, rebased, or abandoned without blocking another
- You want clean diffs and isolated verification per task

If the work is the same task or the same PR-sized change stream, you may stay on one branch and use other coordination methods inside that lane.

## Choose the directory

Use this priority order:

1. Reuse an existing project-local directory if `.worktrees/` or `worktrees/` already exists.
2. If the repository has scoped instructions (`AGENTS.md` or runtime-equivalent guidance), follow any stated worktree location convention.
3. If there is no existing convention, prefer `.worktrees/` only when it is already ignored or can be safely verified as ignored.
4. If neither a safe project-local directory nor a documented convention exists, ask the user where worktrees should live instead of inventing a global path.

Why `.worktrees/` instead of `.worktree/`:

- it holds multiple lane directories, so plural is clearer
- it mirrors common project-local hidden cache/layout conventions
- it avoids overloading singular `.worktree` names that other tools may already use

## Name the lane simply

Keep branch and directory naming predictable instead of encoding full ticket metadata into the path.

- Branch names should follow the repository's existing convention.
- Worktree directory names should stay short and single-segment.
- Prefer names that reveal the lane's task at a glance.

Examples:

- Branch `feat/cache-invalidation`, directory `feat-cache-invalidation`
- Branch `fix/login-timeout`, directory `fix-login-timeout`
- Branch `chore/release-notes`, directory `chore-release-notes`

If multiple agents or attempts work on the same broad task, keep the branch task-focused and only suffix the directory when needed, for example `feat-cache-invalidation-a` and `feat-cache-invalidation-b`.

## Safety checks before creation

Run these checks before creating the worktree:

```bash
git branch --list <branch-name>
git worktree list --porcelain
```

If using a project-local directory, verify that it is ignored:

```bash
git check-ignore -q .worktrees || git check-ignore -q worktrees
```

If the intended local directory is not ignored:

- Do not silently proceed.
- Add or adjust ignore rules only when that repo change is in scope.
- Otherwise stop and ask the user how they want worktrees stored.

Before `git worktree add`, confirm the destination does not already contain unrelated files:

```bash
test ! -e "$worktree_path" || test -d "$worktree_path/.git"
```

## Create or reuse the worktree

Basic flow:

```bash
repo_root="$(git rev-parse --show-toplevel)"
branch_name="<branch-name>"
worktree_dir_name="<single-segment-dir-name>"
worktree_path="$repo_root/.worktrees/$worktree_dir_name"

if [ -d "$worktree_path" ] && git -C "$worktree_path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  cd "$worktree_path"
  git status --short
  git rev-parse --abbrev-ref HEAD
  exit 0
fi

git worktree add -b "$branch_name" "$worktree_path" HEAD
cd "$worktree_path"
```

If the branch already exists and should be reused instead of created, attach it explicitly:

```bash
git worktree add "$worktree_path" "$branch_name"
```

If the branch name contains `/`, flatten it when choosing `worktree_dir_name` so the worktree still sits directly under `.worktrees/`. For example, branch `feature/foo` can use worktree directory `feature-foo`.

After creation, prove that the worktree is registered as a lane under the primary repository instead of assuming clone semantics:

```bash
git -C "$worktree_path" rev-parse --path-format=absolute --git-dir
git -C "$worktree_path" rev-parse --path-format=absolute --git-common-dir
git worktree list --porcelain
```

Expected shape:

- `--git-dir` resolves under the primary checkout's `.git/worktrees/<lane>`
- `--git-common-dir` resolves to the primary checkout's `.git`
- `git worktree list --porcelain` includes `$worktree_path`

If `git worktree add` fails because the branch is already checked out elsewhere, stop and reuse or rename the lane instead of forcing a second checkout of the same branch.

## Bootstrap and baseline

After creation:

1. Read the repository instructions first.
2. Run the repo-native bootstrap command, not a generic guess.
3. Run a baseline verification command that is fast enough to establish a clean starting point.

Examples:

- Rust: documented `cargo make ...`, `cargo xtask ...`, or a scoped `cargo check` / `cargo test` gate
- Node: documented package-manager install plus the repo's quick validation command
- Python: documented environment bootstrap plus the repo's smoke or test command

Do not automatically run the heaviest full-suite command if the repository already documents a lighter baseline gate.

## Outputs

- `worktree_ready` - created a new lane and verified it is usable.
- `worktree_reused` - reused an existing lane with matching task intent.
- `worktree_closed` - finished closeout and reached the default clean target state.
- `worktree_retained` - lane intentionally kept because the task is paused, blocked, or not actually complete.
- `warned` - local cleanup succeeded but some non-fatal cleanup target, usually the remote branch, could not be removed.
- `blocked` - setup or closeout stopped because a hard gate failed.

## Closeout / Teardown

- Closeout is only valid when the task is truly complete or explicitly abandoned.
- Valid closeout states:
  - PR merged and `delivery-closeout` already ran or was explicitly not needed
  - task explicitly abandoned or cancelled with approval to clean up the lane
- Do not clean up a lane that is still in review, still awaiting external action, or still carrying unresolved local investigation.

Before removal, inspect and prove the current state:

```bash
git -C "$worktree_path" status --short
git -C "$worktree_path" rev-parse --abbrev-ref HEAD
git -C "$worktree_path" remote get-url origin
git worktree list --porcelain
```

If the lane is expected to be merged, discover the repo-appropriate integration branch from repo policy, PR/base-branch context, or Git metadata. Only stop and ask when multiple plausible target branches remain or the discovered target conflicts with lane intent.

Then verify it is not carrying unique commits:

```bash
git -C "$worktree_path" branch --merged <target-branch>
git -C "$worktree_path" log <target-branch>..<branch-name>
```

If there is no merge-base, compare divergence explicitly instead of guessing:

```bash
git -C "$worktree_path" rev-list --count <target-branch>..<branch-name>
git -C "$worktree_path" rev-list --count <branch-name>..<target-branch>
```

- If the worktree contains uncommitted edits, stop and inspect them before removal.

Remote-branch check:

```bash
git -C "$worktree_path" ls-remote --heads origin "$branch_name"
```

Teardown flow:

1. Verify the lane outcome and the unique-commit state.
2. If the remote branch still exists and the task is complete, delete it:
   - `git -C "$worktree_path" push origin --delete "$branch_name"`
3. If the remote branch is already absent, record that it was auto-deleted or already cleaned up.
4. Remove the worktree registration cleanly instead of deleting the directory by hand:
   - `git worktree remove "$worktree_path"`
5. Delete the local branch from the primary checkout only after the worktree is detached and the branch is safe to remove:
   - `git -C "$repo_root" branch -D "$branch_name"`
6. Fast-forward the primary checkout's integration branch to the latest upstream state before claiming full closeout:
   - require the primary checkout worktree to be clean
   - if the primary checkout is not already on `<target-branch>`, switch to it only after confirming the checkout is clean
   - `git -C "$repo_root" fetch origin "$target_branch"`
   - `git -C "$repo_root" pull --ff-only origin "$target_branch"`
7. Prune stale worktree metadata if removal left administrative residue:
   - `git -C "$repo_root" worktree prune`

Default closeout target state:

- `.worktrees/<lane>` does not exist
- the lane worktree is absent from `git worktree list`
- the same-named local branch in the shared repository is absent
- the primary checkout is on the integration branch and fast-forwarded to the latest upstream state
- the remote branch is absent

If remote branch deletion fails because of branch protection, platform policy, or network failure, return `warned` instead of falsely claiming a fully clean closeout.

## Red flags

- Creating a project-local worktree without verifying the directory is ignored
- Running a generic bootstrap command while ignoring repo instructions
- Treating a worktree-backed lane as if it had self-contained Git metadata
- Forcing the same branch to be checked out in two worktrees instead of reusing or renaming the lane
- Removing a lane directory with `rm -rf` instead of unregistering it with `git worktree remove`
- Claiming a lane is fully closed while the remote branch still exists without recording whether GitHub auto-deleted it or deletion failed
