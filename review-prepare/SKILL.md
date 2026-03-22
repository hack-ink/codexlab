---
name: review-prepare
description: Use before creating or refreshing a PR head, including after `review-repair` changes the branch, to run the primary self-review gate on the actual diff. Owns branch-readiness review, bounded fix-and-verify rounds, and escalation to `research` when three rounds of patch-on-patch churn do not converge.
---

# Review Prepare

## Scope

- This skill owns the primary self-review gate for branch readiness.
- This skill reviews the actual diff, fixes review findings, reruns verification, and decides whether the branch is clean enough to proceed without any known owned review debt.
- This skill does not create a PR, handle external-review threads, merge, or close out trackers.

## Inputs

- Current diff or branch range
- Current head SHA
- Requirements source
- `plan/1` path when the task is plan-backed
- Verification commands for the touched area

## Outputs

- Emit a machine-readable result envelope with these required fields:
  - `status`: one of `no_findings`, `findings`, `needs_architecture_review`, `blocked`
  - `head_sha`: exact reviewed head SHA that this decision applies to
  - `evidence`: ordered list of verification or review evidence strings for that head; use `[]` when no fresh verification evidence exists yet

Every emitted result must use the stable `head_sha` field name for the reviewed branch state. Do not hide the reviewed SHA only inside prose.

## Hard gates

- Review the actual diff, not memory of the implementation.
- Every fix round must be followed by fresh verification.
- Do not output `no_findings` until you have challenged the current diff from both the implementation lens and an adversarial reviewer lens.
- The adversarial reviewer pass must explicitly check regression risk, missing tests, docs/config drift, and operator-facing fallout for the current diff.
- Do not output `no_findings` without fresh verification evidence for the current branch state.
- Do not output `no_findings` while any known owned issue remains on the current head, even if it is a small or obvious fix.
- External review is input to validate after self review, not a place to hand off known owned cleanup.
- Bind every decision to the explicit reviewed head SHA for that branch state through the stable `head_sha` field.
- Do not proceed to PR creation, PR head refresh, merge readiness, or external-review repair handling until this skill returns `no_findings`.

## Procedure

1. Collect the real review surface:
   - `git status --short`
   - `git rev-parse HEAD`
   - `git diff --stat`
   - `git diff <range>`
2. Run the implementation pass against requirements, plan intent, and the intended user-visible behavior of the diff.
3. Run a second pass from the adversarial reviewer lens:
   - look for regression risk and missing tests
   - look for docs, config, migration, or operator-facing fallout
   - challenge whether the current diff would survive a skeptical re-read even if tests are green
4. Decide whether the current issues are:
   - clear findings to fix now
   - no findings
   - structure problems that need architecture work
5. If findings exist, fix the smallest coherent batch.
6. Run the scoped verification for that batch.
7. Review again from the new diff and re-read `git rev-parse HEAD` if the branch changed during the loop.
8. Emit the machine-readable result envelope with `status`, `head_sha`, and `evidence` for the reviewed branch state.

## Three-round escalation

- Count one round as: review -> fix -> re-verify -> re-review.
- If three consecutive rounds still produce new bugs, owned findings, or structural problems, stop patch-on-patch repair.
- Return `needs_architecture_review`.
- Default escalation target is `research`, not `research-pro`.
- If `research` recommends structural changes to module boundaries, interfaces, data flow, or tests, keep this skill at `needs_architecture_review` and let `research` or the caller hand the result back to `plan-writing`.

## Recommended checks

- Compare requirements against the current diff, not just tests.
- Re-read the current `plan/1` if one exists.
- Re-run the adversarial reviewer pass after every non-trivial repair batch instead of trusting the previous review result.
- Stack `verification-before-completion` before any success claim.
- Stack `scout-skeptic` when the diff is risky or the findings pattern is unclear, or run an explicit local skeptic pass before `no_findings`.

## Red flags

- Calling the branch "ready" because tests happen to pass while the diff still contains obvious review debt
- Returning `no_findings` without a fresh adversarial reviewer pass on the current diff
- Returning `no_findings` while known owned issues are still queued for someone else to catch later
- Creating or refreshing a PR head before self-review reaches `no_findings`
- Carrying GitHub thread behavior into this skill
- Continuing beyond three churn rounds without escalating to `research`
