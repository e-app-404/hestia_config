
#!/usr/bin/env bash
set -Eeuo pipefail
REPO="/n/ha"; cd "$REPO"

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
