---
name: research
description: Use for bounded, decision-oriented research inside the research plugin. Start with one main agent and a brief, add scout or analyst only for clearly independent research slices, prefer a late skeptic pass before recommendation, verify key claims before finalizing, and end with either a decision-ready answer or an explicit not-decision-ready result.
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
Use the codexlab host-level `scout`, `analyst`, and `skeptic` agent roles from `.codex/agents/` plus `.codex/config.toml` as the worker configuration source when dispatching child agents.
Persist every run under the active project root at `docs/research/`.

Always use:
- `research-brief.md`
- `evidence-map.md`
- `final-report.md`
- `report.json`

Use only when needed:
- `option-analysis.md` for recommendations that compare multiple viable options

If the task uses workers, their output must fold back into the same brief, evidence map, and final report.
Every run must write its artifacts to `docs/research/runs/YYYY-MM-DD_<slug>/` and update `docs/research/index.json`.

## Worker model

- Default to one main research agent.
- The main agent owns framing, the canonical brief, the evidence map, and the final report.
- Do not fan out before the brief is clear enough to expose genuinely independent research slices.
- Use the host-level `scout` only for parallel source gathering.
- Use the host-level `analyst` only for independent option evaluation.
- Use the host-level `skeptic` late in the run to challenge a draft recommendation or narrowed option set; otherwise run the challenge pass locally.
- Dispatch worker agents through the codexlab host-level agent registration in `.codex/config.toml`, not through plugin-bundled agent files.
- Keep one canonical brief, one canonical evidence map, and one final report owned by the main agent.
- Use workers to isolate independent slices, not to parallelize every phase of the run and not to write parallel sections of the final report.

## Worker trigger rules

- After the brief and read-first pass, dispatch workers only when the task now exposes one or more clearly independent slices whose outputs can be merged back into the canonical evidence map and final report without overlap.
- Dispatch the host-level `scout` when external research remains and it can be cleanly split into independent source or topic slices.
- Dispatch the host-level `analyst` when at least two viable options remain and each option can be evaluated independently enough to improve the next comparison.
- Prefer dispatching the host-level `skeptic` after the evidence map exists and a draft recommendation or narrowed option set is available.
- Before any decision-ready recommendation, dispatch the host-level `skeptic` unless the run is low-risk and purely descriptive.
- If a trigger fires and child-agent execution is available, dispatch the corresponding worker instead of silently doing the same pass locally.
- If a trigger fires but child-agent execution is unavailable, continue with a local fallback and record that downgrade in both `final-report.md` and `report.json`.
- Do not dispatch overlapping workers that would gather the same evidence or argue the same case in parallel.

## Worker output contract

- `scout` output must provide:
  - source candidates or evidence gathered
  - source quality or credibility notes
  - missing evidence or unresolved gaps
- `analyst` output must provide:
  - option name
  - benefits, risks, assumptions, and rejection conditions
  - supporting and disconfirming evidence IDs or the evidence needed to create them
- `skeptic` output must provide:
  - strongest counter-thesis
  - contradictory evidence or missing evidence
  - weakest assumption in the current recommendation
  - flip condition that would change the recommendation
- The main agent must merge worker output back into the canonical brief, evidence map, option analysis, final report, and report.json before finalizing.
- `report.json` must be derived from the final canonical brief, evidence map, option analysis, and final report rather than written as an independent parallel summary.

## Persistence contract

- The default persistence root is `docs/research/` under the active project root.
- If `docs/research/` does not exist, create it before writing the first run.
- If `docs/research/index.json` does not exist, initialize it as:
  - `{"schema":"research-index/1","runs":[]}`
- Create one run directory per research task at `docs/research/runs/YYYY-MM-DD_<slug>/`.
- Always write:
  - `research-brief.md`
  - `evidence-map.md`
  - `final-report.md`
  - `report.json`
- Write `option-analysis.md` when multiple viable options were compared.
- Update `docs/research/index.json` with the new run ID, date, status, question, confidence, and artifact paths.
- Before claiming success, run the plugin-local consistency validator at `scripts/validate_research_run.py --run-dir <run-dir>` when local scripting is available; otherwise perform the same checks manually.
- Do not claim success until the run artifacts are written.

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
   - If `docs/research/` or `docs/research/index.json` is missing, create and initialize them first.
   - Fill `research-brief.md`.
   - Assign a run ID and run directory under `docs/research/runs/YYYY-MM-DD_<slug>/`.
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
   - If independent external research slices remain after the brief and read-first pass, dispatch the host-level `scout` for those slices and wait for one bounded collect step before finalizing the evidence map.

5. Build the evidence map
   - Record each major claim in `evidence-map.md`.
   - Assign a stable evidence or claim ID to each entry so downstream conclusions can cite it directly.
   - Separate observation, inference, and decision relevance for each major claim.
   - Keep the evidence map as the canonical place for source locators, versions, snapshots, and verification status.

6. Analyze options
   - Fill `option-analysis.md` only when the recommendation compares multiple viable options.
   - Keep each option analysis comparative and brief.
   - For any option that enters the final comparison, cite supporting and disconfirming evidence IDs from the canonical evidence map.
   - If multiple viable options remain and they can be evaluated independently, dispatch the host-level `analyst` for those options and do one bounded collect step before final comparison.

7. Verify key claims
   - Re-check the most decision-critical claims against the cited sources before finalizing.
   - Prefer independent re-checks from different sources or publishers when feasible.
   - If only a same-source re-check is possible, label it explicitly and do not treat it as strong independent corroboration.
   - Confirm that the final recommendation is supported by observations and inferences already recorded in the evidence map.
   - If a decision-critical claim lacks independent re-check support, do not present the result as high confidence.
   - If a decision-critical claim cannot be re-verified at all, mark the result `not decision-ready`.

8. Run the challenge pass
   - Once the evidence map exists and a draft recommendation or narrowed option set is available, prefer dispatching the host-level `skeptic` and do one bounded collect step before locking the recommendation.
   - Ask:
     - What is the strongest case against the current recommendation?
     - Which runner-up option could plausibly be better?
     - What evidence contradicts the current thesis?
     - What new evidence would flip the decision?
   - If this challenge materially weakens the current recommendation, revise or mark the answer `not decision-ready`.

9. Write the final report
   - Fill `final-report.md`.
   - Include the run ID, run directory, worker usage, challenge mode, a clear recommendation, confidence level plus rationale, counterevidence, why not the runner-up, and what would change your mind.
   - For each major conclusion, counterevidence item, and verification check, cite the relevant evidence IDs from the evidence map.
   - Keep detailed source metadata in the evidence map. The final report should cite evidence IDs and summarize only the key source references needed to audit the recommendation.
   - Record any material deviations from the original brief, source hierarchy, or stop rule, and explain why they were necessary.
   - If the answer is still unsafe, record `not decision-ready`, the bounded-budget outcome, and the missing evidence that prevented closure.

10. Write the machine-readable report
   - Fill `report.json`.
   - Derive `report.json` from the final canonical brief, evidence map, option analysis, and final report rather than inventing new claims there.
   - Record the status, decision readiness, confidence, challenge mode, worker usage, missing evidence, and artifact paths.
   - Update `docs/research/index.json` so later runs and follow-up automation can discover this report.
   - Validate the completed run with `scripts/validate_research_run.py --run-dir <run-dir>` when local scripting is available.

## Success condition

This skill succeeds only when one of these is true:

- You have a decision-ready recommendation with explicit evidence, challenge results, confidence, next steps, persisted Markdown artifacts, and `report.json`.
- You have an explicit `not decision-ready` outcome with the missing evidence called out and the persisted run artifacts written.
