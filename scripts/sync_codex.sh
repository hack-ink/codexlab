#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE="${1:-backup}"

usage() {
  cat <<'EOF'
Usage:
  sync_codex.sh [backup [SOURCE_ROOT [TARGET_ROOT]]]
  sync_codex.sh restore [SOURCE_ROOT [TARGET_ROOT]]

Modes:
  backup   Copy ~/.codex into this repository's .codex mirror.
  restore  Copy this repository's .codex mirror back to a target directory.

Only the overlapping managed paths are updated:
  AGENTS.md, config.toml, agents/, themes/, skills/<selected-skill>/
Other files already present under TARGET_ROOT are left untouched.
EOF
}

case "$MODE" in
  backup)
    SOURCE_ROOT="${2:-$HOME/.codex}"
    TARGET_ROOT="${3:-$REPO_ROOT/.codex}"
    SKILLS_SOURCE_ROOT="$SOURCE_ROOT/skills"
    SKILLS_TARGET_ROOT="$TARGET_ROOT/skills"
    ;;
  restore)
    SOURCE_ROOT="${2:-$REPO_ROOT/.codex}"
    TARGET_ROOT="${3:-$HOME/.codex}"
    SKILLS_SOURCE_ROOT="$SOURCE_ROOT/skills"
    SKILLS_TARGET_ROOT="$TARGET_ROOT/skills"
    ;;
  -h|--help|help)
    usage
    exit 0
    ;;
  *)
    printf 'unknown mode: %s\n\n' "$MODE" >&2
    usage >&2
    exit 1
    ;;
esac

SYNC_PATHS=(
  "AGENTS.md"
  "config.toml"
  "agents"
  "themes"
)

for relative_path in "${SYNC_PATHS[@]}"; do
  path="$SOURCE_ROOT/$relative_path"
  if [[ ! -e "$path" ]]; then
    printf 'missing required path: %s\n' "$path" >&2
    exit 1
  fi
done

mapfile -t SKILL_NAMES < <(find "$REPO_ROOT/.codex/skills" -mindepth 2 -maxdepth 2 -name SKILL.md -print | sed "s#^$REPO_ROOT/.codex/skills/##; s#/SKILL.md##" | sort)

if [[ "${#SKILL_NAMES[@]}" -eq 0 ]]; then
  printf 'no selected skills found under %s\n' "$REPO_ROOT/.codex/skills" >&2
  exit 1
fi

SYNC_SKILL_NAMES=()
for skill_name in "${SKILL_NAMES[@]}"; do
  skill_path="$SKILLS_SOURCE_ROOT/$skill_name"
  if [[ -d "$skill_path" && -f "$skill_path/SKILL.md" ]]; then
    SYNC_SKILL_NAMES+=("$skill_name")
    continue
  fi
  if [[ "$MODE" == "restore" ]]; then
    printf 'missing selected skill path: %s\n' "$skill_path" >&2
    exit 1
  fi
done

python3 - "$SOURCE_ROOT" <<'PY'
from pathlib import Path
import re
import sys

source_root = Path(sys.argv[1])
targets = [
    source_root / "AGENTS.md",
    source_root / "config.toml",
    source_root / "agents",
    source_root / "themes",
]

hard_patterns = {
    "api_key_like": re.compile(r"(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{20,})"),
    "bearer_value": re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{10,}"),
}

soft_patterns = {
    "identity_mapping": re.compile(r"GITHUB_PAT_[A-Z]"),
    "env_var_name": re.compile(r"bearer_token_env_var\s*="),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "home_path": re.compile(r"/Users/[A-Za-z0-9._-]+"),
}

hard_hits = []
soft_hits = []

for target in targets:
    files = [target] if target.is_file() else sorted(p for p in target.rglob("*") if p.is_file())
    for file_path in files:
        try:
            text = file_path.read_text(errors="replace")
        except Exception:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for label, pattern in hard_patterns.items():
                if pattern.search(line):
                    hard_hits.append((label, str(file_path), line_no))
            if "=" in line:
                key, raw_value = line.split("=", 1)
                lowered_key = key.lower()
                value = raw_value.strip().strip('"').strip("'")
            else:
                lowered_key = ""
                value = ""
            if (
                lowered_key
                and "env_var" not in lowered_key
                and any(token in lowered_key for token in ("api_key", "token", "secret", "password", "passwd", "bearer"))
            ):
                if value and re.fullmatch(r"[A-Z0-9_]+", value) is None and len(value) >= 10:
                    hard_hits.append(("assigned_secret_value", str(file_path), line_no))
            for label, pattern in soft_patterns.items():
                if pattern.search(line):
                    soft_hits.append((label, str(file_path), line_no))

if hard_hits:
    print("Privacy scan failed: hard secret-like findings detected.", file=sys.stderr)
    for label, file_path, line_no in hard_hits:
        print(f"  HARD {label}: {file_path}:{line_no}", file=sys.stderr)
    sys.exit(2)

print("Privacy scan passed: no hard secret-like findings detected.")
if soft_hits:
    print("Metadata findings to review before publishing:")
    for label, file_path, line_no in soft_hits:
        print(f"  SOFT {label}: {file_path}:{line_no}")
else:
    print("No soft metadata findings detected.")
PY

TMP_ROOT="${TARGET_ROOT}.tmp.$$"
cleanup() {
  rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

rm -rf "$TMP_ROOT"
mkdir -p "$TMP_ROOT/agents" "$TMP_ROOT/themes" "$TMP_ROOT/skills"

cp "$SOURCE_ROOT/AGENTS.md" "$TMP_ROOT/AGENTS.md"
cp "$SOURCE_ROOT/config.toml" "$TMP_ROOT/config.toml"
cp -R "$SOURCE_ROOT/agents/." "$TMP_ROOT/agents/"
cp -R "$SOURCE_ROOT/themes/." "$TMP_ROOT/themes/"
for skill_name in "${SYNC_SKILL_NAMES[@]}"; do
  cp -R "$SKILLS_SOURCE_ROOT/$skill_name" "$TMP_ROOT/skills/$skill_name"
done

mkdir -p "$TARGET_ROOT"
rm -f "$TARGET_ROOT/AGENTS.md" "$TARGET_ROOT/config.toml"
rm -rf "$TARGET_ROOT/agents" "$TARGET_ROOT/themes"
mkdir -p "$SKILLS_TARGET_ROOT"
mv "$TMP_ROOT/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
mv "$TMP_ROOT/config.toml" "$TARGET_ROOT/config.toml"
mv "$TMP_ROOT/agents" "$TARGET_ROOT/agents"
mv "$TMP_ROOT/themes" "$TARGET_ROOT/themes"
for skill_name in "${SYNC_SKILL_NAMES[@]}"; do
  rm -rf "$SKILLS_TARGET_ROOT/$skill_name"
  mv "$TMP_ROOT/skills/$skill_name" "$SKILLS_TARGET_ROOT/$skill_name"
done
rm -rf "$TMP_ROOT"
trap - EXIT

printf 'Synced Codex content (%s) from %s to %s\n' "$MODE" "$SOURCE_ROOT" "$TARGET_ROOT"
