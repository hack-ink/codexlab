---
name: review-repair
description: Use after a PR has review feedback on GitHub. Owns unresolved-thread triage, fix-and-verify rounds, in-thread replies, conditional resolve, and escalation to `research` when three review-repair rounds do not converge.
---

# Review Repair

## Scope

- This skill owns the GitHub review-fix loop after a PR already exists.
- This skill reads unresolved review comments, evaluates them with `receiving-code-review`, fixes valid issues, reruns verification, replies in-thread, and resolves only the threads that are actually complete.
- This skill does not request review, merge, close out trackers, or clean up workspaces.

## Inputs

- PR URL or PR number
- `plan/1` path when applicable
- Optional review round identifier

## Outputs

- `repaired`
- `no_action`
- `needs_re_review`
- `awaiting_external`
- `needs_architecture_review`
- `blocked`

## Hard gates

- Judge each comment with `receiving-code-review` before touching code.
- Re-run fresh verification after every repair batch.
- Reply in the GitHub thread, not as a top-level PR comment.
- Resolve a thread only when all of these are true:
  - the code is actually fixed
  - verification passed on that new state
  - the thread reply matches the fix that landed
- Do not resolve when you are pushing back, asking for clarification, or still carrying unresolved work.

## Procedure

1. Collect unresolved review threads and requested changes.
2. For each thread:
   - restate the technical requirement
   - validate it against the codebase
   - decide: fix now, push back, or ask for clarification
3. Group compatible fixes into the smallest coherent repair batch.
4. Apply the batch and re-run scoped verification.
5. Reply in-thread for every addressed comment.
6. Resolve only the threads that satisfy the hard gates.
7. If the branch changed in a reviewer-visible way, return `needs_re_review`.

## Three-round escalation

- Count one round as: review feedback -> repair -> re-verify -> next review pass.
- If three consecutive rounds still produce new structural problems, stop incremental patching.
- Return `needs_architecture_review`.
- Default escalation target is `research`.
- If `research` changes interfaces, data flow, module ownership, or test shape, keep this skill at `needs_architecture_review` and let `research` or the caller route the result back through `plan-writing`.

## Thread discipline

- Fixes must be acknowledged in the comment thread they address.
- Pushback must be technical and specific.
- Clarification requests must keep the thread open.
- Resolve is part of the repair contract, not an optional courtesy.

## Red flags

- Treating every reviewer suggestion as automatically correct
- Repairing code without re-running verification
- Posting a top-level PR comment instead of replying in-thread
- Resolving a thread before the fix is verified
- Requesting another review round from inside this skill instead of returning `needs_re_review`
