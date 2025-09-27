#!/usr/bin/env bash
set -euo pipefail

CANON="packages/integrations/recorder.yaml"

# 1) Exactly one top-level 'recorder:' across HA-loaded trees, ignoring comments
count=$(
  grep -R --include="*.yaml" -nE "^[[:space:]]*recorder:" configuration.yaml packages 2>/dev/null \
  | grep -vE "^[^:]+:[[:digit:]]+:[[:space:]]*#.*recorder:" \
  | wc -l | tr -d ' '
)
echo "recorder key count: $count"
test "$count" -eq 1

# 2) It must be in the canonical path
if ! grep -nE "^[[:space:]]*recorder:" "$CANON" >/dev/null 2>&1; then
  echo "recorder block not found at canonical path: $CANON" >&2
  exit 1
fi

echo "Single-recorder invariant satisfied at $CANON"
