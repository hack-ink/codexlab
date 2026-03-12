from __future__ import annotations

from pathlib import Path


DEV_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEV_DIR.parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"expected path to exist: {path}")


def assert_absent(path: Path) -> None:
    if path.exists():
        raise AssertionError(f"expected path to be removed: {path}")


def assert_contains(text: str, needle: str, *, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} must contain {needle!r}")


def assert_not_contains(text: str, needle: str, *, label: str) -> None:
    if needle in text:
        raise AssertionError(f"{label} must not contain {needle!r}")


def assert_sidecars_skill() -> None:
    skill_path = REPO_ROOT / "sidecars" / "SKILL.md"
    assert_exists(skill_path)
    text = read_text(skill_path)
    assert_contains(text, "scout", label="sidecars skill")
    assert_contains(text, "skeptic", label="sidecars skill")
    for needle in [
        "ticket-dispatch/1",
        "ticket-result/1",
        "write_scope",
        "review_mode",
        "changed_paths",
    ]:
        assert_not_contains(text, needle, label="sidecars skill")
    print(f"OK: sidecars skill exists ({skill_path})")


def assert_deleted_surface_absent() -> None:
    assert_absent(REPO_ROOT / "multi-agent")
    assert_absent(REPO_ROOT / "dev" / "multi-agent")
    print("OK: deleted multi-agent source surface is absent")


def assert_repo_docs() -> None:
    targets = [
        REPO_ROOT / "README.md",
    ]
    forbidden = [
        "multi-agent",
        "ticket-dispatch/1",
        "ticket-result/1",
        "write_scope",
        "review_mode",
        "changed_paths",
    ]
    for path in targets:
        text = read_text(path)
        assert_not_contains(text, "multi-agent", label=str(path))
        for needle in forbidden[1:]:
            assert_not_contains(text, needle, label=str(path))
    assert_contains(read_text(REPO_ROOT / "README.md"), "sidecars", label="README.md")
    print("OK: repo docs point to sidecars and omit deleted protocol surface")


def main() -> int:
    assert_sidecars_skill()
    assert_deleted_surface_absent()
    assert_repo_docs()
    print("OK: sidecars smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
