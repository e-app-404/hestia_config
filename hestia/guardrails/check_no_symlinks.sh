#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

BAD=$(git ls-files -z | xargs -0 -I{} bash -lc 'test -L "{}" && echo {}' || true)
if [[ -n "$BAD" ]]; then
  echo "ERROR: Tracked symlinks detected:" >&2
  echo "$BAD" >&2
  exit 1
fi
echo "OK: No tracked symlinks."
