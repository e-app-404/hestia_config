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
#!/usr/bin/env bash
set -euo pipefail

# Idempotent helper to mount the canonical edit root at $HOME_SAFE/hass using macOS Keychain-backed
# credentials and mount_smbfs -N. Intended for use from a LaunchAgent with KeepAlive.NetworkState.

MOUNT_POINT="${MOUNT_POINT:-$HOME_SAFE/hass}"
SMB_USER="${SMB_USER:-}"
SMB_HOST="${SMB_HOST:-}"
SMB_SHARE="${SMB_SHARE:-}"

usage() {
  cat <<EOF >&2
Usage: export SMB_USER SMB_HOST SMB_SHARE and run this script.
Example:
  SMB_USER=ha SMB_HOST=192.168.0.104 SMB_SHARE=ha-share $0

The script is idempotent: if $MOUNT_POINT is already mounted it exits 0.
EOF
  exit 2
}

if [ -z "$SMB_USER" ] || [ -z "$SMB_HOST" ] || [ -z "$SMB_SHARE" ]; then
  usage
fi

# Detect already-mounted
if mount | egrep -q " on ${MOUNT_POINT} "; then
  echo "ALREADY_MOUNTED ${MOUNT_POINT}"
  exit 0
fi

mkdir -p "$MOUNT_POINT"
chmod 700 "$MOUNT_POINT"

URL="//${SMB_USER}@${SMB_HOST}/${SMB_SHARE}"
echo "Mounting $URL -> $MOUNT_POINT (using Keychain via -N)"

# Attempt mount using mount_smbfs (macOS). The -N flag uses Keychain credentials.
if command -v mount_smbfs >/dev/null 2>&1; then
  if mount_smbfs -N "$URL" "$MOUNT_POINT"; then
    echo "MOUNT_OK $MOUNT_POINT"
    exit 0
  else
    echo "MOUNT_FAIL mount_smbfs returned non-zero" >&2
    exit 3
  fi
else
  echo "MOUNT_NOT_AVAILABLE: mount_smbfs not found on PATH" >&2
  exit 4
fi
#!/bin/sh
# Idempotent user mount helper for HA Pi /config -> ~/hass
# - exits 0 if already mounted at $MNT
# - uses login keychain (mount_smbfs -N)

set -e
MNT="${MNT:-$HOME_SAFE/hass}"
SRC="${SRC:-//evertappels@homeassistant.local/config}"
LOG="${LOG:-$HOME_SAFE/Library/Logs/hass-mount.log}"

mkdir -p "$MNT" "$(dirname "$LOG")"

if mount | grep -q " on $MNT (smbfs"; then
  NOW="$(date '+%F %T')"
  CUR_SRC="$(mount | awk -v m="$MNT" '$0 ~ " on " m " \\(smbfs" {print $1; exit}')"
  printf "%s already mounted: %s -> %s\n" "$NOW" "$CUR_SRC" "$MNT" >>"$LOG" 2>&1
  exit 0
fi

NOW="$(date '+%F %T')"
printf "%s mounting: %s -> %s\n" "$NOW" "$SRC" "$MNT" >>"$LOG" 2>&1
/sbin/mount_smbfs -N -d 0777 -f 0777 "$SRC" "$MNT" >>"$LOG" 2>&1
RC=$?
if [ $RC -eq 0 ]; then
  printf "%s mounted %s\n" "$(date '+%F %T')" "$MNT" >>"$LOG"
else
  printf "%s mount failed rc=%s\n" "$(date '+%F %T')" "$RC" >>"$LOG"
fi
exit $RC
