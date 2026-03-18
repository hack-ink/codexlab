---
name: review-request
description: Use after a PR exists and `review-prepare` has converged to request Codex review on the pushed branch. Owns review request gating for non-draft PRs with a clean workspace and fresh verification evidence; does not repair comments or merge.
---

# Review Request

## Scope

- This skill owns the PR review request step.
- Default meaning is a Codex review request on an existing PR.
- This skill does not repair comments, resolve threads, merge the PR, or close out trackers.

## Inputs

- PR URL or PR number
- Head SHA
- Optional review summary or scope

## Outputs

- `review_requested`
- `blocked`

## Hard gates

- The PR must already exist.
- The PR must be non-draft.
- The branch must already be pushed.
- The workspace must be clean.
- The current head must have fresh verification evidence.
- `review-prepare` must already be clean for this branch state.

## Procedure

1. Confirm the PR target and current head SHA.
2. Verify that the branch is pushed and the PR is not draft.
3. Confirm the working tree is clean:
   - `git status --short`
4. Confirm fresh verification evidence exists for the current head.
5. Request Codex review through the current repo-approved review entrypoint.
6. Emit `review_requested` with the PR identity and head SHA.

## Hand-off

- After the request is sent, waiting and re-entry belong to orchestration.
- When review comments arrive, switch to `review-repair`.
- If the branch changes and another round is needed, come back here explicitly.

## Red flags

- Requesting review on a draft PR
- Requesting review before the branch is pushed
- Requesting review from a dirty workspace
- Treating this skill as if it owns the repair loop or merge decision
