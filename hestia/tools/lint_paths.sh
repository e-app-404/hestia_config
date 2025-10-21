#!/usr/bin/env bash
# Fail on legacy aliases; exclude historical & imported ADRs.
set -euo pipefail

PATTERN='\$HOME/|~\/hass|/Volumes/|/n/ha|actions-runner/.+?/hass'

# Exclusions (globs)
EXCLUDES=(
  '!**/*.md'
  '!ADR/deprecated/**'
  '!docs/history/**'
  '!library/docs/ADR-imports/**'
  '!hestia/workspace/cache/**'
  '!hestia/workspace/staging/**'
  '!**/.git/**'
  '!**/.venv/**'
  '!**/node_modules/**'
  '!**/*.png' '!**/*.jpg' '!**/*.svg' '!**/*.ico'
)

if command -v rg >/dev/null 2>&1; then
  if rg -nE "$PATTERN" --hidden "${EXCLUDES[@]}" --glob '!**/*.md' --glob '!ADR/deprecated/**' --glob '!docs/history/**' --glob '!library/docs/ADR-imports/**' .; then
    echo 'ERROR: Disallowed path alias detected. Use /config only.' >&2
    exit 1
  fi
else
  echo "[lint] ripgrep not found; falling back to grep (slower)." >&2
  MATCHES=$(git ls-files | grep -vE '\.md$|^ADR/deprecated/|^docs/history/|^library/docs/ADR-imports/|^hestia/workspace/cache/|^hestia/workspace/staging/|^\.git/|^\.venv/|node_modules/|\.png$|\.jpg$|\.svg$|\.ico$' \
    | xargs grep -nE "$PATTERN" -- 2>/dev/null || true)
  if [[ -n "${MATCHES}" ]]; then
    echo "${MATCHES}"
    echo 'ERROR: Disallowed path alias detected. Use /config only.' >&2
    exit 1
  fi
fi

echo "OK: path lint passed"
