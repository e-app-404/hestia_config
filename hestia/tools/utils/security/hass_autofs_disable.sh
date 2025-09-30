#!/bin/sh
# Disable legacy autofs maps that auto-mount /n/ha to avoid duplicate mounts.
# SAFE-GUARDED: requires REPLACE_AUTOF=YES and root.

set -e
[ "${REPLACE_AUTOF:-}" = "YES" ] || { echo "Refusing to modify autofs. Export REPLACE_AUTOF=YES to proceed."; exit 2; }
[ "$(id -u)" -eq 0 ] || { echo "Please run with sudo/root."; exit 2; }

ts() { date +%Y%m%d%H%M%S; }
bak() { cp "$1" "$1.bak.$(ts)"; echo "backup: $1 -> $1.bak.$(ts)"; }

if [ -f /etc/auto_master ]; then
  echo "Backing up /etc/auto_master ..."
  bak /etc/auto_master
  # Comment out lines that enable custom smb maps (BSD sed -i syntax)
  sed -i '' 's/^\([[:space:]]*\/\-[[:space:]]\+auto_ha.*\)$/# \1/' /etc/auto_master || true
  sed -i '' 's/^\([[:space:]]*\/\-[[:space:]]\+auto_smb.*\)$/# \1/' /etc/auto_master || true
fi

for f in /etc/auto_ha /etc/auto_master.d/ha.autofs; do
  if [ -e "$f" ]; then
    mv "$f" "$f.disabled.$(ts)"
    echo "disabled: $f -> $f.disabled.$(ts)"
  fi
done

echo "Reloading automounter ..."
automount -cv || true

echo "Verifying /n/ha inactive ..."
if mount | egrep -q '/System/Volumes/Data/n/ha'; then
  echo "WARNING: /n/ha still active (may be busy); consider reboot to fully clear."
else
  echo "OK: /n/ha not mounted."
fi
