---
name: plan-execution
description: Use when the user wants to execute an existing implementation plan, continue from `docs/plans/*`, implement a saved plan in a separate session, or resume work after leaving Plan mode. Reviews the plan as the source of truth, executes one coherent checkpoint or small task batch at a time, verifies each batch, and reports progress before continuing.
---

# Plan Execution

## Purpose

Turn a saved implementation plan into verified code changes without re-planning the whole task from scratch.

Typical triggers:

- The user says "execute this plan" or links a plan doc
- Work should continue from `docs/plans/YYYY-MM-DD_<feature-name>.md`
- A separate session is asked to implement a saved plan
- Plan mode is over and execution should begin

## Core rules

- Treat the plan document as the current source of truth for scope and sequencing.
- Review the plan critically against the current repo state before coding. Do not assume the plan is still correct.
- If the plan is stale, contradictory, or missing a decision needed to proceed, stop and update or clarify the plan before implementation.
- Prefer an isolated worktree when branch isolation, risky changes, or concurrent work make that useful. Follow `git-worktrees` when applicable.
- Before any commit or push, follow the local `pre-commit` gate. If the repo or user requires review, stop at a reviewable checkpoint instead of self-approving.

## Execution workflow

1. Load the plan and identify the next unfinished checkpoint.
2. Re-read the referenced files and commands that matter for that checkpoint.
3. Challenge the plan briefly:
   - Is the file layout still current?
   - Do the listed commands still exist?
   - Did earlier work change the intended order or scope?
4. If the checkpoint is still sound, execute a batch.
5. Run the checkpoint's verification before reporting progress.
6. Report what changed, what passed, and any blockers before starting the next batch.

## Batch sizing

- Default to one coherent checkpoint from the plan.
- If the plan decomposes work into very small tasks, execute a small batch of 1-3 closely related tasks before stopping.
- If the plan's boundary is naturally larger or smaller than that, follow the plan's structure instead of forcing a fixed batch size.
- Stop early when a blocker appears, verification fails, or the remaining work would cross into a new review boundary.

## Verification

- Run the exact verification commands named in the plan whenever they still apply.
- If a command has drifted, replace it only after confirming the repo's current equivalent.
- Do not report a batch as complete until the relevant verification has run on the current state.
- If verification fails, report the failure and either fix it within the current checkpoint or stop for plan clarification.

## Progress reporting

After each batch, report:

- Which checkpoint or tasks were completed
- Which files changed
- Which verification commands ran and whether they passed
- Any blockers, plan updates, or decisions needed before continuing

Then either continue with the next checkpoint or wait if the user asked for staged review.

## Integration

- `plan-writing` produces the plan artifact that this skill executes.
- `git-worktrees` prepares an isolated workspace when execution should not happen in the current checkout.
- `pre-commit` applies before `git commit` or `git push`.
- If review gates apply, use the repo's required review workflow before calling the work done.

## Red flags

- Starting implementation without reading the saved plan
- Treating an old plan as correct after the codebase has moved
- Blasting through many checkpoints without intermediate verification
- Replacing repo-native commands with generic defaults
- Continuing past a blocker instead of updating the plan or asking for clarification
