---
name: research
description: Use for bounded, decision-oriented research inside the research plugin. Default to one main agent, add scout or analyst only when the work cleanly parallelizes, frame rival hypotheses before broad search, verify key claims before finalizing, run a mandatory challenge pass, and end with either a decision-ready answer or an explicit not-decision-ready result.
---

# Research

## Objective

Turn an ambiguous question into a decision-ready recommendation with enough evidence to act, without drifting into open-ended deep research by default.

## Core stance

- This plugin is for **bounded research**, not deep research.
- Optimize for the best recommendation that can be justified within a modest time and evidence budget.
- Prefer a smaller set of high-quality sources over a large pile of low-signal search results.
- Stop when the answer is decision-ready.
- If the bounded pass cannot safely close the decision, stop and say `not decision-ready`.

## What this skill should do well

- Frame the decision before searching.
- Frame competing hypotheses before broad search.
- Gather enough current evidence to support or reject viable options.
- Compare at least two realistic options when a recommendation is required.
- Separate observations from inferences and recommendations.
- Verify key claims before finalizing.
- Run a lightweight adversarial challenge before finalizing.
- Say `not decision-ready` when the evidence budget is exhausted but the answer is still unsafe.

## What this skill is not

- It is not a long-running deep-research workflow.
- It is not the default place for broad architecture exploration across many rounds.
- It is not a "search forever" loop.
- It does not manage deep-research escalation or long-running orchestration.

## Required artifacts

Use the plugin-local templates in this plugin's `templates/` directory as the execution contract.

Always use:
- `research-brief.md`
- `evidence-map.md`
- `final-report.md`

Use only when needed:
- `option-analysis.md` for recommendations that compare multiple viable options

If the task uses workers, their output must fold back into the same brief, evidence map, and final report.

## Worker model

- Default to one main research agent.
- Use `scout` only for parallel source gathering.
- Use `analyst` only for independent option evaluation.
- Reuse `skeptic` only for a separate adversarial pass; otherwise run the challenge pass locally.
- Keep one canonical brief, one canonical evidence map, and one final report owned by the main agent.

## Hard rules

1. Read provided materials first, or state explicitly that none were provided.
2. Write a decision brief before broad search.
3. Ask only blocking questions.
4. Prefer three independent external sources by default when current guidance matters.
5. No evidence, no claim.
6. Compare at least two viable options when making a recommendation.
7. Define the leading hypothesis, rival hypotheses, and what evidence would falsify them before broad search; if the problem is still exploratory, say so explicitly and derive candidate hypotheses after an initial source scan.
8. Verify key claims before finalizing.
9. Run the challenge pass before finalizing.
10. If the result is still unsafe after bounded research, say `not decision-ready`.

## Workflow

1. Build the brief
   - Fill `research-brief.md`.
   - Capture the decision, success criteria, constraints, freshness requirement, non-goals, and bounded budget.
   - State the primary working hypothesis, the main rival hypotheses, and what evidence would falsify each one.
   - If the task is exploratory and the hypotheses are not yet credible, mark the brief as exploratory and define the smallest initial scan needed to derive candidate hypotheses.
   - Define what "enough to decide" means before searching.
   - Define the stop rule before broad search.

2. Read first
   - Summarize provided materials.
   - Confirm the pain points and why the decision matters now.

3. If exploratory, run the smallest useful initial scan and rewrite the brief
   - Use the smallest source scan needed to produce credible candidate hypotheses.
   - Rewrite the brief with explicit primary and rival hypotheses before entering the main bounded search.
   - If the initial scan still cannot produce credible hypotheses, stop and say `not decision-ready`.

4. Search with a bounded budget
   - Prefer primary documentation and current sources.
   - Keep a compact search log.
   - Record meaningful negative results and abandoned search paths when they affect confidence or coverage.
   - Stay within the brief's time, source, and search-round budget.
   - Search for confirming and disconfirming evidence instead of only supporting evidence.
   - Stop gathering once the evidence is sufficient to evaluate the leading options and rival hypotheses.

5. Build the evidence map
   - Record each major claim in `evidence-map.md`.
   - Assign a stable evidence or claim ID to each entry so downstream conclusions can cite it directly.
   - Separate observation, inference, and decision relevance for each major claim.
   - Keep the evidence map as the canonical place for source locators, versions, snapshots, and verification status.

6. Analyze options
   - Fill `option-analysis.md` only when the recommendation compares multiple viable options.
   - Keep each option analysis comparative and brief.
   - For any option that enters the final comparison, cite supporting and disconfirming evidence IDs from the canonical evidence map.
   - Use `analyst` only when those option evaluations can run independently.

7. Verify key claims
   - Re-check the most decision-critical claims against the cited sources before finalizing.
   - Prefer independent re-checks from different sources or publishers when feasible.
   - If only a same-source re-check is possible, label it explicitly and do not treat it as strong independent corroboration.
   - Confirm that the final recommendation is supported by observations and inferences already recorded in the evidence map.
   - If a decision-critical claim lacks independent re-check support, do not present the result as high confidence.
   - If a decision-critical claim cannot be re-verified at all, mark the result `not decision-ready`.

8. Run the challenge pass
   - Ask:
     - What is the strongest case against the current recommendation?
     - Which runner-up option could plausibly be better?
     - What evidence contradicts the current thesis?
     - What new evidence would flip the decision?
   - If this challenge materially weakens the current recommendation, revise or mark the answer `not decision-ready`.

9. Write the final report
   - Fill `final-report.md`.
   - Include the research mode, a clear recommendation, confidence level plus rationale, counterevidence, why not the runner-up, and what would change your mind.
   - For each major conclusion, counterevidence item, and verification check, cite the relevant evidence IDs from the evidence map.
   - Keep detailed source metadata in the evidence map. The final report should cite evidence IDs and summarize only the key source references needed to audit the recommendation.
   - Record any material deviations from the original brief, source hierarchy, or stop rule, and explain why they were necessary.
   - If the answer is still unsafe, record `not decision-ready`, the bounded-budget outcome, and the missing evidence that prevented closure.

## Success condition

This skill succeeds only when one of these is true:

- You have a decision-ready recommendation with explicit evidence, challenge results, confidence, and next steps.
- You have an explicit `not decision-ready` outcome with the missing evidence called out.
