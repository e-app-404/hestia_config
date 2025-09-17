#!/bin/bash
set -Eeuo pipefail
IFS=$'\n\t'
source "$HOME/ha_path.sh" || exit 2

echo "== HESTIA DOCTOR =="
echo "HESTIA_CONFIG: $HESTIA_CONFIG"
echo "Config file    : ${HESTIA_CONFIG_FILE:-configuration.yaml}"
echo "Exists         : $([ -d "$HESTIA_CONFIG" ] && echo YES || echo NO)"
echo "Writable       : $([ -w "$HESTIA_CONFIG" ] && echo YES || echo NO)"
echo "Git root       : $(git -C "$HESTIA_CONFIG" rev-parse --show-toplevel 2>/dev/null || echo "not a git work tree")"
echo "Mount info     :"
df -h "$HESTIA_CONFIG" | sed -n '1,2p' || true

probe() {
  local h=$1 p=$2
  if command -v nc >/dev/null 2>&1; then
    nc -z -G 1 "$h" "$p" >/dev/null 2>&1 && echo "open" || echo "closed/filtered"
  else
    (echo > /dev/tcp/$h/$p) >/dev/null 2>&1 && echo "open" || echo "closed/filtered"
  fi
}
HA_IP_LAN="192.168.0.129"
echo "Port 8123 (LAN $HA_IP_LAN): $(probe $HA_IP_LAN 8123)"
echo "Port 22222 (HA CLI,  $HA_IP_LAN): $(probe $HA_IP_LAN 22222)"

[ -d /Volumes/HA/config ] && echo "/Volumes/ha present" || echo "/Volumes/ha not present"
[ -d /Volumes/HA/config ] && echo "/Volumes/HA present" || echo "/Volumes/HA not present"
[ -d /n/ha ] && echo "/n/ha mount point present" || echo "/n/ha missing (run autofs setup)"
