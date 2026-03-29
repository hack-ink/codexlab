---
name: pr-land
description: Use when a PR may be ready to land. Owns PR readiness checks, delivery-history-aware merge policy, necessary branch sync decisions, and merge execution; does not produce `delivery/1`, close out trackers, or clean up worktrees and branches.
---

# PR Land

## Scope

- This skill is a land-lite merge workflow for an existing PR.
- It owns the merge decision and merge execution once the PR is truly ready.
- It does not request review, repair review comments, produce `delivery/1`, close out trackers, or clean up worktrees and branches.
- If a delivery-style PR needs a merge commit, this skill must consume an explicit merge-commit `delivery/1` message prepared by `delivery-prepare`; it does not invent that payload itself.

## Inputs

- PR URL or PR number
- Merge policy
- Required checks
- Optional base branch

## Outputs

- `merged`
- `not_ready`
- `needs_sync`
- `blocked`

## Hard gates

- The PR must be non-draft.
- Required review must be satisfied.
- Required checks must be green.
- Base freshness must satisfy repo policy.
- If branch sync needs commit or push, route back through `delivery-prepare` before continuing.
- Do not wait inside this skill for review or CI. Return state and let orchestration re-enter later.

## Merge policy

- If every commit in the PR already uses `delivery/1`, preserve that style:
  - do not squash
  - do not discard commit-level delivery metadata
  - if a merge commit is required, obtain the merge commit message from `delivery-prepare` first, then use that explicit `delivery/1` payload for the merge commit
- If the PR is not entirely `delivery/1` history, use the normal squash/default merge flow for non-delivery history.

## Procedure

1. Inspect PR state:
   - draft vs ready
   - review approvals or requested changes
   - required checks
   - base freshness / mergeability
2. If the PR is stale against base, return `needs_sync` unless policy and context already authorize performing the sync now.
3. If sync is performed and it requires commit or push, run `delivery-prepare` before pushing the sync result.
4. If review or CI is still pending, return `not_ready`.
5. If the PR is delivery-style and the landing path requires a merge commit, run `delivery-prepare` to obtain the merge commit `delivery/1` payload before executing the merge.
6. If all gates pass, execute the merge with the repo-appropriate policy.
7. Stop after merge. `delivery-closeout` and cleanup belong to later steps.

## Red flags

- Waiting inside this skill for CI or review to finish
- Treating this skill as if it owns tracker closeout
- Cleaning up branches or worktrees here
- Squashing a PR whose commits already use `delivery/1`
