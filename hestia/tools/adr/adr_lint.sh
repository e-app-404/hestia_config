#!/usr/bin/env bash
set -euo pipefail
: "${WORKSPACE_ROOT:=$HOME/actions-runner/Projects}"
source "$WORKSPACE_ROOT/.venv/bin/activate"
exec hestia-adr-lint "$@"