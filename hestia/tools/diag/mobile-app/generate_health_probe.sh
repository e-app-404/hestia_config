#!/bin/bash
# --- BEGIN HOME STABILIZER ---
# Resolve the login home from Directory Service so we don't trust a modified $HOME (e.g., actions-runner)
USER_REAL_HOME="$(/usr/bin/dscl . -read /Users/$USER NFSHomeDirectory 2>/dev/null | awk '{print $2}')"
[ -n "$USER_REAL_HOME" ] || USER_REAL_HOME="/Users/$USER"
HOME_SAFE="$USER_REAL_HOME"

# If a process set HOME to actions-runner, override it for this script
case "$HOME" in
    */actions-runner/*)
        echo "[hass] WARNING: overriding HOME ('$HOME') -> '$HOME_SAFE'" >&2
        HOME="$HOME_SAFE"; export HOME;;
esac
# --- END HOME STABILIZER ---

# Health probe generator for HASS mount status
# Creates JSON status file for file sensor fallback

set -euo pipefail

# Configuration
HA_MOUNT="${HA_MOUNT:-$HOME_SAFE/hass}"
STATUS_FILE="$HA_MOUNT/hestia/config/diagnostics/.last_mount_status.json"
HOSTNAME="$(hostname -s)"
USER="$(whoami)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Check mount status
if mount | egrep -q "on $HA_MOUNT .*smbfs"; then
    MOUNTED=true
    MOUNT_DETAILS="$(mount | egrep "on $HA_MOUNT .*smbfs")"
else
    MOUNTED=false
    MOUNT_DETAILS=""
fi

# Check write access
if [[ "$MOUNTED" == "true" ]] && test -w "$HA_MOUNT"; then
    WRITE_OK=true
else
    WRITE_OK=false
fi

# Check config presence
if [[ "$MOUNTED" == "true" ]] && test -f "$HA_MOUNT/configuration.yaml"; then
    CONFIG_PRESENT=true
else
    CONFIG_PRESENT=false
fi

# Check keychain status
if security find-internet-password -w -s "homeassistant.local" -a "evertappels" >/dev/null 2>&1; then
    KEYCHAIN_OK=true
else
    KEYCHAIN_OK=false
fi

# Check LaunchAgent status
if launchctl print "gui/$(id -u)/com.local.hass.mount" >/dev/null 2>&1; then
    AGENT_LOADED=true
    AGENT_STATE="$(launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'state =' | awk '{print $3}')"
    AGENT_EXIT_CODE="$(launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'last exit code' | awk '{print $5}' | cut -d: -f1)"
else
    AGENT_LOADED=false
    AGENT_STATE="not loaded"
    AGENT_EXIT_CODE="-1"
fi

# Overall health summary
if [[ "$MOUNTED" == "true" && "$WRITE_OK" == "true" && "$CONFIG_PRESENT" == "true" && "$KEYCHAIN_OK" == "true" && "$AGENT_LOADED" == "true" && "$AGENT_EXIT_CODE" == "0" ]]; then
    HEALTH_SUMMARY="OK"
elif [[ "$MOUNTED" == "true" && "$WRITE_OK" == "true" && "$CONFIG_PRESENT" == "true" ]]; then
    HEALTH_SUMMARY="DEGRADED"
else
    HEALTH_SUMMARY="CRITICAL"
fi

# Build comprehensive JSON
JSON_OUTPUT=$(cat <<EOF
{
  "health": {
    "summary": "$HEALTH_SUMMARY",
    "timestamp": "$TIMESTAMP",
    "host": "$HOSTNAME",
    "user": "$USER"
  },
  "mount": {
    "mounted": $MOUNTED,
    "write_ok": $WRITE_OK,
    "config_present": $CONFIG_PRESENT,
    "details": "$MOUNT_DETAILS"
  },
  "authentication": {
    "keychain_ok": $KEYCHAIN_OK
  },
  "agent": {
    "loaded": $AGENT_LOADED,
    "state": "$AGENT_STATE",
    "exit_code": $AGENT_EXIT_CODE
  }
}
EOF
)

# Write to status file
mkdir -p "$(dirname "$STATUS_FILE")"
echo "$JSON_OUTPUT" > "$STATUS_FILE"

echo "Health probe written to $STATUS_FILE: $HEALTH_SUMMARY"