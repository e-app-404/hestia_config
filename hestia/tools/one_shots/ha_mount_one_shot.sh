cat >"$HOME/ha_mount_one_shot.sh" <<'SCRIPT'
#!/usr/bin/env bash
set -e

# variables up-front (edit user/host if needed)
AGENT="$HOME/Library/LaunchAgents/com.local.hass.mount.plist"
LOG="$HOME/Library/Logs/hass-mount.log"
MNT="$HOME/hass"

# Deconflict: stop any previous agents/daemons that might own ~/hass
launchctl bootout gui/$(id -u)/com.local.ha.mount      2>/dev/null || true
launchctl bootout gui/$(id -u)/com.local.hass.mount    2>/dev/null || true
sudo launchctl bootout system/com.local.ha.mount.real  2>/dev/null || true

# Ensure agent is unloaded before we overwrite the plist
launchctl unload -w "$AGENT" 2>/dev/null || true

# Unmount and create directories
/sbin/umount "$MNT" 2>/dev/null || true
mkdir -p "$MNT" "$(dirname "$AGENT")" "$(dirname "$LOG")"

# Ensure the login keychain has the HA Samba creds (so -N is non-interactive)
read -r -s -p "Password for evertappels@homeassistant.local: " PW; echo
security delete-internet-password -s homeassistant.local -a evertappels -r "smb " >/dev/null 2>&1 || true
security add-internet-password -s homeassistant.local -a evertappels -r "smb " -T /sbin/mount_smbfs -l ha_haos_login -w "$PW"
unset PW

# Create the user LaunchAgent that mounts the PI's /config -> ~/hass
cat >"$AGENT"<<EOF
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
    <string>\${MNT}</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StandardOutPath</key><string>\${LOG}</string>
  <key>StandardErrorPath</key><string>\${LOG}</string>
</dict></plist>
EOF

# Load and verify
launchctl load -w "$AGENT"
sleep 1
echo "--- VERIFY ---"
mount | grep " ${MNT} " || echo "NOT_MOUNTED"
smbutil statshares -m "${MNT}" | grep -E "SERVER_NAME|USER_ID|SMB_VERSION" -n || true
touch "${MNT}/.strategos_write_test" && echo "WRITE_OK" || echo "WRITE_FAIL"
SCRIPT