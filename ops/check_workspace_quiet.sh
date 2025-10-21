#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# Wrapper shim to maintain backward compatibility with CI and docs
CONFIG_ROOT="${CONFIG_ROOT:-/config}"
BACKING_SCRIPT="${CONFIG_ROOT}/hestia/tools/ops/check_workspace_quiet.sh"

if [[ -x "${BACKING_SCRIPT}" ]]; then
  exec "${BACKING_SCRIPT}" "$@"
else
  echo "ERROR: backing script not found at ${BACKING_SCRIPT}" >&2
  exit 127
fi
