---
name: review-prepare
description: Use before creating or updating a PR to run the self-review loop on the actual diff. Owns pre-PR review, bounded fix-and-verify rounds, and escalation to `research` when three rounds of patch-on-patch churn do not converge.
---

# Review Prepare

## Scope

- This skill owns the PR-preparation self-review loop.
- This skill reviews the actual diff, fixes review findings, reruns verification, and decides whether the branch is clean enough to enter PR review.
- This skill does not create a PR, request external review, handle GitHub threads, merge, or close out trackers.

## Inputs

- Current diff or branch range
- Requirements source
- `plan/1` path when the task is plan-backed
- Verification commands for the touched area

## Outputs

- `no_findings`
- `findings`
- `needs_architecture_review`
- `blocked`

## Hard gates

- Review the actual diff, not memory of the implementation.
- Every fix round must be followed by fresh verification.
- Do not output `no_findings` without fresh verification evidence for the current branch state.
- Do not proceed to PR creation or `review-request` until this skill returns `no_findings`.

## Procedure

1. Collect the real review surface:
   - `git status --short`
   - `git diff --stat`
   - `git diff <range>`
2. Review the diff against requirements, plan intent, regression risk, missing tests, and docs/config impact.
3. Decide whether the current issues are:
   - clear findings to fix now
   - no findings
   - structure problems that need architecture work
4. If findings exist, fix the smallest coherent batch.
5. Run the scoped verification for that batch.
6. Review again from the new diff.

## Three-round escalation

- Count one round as: review -> fix -> re-verify -> re-review.
- If three consecutive rounds still produce new structural findings, stop patch-on-patch repair.
- Return `needs_architecture_review`.
- Default escalation target is `research`, not `research-pro`.
- If `research` recommends structural changes to module boundaries, interfaces, data flow, or tests, keep this skill at `needs_architecture_review` and let `research` or the caller hand the result back to `plan-writing`.

## Recommended checks

- Compare requirements against the current diff, not just tests.
- Re-read the current `plan/1` if one exists.
- Stack `verification-before-completion` before any success claim.
- Stack `scout-skeptic` when the diff is risky or the findings pattern is unclear.

## Red flags

- Calling the branch "ready" because tests happen to pass while the diff still contains obvious review debt
- Creating or updating a PR before self-review reaches `no_findings`
- Carrying GitHub thread behavior into this skill
- Continuing beyond three churn rounds without escalating to `research`
