---
id: ha-mount-installer
title: "HA Mount Installer: Sticky, Clean, and ADR-0024-Compliant Integration"
slug: ha-mount-installer
date: 2024-06-11
tags: ["playbook", "ha_mount", "macos", "smb", "adr-0024", "integration", "mount", "samba"]
related: []
---
# Integration Playbook: Sticky, Clean, and ADR-0024-Compliant

**Assumptions**

- **Platform:** macOS (zsh, Apple Silicon)
- **Canonical interface:** `/config` (APFS synthetic entry → `/System/Volumes/Data/homeassistant`)
- **Home Assistant Samba add-on:**  
    - Host: `homeassistant.local`  
    - IP: `192.168.0.129`  
    - Share: `config`  
    - User: `evertappels`  
    - Credentials: Saved in your login Keychain (not root)
- **Mounting:** Already validated as user (no `sudo`)

**What “sticky & integrated” means**

- **Auto-mount** on login and network availability (user LaunchAgent + robust user-mode mount script)
- **Idempotent manual up/down commands** (`ha-up`, `ha-down`) available anytime
- **VS Code** opens the `/config` workspace directly (no `/Volumes` anchoring)
- **Health check** script to detect drift or mount issues quickly
- **Zero password prompts** after initial setup (Keychain handles credentials)
- **No root keychain or `sudo mount_smbfs`** required

```bash
set -euo pipefail

# 1) Ensure ~/bin exists and install scripts
install -d -m 0755 "$HOME/bin"
cat > "$HOME/bin/ha-mount.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
HOST="homeassistant.local"
IP="192.168.0.129"
SMB_USER="evertappels"
SHARE="config"
MNT="/System/Volumes/Data/homeassistant"
DOMAIN="WORKGROUP"
log() { printf '[ha-mount] %s\n' "$*"; }
already_mounted() { mount | grep -E "on $MNT .*smbfs" >/dev/null 2>&1; }
mkdir -p "$MNT"
chown "$USER":staff "$MNT"
if already_mounted; then log "already mounted at $MNT"; exit 0; fi
if /sbin/mount_smbfs -f 0644 -d 0755 "//$SMB_USER@$IP/$SHARE" "$MNT" 2>/dev/null; then
  log "mounted //$SMB_USER@$IP/$SHARE → $MNT"; exit 0; fi
/sbin/mount_smbfs -f 0644 -d 0755 "//${DOMAIN};${SMB_USER}@$IP/$SHARE" "$MNT"
log "mounted //${DOMAIN};${SMB_USER}@$IP/$SHARE → $MNT"
SH
chmod +x "$HOME/bin/ha-mount.sh"

cat > "$HOME/bin/ha-unmount.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
MNT="/System/Volumes/Data/homeassistant"
diskutil unmount "$MNT" >/dev/null 2>&1 || true
printf '[ha-unmount] unmounted (or not mounted): %s\n' "$MNT"
SH
chmod +x "$HOME/bin/ha-unmount.sh"

cat > "$HOME/bin/config-health" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-/config}"
[[ -d "$TARGET" ]] || { echo "FAIL: $TARGET not a directory"; exit 2; }
python3 - <<'PY'
import os, sys
p = sys.argv[1]
print("OK dir:", p)
print("realpath:", os.path.realpath(p))
PY "$TARGET"
MNT="/System/Volumes/Data/homeassistant"
if mount | grep -E "on $MNT .*smbfs" >/dev/null 2>&1; then
  echo "OK mount: smbfs active on $MNT"
else
  echo "WARN: smbfs not active on $MNT"
fi
if [[ "${REQUIRE_CONFIG_WRITABLE:-0}" = "1" ]]; then
  TMP="$TARGET/.health_rw_probe"
  ( : > "$TMP" ) && rm -f "$TMP" && echo "OK RW: write probe"
fi
SH
chmod +x "$HOME/bin/config-health"

# 2) Install LaunchAgent
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$HOME/Library/LaunchAgents/com.hestia.mount.homeassistant.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.hestia.mount.homeassistant</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/evertappels/bin/ha-mount.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StartInterval</key><integer>60</integer>
  <key>StandardOutPath</key><string>/Users/evertappels/Library/Logs/hestia.mount.out</string>
  <key>StandardErrorPath</key><string>/Users/evertappels/Library/Logs/hestia.mount.err</string>
</dict></plist>
PLIST
plutil -lint "$HOME/Library/LaunchAgents/com.hestia.mount.homeassistant.plist" >/dev/null

# 3) Load/reload agent
launchctl unload "$HOME/Library/LaunchAgents/com.hestia.mount.homeassistant.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.hestia.mount.homeassistant.plist"

# 4) Shell helpers (append once)
ZRC="$HOME/.zshrc"
grep -q "alias cfg=" "$ZRC" 2>/dev/null || cat >> "$ZRC" <<'Z'
# ADR-0024 helpers
alias cfg='cd /config'
alias codecfg='code -n /config'
alias codecfg-i='code-insiders -n /config'
alias ha-up='~/bin/ha-mount.sh'
alias ha-down='~/bin/ha-unmount.sh'
Z
```
