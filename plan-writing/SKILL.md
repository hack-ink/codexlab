---
name: plan-writing
description: Use when the user asks for a plan, when a multi-step or risky task should be decomposed before implementation, or when the runtime is in Plan mode. Produces or updates a durable implementation plan at `docs/plans/YYYY-MM-DD_feature-name.md`, grounded in the current repo's actual file paths, verification commands, dependencies, and open questions before code changes begin.
---

# Plan Writing

## Purpose

Create execution-ready plan documents that another agent or a later session can follow without re-discovering the codebase from scratch.

Typical triggers:

- The user explicitly asks for a plan, design, or implementation breakdown
- The task is large enough that coding immediately would be sloppy or risky
- The runtime is already in a dedicated Plan mode
- The next step should be a durable plan document before work starts

## Core rules

- Stay in planning scope. Do not start implementation unless the user explicitly asks to execute now.
- Ground the plan in current repo evidence. Read enough code, docs, and instructions to avoid placeholder guidance.
- Write for an executor who is technically strong but new to this codebase.
- Prefer exact file paths, exact commands, and explicit dependencies whenever you can resolve them now.
- If an important detail is still unknown after reasonable inspection, record it as an open question instead of pretending certainty.
- Make the saved plan easy to resume. Capture durable execution state and decision points, not a chat transcript.

## Plan-mode contract

- In runtimes with a dedicated Plan mode, this skill owns the planning artifact.
- Use Plan mode to converge on scope, assumptions, risks, and execution order.
- The main output of the turn should be a saved or updated plan document, not code changes.
- If the user wants execution immediately after planning, treat the saved plan as the source of truth for the next phase.

## Save location

- Save plans under `docs/plans/YYYY-MM-DD_<feature-name>.md`.
- Use the local current date in `YYYY-MM-DD` form.
- Use a short, stable feature slug after the underscore. Prefer lowercase ASCII words joined with hyphens.
- If a matching plan already exists for the same feature, update it instead of creating duplicates.

Example:

```text
docs/plans/2026-03-10_query-ast.md
```

## Living artifact contract

- The saved plan is a lightweight execution artifact, not a one-turn brainstorm.
- Record only durable state another executor needs: task status, owner, next checkpoint, blockers, dependency shifts, and decisions that change the path.
- Use task-level `Status` as the only completion authority. Keep `Execution State` limited to resume metadata such as `Last Updated`, `Next Checkpoint`, and `Blockers`.
- Keep ephemeral chatter out of the plan. Notes like "read file", "thinking", or "retrying command" belong in chat unless they change execution.
- For important drift or decision changes, add a short factual note with the evidence source that caused the update.
- Reference adjacent skills for operational procedure instead of re-documenting them inline. Point to flows like `git-worktrees`, `pre-commit`, or `multi-agent` when they apply.
- If the work will likely split into a separate worktree, review stop, or `multi-agent` lane, say so in the plan instead of pretending the whole effort is one uninterrupted lane.

## Planning workflow

1. Read the request, issue, spec, or surrounding instructions.
2. Inspect enough repository context to understand the relevant modules, constraints, and verification path.
3. Decide the plan boundary: goal, scope, non-goals, dependencies, open questions, and likely handoff points.
4. Set the initial execution state so a later session can see where to start.
5. Break the work into reviewable tasks with clear sequencing, ownership, and visible progress signals.
6. For each task, record the files, intended changes, dependencies, and verification commands.
7. Save or update the plan document and summarize the recommended execution path.

## Quality bar

- Make tasks small enough to execute and review independently, but not so tiny that the plan turns into noise.
- A task should usually correspond to one coherent checkpoint, not one sentence-long micro-action.
- Include exact verification commands when known, using repo-native workflows instead of generic guesses.
- Make accountability visible without ceremony. Each task should have one clear owner.
- Call out when work should happen in an isolated worktree or when tasks can be parallelized safely.
- Call out review or routing boundaries when a checkpoint should stop for inspection, hand off to `plan-execution`, or move into a separate worktree/PR-sized/`multi-agent` lane.
- If docs, migrations, config, or rollout steps matter, include them explicitly rather than leaving them implied.

## Required plan structure

Every plan should follow this shape:

````markdown
# <Feature Name> Plan

## Goal

<One short paragraph on what this change should accomplish.>

## Scope

- <What is in scope>
- <What is in scope>

## Non-goals

- <What this plan intentionally does not change>

## Constraints

- <Repo rules, compatibility limits, rollout limits, or time constraints>

## Open Questions

- None.

## Execution State

- Last Updated: <YYYY-MM-DD>
- Next Checkpoint: Task 1
- Blockers: None.

## Decision Notes

- None.

## Implementation Outline

<Two or three short paragraphs describing the approach and key tradeoffs.>

## Task 1: <Checkpoint name>

**Owner**

<Who is accountable for driving this checkpoint or execution lane handoff. This is not `multi-agent` role selection or `ownership_paths` write authority.>

**Status**

pending

**Outcome**

<What will be true after this task completes.>

**Files**

- Modify: `path/to/existing/file`
- Create: `path/to/new/file`
- Review: `path/to/related/doc.md`

**Changes**

1. <Concrete change>
2. <Concrete change>

**Verification**

- `exact command`
- `exact command`

**Dependencies**

- None.

## Task 2: <Checkpoint name>

...

## Rollout Notes

- <Only when relevant>

## Suggested Execution

- Sequential: <why>
- Parallelizable: <which tasks, if any>
````

## Task-writing guidance

- Prefer "Modify `path/to/router/file` to register the new endpoint" over "Update routing".
- Prefer "Run the repo's verified test or lint command" over "Run tests".
- Give each task one clear owner, even if the same executor owns most of the plan.
- Use `Owner` for checkpoint accountability and execution handoff, not for `multi-agent` role selection or `ownership_paths` authority.
- Use explicit task status values such as `pending`, `in progress`, `blocked`, and `done`.
- Treat task-level `Status` as the only completion authority. Use `Execution State` only for resume metadata, not for a second progress field.
- If a task depends on a prior task, say so explicitly.
- If a task may need a worktree, say so explicitly and point to the `git-worktrees` workflow.
- Reference adjacent skills for operational mechanics instead of pasting their procedures into the plan.
- If a task should stop for review or branch into a separate PR-sized or `multi-agent` stream, say where execution should pause and reroute.
- For material decisions or drift corrections, use a short `Decision Notes` bullet with the reason and evidence pointer instead of a long narrative.
- If a task is risky or likely to branch, note the decision point before the risky step.

## Handoff

After saving the plan:

- Report the saved path.
- Summarize the execution shape in a few lines.
- List any open questions or assumptions that still need confirmation.
- Call out the initial execution state and any expected worktree or review boundary.
- If execution should happen next, recommend whether to proceed sequentially in the current session or hand the saved plan to `plan-execution` in the current or a separate session.

## Red flags

- Starting code changes before the plan is written
- Writing a plan with vague steps such as "implement logic" or "fix tests"
- Omitting verification commands even though the repo has known build or test entrypoints
- Leaving file paths unresolved when local inspection could have identified them
- Producing a plan that is only useful to the current session and not to a later executor
