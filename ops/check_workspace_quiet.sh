#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

ROOT="${1:-.}"

cd "$ROOT"

# Ensure no uncommitted changes or untracked large binaries in critical areas
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Workspace not quiet: uncommitted changes present" >&2
  git status -s || true
  exit 1
fi

# Ban common large/binary types tracked in git
if git ls-files -z | tr '\0' '\n' | grep -E '\.(bin|exe|dll|dmg|iso|img)$' >/dev/null; then
  echo "Forbidden binary artifacts tracked in git" >&2
  git ls-files | grep -E '\.(bin|exe|dll|dmg|iso|img)$' || true
  exit 1
fi

echo "Workspace quiet."
