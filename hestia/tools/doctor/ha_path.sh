#!/bin/bash
# ~/ha_path.sh — resilient locator for Home Assistant config
# Idempotent; emits BLOCKED: diagnostics on failure

set -Eeuo pipefail
IFS=$'\n\t'

: "${HESTIA_CONFIG_OVERRIDE:=}"

_candidates=(
  "$HESTIA_CONFIG_OVERRIDE"
  "/n/ha"                      # autofs neutral path (optional)
  "/n/ha"
  "/n/ha"
)

_realpath() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$1" <<'PY'
import os,sys
print(os.path.realpath(sys.argv[1]))
PY
  else
    (cd "$1" 2>/dev/null && pwd) || return 1
  fi
}

# case-insensitive config filename resolution (returns path to the file if present)
_cfg_file() {
  local d="$1"
  for n in configuration.yaml Configuration.yaml CONFIGURATION.YAML; do
    [ -f "$d/$n" ] && { echo "$n"; return 0; }
  done
  return 1
}

_resolve_first() {
  local p f
  for p in "${_candidates[@]}"; do
    [ -n "$p" ] || continue
    if [ -d "$p" ] && f="$(_cfg_file "$p")"; then
      printf "%s\n" "$(_realpath "$p")"
      return 0
    fi
  done
  return 1
}

_die() {
  echo "BLOCKED: unable to locate Home Assistant config root (configuration.yaml)" >&2
  echo "Checked:" >&2
  local p
  for p in "${_candidates[@]}"; do
    [ -n "$p" ] || continue
    printf ' - %s : ' "$p" >&2
    if [ -e "$p" ]; then
      if [ -d "$p" ]; then
        if f="$(_cfg_file "$p")"; then
          echo "OK (has $f)" >&2
        else
          echo "MISSING configuration.yaml (any case)" >&2
        fi
      else
        echo "NOT A DIRECTORY" >&2
      fi
    else
      echo "NOT FOUND" >&2
    fi
  done
  echo "Fix: mount the HA 'config' share or set HESTIA_CONFIG_OVERRIDE to the correct path." >&2
  exit 2
}

if ! HESTIA_CONFIG="$(_resolve_first)"; then _die; fi
export HESTIA_CONFIG

# expose the resolved config filename for tools (e.g., VS Code helpers)
if f="$(_cfg_file "$HESTIA_CONFIG")"; then
  export HESTIA_CONFIG_FILE="$f"
fi

# Optional venv convenience
if [ -x "$HESTIA_CONFIG/.venv/bin/python" ]; then
  export HESTIA_VENV="$HESTIA_CONFIG/.venv/bin/python"
  export PATH="$HESTIA_CONFIG/.venv/bin:$PATH"
fi

# Guard common footguns
[ -w "$HESTIA_CONFIG" ] || echo "WARN: $HESTIA_CONFIG is not writable; some tasks may fail." >&2
