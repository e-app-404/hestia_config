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
# End-to-end verification checklist for HA mount telemetry
# Each test prints OK/FAIL with actionable guidance

set -euo pipefail

echo "=== HA MOUNT TELEMETRY VERIFICATION ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Host: $(hostname)"
echo

# Prefer canonical /config mount per ADR-0024; fall back to legacy $HOME_SAFE/hass if needed
CONFIG_MP="/config"
LEGACY_MP="$HOME_SAFE/hass"
CONFIG_MP_REAL="$(realpath "$CONFIG_MP" 2>/dev/null || echo "$CONFIG_MP")"
LEGACY_MP_REAL="$(realpath "$LEGACY_MP" 2>/dev/null || echo "$LEGACY_MP")"

# Test 1: Mount Status
echo -n "1. Mount Status: "
if mount | egrep -q " on $CONFIG_MP_REAL .*smbfs"; then
    echo "OK - SMB mount active at $CONFIG_MP_REAL (/config)"
elif mount | egrep -q " on $LEGACY_MP_REAL .*smbfs"; then
    echo "OK - SMB mount active at $LEGACY_MP_REAL (legacy path)"
    echo "   NOTE: Consider migrating to /config per ADR-0024"
else
    echo "FAIL - No SMB mount found"
    echo "   ACTION: Run 'launchctl kickstart -k \"gui/\$(id -u)/com.local.hass.mount\"' or mount_smbfs to /config"
fi

# Test 2: Write Access
echo -n "2. Write Access: "
if test -w "$CONFIG_MP"; then
    echo "OK - Mount is writable at $CONFIG_MP"
elif test -w "$LEGACY_MP"; then
    echo "OK - Mount is writable at $LEGACY_MP (legacy path)"
    echo "   NOTE: Consider migrating to /config per ADR-0024"
else
    echo "FAIL - Mount not writable"
    echo "   ACTION: Check SMB permissions or remount"
fi

# Test 3: Config Present
echo -n "3. Config Present: "
if test -f "$CONFIG_MP/configuration.yaml"; then
    echo "OK - configuration.yaml found at $CONFIG_MP"
elif test -f "$LEGACY_MP/configuration.yaml"; then
    echo "OK - configuration.yaml found at $LEGACY_MP (legacy path)"
    echo "   NOTE: Consider migrating to /config per ADR-0024"
else
    echo "FAIL - configuration.yaml missing"
    echo "   ACTION: Verify HA instance and SMB share path"
fi

# Test 4: LaunchAgent Loaded
echo -n "4. Mount Agent: "
if launchctl print "gui/$(id -u)/com.local.hass.mount" >/dev/null 2>&1; then
    EXIT_CODE="$(launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'last exit code' | awk '{print $5}' | cut -d: -f1)"
    if [[ "$EXIT_CODE" == "0" ]]; then
        echo "OK - Agent loaded, exit code 0"
    else
        echo "FAIL - Agent loaded but exit code $EXIT_CODE"
        echo "   ACTION: Check $HOME_SAFE/Library/Logs/hass-mount.log"
    fi
else
    echo "FAIL - Agent not loaded"
    echo "   ACTION: Run bootstrap command from ACTIONS section"
fi

# Test 5: Telemetry Agent
echo -n "5. Telemetry Agent: "
if launchctl print "gui/$(id -u)/com.local.hass.telemetry" >/dev/null 2>&1; then
    echo "OK - Telemetry agent loaded"
else
    echo "FAIL - Telemetry agent not loaded"
    echo "   ACTION: launchctl bootstrap \"gui/\$(id -u)\" \"\$HOME_SAFE/Library/LaunchAgents/com.local.hass.telemetry.plist\""
fi

# Test 6: Keychain Access
echo -n "6. Keychain Access: "
if security find-internet-password -w -s "homeassistant.local" -a "evertappels" >/dev/null 2>&1; then
    echo "OK - SMB credentials stored"
else
    echo "FAIL - No credentials for homeassistant.local"
    echo "   ACTION: Run keychain setup from ACTIONS section"
fi

# Test 7: Telemetry Script Execution
echo -n "7. Telemetry Script: "
if [[ -x "$HOME_SAFE/bin/hass_telemetry.sh" ]]; then
    # Prefer canonical /config for HA_MOUNT to avoid legacy path false negatives
    if HA_MOUNT="/config" "$HOME_SAFE/bin/hass_telemetry.sh" >/dev/null 2>&1; then
        echo "OK - hass_telemetry.sh executes successfully"
    else
        echo "FAIL - hass_telemetry.sh execution failed"
        echo "   ACTION: Check script permissions and HA webhook availability"
    fi
else
    echo "SKIP - hass_telemetry.sh not found; skipping"
fi

# Test 8: Webhook Connectivity (use correct, random ID)
echo -n "8. Webhook Endpoint: "
WEBHOOK_ID="${MACBOOK_HASS_MOUNT_WEBHOOK_ID:-macbook_hass_mount_telemetry_f8d2a9b4c7e1}"
WEBHOOK_URL="http://homeassistant.local:8123/api/webhook/${WEBHOOK_ID}"
if curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"test":"connectivity"}' "$WEBHOOK_URL" | egrep -q "200"; then
    echo "OK - Webhook endpoint reachable"
else
    echo "FAIL - Webhook endpoint not reachable"
    echo "   ACTION: Verify HA is running and webhook automation is loaded; ensure secrets.yaml contains macbook_hass_mount_webhook_id and telemetry script uses the same ID"
fi

# Test 9: Log Files Present
echo -n "9. Log Files: "
LOGS_OK=0
if [[ -f "$HOME_SAFE/Library/Logs/hass-mount.log" ]]; then
    ((LOGS_OK++))
fi
if [[ -f "$HOME_SAFE/Library/Logs/hass-telemetry.log" ]]; then
    ((LOGS_OK++))
fi
if [[ $LOGS_OK -eq 2 ]]; then
    echo "OK - Both log files present"
elif [[ $LOGS_OK -eq 1 ]]; then
    echo "PARTIAL - Only one log file present"
else
    echo "FAIL - No log files found"
    echo "   ACTION: Wait for agents to run or check LaunchAgent permissions"
fi

# Test 10: Recent Telemetry
echo -n "10. Recent Activity: "
if [[ -f "$HOME_SAFE/Library/Logs/hass-telemetry.log" ]] && tail -n 1 "$HOME_SAFE/Library/Logs/hass-telemetry.log" 2>/dev/null | grep -q "$(date '+%b %_d')"; then
    echo "OK - Recent telemetry activity logged"
else
    echo "FAIL - No recent telemetry activity"
    echo "    ACTION: Check telemetry agent status and logs"
fi

echo
echo "=== SUMMARY ==="
TOTAL_TESTS=10

# Count passed tests manually (aligned with tests above)
PASSED_TESTS=0
# 1. mount
mount | egrep -q " on $CONFIG_MP_REAL .*smbfs" && ((PASSED_TESTS++)) || mount | egrep -q " on $LEGACY_MP_REAL .*smbfs" && ((PASSED_TESTS++))
# 2. write access
test -w "$CONFIG_MP" && ((PASSED_TESTS++)) || test -w "$LEGACY_MP" && ((PASSED_TESTS++))
# 3. config present
test -f "$CONFIG_MP/configuration.yaml" && ((PASSED_TESTS++)) || test -f "$LEGACY_MP/configuration.yaml" && ((PASSED_TESTS++))
# 4. mount agent
launchctl print "gui/$(id -u)/com.local.hass.mount" >/dev/null 2>&1 && ((PASSED_TESTS++))
# 5. telemetry agent
launchctl print "gui/$(id -u)/com.local.hass.telemetry" >/dev/null 2>&1 && ((PASSED_TESTS++))
# 6. keychain
security find-internet-password -w -s "homeassistant.local" -a "evertappels" >/dev/null 2>&1 && ((PASSED_TESTS++))
# 7. telemetry script exec (use /config)
HA_MOUNT="/config" "$HOME_SAFE/bin/hass_telemetry.sh" >/dev/null 2>&1 && ((PASSED_TESTS++))
# 8. webhook endpoint reachable (correct ID)
curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"test":"connectivity"}' "$WEBHOOK_URL" | egrep -q "200" && ((PASSED_TESTS++))
# 9. logs present
[[ -f "$HOME_SAFE/Library/Logs/hass-mount.log" && -f "$HOME_SAFE/Library/Logs/hass-telemetry.log" ]] && ((PASSED_TESTS++))
# 10. recent activity
[[ -f "$HOME_SAFE/Library/Logs/hass-telemetry.log" ]] && tail -n 1 "$HOME_SAFE/Library/Logs/hass-telemetry.log" 2>/dev/null | grep -q "$(date '+%b %_d')" && ((PASSED_TESTS++))

echo "Tests passed: $PASSED_TESTS/$TOTAL_TESTS"

if [[ $PASSED_TESTS -eq $TOTAL_TESTS ]]; then
    echo "STATUS: ALL TESTS PASSED ✅"
    exit 0
elif [[ $PASSED_TESTS -ge 7 ]]; then
    echo "STATUS: MOSTLY WORKING ⚠️  - Minor issues to resolve"
    exit 1
else
    echo "STATUS: MAJOR ISSUES ❌ - Significant problems need attention"
    exit 2
fi
