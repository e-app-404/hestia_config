#!/bin/bash
# Rollback script for HA mount telemetry changes
# Run this to revert all changes made during setup

set -euo pipefail

echo "=== HA MOUNT TELEMETRY ROLLBACK ==="
echo "This will revert all telemetry changes made during setup"
read -p "Continue? (y/N): " -n 1 -r
echo
[[ ! $REPLY =~ ^[Yy]$ ]] && exit 0

echo "1. Stopping and removing telemetry LaunchAgent..."
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.telemetry.plist" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.local.hass.telemetry.plist"

echo "2. Removing telemetry script..."
rm -f "$HOME/bin/hass_telemetry.sh"
rm -f "$HOME/hass/hestia/config/diagnostics/generate_hass_mount_diagnostics.sh"

echo "3. Removing verification script..."
rm -f "$HOME/hass/hestia/config/diagnostics/verify_hass_mount_telemetry.sh"

echo "4. Removing webhook package..."
rm -f "$HOME/hass/packages/hestia/ha_mount_telemetry_webhook.yaml"

echo "5. Reverting mount LaunchAgent to original (mount_smbfs direct)..."
cat > "$HOME/Library/LaunchAgents/com.local.hass.mount.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.local.hass.mount</string>
  <key>ProgramArguments</key>
  <array>
    <string>/sbin/mount_smbfs</string>
    <string>-N</string>
    <string>-d</string><string>0777</string>
    <string>-f</string><string>0777</string>
    <string>//evertappels@homeassistant.local/config</string>
    <string>/Users/evertappels/hass</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StandardOutPath</key><string>/Users/evertappels/Library/Logs/hass-mount.log</string>
  <key>StandardErrorPath</key><string>/Users/evertappels/Library/Logs/hass-mount.log</string>
</dict></plist>
EOF

echo "6. Reloading mount LaunchAgent..."
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.mount.plist" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.mount.plist"

echo "7. Cleaning up log files..."
rm -f "$HOME/Library/Logs/hass-telemetry.log"

echo "8. Removing temp files..."
rm -f /tmp/verify_hass_mount_telemetry.sh
rm -f /tmp/ha_mount_telemetry.yaml
rm -f /tmp/com.local.hass.mount.plist.patch

echo
echo "ROLLBACK COMPLETE"
echo "- Telemetry system removed"
echo "- Mount LaunchAgent reverted to original (will require manual password entry)"
echo "- All related files cleaned up"
echo
echo "To restore hardened mount (without telemetry):"
echo "  launchctl bootout \"gui/\$(id -u)\" \"\$HOME/Library/LaunchAgents/com.local.hass.mount.plist\""
echo "  # Edit plist to use: /bin/zsh -lc \$HOME/bin/hass_mount_once.sh"
echo "  launchctl bootstrap \"gui/\$(id -u)\" \"\$HOME/Library/LaunchAgents/com.local.hass.mount.plist\""