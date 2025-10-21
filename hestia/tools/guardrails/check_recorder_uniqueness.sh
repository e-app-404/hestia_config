#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# Ensures exactly one recorder: block exists across repo YAML (HA policy)

mapfile -t files < <(git ls-files '*.yaml' | grep -vE '^\.github/|hestia/workspace/archive/' || true)

count=0
for f in "${files[@]}"; do
  # match top-level-ish occurrences (allow indentation), ignore commented lines
  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    if [[ "$line" =~ ^[[:space:]]*recorder:[[:space:]]*$ ]]; then
      ((count++))
    fi
  done <"$f"
done

if (( count == 1 )); then
  echo "OK: recorder block present exactly once"
  exit 0
fi

echo "ERROR: recorder block count != 1 (count=$count)" >&2
if (( count == 0 )); then
  echo "Hint: add or ensure a single recorder: configuration" >&2
else
  echo "Hint: consolidate to a single recorder: block" >&2
fi
exit 1
