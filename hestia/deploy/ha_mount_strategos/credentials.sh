sudo /bin/bash -s <<'BASH'
set -euo pipefail

# initialize to avoid 'unbound variable' with set -u
SMBUSER=''
PW=''

read -r -p "SMB username (DSM): " SMBUSER

# Read password securely:
# - prefer an interactive terminal
# - try /dev/tty if stdin is redirected
# - fallback to non-interactive read (may be empty)
if [ -t 0 ]; then
  # interactive stdin
  read -r -s -p "SMB password for ${SMBUSER}: " PW
  echo
elif [ -r /dev/tty ]; then
  # stdin redirected, but we have a controlling terminal
  read -r -s -p "SMB password for ${SMBUSER}: " PW </dev/tty
  echo
else
  # non-interactive fallback (may read from a pipe)
  read -r PW || PW=''
fi

# validate presence (use defaults to avoid unbound errors)
[ -n "${SMBUSER-}" ] && [ -n "${PW-}" ] || {
  echo "ABORT_EMPTY_CREDS"
  echo "Hint: credentials were empty. Run this script interactively from a terminal and enter both username and password when prompted."
  echo "If running from automation, consider using the macOS keychain or a credentials file and avoid passing passwords on the command line."
  echo "Exit code: 70"
  exit 70
}

urlenc() {
  local s="$1" i ch hex out=""
  for ((i=0;i<${#s};i++)); do
    ch=${s:i:1}
    case "$ch" in
      [a-zA-Z0-9._~-]) out+="$ch" ;;
      *)
        # printf with ASCII code of the char
        printf -v hex '%%%02X' "'$ch"
        out+="$hex"
        ;;
    esac
  done
  printf '%s' "$out"
}

PW_ENC="$(urlenc "$PW")"
SERVER=192.168.0.104
MP=/private/var/ha_real

umount -f "$MP" 2>/dev/null || true
install -d -o root -g wheel -m 755 "$MP"

mounted=0
used=""

for share in HA_MIRROR home git hestia; do
  if mount_smbfs "//${SMBUSER}:${PW_ENC}@${SERVER}/${share}" "$MP" 2>/tmp/ha_mount_err.txt; then
    mounted=1
    used="$share"
    break
  fi
done

if [ "$mounted" -ne 1 ]; then
  echo "AUTH_OR_ACCESS_DENIED"
  echo "Mount attempt failed for all candidate shares: HA_MIRROR, home, git, hestia"
  echo "- Verify username and password are correct and the DSM (NAS) account has SMB access."
  echo "- If password contains special characters, this script URL-encodes them; consider using a keychain-stored credential if mounting still fails."
  echo "--- stderr (first 80 lines) ---"
  sed -n "1,80p" /tmp/ha_mount_err.txt || true
  echo "Exit code: 66"
  exit 66
fi

if ! echo ok > "$MP/probe.txt"; then
  echo "WRITE_FAIL_ON_${used}"
  echo "Hint: mount succeeded but writing to the share failed."
  echo "- Check that the chosen share (${used}) allows writing for the NAS account."
  echo "- Ensure filesystem ACLs or NAS permissions do not block dotfiles."
  echo "Exit code: 67"
  exit 67
fi

echo "MOUNT_OK share=${used} path=${MP}"
mount | grep " $MP " || true
BASH