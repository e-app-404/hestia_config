#!/usr/bin/env bash
set -euo pipefail

# Change to BASE="$HOME/HA" if /Volumes gives you grief
BASE="/n/ha"
SHARES=(config addons share)
HOSTS=(homeassistant.reverse-beta.ts.net homeassistant.local 192.168.0.129)

log(){ printf "[%s] %s\n" "$(date '+%F %T')" "$*" >&2; }

is_mounted(){ mount -t smbfs | awk -v p="$1" '$0 ~ (" on " p " ") {found=1} END{exit(found?0:1)}'; }
is_live(){ ls -d "$1/." >/dev/null 2>&1; }

# Only touch local mountpoints that are NOT mounted
clean_local_mountpoint(){
  local mp="${1:-}"; [ -n "$mp" ] || { log "internal: missing mp"; return 1; }
  if ! is_mounted "$mp"; then
    # nuke anything Finder may have dropped (.DS_Store, etc.)
    find "$mp" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
    # if empty, recreate to ensure clean inode
    rmdir "$mp" 2>/dev/null || true
    mkdir -p "$mp"
  fi
}

pick_host(){
  for h in "${HOSTS[@]}"; do
    if nc -z -G 2 "$h" 445 >/dev/null 2>&1; then echo "$h"; return 0; fi
  done
  return 1
}

try_mount_once(){
  local host="$1" share="$2" mp="$3"
  /sbin/mount_smbfs -N "//$host/$share" "$mp"
}

ensure_share(){
  local share="${1:-}"; [ -n "$share" ] || { log "internal: missing share"; return 1; }
  local mp="${BASE}/${share}"
  mkdir -p "$mp"

  # If already mounted & alive, we're done
  if is_mounted "$mp"; then
    if is_live "$mp"; then
      log "OK: $share already mounted at $mp"
      return 0
    else
      log "Stale mount at $mp; unmounting"
      umount -f "$mp" || true
    fi
  fi

  clean_local_mountpoint "$mp"

  local host; host="$(pick_host)" || { log "No SMB host reachable"; return 1; }

  # Recheck just before mounting to avoid races
  if is_mounted "$mp" && is_live "$mp"; then
    log "OK: $share mounted by another process"
    return 0
  fi

  log "Mounting //$host/$share -> $mp"

  # Up to 3 attempts, cleaning before each, and treating concurrent success as OK
  local i
  for i in 1 2 3; do
    clean_local_mountpoint "$mp"
    if try_mount_once "$host" "$share" "$mp"; then
      log "OK: mounted $share"
      return 0
    fi
    # If someone else mounted during our attempt, call it success
    if is_mounted "$mp" && is_live "$mp"; then
      log "OK: $share mounted concurrently"
      return 0
    fi
    sleep 0.2
  done

  log "FAIL: could not mount //$host/$share at $mp"
  return 1
}

main(){
  local rc=0
  if [ "${#SHARES[@]}" -eq 0 ]; then log "No shares configured"; exit 1; fi
  # Ownership guard: user must own BASE and subdirs to avoid "Operation not permitted"
  if [ ! -O "$BASE" ]; then
    log "Fixing owner on $BASE (sudo once)"
    sudo chown -R "$USER":"$(id -gn)" "$BASE" || true
    sudo chmod 755 "$BASE" || true
  fi
  for s in "${SHARES[@]}"; do
    mkdir -p "$BASE/$s"
    if [ ! -O "$BASE/$s" ]; then sudo chown "$USER":"$(id -gn)" "$BASE/$s" || true; sudo chmod 755 "$BASE/$s" || true; fi
    ensure_share "$s" || rc=1
  done
  exit "$rc"
}
main "$@"
