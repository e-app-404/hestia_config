---
title: "Home Assistant SMB Mount Operations Guide"
date: 2025-10-02
authors:
  - "e-app-404"
status: Active
related:
  - "ADR-0016: Canonical HA edit root & non-interactive SMB mount"
  - "hass_automount.md: Comprehensive playbook for automated mounting"
---

# Home Assistant SMB Mount Operations Guide

**Objective**: Establish reliable automatic mounting of Home Assistant configuration from SMB share to `~/hass` with comprehensive automation and resilience.

**Prerequisites**: 
- macOS with SMB client support
- Valid credentials for Home Assistant SMB share  
- Network connectivity to Home Assistant host
- User LaunchAgent approach (no system daemon conflicts)

## Executive Summary

This guide implements a robust per-user mount of the Home Assistant Pi `/config` Samba share at `~/hass` using LaunchAgents, keychain authentication, and network resilience patterns. The solution provides a single, user-owned edit root that editors like VS Code can write to without permission issues, includes automated retry logic for network interruptions, and comprehensive diagnostics for troubleshooting.

## Quick Start (Mount Now)

1. **Immediate Mount**
   ```bash
   $HOME/bin/hass_mount_once.sh
   mount | egrep -i "on $HOME/hass .*smbfs" && echo MOUNT_OK || echo MOUNT_FAIL
   test -w "$HOME/hass" && echo WRITE_OK || echo WRITE_FAIL  
   test -f "$HOME/hass/configuration.yaml" && echo CONFIG_OK || echo CONFIG_MISSING
   ```

2. **Troubleshoot Failed Mount**
   ```bash
   tail -n 120 "$HOME/Library/Logs/hass-mount.log" || true
   ```

## Current Working State (Validation)
- Active mount: `//evertappels@homeassistant.local/config` on `/Users/evertappels/hass` (mounted by user, 0777)
- Write test as user succeeds (touch creates a file owned by the console user)
- Per-user LaunchAgent loaded and can mount non-interactively using login keychain
- No system daemon manages this path; the `/private/var/ha_real` system path is not used

## LaunchAgent Configuration

### Primary Mount Agent

1. **Install Helper and Agent (User Context)**
   ```bash
   # Create directories and install components
   install -d "$HOME/bin" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
   install -m 0755 ${HA_MOUNT:-$HOME/hass}/hestia/tools/one_shots/hass_mount_once.sh "$HOME/bin/hass_mount_once.sh"
   install -m 0644 ${HA_MOUNT:-$HOME/hass}/hestia/tools/one_shots/com.local.hass.mount.plist "$HOME/Library/LaunchAgents/com.local.hass.mount.plist"
   ```

2. **Load and Activate Agent**
   ```bash
   launchctl unload -w  "$HOME/Library/LaunchAgents/com.local.hass.mount.plist" 2>/dev/null || true
   launchctl load   -w  "$HOME/Library/LaunchAgents/com.local.hass.mount.plist"
   launchctl list | grep com.local.hass.mount || true
   ```

3. **Alternative Manual LaunchAgent Creation**
   ```bash
   cat >"$HOME/Library/LaunchAgents/com.local.hass.mount.plist" <<'PL'
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
     <dict>
       <key>Label</key><string>com.local.hass.mount</string>
       <key>ProgramArguments</key>
       <array>
         <string>/bin/zsh</string>
         <string>-lc</string>
         <string>$HOME/bin/hass_mount_once.sh</string>
       </array>
       <key>RunAtLoad</key><true/>
       <key>KeepAlive</key>
       <dict>
         <key>NetworkState</key><true/>
       </dict>
       <key>StandardOutPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
       <key>StandardErrorPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
     </dict>
   </plist>
   PL
   ```

### Optional: Watchdog Agent (Periodic Checks)

1. **Create Watchdog LaunchAgent for Additional Resilience**
   ```bash
   cat >"$HOME/Library/LaunchAgents/com.local.hass.mount.watch.plist" <<'PL'
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
     <dict>
       <key>Label</key><string>com.local.hass.mount.watch</string>
       <key>ProgramArguments</key>
       <array>
         <string>/bin/zsh</string>
         <string>-lc</string>
         <string>mount | egrep -qi "on $HOME/hass .*smbfs" || $HOME/bin/hass_mount_once.sh</string>
       </array>
       <key>StartInterval</key><integer>180</integer>
       <key>StandardOutPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
       <key>StandardErrorPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
     </dict>
   </plist>
   PL
   ```

2. **Activate Watchdog**
   ```bash
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.mount.watch.plist"
   launchctl kickstart -k "gui/$(id -u)/com.local.hass.mount.watch"
   ```

## Environment Configuration

### Shell Environment
```bash
grep -F 'export HA_MOUNT="$HOME/hass"' "$HOME/.zshrc" || echo 'export HA_MOUNT="$HOME/hass"' >> "$HOME/.zshrc"
```

## Files Created/Changed (Locations & Purpose)
- `~/bin/hass_mount_once.sh` (idempotent helper; exits 0 if already mounted)
- `~/Library/LaunchAgents/com.local.hass.mount.plist` (LaunchAgent that runs the helper at login/network change)
- `~/Library/LaunchAgents/com.local.hass.mount.watch.plist` (optional watchdog for periodic checks)
- Login keychain internet-password entries:
  - Server: `homeassistant.local` (or Pi IP)
  - Account: `evertappels`  
  - Protocol: `smb ` (note the trailing space required by the `security` CLI)
  - Debug (metadata only):
    ```bash
    security find-internet-password -s homeassistant.local -a evertappels -r 'smb '
    ```

**Retired Components**: System LaunchDaemon and helper paths such as `/Library/LaunchDaemons/com.local.ha.mount.real.plist`, `/usr/local/sbin/ha_mount_helper`, and `/private/var/ha_real` are not used in this per-user model and should remain retired to avoid conflicting mounts.

**Important**: ADR-0016 requires explicit acknowledgement before disabling or removing system daemons. Any operator action or script that unloads/removes a system LaunchDaemon MUST set the environment token `ACK_DISABLE_SYSTEM_DAEMON=I_UNDERSTAND` to avoid accidental destructive changes.

## Quick interactive test (end-to-end)
Make a temporary mount point and mount as the console user (non-interactive if the login keychain item exists):

```bash
mkdir -p ~/ha_test_mount
/sbin/mount_smbfs -N -d 0777 -f 0777 "//evertappels@homeassistant.local/config" ~/ha_test_mount

# verify mount and write
mount | grep " $HOME/ha_test_mount "
ls -ladn ~/ha_test_mount
date > ~/ha_test_mount/.ha_write_test && echo "user write ok"
ls -l ~/ha_test_mount/.ha_write_test
umount ~/ha_test_mount && rmdir ~/ha_test_mount
```

## Load/unload the user LaunchAgent (runs as logged-in user)

```bash
launchctl unload -w  ~/Library/LaunchAgents/com.local.hass.mount.plist 2>/dev/null || true
launchctl load   -w  ~/Library/LaunchAgents/com.local.hass.mount.plist

# check agent listed
launchctl list | grep com.local.hass.mount || true
```

## If you prefer a different mount point (e.g. `/Volumes/config`)
Pick **one** approach:

**A) Direct plist (recommended)**
- Edit the **last** `ProgramArguments` item in `~/Library/LaunchAgents/com.local.hass.mount.plist` to the new path (e.g. `/Volumes/config`), then reload the agent:
```bash
plutil -p ~/Library/LaunchAgents/com.local.hass.mount.plist | sed -n '1,120p'
launchctl unload -w  ~/Library/LaunchAgents/com.local.hass.mount.plist
launchctl load   -w  ~/Library/LaunchAgents/com.local.hass.mount.plist
```

**B) Helper-based (only if you use a wrapper script)**
- If your helper reads `MOUNT_POINT`, set it before invoking the helper **or** hardcode inside the helper:
```bash
export MOUNT_POINT=/Volumes/config
```

> Note: with the current direct-`ProgramArguments` approach, option **A** is the correct way to change the mount point.

## Validation & Testing

### Post-Reboot Acceptance Test
```bash
mount | egrep -i "on $HOME/hass .*smbfs" && echo MOUNT_OK || echo MOUNT_FAIL
test -w "$HOME/hass" && echo WRITE_OK || echo WRITE_FAIL
test -f "$HOME/hass/configuration.yaml" && echo CONFIG_OK || echo CONFIG_MISSING
tail -n 80 "$HOME/Library/Logs/hass-mount.log" | tail -n 40
```

### Comprehensive Verification (Copy-Paste)
```bash
MNT="$HOME/hass"
[ -d "$MNT" ] && echo DIR_OK || echo DIR_MISSING
mount | grep " on $MNT (smbfs" >/dev/null && echo MOUNTED_SMB || echo NOT_MOUNTED
SRC=$(mount | grep " on $MNT (smbfs" | awk '{print $1}')
echo "SRC=$SRC"
echo "$SRC" | grep -Eq '@(homeassistant|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/config$' && echo SOURCE_OK_PI_CONFIG || echo SOURCE_NEEDS_ATTENTION
touch "$MNT/.strategos_write_test" && echo WRITE_OK || echo WRITE_FAIL
smbutil statshares -m "$MNT" | sed -n '1,40p' || true
launchctl list | grep -q com.local.hass.mount && echo AGENT_LOADED || echo AGENT_NOT_LOADED
sudo launchctl list 2>/dev/null | grep -q com.local.ha.mount.real && echo SYSTEM_DAEMON_STILL_RUNNING || echo SYSTEM_DAEMON_NOT_RUNNING
```

### Diagnostic Commands
```bash
# LaunchAgent status
launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'state|last exit code|error|program' || true

# Network connectivity test  
smbutil view //evertappels@homeassistant </dev/null || true

# Force remount
diskutil unmount "$HOME/hass" 2>/dev/null || true
"$HOME/bin/hass_mount_once.sh"
```

## Keychain Setup

### Add Login Keychain Entry for Non-Interactive Mounts
Run as the console user (no sudo):

```bash
# Store login keychain Internet-password for the Pi
read -s -p "Password for evertappels@homeassistant.local: " PW; echo
security delete-internet-password -s homeassistant.local -a evertappels -r "smb " >/dev/null 2>&1 || true
security add-internet-password -s homeassistant.local -a evertappels -r "smb " -T /sbin/mount_smbfs -l ha_haos_login -w "$PW"
unset PW
```

### Verify Existing Credentials
```bash
security find-internet-password -w -s "homeassistant" -a "evertappels" >/dev/null
security find-internet-password -w -s "homeassistant.local" -a "evertappels" >/dev/null  
```

### Add Missing Credentials (Alternative Method)
```bash
read -r -s -p "SMB password for evertappels: " PASS; echo
security add-internet-password -U -s "homeassistant" -a "evertappels" -w "$PASS"
security add-internet-password -U -s "homeassistant.local" -a "evertappels" -w "$PASS"
unset PASS
```

### Keychain Check (Metadata Only)
Avoid `-g` unless you want the password printed to stderr:

```bash
security find-internet-password -s homeassistant.local -a evertappels -r "smb "
```

**Notes:**
- Avoid placing plaintext credentials in `/etc/nsmb.conf` — keychain is preferred
- Do not have both a system daemon and a user agent mount the same share (causes "File exists" and ownership conflicts)

## Network Resilience Hardening

### Option 1: Mount Script Retry Loop

Append this retry logic to `$HOME/bin/hass_mount_once.sh` before final validations:

```bash
i=0; until mount | egrep -qi "on $HOME/hass .*smbfs"; do
  i=$((i+1))
  [ $i -gt 5 ] && break
  sleep 2
  "$HOME/bin/hass_mount_once.sh" || true
done
```

### Option 2: Separate Retry Wrapper

Create `$HOME/bin/hass_mount_retry.sh`:
```bash
#!/bin/bash
i=0; until mount | egrep -qi "on $HOME/hass .*smbfs"; do
  i=$((i+1))
  [ $i -gt 5 ] && break
  sleep 2
  "$HOME/bin/hass_mount_once.sh" || true
done
```

## Relationship map
- `~/Library/LaunchAgents/com.local.hass.mount.plist` → invokes `/sbin/mount_smbfs` with the above arguments.
- Login keychain Internet-password (`homeassistant.local` / `evertappels`, proto `smb `) → used by `mount_smbfs -N`.
- Repo-embedded symlinks pointing to live system paths were removed to avoid coupling runtime configuration into the HA config repo.

## Troubleshooting Guide

| Symptom | Check Command | Resolution |
|---------|--------------|------------|
| Mount not present | `mount \| grep hass` | Run `$HOME/bin/hass_mount_once.sh` |
| LaunchAgent not running | `launchctl print "gui/$(id -u)/com.local.hass.mount"` | Bootstrap and kickstart agent |
| Keychain prompts | `security find-internet-password -s homeassistant` | Re-add credentials to keychain |
| Network timeout | `smbutil view //evertappels@homeassistant` | Check network connectivity |
| Permission denied | `test -w "$HOME/hass"` | Verify mount options and credentials |

## Reproducible Checklist (From Scratch)
1. Add login keychain Internet-password for `homeassistant.local` / `evertappels`
2. Create `~/Library/LaunchAgents/com.local.hass.mount.plist` with ProgramArguments calling `mount_smbfs -N -d 0777 -f 0777 //evertappels@homeassistant.local/config $HOME/hass`
3. `launchctl load -w ~/Library/LaunchAgents/com.local.hass.mount.plist`
4. Verify:

```bash
mount | grep " $HOME/hass " && echo MOUNT_OK || echo MOUNT_FAIL
touch "$HOME/hass/.write_test" && echo WRITE_OK || echo WRITE_FAIL
smbutil statshares -m "$HOME/hass" | sed -n "1,40p"
```

## What's been done so far
- Created and loaded `~/Library/LaunchAgents/com.local.hass.mount.plist` (user LaunchAgent mounts `//evertappels@homeassistant.local/config` → `~/hass`).
- Added/verified login keychain Internet-password for `homeassistant.local` / `evertappels`.
- Retired the system LaunchDaemon and `/private/var/ha_real` path for this workflow.
- Removed repo-embedded symlinks pointing at live system paths to avoid drift.

## Mount point(s)
- User mount: `$HOME/hass` (`/Users/evertappels/hass`) — mounted by the user LaunchAgent (authoritative).
- System mount: not used in this model.

## Monitoring & Diagnostics

### Key Monitoring Points
- **Log Location**: `$HOME/Library/Logs/hass-mount.log`
- **Mount Check**: `mount | egrep "on $HOME/hass .*smbfs"`
- **Write Test**: `test -w "$HOME/hass"`
- **Config Validation**: `test -f "$HOME/hass/configuration.yaml"`

### Machine-Readable Diagnostics
For comprehensive system health assessment:
```bash
$HOME/hass/hestia/tools/utils/mount/generate_hass_mount_diagnostics.sh
```

Output: `hestia/config/diagnostics/hass_mount_status_current.yaml`

### Debug & Utilities
- Inspect SMB share metadata for a mounted path:
```bash
smbutil statshares -m "$HOME/hass"
```
- List mounts and search for the mountpoint:
```bash
mount | grep " $HOME/hass "
```
- Keychain (login) metadata:
```bash
security find-internet-password -s homeassistant.local -a evertappels -r "smb "
```

### Advanced Diagnostics
For detailed troubleshooting, see the comprehensive diagnostics template at:
`hestia/config/diagnostics/hass_mount_status.yaml`
