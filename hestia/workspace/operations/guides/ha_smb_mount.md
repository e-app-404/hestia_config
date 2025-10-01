---
title: "Interactive SMB mount for Home Assistant data"
date: 2025-09-24
authors:
  - "Evert Appels"
status: Draft
related:
  - "ADR-0016: Canonical HA edit root & non-interactive SMB mount"
---

# Interactive SMB mount for Home Assistant data

This document describes the recommended per-user mount of the Home Assistant Pi `/config` Samba share into the console user's home directory. The goal is a single, user-owned edit root at `~/hass` that editors like VS Code can write to without permission issues. This guide covers what changed, where files live, exact reproducible commands, and recommended follow-ups (keychain, launchd, and avoiding duplicate mounts).

## One-line summary
We mount the Home Assistant Pi's Samba `/config` share to `~/hass` using a user LaunchAgent (no system daemon). Authentication for non-interactive mounts uses the login keychain Internet-password for `homeassistant.local` (or the Pi's IP) and your Samba username. Result: a single, user-writable edit root for editors.

## What currently works (success evidence)
- Active mount: `//evertappels@homeassistant.local/config` on `/Users/evertappels/hass` (mounted by user, 0777).
- Write test as user succeeds (touch creates a file owned by the console user).
- Per-user LaunchAgent is loaded and can mount non-interactively using the login keychain.
- No system daemon manages this path; the `/private/var/ha_real` system path is not used.

## Install (helper + LaunchAgent template)
```bash
# install helper + agent (user context)
install -d "$HOME/bin" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
install -m 0755 ${HA_MOUNT:-$HOME/hass}/hestia/tools/one_shots/hass_mount_once.sh "$HOME/bin/hass_mount_once.sh"
install -m 0644 ${HA_MOUNT:-$HOME/hass}/hestia/tools/one_shots/com.local.hass.mount.plist "$HOME/Library/LaunchAgents/com.local.hass.mount.plist"

# load agent
launchctl unload -w  "$HOME/Library/LaunchAgents/com.local.hass.mount.plist" 2>/dev/null || true
launchctl load  -w   "$HOME/Library/LaunchAgents/com.local.hass.mount.plist"
```

## Files created / changed (locations & purpose)
- `~/bin/hass_mount_once.sh` (idempotent helper; exits 0 if already mounted)
- `~/Library/LaunchAgents/com.local.hass.mount.plist` (LaunchAgent that runs the helper at login / network change)
- Login keychain internet-password (login keychain):
  - Server: `homeassistant.local` (or Pi IP)
  - Account: `evertappels`
  - Protocol: `smb ` (note the trailing space required by the `security` CLI)
  - Debug (metadata only):
    ```bash
    security find-internet-password -s homeassistant.local -a evertappels -r 'smb '
    ```

 - Retired: system LaunchDaemon and helper paths such as `/Library/LaunchDaemons/com.local.ha.mount.real.plist`, `/usr/local/sbin/ha_mount_helper`, and `/private/var/ha_real` are not used in this per-user model and should remain retired to avoid conflicting mounts.

Important: ADR-0016 requires an explicit acknowledgement before disabling or removing system daemons. Any operator action or script that unloads/removes a system LaunchDaemon MUST set the environment token `ACK_DISABLE_SYSTEM_DAEMON=I_UNDERSTAND` (or otherwise follow ADR enforcement) to avoid accidental destructive changes.

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

## Quick verification (copy–paste)
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

## Keychain: add login keychain entry for non-interactive mounts
Run as the console user (no sudo):

```bash
# store login keychain Internet-password for the Pi
read -s -p "Password for evertappels@homeassistant.local: " PW; echo
security delete-internet-password -s homeassistant.local -a evertappels -r "smb " >/dev/null 2>&1 || true
security add-internet-password -s homeassistant.local -a evertappels -r "smb " -T /sbin/mount_smbfs -l ha_haos_login -w "$PW"
unset PW
```

Notes:
- Avoid placing plaintext credentials in `/etc/nsmb.conf` — keychain is preferred.
- Do not have both a system daemon and a user agent mount the same share (this causes "File exists" and ownership conflicts).

## Keychain check (metadata only)
Avoid `-g` unless you want the password printed to stderr.

```bash
security find-internet-password -s homeassistant.local -a evertappels -r "smb "
```

## Relationship map
- `~/Library/LaunchAgents/com.local.hass.mount.plist` → invokes `/sbin/mount_smbfs` with the above arguments.
- Login keychain Internet-password (`homeassistant.local` / `evertappels`, proto `smb `) → used by `mount_smbfs -N`.
- Repo-embedded symlinks pointing to live system paths were removed to avoid coupling runtime configuration into the HA config repo.

## Reproducible checklist (from scratch)
1. Add login keychain Internet-password for `homeassistant.local` / `evertappels`.
2. Create `~/Library/LaunchAgents/com.local.hass.mount.plist` with ProgramArguments calling `mount_smbfs -N -d 0777 -f 0777 //evertappels@homeassistant.local/config $HOME/hass`.
3. `launchctl load -w ~/Library/LaunchAgents/com.local.hass.mount.plist`.
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

## Debug & utilities
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
