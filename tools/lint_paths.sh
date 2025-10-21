#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# Wrapper to satisfy CI workflows expecting tools/lint_paths.sh
# Delegates to the canonical linter under hestia/tools/lint_paths.sh per ADR-0024

CONFIG_ROOT="${CONFIG_ROOT:-/config}"

BACKING_LINTER="${CONFIG_ROOT}/hestia/tools/lint_paths.sh"
if [[ -x "${BACKING_LINTER}" ]]; then
  exec "${BACKING_LINTER}" "$@"
else
  echo "ERROR: backing linter not found at ${BACKING_LINTER}" >&2
  exit 127
fi
