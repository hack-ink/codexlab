---
name: git-workspaces
description: Use when starting feature work that benefits from branch isolation, independent parallel implementation lanes, or a disposable workspace. Creates clone-backed Git workspaces with safe directory selection, ignore verification, repo-native bootstrap, and lane naming guidance.
---

# Git Workspaces

## Purpose

Use clone-backed Git workspaces when you need an isolated branch checkout without disturbing the current workspace.

Typical triggers:

- Multiple unrelated implementation tasks or PR-like streams on the same repository
- Parallel feature work on the same repository
- Executing a plan in a clean branch-specific workspace
- Hotfix work while the current tree is dirty or mid-refactor
- Large Rust repos where branch isolation is useful

## Core rule

- Prefer an existing workspace layout over inventing a new one.
- When work is independent, default to one workspace per task lane instead of mixing unrelated changes in one branch or one agent run.
- Keep project-local workspace directories ignored.
- Use self-contained clone-backed workspaces, not linked shared-Git checkouts, when the lane itself needs to run `git add`, `git commit`, `git push`, or other Git writes under sandboxed execution.
- Run the repository's documented bootstrap and baseline verification after creation.

## Lane model

Treat each workspace as one independent lane:

- One task, branch, and review stream per workspace
- One agent or human owner at a time unless the lane is explicitly shared
- Keep unrelated fixes in separate workspaces even if they touch the same repository

Use separate workspaces by default when:

- Two tasks could land as separate PRs
- One lane may need to be paused, rebased, or abandoned without blocking another
- You want clean diffs and isolated verification per task

If the work is the same task or the same PR-sized change stream, you may stay on one branch and use other coordination methods inside that lane.

## Choose the directory

Use this priority order:

1. Reuse an existing project-local directory if `.workspaces/` or `workspaces/` already exists.
2. If the repository has scoped instructions (`AGENTS.md` or runtime-equivalent guidance), follow any stated workspace location convention.
3. If there is no existing convention, prefer `.workspaces/` only when it is already ignored or can be safely verified as ignored.
4. If neither a safe project-local directory nor a documented convention exists, ask the user where workspaces should live instead of inventing a global path.

Why `.workspaces/` instead of `.workspace/`:

- it holds multiple lane directories, so plural is clearer
- it mirrors common project-local hidden cache/layout conventions
- it avoids overloading singular `.workspace` names that other tools may already use

## Name the lane simply

Keep branch and directory naming predictable instead of encoding full ticket metadata into the path.

- Branch names should follow the repository's existing convention.
- Workspace directory names should stay short and single-segment.
- Prefer names that reveal the lane's task at a glance.

Examples:

- Branch `feat/cache-invalidation`, directory `feat-cache-invalidation`
- Branch `fix/login-timeout`, directory `fix-login-timeout`
- Branch `chore/release-notes`, directory `chore-release-notes`

If multiple agents or attempts work on the same broad task, keep the branch task-focused and only suffix the directory when needed, for example `feat-cache-invalidation-a` and `feat-cache-invalidation-b`.

## Safety checks before creation

Run these checks before creating the workspace:

```bash
git branch --list <branch-name>
```

If using a project-local directory, verify that it is ignored:

```bash
git check-ignore -q .workspaces || git check-ignore -q workspaces
```

If the intended local directory is not ignored:

- Do not silently proceed.
- Add or adjust ignore rules only when that repo change is in scope.
- Otherwise stop and ask the user how they want workspaces stored.

## Create the workspace

Basic flow:

```bash
repo_root="$(git rev-parse --show-toplevel)"
branch_name="<branch-name>"
workspace_dir_name="<single-segment-dir-name>"
workspace_path="$repo_root/.workspaces/$workspace_dir_name"

git clone --no-checkout . "$workspace_path"

origin_url="$(git -C "$repo_root" remote get-url origin 2>/dev/null || true)"
if [ -n "$origin_url" ]; then
  git -C "$workspace_path" remote set-url origin "$origin_url"
fi

git -C "$workspace_path" checkout -B "$branch_name" HEAD
cd "$workspace_path"
```

If the branch name contains `/`, flatten it when choosing `workspace_dir_name` so the workspace still sits directly under `.workspaces/`. For example, branch `feature/foo` can use workspace directory `feature-foo`.

After creation, prove that the workspace is self-contained before handing it to another agent or sandbox:

```bash
git -C "$workspace_path" rev-parse --path-format=absolute --git-dir
git -C "$workspace_path" rev-parse --path-format=absolute --git-common-dir
```

Both paths should resolve inside `"$workspace_path"`. If either path escapes the lane root, stop and fix the workspace backend instead of letting the child lane discover it later during `git add`.

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

## Notes

- A clone-backed workspace is self-contained, so deleting the directory also deletes the local branch ref stored in that clone.
- If you need to preserve the lane branch beyond teardown, push it or record the commit SHA before removing the workspace.
- Reusing the same deterministic workspace path for retries is fine; reusing shared Git administrative storage is not.

## Closeout / Teardown

Use this when a lane is merged, intentionally abandoned, or paused long enough that the checkout should be reclaimed.

Before removal:

- Confirm the lane outcome first: merged, intentionally abandoned, or explicitly paused.
- Inspect the current state:

```bash
git status --short
git rev-parse --abbrev-ref HEAD
```

- If the lane is expected to be merged, first discover the repo-appropriate, up-to-date integration branch for that lane from repo policy, PR or base-branch context, or Git metadata. Only stop and confirm if multiple plausible target branches remain or the discovered target conflicts with lane intent.
- Then verify it is not carrying unique commits. Prefer checks such as:

```bash
git branch --merged <target-branch>
git log <target-branch>..<branch-name>
```

- If the workspace contains uncommitted edits, stop and inspect them before removal.

Teardown flow:

1. Remove the workspace directory with `rm -rf <path>` only after showing the dirty state and unique-commit risk.
2. If the branch needs to live on, push it or record the SHA before removal.
3. If the branch is already merged and no longer needed locally, simply deleting the clone-backed workspace is enough.

## Red flags

- Creating a project-local workspace without verifying the directory is ignored
- Running a generic bootstrap command while ignoring repo instructions
- Treating a clone-backed workspace as if it still shared Git administrative state with the original checkout
- Using linked shared-Git checkouts for sandboxed child lanes that must perform lane-local Git writes
