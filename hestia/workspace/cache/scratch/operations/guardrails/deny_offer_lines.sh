#!/usr/bin/env bash
set -euo pipefail
# deny_offer_lines.sh - exit non-zero if files contain solicitation phrases

regex="(?i)\b(if you(?:'d| would)?(?: like| want(?: me to)?)?|if you'd like|if you want me to|I can (?:also )?(?:do|add|implement))\b"

# iterate all filenames given by pre-commit
status=0
for file in "$@"; do
  if grep -Pqo "$regex" "$file"; then
    echo "Error: forbidden offer-phrase found in $file"
    grep -nP "$regex" "$file" || true
    status=1
  fi
done
exit $status