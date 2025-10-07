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
#!/bin/bash
# Home Assistant mount telemetry generator for macOS
# Sends retained MQTT messages with mount status and diagnostics

set -euo pipefail

# Configuration
HA_MOUNT="${HA_MOUNT:-$HOME_SAFE/hass}"
MQTT_HOST="${MQTT_HOST:-homeassistant.local}"
MQTT_PORT="${MQTT_PORT:-1883}"
MQTT_TOPIC="home/macbook/hass_mount/status"
HOSTNAME="$(hostname -s)"
USER="$(whoami)"

# Generate timestamp
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EPOCH="$(date +%s)"

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

# Calculate age since last successful mount
LAST_MOUNT_LOG="$(tail -n 100 "$HOME_SAFE/Library/Logs/hass-mount.log" 2>/dev/null | grep "mounted $HA_MOUNT" | tail -n 1 | awk '{print $1" "$2}' || echo "")"
if [[ -n "$LAST_MOUNT_LOG" ]]; then
    LAST_MOUNT_EPOCH="$(date -j -f "%Y-%m-%d %H:%M:%S" "$LAST_MOUNT_LOG" +%s 2>/dev/null || echo "0")"
    AGE_S=$((EPOCH - LAST_MOUNT_EPOCH))
else
    AGE_S=999999
fi

# Binary status (for binary_sensor)
if [[ "$MOUNTED" == "true" && "$WRITE_OK" == "true" && "$CONFIG_PRESENT" == "true" ]]; then
    BINARY_STATE="ON"
else
    BINARY_STATE="OFF"
fi

# Build JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "state": "$BINARY_STATE",
  "mounted": $MOUNTED,
  "write_ok": $WRITE_OK,
  "config_present": $CONFIG_PRESENT,
  "keychain_ok": $KEYCHAIN_OK,
  "agent_loaded": $AGENT_LOADED,
  "agent_state": "$AGENT_STATE",
  "agent_exit_code": $AGENT_EXIT_CODE,
  "host": "$HOSTNAME",
  "user": "$USER",
  "last_run": "$TIMESTAMP",
  "age_s": $AGE_S,
  "mount_details": "$MOUNT_DETAILS"
}
EOF
)

# Send via webhook (fallback when MQTT auth not configured)
WEBHOOK_ID="macbook_hass_mount_telemetry"
WEBHOOK_URL="http://$MQTT_HOST:8123/api/webhook/$WEBHOOK_ID"

if curl -s -X POST -H "Content-Type: application/json" -d "$JSON_PAYLOAD" "$WEBHOOK_URL" >/dev/null; then
    echo "$(date): Sent telemetry via webhook: $BINARY_STATE"
else
    echo "$(date): ERROR: Failed to send webhook to $WEBHOOK_URL"
    exit 1
fi