#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "review-repair" / "SKILL.md"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"review-repair skill must contain {needle!r}")


def assert_block(text: str, block: str) -> None:
    needle = dedent(block).strip()
    if needle not in text:
        raise AssertionError(f"review-repair skill must contain block:\n{needle}")


def main() -> int:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: review-repair",
        "External review feedback is input to evaluate",
        "machine-readable result envelope",
        "`status`",
        "`head_sha`",
        "`pr_ref`",
        "`evidence`",
        "repaired head SHA",
        "Reply in the GitHub thread",
        "Resolve a thread only",
        "resolve it through GitHub instead of leaving manual cleanup behind",
        "If a repair batch needs `git commit` or `git push`, route through `delivery-prepare` before committing or pushing that repaired head.",
        "A repair batch that produces and pushes a new head is not review-complete by itself; return `needs_re_review` for that pushed head so the branch re-enters `review-request`.",
        "`gh api graphql`",
        "use `path`, `line` / `startLine`, and the latest comment `url` or body to match the right `$THREAD_ID` before resolving",
        "`needs_re_review`",
        "`awaiting_external`",
        "three consecutive rounds",
        "technical reasoning",
        "`research`",
    ]:
        assert_contains(text, needle)
    assert_block(
        text,
        """
        reviewThreads(first: 100) {
                    nodes {
                      id
                      isResolved
                      isOutdated
                      path
                      line
                      startLine
                      comments(last: 1) {
        """,
    )
    assert_block(
        text,
        """
        mutation($threadId: ID!) {
              resolveReviewThread(input: {threadId: $threadId}) {
        """,
    )
    assert_block(
        text,
        """
        mutation($threadId: ID!) {
              unresolveReviewThread(input: {threadId: $threadId}) {
        """,
    )
    print("OK: review-repair contract captures verified thread repair and resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
