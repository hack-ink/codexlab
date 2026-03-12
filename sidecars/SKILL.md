---
name: sidecars
description: Use when a task benefits from helper-agent fan-out for exploration or critique while the main thread remains the only implementation owner.
---

# Sidecars

## Purpose

Use Codex helper agents as optional, read-only sidecars inside one task. This skill explains when to spawn helpers, when not to, and how to ask for evidence that the main thread can use immediately.

## Core model

- The main thread owns the task from start to finish.
- `scout` and `skeptic` are disposable helper agents.
- Helpers are read-only. They must not edit repo content, delegate further, or take implementation ownership.
- If a helper concludes that code should change, it stops and hands that conclusion back to the main thread.

## Spawn a `scout` when

- You need codebase exploration, repo probing, reproductions, or evidence gathering in parallel.
- You need multiple independent research questions answered faster than one serial pass.
- You want a helper to gather evidence while the main thread continues direct work.

## Spawn a `skeptic` when

- You want an adversarial read on the current theory or planned change.
- You need someone to look for missed edge cases, missing tests, missing evidence, or regression risks.
- You want a read-only review pass before trusting a fix, explanation, or closeout claim.

## Do not spawn anything when

- A short local probe by the main thread will answer the question.
- The subtask would require repo edits or sustained implementation ownership.
- Two helpers would duplicate the same objective.
- The output would not materially change the next main-thread step.

## Writing a good helper prompt

- Give the helper exactly one narrow objective.
- Point to the smallest relevant files, commands, or evidence sources.
- Ask for concrete findings, not open-ended brainstorming.
- Ask the helper to stop at evidence and recommended next checks, not implementation.
- Keep prompts short enough that the helper does not need to reconstruct the whole task.

Good `scout` prompt shape:

```text
Inspect <paths> and determine whether <specific claim> is true.
Return only the evidence, the confidence level, and the smallest next check if evidence is missing.
Do not edit files.
```

Good `skeptic` prompt shape:

```text
Challenge this theory: <current theory>.
Look for missing edge cases, contradictory evidence, or tests we would still need before trusting it.
Do not edit files.
```

## Concurrency rules

- Do not add a local cap beyond whatever the runtime already enforces.
- Every helper must have a distinct objective.
- Every helper's output must be consumable by the main thread.
- Once enough evidence exists, retire stale or redundant helpers instead of waiting for them.

## Red flags

- Treating a helper as a code-writing lane
- Spawning helpers with overlapping objectives
- Waiting on a stale helper that no longer affects the next decision
- Adding custom protocols, schedulers, or recovery logic on top of the runtime

## Maintainer check

- `python3 dev/sidecars/run_smoke.py`
