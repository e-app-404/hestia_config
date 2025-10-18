#!/bin/bash
# HASS Mount Operations Runbook
# Pin this for zero-thought maintenance

echo "=== HASS MOUNT OPS RUNBOOK ==="
echo "Choose an operation:"
echo
echo "1) acceptance - Post-reboot/change acceptance test"
echo "2) force-cycle - Force clean mount cycle"
echo "3) check-telemetry - Test webhook telemetry"
echo "4) agent-status - Show all agent states"
echo "5) logs - Show recent activity"
echo "6) health-probe - Check JSON health file"
echo "7) keychain-verify - Verify SMB credentials"
echo "8) full-diagnostic - Complete system diagnostic"
echo

read -p "Enter choice (1-8): " choice

case $choice in
  1)
    echo "=== ACCEPTANCE TEST ==="
  mount | egrep -i " on /config .*smbfs" && echo "✅ MOUNT_OK (/config)" || mount | egrep -i " on $HOME/hass .*smbfs" && echo "✅ MOUNT_OK (legacy $HOME/hass)" || echo "❌ MOUNT_FAIL"
  test -w "/config" && echo "✅ WRITE_OK (/config)" || test -w "$HOME/hass" && echo "✅ WRITE_OK (legacy $HOME/hass)" || echo "❌ WRITE_FAIL"
  test -f "/config/configuration.yaml" && echo "✅ CONFIG_OK (/config)" || test -f "$HOME/hass/configuration.yaml" && echo "✅ CONFIG_OK (legacy $HOME/hass)" || echo "❌ CONFIG_MISSING"
    launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'last exit code'
    tail -n 5 "$HOME/Library/Logs/hass-mount.log" | sed -n '$p'
    ;;

  2)
    echo "=== FORCE CLEAN CYCLE ==="
  diskutil unmount "/config" || diskutil unmount "$HOME/hass" || true
    launchctl kickstart -k "gui/$(id -u)/com.local.hass.mount"
    sleep 2
    mount | egrep -i "on $HOME/hass .*smbfs" && echo "✅ REMOUNT_OK" || echo "❌ REMOUNT_FAIL"
    ;;

  3)
    echo "=== CHECK TELEMETRY ==="
  if [[ -x "$HOME/bin/hass_telemetry.sh" ]]; then "$HOME/bin/hass_telemetry.sh" && echo "✅ WEBHOOK_OK"; else echo "SKIP - hass_telemetry.sh not present"; fi
    echo "Recent telemetry:"
    tail -n 3 "$HOME/Library/Logs/hass-telemetry.log"
    ;;

  4)
    echo "=== AGENT STATUS ==="
    echo "Primary Mount Agent:"
    launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'state|last exit code' | sed 's/^/  /'

    echo "Telemetry Agent:"
    if launchctl print "gui/$(id -u)/com.local.hass.telemetry" >/dev/null 2>&1; then
      echo "  ✅ Running"
    else
      echo "  ❌ Not loaded"
    fi

    echo "Watchdog Agent:"
    if launchctl print "gui/$(id -u)/com.local.hass.mount.watch" >/dev/null 2>&1; then
      echo "  ✅ Running"
    else
      echo "  ❌ Not loaded"
    fi
    ;;

  5)
    echo "=== RECENT LOGS ==="
    echo "Mount log (last 5):"
    tail -n 5 "$HOME/Library/Logs/hass-mount.log" | sed 's/^/  /'
    echo
    echo "Telemetry log (last 3):"
    tail -n 3 "$HOME/Library/Logs/hass-telemetry.log" | sed 's/^/  /'
    ;;

  6)
    echo "=== HEALTH PROBE ==="
    if [[ -f "/config/hestia/config/diagnostics/.last_mount_status.json" ]]; then
      python3 -c "
import json
with open('/config/hestia/config/diagnostics/.last_mount_status.json') as f:
    data = json.load(f)
    print(f'Health: {data[\"health\"][\"summary\"]}')
    print(f'Last Update: {data[\"health\"][\"timestamp\"]}')
    print(f'Mount: {data[\"mount\"][\"mounted\"]} | Write: {data[\"mount\"][\"write_ok\"]} | Config: {data[\"mount\"][\"config_present\"]}')
    print(f'Agent Exit Code: {data[\"agent\"][\"exit_code\"]}')
"
    else
      echo "❌ Health probe file missing"
    fi
    ;;

  7)
    echo "=== KEYCHAIN VERIFY ==="
    security find-internet-password -w -s "homeassistant" -a "evertappels" >/dev/null && echo "✅ homeassistant credential OK" || echo "❌ homeassistant credential MISSING"
    security find-internet-password -w -s "homeassistant.local" -a "evertappels" >/dev/null && echo "✅ homeassistant.local credential OK" || echo "❌ homeassistant.local credential MISSING"
    ;;

  8)
    echo "=== FULL DIAGNOSTIC ==="
    "$HOME/hass/hestia/config/diagnostics/acceptance_test.sh"
    echo
    echo "=== REGRESSION CHECKS ==="
    echo "LaunchAgent Configuration:"
    plutil -extract ProgramArguments raw -o - "$HOME/Library/LaunchAgents/com.local.hass.mount.plist"
    echo
    echo "Helper Script Hardening:"
    grep -q 'ENC_PASS' "$HOME/bin/hass_mount_once.sh" && echo "✅ URL encoding present" || echo "❌ URL encoding missing"
    grep -q 'chmod 000' "$HOME/bin/hass_mount_once.sh" && echo "✅ Lock mechanism present" || echo "❌ Lock mechanism missing"
    echo
    echo "Webhook Security:"
    grep -q '!secret' "$HOME/hass/packages/hestia/ha_mount_telemetry_webhook.yaml" && echo "✅ Webhook ID in secrets" || echo "❌ Webhook ID hardcoded"
    ;;

  *)
    echo "Invalid choice. Use 1-8."
    exit 1
    ;;
esac
