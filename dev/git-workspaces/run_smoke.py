#!/usr/bin/env python3

import subprocess
import tempfile
from pathlib import Path


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


def main() -> None:
    branch_name = "feature/foo"
    workspace_dir_name = "feature-foo"
    target_branch = "main"

    with tempfile.TemporaryDirectory(prefix="git-workspaces-smoke-") as tmp_dir:
        temp_root = Path(tmp_dir)
        repo_root = temp_root / "repo"
        repo_root.mkdir()

        run(["git", "init", "-b", target_branch], cwd=repo_root)
        run(["git", "config", "user.name", "Smoke Test"], cwd=repo_root)
        run(["git", "config", "user.email", "smoke@example.com"], cwd=repo_root)
        run(["git", "remote", "add", "origin", "https://github.com/example/repo.git"], cwd=repo_root)

        write_file(repo_root / ".gitignore", ".workspaces/\n")
        write_file(repo_root / "README.md", "# temp repo\n")
        run(["git", "add", ".gitignore", "README.md"], cwd=repo_root)
        run(["git", "commit", "-m", "init"], cwd=repo_root)
        print("OK: created temp repository with ignored .workspaces/ layout")

        (repo_root / ".workspaces").mkdir()
        check_ignore = run(
            ["git", "check-ignore", "-q", ".workspaces/probe"],
            cwd=repo_root,
            check=False,
        )
        assert_equal(check_ignore.returncode, 0, ".workspaces subtree should be ignored")
        print("OK: verified project-local .workspaces/ is ignored")

        repo_git_common_dir = Path(
            run(
                ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        print("OK: recorded baseline repository git metadata root")

        workspace_path = repo_root / ".workspaces" / workspace_dir_name
        run(["git", "clone", "--no-checkout", ".", str(workspace_path)], cwd=repo_root)
        run(
            ["git", "-C", str(workspace_path), "remote", "set-url", "origin", "https://github.com/example/repo.git"],
            cwd=repo_root,
        )
        run(["git", "-C", str(workspace_path), "checkout", "-B", branch_name, "HEAD"], cwd=repo_root)
        assert_equal(workspace_path.parent, repo_root / ".workspaces", "workspace parent should be .workspaces")
        assert_equal(len(workspace_path.relative_to(repo_root / ".workspaces").parts), 1, "workspace dir should be single-segment")
        print(f"OK: created {workspace_path.relative_to(repo_root)} from branch {branch_name}")

        git_dir = Path(
            run(
                ["git", "-C", str(workspace_path), "rev-parse", "--path-format=absolute", "--git-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        git_common_dir = Path(
            run(
                ["git", "-C", str(workspace_path), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        workspace_root = workspace_path.resolve()
        if not git_dir.is_relative_to(workspace_root):
            raise AssertionError(f"git dir escaped workspace root: {git_dir} not under {workspace_root}")
        if not git_common_dir.is_relative_to(workspace_root):
            raise AssertionError(
                f"git common dir escaped workspace root: {git_common_dir} not under {workspace_root}"
            )
        if git_common_dir == repo_git_common_dir:
            raise AssertionError(
                f"workspace reused repository git metadata root: {git_common_dir} == {repo_git_common_dir}"
            )
        print("OK: verified workspace keeps its git metadata inside the lane root")

        lane_file = workspace_path / "lane.txt"
        write_file(lane_file, "lane-owned change\n")
        run(["git", "add", "lane.txt"], cwd=workspace_path)
        run(["git", "commit", "-m", "add lane change"], cwd=workspace_path)
        print("OK: committed a lane change inside the clone-backed workspace")

        lane_head = run(["git", "rev-parse", "HEAD"], cwd=workspace_path).stdout.strip()
        run(["git", "fetch", str(workspace_path), branch_name], cwd=repo_root)
        run(["git", "merge", "--ff-only", "FETCH_HEAD"], cwd=repo_root)
        main_head = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
        assert_equal(main_head, lane_head, "main should fast-forward to the lane head")
        print("OK: merged lane into main with fast-forward history preservation")

        unique_commits = run(["git", "log", f"{target_branch}..{lane_head}"], cwd=repo_root).stdout.strip()
        assert_equal(unique_commits, "", "lane head should have no unique commits after merge")
        print("OK: verified no unique lane commits remain after merge")

        clean_status = run(["git", "status", "--short"], cwd=workspace_path).stdout.strip()
        assert_equal(clean_status, "", "workspace should be clean before teardown")
        print("OK: verified workspace is clean before teardown")

        run(["rm", "-rf", str(workspace_path)], cwd=repo_root)
        if workspace_path.exists():
            raise AssertionError(f"workspace path still exists after removal: {workspace_path}")
        print("OK: removed the clone-backed workspace")

        repo_git_common_dir_after = Path(
            run(
                ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                cwd=repo_root,
            ).stdout.strip()
        ).resolve()
        assert_equal(
            repo_git_common_dir_after,
            repo_git_common_dir,
            "repository git metadata root should remain unchanged after workspace lifecycle",
        )
        print("OK: confirmed workspace lifecycle stayed isolated from repository git metadata")

        print("OK: lifecycle smoke completed")


if __name__ == "__main__":
    main()
