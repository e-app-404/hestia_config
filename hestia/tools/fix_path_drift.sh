#!/usr/bin/env bash
# Narrow, idempotent replacement to /config. Backs up touched files.
set -euo pipefail

# Choose sed (BSD or GNU)
if command -v gsed >/dev/null 2>&1; then SED=gsed; else SED=sed; fi

# Target files (scripts/yaml/json only)
FILES=$(git ls-files \
  ':config/**' ':hestia/**' ':tools/**' ':scripts/**' \
  ':.github/**' ':.devcontainer/**' ':.vscode/**' \
  | grep -E '\.(sh|bash|zsh|py|yaml|yml|json)$' || true)

if [[ -z "${FILES}" ]]; then
  echo "No candidate files found."
  exit 0
fi

for f in $FILES; do
  # Skip historical/imported ADRs just in case
  [[ "$f" == ADR/deprecated/* ]] && continue
  [[ "$f" == docs/history/* ]] && continue
  [[ "$f" == library/docs/ADR-imports/* ]] && continue

  before=$(cksum "$f" | awk '{print $1}')
  cp -p "$f" "$f.bak_adr0024" || true

  $SED -E -i '' \
    -e 's#\$(HOME)/hass#\/config#g' \
    -e 's#\~\/hass#\/config#g' \
    -e 's#(/Volumes(/[^ ]*)?)\/HA\/Config#\/config#g' \
    -e 's#(/Volumes(/[^ ]*)?)\/Config#\/config#g' \
    -e 's#\/n\/ha#\/config#g' \
    -e 's#actions-runner\/[^ ]*\/hass#config#g' \
    "$f"

  after=$(cksum "$f" | awk '{print $1}')
  if [[ "$before" != "$after" ]]; then
    echo "Patched: $f"
  else
    rm -f "$f.bak_adr0024" || true
  fi
done

echo "Fix completed."