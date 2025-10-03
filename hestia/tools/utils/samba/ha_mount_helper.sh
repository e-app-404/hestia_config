#!/bin/bash
# Safe mount helper for macOS smbfs
# - sanitizes TARGET_USER and falls back to root if unresolved
# - logs actions to /var/log/ha-mount.log
# - uses mount_smbfs -o file_mode,dir_mode,uid,gid for ownership/permissions
# - optionally retries with password-authenticated mount if PASSWORD env is provided

set -euo pipefail

SERVER="192.168.0.104"
ACCOUNT="babylonrobot"
MP="/private/var/ha_real"
SHARE="HA_MIRROR"
LOG="/var/log/ha-mount.log"
# Optional: export PASSWORD in the environment to try an authenticated mount
PASSWORD_ENV_VAR_NAME="HA_MOUNT_PASSWORD"

log() {
  /bin/date "+%Y-%m-%d %H:%M:%S" | { read ts; printf "%s %s\n" "$ts" "$*" >>"$LOG"; }
}

mkdir -p "$MP"
# Ensure log exists and has sensible perms
: >"$LOG"
chown root:admin "$LOG" 2>/dev/null || true
chmod 640 "$LOG" || true

# Resolve target user safely
RAW_TARGET_USER="${SUDO_USER:-$(stat -f%Su /dev/console || true)}"
if [ -z "$RAW_TARGET_USER" ] || ! id "$RAW_TARGET_USER" >/dev/null 2>&1; then
  log "TARGET_USER '$RAW_TARGET_USER' not resolvable; falling back to root"
  TARGET_USER="root"
else
  TARGET_USER="$RAW_TARGET_USER"
fi
TARGET_UID=$(id -u "$TARGET_USER")
TARGET_GID=$(id -g "$TARGET_USER")
log "Using TARGET_USER='$TARGET_USER' UID=$TARGET_UID GID=$TARGET_GID"

# Check existing mount
if mount | grep -qE "^//${ACCOUNT}@${SERVER}/${SHARE} on ${MP} \(smbfs\)"; then
  log "already mounted (uid=$TARGET_UID gid=$TARGET_GID)"
  exit 0
fi
if mount | grep -qE " on ${MP} \(smbfs\)"; then
  log "different smb mount on ${MP}; unmounting"
  if umount -f "$MP" 2>>"$LOG"; then
    log "unmounted existing mount on ${MP}"
  else
    log "ERROR: unmount failed"
    exit 1
  fi
fi

# Helper that attempts mount with given options and logs result
attempt_mount() {
  local extra_opts="$1"
  log "attempting mount: //${ACCOUNT}@${SERVER}/${SHARE} -> ${MP} (opts: $extra_opts)"
  if mount_smbfs -N -o "$extra_opts" "//${ACCOUNT}@${SERVER}/${SHARE}" "$MP" 2>>"$LOG"; then
    log "mounted ${MP} (opts: $extra_opts)"
    return 0
  fi
  return 1
}

# Primary mount options using file_mode/dir_mode/uid/gid
PRIMARY_OPTS="file_mode=0777,dir_mode=0777,uid=${TARGET_UID},gid=${TARGET_GID}"
if attempt_mount "$PRIMARY_OPTS"; then
  log "mount succeeded with primary options"
  exit 0
fi

# If password env var present, try authenticated mount (will prompt if not using -N)
PASSWORD="${!PASSWORD_ENV_VAR_NAME:-}"
if [ -n "$PASSWORD" ]; then
  log "primary mount failed; trying authenticated mount using env $PASSWORD_ENV_VAR_NAME"
  # Use a temporary credentials file to avoid exposing password in ps
  CREDFILE=$(mktemp -t ha_mount_cred.XXXX)
  chmod 600 "$CREDFILE"
  printf "%s\n" "$PASSWORD" >"$CREDFILE"
  # mount_smbfs accepts the password on stdin when using -N? If not, we try without -N
  # Try without -N so mount_smbfs can prompt; feed password via stdin
  if printf "%s\n" "$PASSWORD" | mount_smbfs -o "$PRIMARY_OPTS" "//${ACCOUNT}@${SERVER}/${SHARE}" "$MP" 2>>"$LOG"; then
    log "mounted ${MP} with authenticated attempt"
    rm -f "$CREDFILE"
    exit 0
  else
    log "authenticated mount attempt failed"
    rm -f "$CREDFILE"
  fi
fi

# As a last resort, try a permissive mount (uid/gid=0 and wide perms) to detect server ACL behavior
FALLBACK_OPTS="file_mode=0777,dir_mode=0777,uid=0,gid=0"
log "primary+auth attempts failed; trying fallback options (uid=0 gid=0) to test ACLs"
if attempt_mount "$FALLBACK_OPTS"; then
  log "mounted ${MP} with fallback uid=0 gid=0; this indicates server ACLs restrict non-root access"
  exit 0
fi

log "ERROR: all mount attempts failed. Inspect server-side ACLs, credentials, and /var/log/ha-mount.log"

# Extra diagnostic: attempt to stat the mount point via smbutil for more info
if command -v smbutil >/dev/null 2>&1; then
  log "running 'smbutil statshares -m $MP' for diagnostics"
  if smbutil statshares -m "$MP" >>"$LOG" 2>&1; then
    log "smbutil statshares returned info"
  else
    log "smbutil statshares failed (see $LOG)"
  fi
fi

exit 1
