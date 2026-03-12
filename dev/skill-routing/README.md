# skill-routing dev notes

This folder covers the source-repo denylist-only child policy contract.

## Contract

- Keep [`skill-routing/child-skill-policy.toml`](../../skill-routing/child-skill-policy.toml) minimal and distribution-safe.
- The shipped template is version 4 with `main_thread_only = []`.
- `main_thread_only` is the only restriction field in the source-repo shape.
- Omitted skills are allowed by default.
- Denylisted skills must be known local skill names from the relevant catalog.
- There is no `dispatch-authorized`, `authorized_skills`, runtime oracle, or full-coverage classification requirement in this method.

## Repo workflow

1. Keep the repo template empty unless the denylist contract itself changes.
2. Canonicalize the template when needed:
   - `python3 skill-routing/scripts/build_child_skill_policy.py --write`
3. Run the repo smoke:
   - `python3 dev/skill-routing/run_smoke.py`

## Optional runtime check

- Use the optional runtime check only when validating an installed runtime policy file.
- The smoke parses the runtime policy separately from the source template.
- Runtime denylist entries must resolve against the installed skills root, not the source-repo catalog.
- If an installed runtime policy is still on the legacy classification table, the smoke only projects its `main-thread-only` entries into the denylist check.
- Example:
  - `python3 dev/skill-routing/run_smoke.py --runtime-policy ~/.codex/skills/skill-routing/child-skill-policy.toml --runtime-skills-root ~/.codex/skills`

## Smoke expectations

- Repo template parses and stays canonically empty.
- A denylist fixture parses in version-4 form.
- Denylisted skills are blocked for child self-initiation.
- Omitted skills remain allowed.
- Unknown denylist entries are rejected.
- Optional runtime policy input parses and only references known installed skills.
