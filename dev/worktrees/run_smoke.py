#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / ".codex" / "skills" / "worktrees" / "SKILL.md"


def run(cmd, cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        cmd_text = " ".join(cmd)
        raise AssertionError(
            f"command failed: {cmd_text}\n"
            f"cwd: {cwd}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return proc


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected!r}, got {actual!r}")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def assert_contains(text: str, needle: str, *, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} must contain {needle!r}")


def assert_skill_doc() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")
    for needle in [
        "name: worktrees",
        "worktree_ready",
        "worktree_reused",
        "worktree_closed",
        "worktree_retained",
        "warned",
        "push origin --delete",
        "remote branch is absent",
        "create or update it from inside the active worktree",
        "Do not leave task-local `docs/plans/...` artifacts behind in the primary checkout",
        "pull --ff-only origin \"$target_branch\"",
        "primary checkout is on the integration branch and fast-forwarded to the latest upstream state",
        "git worktree add -b \"$branch_name\" \"$worktree_path\" HEAD",
        "git worktree remove \"$worktree_path\"",
        "worktree-backed `.worktrees/<lane>` lane",
    ]:
        assert_contains(text, needle, label="worktrees skill")
    print("OK: worktrees skill documents setup and cleanup outputs")


def main() -> None:
    assert_skill_doc()

    branch_name = "feature/foo"
    worktree_dir_name = "feature-foo"
    target_branch = "main"

    with tempfile.TemporaryDirectory(prefix="worktrees-smoke-") as tmp_dir:
        temp_root = Path(tmp_dir)
        remote_root = temp_root / "origin.git"
        repo_root = temp_root / "repo"

        run(["git", "init", "--bare", str(remote_root)], cwd=temp_root)
        repo_root.mkdir()
        run(["git", "init", "-b", target_branch], cwd=repo_root)
        run(["git", "config", "user.name", "Smoke Test"], cwd=repo_root)
        run(["git", "config", "user.email", "smoke@example.com"], cwd=repo_root)
        run(["git", "remote", "add", "origin", str(remote_root)], cwd=repo_root)

        write_file(repo_root / ".gitignore", ".worktrees/\n")
        write_file(repo_root / "README.md", "# temp repo\n")
        run(["git", "add", ".gitignore", "README.md"], cwd=repo_root)
        run(["git", "commit", "-m", "init"], cwd=repo_root)
        run(["git", "push", "-u", "origin", target_branch], cwd=repo_root)
        print("OK: created temp repository with ignored .worktrees/ layout")

        (repo_root / ".worktrees").mkdir()
        check_ignore = run(
            ["git", "check-ignore", "-q", ".worktrees/probe"],
            cwd=repo_root,
            check=False,
        )
        assert_equal(check_ignore.returncode, 0, ".worktrees subtree should be ignored")
        print("OK: verified project-local .worktrees/ is ignored")

        repo_git_common_dir = Path(
            run(
                ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        print("OK: recorded baseline repository git metadata root")

        worktree_path = repo_root / ".worktrees" / worktree_dir_name
        run(["git", "worktree", "add", "-b", branch_name, str(worktree_path), "HEAD"], cwd=repo_root)
        run(["git", "-C", str(worktree_path), "config", "user.name", "Smoke Test"], cwd=repo_root)
        run(["git", "-C", str(worktree_path), "config", "user.email", "smoke@example.com"], cwd=repo_root)
        assert_equal(worktree_path.parent, repo_root / ".worktrees", "worktree parent should be .worktrees")
        assert_equal(len(worktree_path.relative_to(repo_root / ".worktrees").parts), 1, "worktree dir should be single-segment")
        print(f"OK: created {worktree_path.relative_to(repo_root)} from branch {branch_name}")

        git_dir = Path(
            run(
                ["git", "-C", str(worktree_path), "rev-parse", "--path-format=absolute", "--git-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        git_common_dir = Path(
            run(
                ["git", "-C", str(worktree_path), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        worktree_root = worktree_path.resolve()
        worktrees_root = (repo_git_common_dir / "worktrees").resolve()
        if git_dir.is_relative_to(worktree_root):
            raise AssertionError(f"git dir unexpectedly stayed inside worktree root: {git_dir}")
        if not git_dir.is_relative_to(worktrees_root):
            raise AssertionError(f"git dir should live under shared worktrees metadata: {git_dir}")
        assert_equal(git_common_dir, repo_git_common_dir, "worktree should share repository git common dir")
        worktree_list = run(["git", "worktree", "list", "--porcelain"], cwd=repo_root).stdout
        assert_contains(worktree_list, str(worktree_root), label="worktree list")
        print("OK: verified worktree registration and shared git metadata layout")

        lane_file = worktree_path / "lane.txt"
        write_file(lane_file, "lane-owned change\n")
        run(["git", "add", "lane.txt"], cwd=worktree_path)
        run(["git", "commit", "-m", "add lane change"], cwd=worktree_path)
        run(["git", "push", "-u", "origin", branch_name], cwd=worktree_path)
        print("OK: committed a lane change inside the worktree-backed worktree")

        lane_head = run(["git", "rev-parse", "HEAD"], cwd=worktree_path).stdout.strip()
        run(["git", "fetch", "origin", branch_name], cwd=repo_root)
        run(["git", "merge", "--ff-only", "FETCH_HEAD"], cwd=repo_root)
        run(["git", "push", "origin", target_branch], cwd=repo_root)
        main_head = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
        assert_equal(main_head, lane_head, "main should fast-forward to the lane head")
        print("OK: merged lane into main with fast-forward history preservation")

        unique_commits = run(["git", "log", f"{target_branch}..{lane_head}"], cwd=repo_root).stdout.strip()
        assert_equal(unique_commits, "", "lane head should have no unique commits after merge")
        print("OK: verified no unique lane commits remain after merge")

        clean_status = run(["git", "status", "--short"], cwd=worktree_path).stdout.strip()
        assert_equal(clean_status, "", "worktree should be clean before teardown")
        print("OK: verified worktree is clean before teardown")

        run(["git", "push", "origin", "--delete", branch_name], cwd=worktree_path)
        remote_listing = run(
            ["git", "ls-remote", "--heads", "origin", branch_name],
            cwd=worktree_path,
            check=False,
        ).stdout.strip()
        assert_equal(remote_listing, "", "remote branch should be absent after cleanup")
        print("OK: verified remote branch cleanup target state")

        run(["git", "worktree", "remove", str(worktree_path)], cwd=repo_root)
        if worktree_path.exists():
            raise AssertionError(f"worktree path still exists after worktree removal: {worktree_path}")
        print("OK: removed the worktree lane")

        run(["git", "branch", "-D", branch_name], cwd=repo_root)
        branch_listing = run(["git", "branch", "--list", branch_name], cwd=repo_root).stdout.strip()
        assert_equal(branch_listing, "", "shared repository lane branch should be removed")
        print("OK: removed the same-named branch from the shared repository")

        run(["git", "worktree", "prune"], cwd=repo_root)
        repo_git_common_dir_after = Path(
            run(
                ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        assert_equal(
            repo_git_common_dir_after,
            repo_git_common_dir,
            "repository git metadata root should remain unchanged after worktree lifecycle",
        )
        worktree_list_after = run(["git", "worktree", "list", "--porcelain"], cwd=repo_root).stdout
        if str(worktree_root) in worktree_list_after:
            raise AssertionError(f"stale worktree registration remained for {worktree_root}")
        assert_true(
            not (repo_root / ".worktrees" / worktree_dir_name).exists(),
            "worktree directory should stay absent after teardown",
        )
        print("OK: confirmed worktree lifecycle cleaned up worktree registration")

        print("OK: lifecycle smoke completed")


if __name__ == "__main__":
    main()
