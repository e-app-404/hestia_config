#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# Wrapper for canonical guardrails implementation
CONFIG_ROOT="${CONFIG_ROOT:-/config}"
BACKING="${CONFIG_ROOT}/hestia/guardrails/check_rest_command_guardrails.sh"

if [[ -x "${BACKING}" ]]; then
  exec "${BACKING}" "$@"
else
  echo "ERROR: backing script not found at ${BACKING}" >&2
  exit 127
fi
