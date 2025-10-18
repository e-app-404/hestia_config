# --- BEGIN HOME STABILIZER ---
USER_REAL_HOME="$(/usr/bin/dscl . -read /Users/$USER NFSHomeDirectory 2>/dev/null | awk '{print $2}')"
[ -n "$USER_REAL_HOME" ] || USER_REAL_HOME="/Users/$USER"
HOME_SAFE="$USER_REAL_HOME"
case "$HOME" in
    */actions-runner/*)
        echo "[hass] WARNING: overriding HOME ('$HOME') -> '$HOME_SAFE'" >&2; HOME="$HOME_SAFE"; export HOME;;
esac
# --- END HOME STABILIZER ---
#!/bin/bash
# Post-reboot acceptance test for HASS mount telemetry
# Tape this to muscle memory

echo "=== HASS MOUNT ACCEPTANCE TEST ==="
echo "Date: $(date)"
echo

mount | egrep -i " on /config .*smbfs" && echo "✅ MOUNT_OK (/config)" || mount | egrep -i " on $HOME_SAFE/hass .*smbfs" && echo "✅ MOUNT_OK (legacy $HOME_SAFE/hass)" || echo "❌ MOUNT_FAIL"
test -w "/config" && echo "✅ WRITE_OK (/config)" || test -w "$HOME_SAFE/hass" && echo "✅ WRITE_OK (legacy $HOME_SAFE/hass)" || echo "❌ WRITE_FAIL"
test -f "/config/configuration.yaml" && echo "✅ CONFIG_OK (/config)" || test -f "$HOME_SAFE/hass/configuration.yaml" && echo "✅ CONFIG_OK (legacy $HOME_SAFE/hass)" || echo "❌ CONFIG_MISSING"
launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'last exit code' | sed 's/^.*last exit code/✅ EXIT_CODE/'

echo
echo "=== AGENT STATUS ==="
echo "Mount Agent:"
launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'state =' | sed 's/^.*state/  State:/'

echo "Telemetry Agent:"
if launchctl print "gui/$(id -u)/com.local.hass.telemetry" >/dev/null 2>&1; then
    echo "  ✅ Loaded and running"
else
    echo "  ❌ Not loaded"
fi

echo "Watchdog Agent:"
if launchctl print "gui/$(id -u)/com.local.hass.mount.watch" >/dev/null 2>&1; then
    echo "  ✅ Loaded and running"
else
    echo "  ❌ Not loaded"
fi

echo
echo "=== HEALTH PROBE ==="
if [[ -f "/config/hestia/config/diagnostics/.last_mount_status.json" ]]; then
    HEALTH=$(python3 -c "import json; print(json.load(open('/config/hestia/config/diagnostics/.last_mount_status.json'))['health']['summary'])" 2>/dev/null || echo "PARSE_ERROR")
    echo "Health Status: $HEALTH"
else
    echo "Health probe file missing"
fi

echo
echo "=== RECENT TELEMETRY ==="
if [[ -f "$HOME_SAFE/Library/Logs/hass-telemetry.log" ]]; then
    echo "Last 3 telemetry entries:"
    tail -n 3 "$HOME_SAFE/Library/Logs/hass-telemetry.log" | sed 's/^/  /'
else
    echo "No telemetry log found"
fi
