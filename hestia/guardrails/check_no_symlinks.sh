#!/usr/bin/env bash
set -euo pipefail
# Fail if any symlink exists under HA-loaded trees.
bad=$(find configuration.yaml packages -xtype l 2>/dev/null || true)
if [[ -n "$bad" ]]; then
  echo "Symlinks found (disallowed):"
  echo "$bad"
  exit 1
fi
echo "No symlinks detected."
