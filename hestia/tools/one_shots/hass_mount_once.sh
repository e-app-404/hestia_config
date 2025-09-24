#!/bin/sh
# Idempotent user mount helper for HA Pi /config -> ~/hass
# - exits 0 if already mounted at $MNT
# - uses login keychain (mount_smbfs -N)

set -e
MNT="${MNT:-$HOME/hass}"
SRC="${SRC:-//evertappels@homeassistant.local/config}"
LOG="${LOG:-$HOME/Library/Logs/hass-mount.log}"

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
