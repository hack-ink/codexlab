#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Usage: $(basename "$0") <agent-browser args...>" >&2
  exit 64
fi

if ! command -v node >/dev/null 2>&1; then
  echo "node not found in PATH" >&2
  exit 69
fi

if [[ -n "${AGENT_BROWSER_JS_PATH:-}" ]]; then
  js_path="$AGENT_BROWSER_JS_PATH"
else
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm not found in PATH" >&2
    echo "Set AGENT_BROWSER_JS_PATH to the installed agent-browser JS wrapper." >&2
    exit 69
  fi
  npm_root="$(npm root -g 2>/dev/null)"
  js_path="${npm_root}/agent-browser/bin/agent-browser.js"
fi

if [[ ! -f "$js_path" ]]; then
  echo "agent-browser JS wrapper not found: $js_path" >&2
  echo "Set AGENT_BROWSER_JS_PATH or reinstall agent-browser." >&2
  exit 66
fi

exec node "$js_path" "$@"
