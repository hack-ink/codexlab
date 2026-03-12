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
- Keep the saved plan current when durable execution state changes. The plan should stay resumable for the next session.
- Prefer an isolated workspace when branch isolation, risky changes, or concurrent work make that useful.
- Before any commit or push, follow the local commit/push gate. If the repo or user requires review, stop at a reviewable checkpoint instead of self-approving.

## Plan maintenance contract

- Update the saved plan when execution changes durable state: task status, owner, next checkpoint, blockers, dependencies, verification path, or a decision that changes later work.
- Task-level `Status` is the sole completion authority for resuming work. Treat `Execution State` as resume metadata only.
- Update the saved plan when a checkpoint becomes a review stop, an isolated-workspace candidate, or a new helper round.
- A chat-only note is enough for transient execution detail that does not change what the next executor should do.
- Keep plan updates terse. Record state and evidence, not a diary.
- Keep operational procedure in adjacent workflows instead of re-documenting it in the saved plan.

## Execution workflow

1. Load the plan and identify the next unfinished checkpoint from task-level `Status`, using `Next Checkpoint` as the resume pointer when it is current.
2. Re-read the referenced files and commands that matter for that checkpoint.
3. Challenge the plan briefly:
   - Is the file layout still current?
   - Do the listed commands still exist?
   - Did earlier work change the intended order or scope?
4. If the checkpoint is still sound, execute a batch.
5. Run the checkpoint's verification before reporting progress.
6. If execution changed durable state, update the saved plan in the same batch.
7. Report what changed, what passed, and any blockers before starting the next batch.

## Batch sizing

- Default to one coherent checkpoint from the plan.
- If the plan decomposes work into very small tasks, execute a small batch of 1-3 closely related tasks before stopping.
- If the plan's boundary is naturally larger or smaller than that, follow the plan's structure instead of forcing a fixed batch size.
- Stop early when a blocker appears, verification fails, or the remaining work would cross into a new review boundary.
- If the remaining work now needs an isolated workspace or a bounded helper round, stop and reroute instead of stretching the current batch.

## Verification

- Run the exact verification commands named in the plan whenever they still apply.
- If a command has drifted, replace it only after confirming the repo's current equivalent.
- Do not report a batch as complete until the relevant verification has run on the current state.
- If verification fails, report the failure and either fix it within the current checkpoint or stop for plan clarification.
- When verification changes the path forward, record the result in the plan tersely enough that the next executor can see why the state changed.

## When to update the saved plan

- Mark tasks `in progress`, `blocked`, or `done` when that status matters for resuming later.
- Treat `Owner` as checkpoint accountability or execution handoff, not as child-role selection or write authority.
- Refresh `Execution State` metadata when `Last Updated`, `Next Checkpoint`, or `Blockers` change. Do not use it as a second completion channel.
- Update file paths, commands, or task text if the original plan is no longer accurate.
- Add or refresh a short `Decision Notes` entry when a material decision or drift update changes the path or rationale. Include the evidence source tersely.
- Skip plan edits for transient chatter that leaves scope, order, and next action unchanged.

## Progress reporting

After each batch, report:

- Which checkpoint or tasks were completed
- Which files changed
- Which verification commands ran and whether they passed
- Any blockers, plan updates, or decisions needed before continuing

Then either continue with the next checkpoint or wait if the user asked for staged review.

## Integration

- This skill consumes a saved plan artifact produced earlier.
- Use the repo's isolated-workspace workflow when execution should not happen in the current checkout.
- Apply the repo's commit/push gate before `git commit` or `git push`.
- If review gates apply, use the repo's required review workflow before calling the work done.
- If execution reveals a needed helper round or isolated workspace, stop and hand off through the appropriate flow instead of continuing on stale assumptions.

## Red flags

- Starting implementation without reading the saved plan
- Treating an old plan as correct after the codebase has moved
- Blasting through many checkpoints without intermediate verification
- Replacing repo-native commands with generic defaults
- Continuing past a blocker instead of updating the plan or asking for clarification
