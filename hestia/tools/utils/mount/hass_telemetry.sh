#!/usr/bin/env bash
set -euo pipefail

# --- BEGIN HOME STABILIZER ---
USER_REAL_HOME="$((/usr/bin/dscl . -read "/Users/${USER}" NFSHomeDirectory 2>/dev/null) | awk '{print $2}')"
[ -n "$USER_REAL_HOME" ] || USER_REAL_HOME="/Users/${USER}"
HOME_SAFE="$USER_REAL_HOME"
case "$HOME" in
  */actions-runner/*)
    echo "[hass] WARNING: overriding HOME ('$HOME') -> '$HOME_SAFE'" >&2
    HOME="$HOME_SAFE"; export HOME;;
esac
# --- END HOME STABILIZER ---

LOG_DIR="$HOME_SAFE/Library/Logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/hass-telemetry.log"

# Configuration (ADR-0024: prefer /config)
HA_MOUNT="${HA_MOUNT:-/config}"
HA_HOST="${HA_HOST:-homeassistant.local}"
WEBHOOK_ID="${MACBOOK_HASS_MOUNT_WEBHOOK_ID:-macbook_hass_mount_telemetry_f8d2a9b4c7e1}"
WEBHOOK_URL="http://${HA_HOST}:8123/api/webhook/${WEBHOOK_ID}"

HOSTNAME_SHORT="$(hostname -s)"
USER_NAME="$(whoami)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EPOCH="$(date +%s)"

# Resolve mountpoint real path
HA_MOUNT_REAL="$(realpath "$HA_MOUNT" 2>/dev/null || echo "$HA_MOUNT")"

# Detect mount status
if mount | egrep -q " on ${HA_MOUNT_REAL} .*smbfs"; then
  MOUNTED=true
  MOUNT_DETAILS="$(mount | egrep " on ${HA_MOUNT_REAL} .*smbfs" | head -n1)"
else
  MOUNTED=false
  MOUNT_DETAILS=""
fi

# Basic probes
if [[ "$MOUNTED" == "true" ]] && test -w "$HA_MOUNT"; then WRITE_OK=true; else WRITE_OK=false; fi
if [[ "$MOUNTED" == "true" ]] && test -f "$HA_MOUNT/configuration.yaml"; then CONFIG_PRESENT=true; else CONFIG_PRESENT=false; fi

# Keychain credential presence (non-fatal)
if security find-internet-password -w -s "homeassistant.local" -a "$USER_NAME" >/dev/null 2>&1; then KEYCHAIN_OK=true; else KEYCHAIN_OK=false; fi

# LaunchAgent status
if launchctl print "gui/$(id -u)/com.local.hass.mount" >/dev/null 2>&1; then
  AGENT_LOADED=true
  RAW_STATE="$(launchctl print "gui/$(id -u)/com.local.hass.mount" 2>/dev/null | egrep 'state\s*=\s*' | awk '{print $3}' | tr -d '\r' | head -n1)"
  if [[ "$RAW_STATE" == "running" ]]; then AGENT_STATE="running"; else AGENT_STATE="not_running"; fi
  AGENT_EXIT_CODE="$(launchctl print "gui/$(id -u)/com.local.hass.mount" 2>/dev/null | egrep 'last exit code' | awk '{print $5}' | cut -d: -f1 | tr -d '\r')"
else
  AGENT_LOADED=false
  AGENT_STATE="not_running"
  AGENT_EXIT_CODE="-1"
fi

# Freshness (age_s): 0 when mounted; else derive from last mount log occurrence
if [[ "$MOUNTED" == "true" ]]; then
  AGE_S=0
else
  LAST_MOUNT_LOG="$(tail -n 200 "$HOME_SAFE/Library/Logs/hass-mount.log" 2>/dev/null | \
    egrep "mounted (/config|$HOME_SAFE/hass)" | tail -n 1 | awk '{print $1" "$2}')"
  if [[ -n "$LAST_MOUNT_LOG" ]]; then
    LAST_MOUNT_EPOCH="$(date -j -f "%Y-%m-%d %H:%M:%S" "$LAST_MOUNT_LOG" +%s 2>/dev/null || echo 0)"
    AGE_S=$(( EPOCH - LAST_MOUNT_EPOCH ))
  else
    AGE_S=999999
  fi
fi

# Binary summary
if [[ "$MOUNTED" == "true" && "$WRITE_OK" == "true" && "$CONFIG_PRESENT" == "true" ]]; then
  BINARY_STATE="ON"
else
  BINARY_STATE="OFF"
fi

# JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "state": "${BINARY_STATE}",
  "mounted": ${MOUNTED},
  "write_ok": ${WRITE_OK},
  "config_present": ${CONFIG_PRESENT},
  "keychain_ok": ${KEYCHAIN_OK},
  "agent_loaded": ${AGENT_LOADED},
  "agent_state": "${AGENT_STATE}",
  "agent_exit_code": ${AGENT_EXIT_CODE},
  "host": "${HOSTNAME_SHORT}",
  "user": "${USER_NAME}",
  "last_run": "${TIMESTAMP}",
  "age_s": ${AGE_S},
  "mount_details": "${MOUNT_DETAILS}"
}
EOF
)

# Send and log
RC=0
if curl -s -X POST -H "Content-Type: application/json" -d "$JSON_PAYLOAD" "$WEBHOOK_URL" >/dev/null; then
  echo "$(date): Sent telemetry via webhook: ${BINARY_STATE}" >> "$LOG"
else
  echo "$(date): ERROR posting telemetry to ${WEBHOOK_URL}" >> "$LOG"
  RC=1
fi

# Write one-line JSON health file for HA File integration (expects last line to be valid JSON)
HEALTH_FILE="/config/hestia/config/diagnostics/.last_mount_status.json"
ONE_LINE_JSON=$(echo "$JSON_PAYLOAD" | python3 -c 'import sys,json; print(json.dumps(json.load(sys.stdin)))' 2>/dev/null || true)
if [ -n "$ONE_LINE_JSON" ]; then
  printf "%s\n" "$ONE_LINE_JSON" > "$HEALTH_FILE" || true
else
  # Fallback: minify without parsing (not ideal but single-line)
  printf "%s\n" "$JSON_PAYLOAD" | tr -d '\n' > "$HEALTH_FILE" || true
fi

# Bounded log rotation
if [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 1048576 ]; then
  tail -n 200 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

exit $RC
