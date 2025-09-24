#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
BRANCH="$(git symbolic-ref --quiet --short HEAD || echo main)"
git push -u nas "${BRANCH}"
