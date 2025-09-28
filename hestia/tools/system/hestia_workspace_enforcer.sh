#!/usr/bin/env bash
set -euo pipefail
# Block root-level packaging/build droppings in HA share
for f in pyproject.toml setup.cfg setup.py Pipfile poetry.lock package.json yarn.lock pnpm-lock.yaml node_modules dist build .venv; do
  if [ -e "./$f" ]; then
    echo "ERROR: Disallowed file/dir at repo root: $f" >&2
    exit 1
  fi
done
echo "Workspace enforcer: OK"

#!/usr/bin/env bash
set -Eeuo pipefail
# Detect repo root dynamically (works in GitHub Actions and local environments)
REPO="${GITHUB_WORKSPACE:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$REPO"

[ -f configuration.yaml ] || { echo "BLOCKED: missing configuration.yaml at $REPO"; exit 1; }

# Fail on forbidden volume paths within config/code text files only
if git grep -nI -E '/Volumes/(HA|ha)' -- \
  ':!hestia/core/architecture/**' ':!hestia/vault/**' ':!hestia/work/**' \
  '*.sh' '*.py' '*.md' '*.yaml' '*.yml' '*.json' '*.ini' '*.conf' '*.env' '*.code-workspace' '*.txt' >/dev/null; then
  echo "BLOCKED: forbidden /Volumes/(HA|ha) path in tracked config/code."
  echo "Remedy: neutralize to /n/ha or $HESTIA_CONFIG and re-run."
  exit 1
fi

echo "OK: workspace paths neutral"
