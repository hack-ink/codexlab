# AGENTS.md — Shared Policy + Main-Thread Workflow

## Applicability

- `Shared Policy` applies to every agent in this repo scope.
- `Main-Thread Entry` and `Main-Thread Workflow` apply only to the root or main thread.
- `Child Capability Boundary` applies to spawned child agents.
- Spawned child agents must follow the explicit dispatch plus their role-specific developer instructions.
- Spawned child agents must not reinterpret main-thread workflow text as permission to reroute, orchestrate, or delegate unless the dispatch explicitly tells them to.

## Main-Thread Entry

- Before any response or action, when you are the main thread, load and follow the `skill-routing` skill first.
- Treat `skill-routing` as the default entrypoint for skill discovery, selection, and loading discipline in this repo.
- If `skill-routing` is unavailable in the current runtime, say so briefly and continue with the best local fallback rather than blocking.

## Main-Thread Workflow

- Keep implementation ownership on the main thread by default. Route through the appropriate process skill before coding, but do not hand implementation ownership to child agents.
- For implementation work, route into `workspaces` first unless the task is read-only or the correct lane is already active.
- This repo does not require a persisted `plan/1` by default. Route through `plan-writing` and `plan-execution` only when the user explicitly asks for a plan, the task explicitly needs saved plan authority, or an already-active lane already depends on the correct current `plan/1`.
- When a task does use a persisted `plan/1`, keep that artifact inside the active workspace lane instead of leaving task-local plan files behind in the primary checkout.
- Start with one short local probe when it can cheaply reduce uncertainty.
- After that probe, run a scout/skeptic checkpoint for any non-trivial task.
- Treat a task as non-trivial once the first short probe still leaves either:
  - at least two independent read-only questions, hypotheses, or evidence gaps
  - one implementation path plus a second distinct verification, regression, or reviewer-risk question
- If parallel child-agent execution is unavailable or unnecessary, still run the checkpoint locally instead of skipping it outright.
- A local checkpoint is complete only when it records the current theory, the strongest contradictory evidence or risk, the missing evidence or test, and the next direct action.
- Load the `scout-skeptic` skill as an additive overlay when there are multiple independent questions, files, or evidence sources to inspect in parallel.
- Load the `scout-skeptic` skill as an additive overlay when there are multiple plausible hypotheses, meaningful regression risks, or missing tests to challenge.
- Load the `scout-skeptic` skill as an additive overlay when a read-only adversarial check would materially improve confidence before implementation or closeout.
- Load the `scout-skeptic` skill as an additive overlay when isolating exploration from the main context would reduce context bloat.
- Do not skip `scout-skeptic` solely because another process skill already applies.
- Use `scout` for read-only exploration, repo probing, reproductions, research, and evidence gathering.
- Use `skeptic` for read-only critique, gap-finding, verification, and adversarial review of the current theory or planned change.
- Create scout/skeptic child-agent objectives only when each objective is distinct and its output will be consumed by the main thread.
- Scout/skeptic child agents must not edit repo content, delegate further, or claim implementation ownership.
- Use one bounded scout/skeptic checkpoint round at a time: when child agents are warranted, dispatch distinct objectives, keep executing directly, do one bounded collect step at the next decision boundary, treat a timed-out collect as not ready yet, and retire stale child agents once enough evidence exists.
- Retire a child agent only when its missing evidence is already covered elsewhere or the main thread's acceptance is already independently satisfied.
- If a child agent still holds the only missing evidence, do one more bounded collect step or dispatch a narrower replacement instead of retiring it.
- If a child agent concludes that code should change, the main thread makes that change directly.
- If one bounded collect step still leaves the main thread without enough evidence, start a narrower new round or mark the task blocked.
- Spawned child agents do not execute this workflow section unless the dispatch explicitly asks them to.

## Child Capability Boundary

- Scout/skeptic child-agent capability boundaries are behavior rules, not skill-name allowlists.
- Child skill discovery does not grant authority by itself.
- Child agents must never initiate control-plane behavior unless the explicit dispatch requires it.
- Child agents must never change global or runtime state.
- Child agents must never widen task scope or reinterpret the task into a new workflow.
- Child agents must never become implementation owners.
- Child agents must never perform side effects outside the explicit dispatch.

## Shared Policy

### LLM-First

- Prefer acting over asking: run small probes or inspections first to reduce uncertainty.
- Only ask the user when truly blocked or when a choice affects scope or risk materially.

### MCP Routing

- For external library, framework, or API reference questions, use Context7 before generic web search.
- For questions about a GitHub repository outside the current workspace, use DeepWiki first when the repo is available there.
- For current-workspace implementation questions, inspect local files first; use DeepWiki only for upstream comparison or when local context is missing.
- If Context7 or DeepWiki is insufficient, fall back to official docs or direct repo inspection and say so briefly.

### Identity Routing

- Treat Git identity and Linear workspace selection as machine-routable context, not guesswork.
- Inside a Git worktree, read `git config --get codex.github-identity` and `git config --get codex.linear-workspace` from the current worktree.
- Do not treat inherited session-level `CODEX_*` environment variables as canonical routing inside a Git worktree.
- The canonical mapping is:
- `x` -> person `xavier` -> GitHub token `GITHUB_PAT_X` -> Linear workspace `helixbox` -> MCP server `linear_helixbox`
- `y` -> person `yvette` -> GitHub token `GITHUB_PAT_Y` -> Linear workspace `hackink` -> MCP server `linear_hackink`
- Inside a Git worktree, treat missing or invalid `codex.github-identity` as an error and stop rather than silently defaulting to another identity.
- If `codex.linear-workspace` is missing, derive it from `codex.github-identity` using the mapping above.
- Treat an invalid `codex.linear-workspace` as an error.
- Treat a mismatch between `codex.github-identity` and `codex.linear-workspace` as invalid configuration.
- Outside a Git worktree, or when no repo-specific override exists, default to `x` and `helixbox`.
- When a task touches GitHub or Linear state, use the routed identity/workspace from these signals unless the user explicitly says otherwise.

### Change Control

- Do not edit unrelated content.
- If unrelated local changes exist and do not conflict with the current task, leave them untouched and continue with your own scoped implementation.
- If unrelated local changes would be overwritten, create ambiguity, or otherwise conflict with the current task, do not discard them silently (no `git restore`); stop and ask the user how to handle them.
- If a conflict is detected, stop and report before proceeding.
- For parallel implementation lanes, prefer isolated clone-backed workspaces under a repo-local `.workspaces/` directory over shared-Git linked checkouts when lane-local Git writes or sandbox boundaries matter.
- Default one `.workspaces/*` lane per task, branch, and review stream.
- When multiple `.workspaces/*` lanes conflict, route to `workspace-reconcile` and keep one surviving lane.
- After a task is truly complete, return to `workspaces` for cleanup of the workspace plus local and remote branches.
- Treat remote branch cleanup as part of the target clean state. If GitHub already auto-deleted the branch after merge, confirm that absence and record it instead of treating cleanup as optional.

### Planning Workflow

- Default development flow is: `workspaces` -> `review-prepare` -> `pr-land` -> `delivery-closeout` -> `workspaces` cleanup.
- Treat the review stages as a required gate, not an optional tail step. Before downstream merge, closeout, or cleanup work, the current branch must clear the self-review gate (`review-prepare`, or the repaired-head `review-loop` path inside `review-repair`), and any external review already present on that PR head must go through `review-repair` before downstream steps.
- `plan-writing` and `plan-execution` are conditional overlays in this repo, not the default path. Use them only when the task explicitly needs saved `plan/1` authority.
- If a task uses a persisted `plan/1`, create, revise, and execute it from inside the active workspace lane so planning and implementation stay together.
- `plan-writing` owns the durable `plan/1` artifact and strategy when that artifact exists.
- `plan-execution` owns implementation against that saved `plan/1` when such a plan is the chosen authority.
- `plan/1` completion is plan-local. A saved plan reaching `done` does not by itself bypass downstream review, merge, `delivery-closeout`, or workspace cleanup gates unless those lifecycle stages are explicit tasks in that same saved plan.
- If implementation hits a blocker, structural change, or architecture result that changes task shape, route back through `plan-writing` before continuing only when the task is already using a saved `plan/1`; otherwise re-scope directly from the active workspace and research result.

### Git Gate

- Before any `git commit` or `git push`, run the `delivery-prepare` skill.
- `delivery-prepare` must discover and use the repo-native documented local gate. Do not assume a universal command sequence from file names alone.
- If a pushed delivery also needs tracker-state sync, run `delivery-closeout` after the push anchor exists.
- If a project or change is not actually tracked in Linear, `delivery` refs may be empty; do not create or require placeholder Linear issues only to satisfy the workflow.

### Review Workflow

- Run `review-prepare` before creating or refreshing a PR. Do not enter merge readiness or external-review repair handling until it returns `no_findings`.
- `review-prepare` and `review-repair` share the bounded `review-loop` engine for review -> fix -> verify -> re-review.
- `review-prepare` wraps `review-loop` for self review on the current diff before PR creation or PR head refresh.
- Treat any review on the PR beyond self review as external review.
- Treat external review as input to validate, not as a place to hand off known owned bugs or small cleanup.
- Use `review-repair` for PR review feedback. Check whether each external-review claim is true, repair the verified issues through the shared `review-loop`, reply in-thread, and resolve the threads whose fixes are actually verified.
- If a `review-repair` batch changes the branch, do not commit, push, or resolve against that repaired head until its repaired diff reaches `clean` through the shared `review-loop`.
- A repaired head that reaches `clean` through `review-loop` inside `review-repair` satisfies the current-head self-review gate for downstream merge, closeout, or cleanup decisions.
- If a `review-repair` batch needs commit or push, run `delivery-prepare` only after `review-loop` reaches `clean` for that repaired head, then continue the external-review repair loop on the new head.
- Every review-stage result must bind to an explicit head SHA for the branch state it reviewed or repaired.
- Treat review as incomplete for the current head until all relevant gates are satisfied:
  - the current branch state is clean either through `review-prepare` or through the repaired-head `review-loop` path inside `review-repair`
  - any external review feedback for that head has been handled through `review-repair`, with no owned unresolved repair work still blocking progress
- If the branch changes after an external-review repair round, re-enter the review flow for the new head instead of continuing downstream on stale review state.
- Do not enter `pr-land`, `delivery-closeout`, or `workspaces` cleanup until the current head's review flow is complete.
- If the shared `review-loop`, `review-prepare`, or `review-repair` still finds new bugs after three rounds, stop patch-on-patch churn and escalate to `research` for a deeper architecture or design pass. If the result changes module boundaries, interfaces, data flow, or test shape, return to `plan-writing` only when an active saved plan is part of the task.
- Waiting, polling, timer cadence, and retry policy for review or CI remain orchestration concerns. Skills should return state and let `maestro` re-enter later.

### PR Merge

- Use `pr-land` for PR readiness checks, sync decisions, and merge execution.
- `pr-land` stops at merge. It must not swallow `delivery-closeout` or workspace cleanup.
- `pr-land` is downstream of the review gate. Do not route into it while the current head still needs `review-prepare` or unresolved `review-repair`.
- If a delivery-style PR needs a merge commit, generate that merge commit's explicit `delivery/1` payload via `delivery-prepare` first; `pr-land` consumes that payload but does not author it.
- If every commit in a PR already uses the `delivery/1` format, preserve that style when merging: do not squash, do not discard commit-level delivery metadata, and keep the history style consistent.
- If that delivery-style PR cannot be fast-forwarded and requires a merge commit, the merge commit must also use the `delivery/1` format. Do not introduce a free-form merge commit into otherwise delivery-formatted history.
- If a PR does not consist entirely of `delivery/1` commits, treat it as non-delivery history and use a normal squash merge. No special commit-message policy is required in that case; the PR title or the platform default is fine.

### Delivery Closeout

- `delivery-closeout` is downstream of review completion and merge completion.
- Do not route into `delivery-closeout` until the current head has cleared the review gate and `pr-land` has finished the merge step or explicitly determined that merge is not pending.
- Treat workspace cleanup the same way: no cleanup before the review gate and merge/closeout state are actually satisfied.

### Language

- Default to English for internal work and durable artifacts unless the user explicitly requests otherwise.
- User-facing chat replies may mirror the user's language.

### Fetch Escalation

- Default to the lightest and fastest viable retrieval path first: local files, `curl`, built-in web fetch tools, or direct docs access before specialized scraping skills.
- Only invoke the `scrapling` skill to acquire content when `curl` or an equivalent lightweight fetch path returns blocked access such as `403 Forbidden`, `Access Denied`, or a comparable anti-bot refusal and therefore cannot retrieve the content.
- Do not use `scrapling` as the default browsing or research path when the lightweight fetch already succeeds.
- After `scrapling` obtains the blocked content, return to lighter local or text-based processing for extraction, analysis, and summarization.
