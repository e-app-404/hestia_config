#!/usr/bin/env bash
set -euo pipefail
: "${HA_MOUNT:=$HOME/hass}"
HOST="192.168.0.104"
USER="babylonrobot"
SSH_PORT=22
LOCAL_SNIPPET="${HA_MOUNT:-$HOME/hass}/hestia/deploy/dsm/snippets/nginx_portal_headers.inc"
REMOTE_INCLUDE_DIR="/usr/local/nginx/includes"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REMOTE_TMP_SNIPPET="/tmp/portal_headers.inc"
LOCAL_HELPER="/tmp/local_hestia_helper_${TIMESTAMP}.sh"

if [ ! -f "${LOCAL_SNIPPET}" ]; then
  echo "Snippet not found: ${LOCAL_SNIPPET}"
  exit 1
fi

scp -P "${SSH_PORT}" "${LOCAL_SNIPPET}" "${USER}@${HOST}:${REMOTE_TMP_SNIPPET}"

cat > "${LOCAL_HELPER}" <<'EOF'
#!/bin/sh
set -euo pipefail
TIMESTAMP="$1"
REMOTE_INCLUDE_DIR="/usr/local/nginx/includes"
REMOTE_INCLUDE_PATH="${REMOTE_INCLUDE_DIR}/portal_headers.inc"
BACKUP_DIR="/var/backups/hestia_nginx_${TIMESTAMP}"
REMOTE_TMP_SNIPPET="/tmp/portal_headers.inc"
NGINX_BIN=""
for p in /usr/sbin/nginx /usr/syno/sbin/nginx /usr/local/nginx/sbin/nginx; do
  if [ -x "$p" ]; then
    NGINX_BIN="$p"
    break
  fi
done
if [ -z "$NGINX_BIN" ]; then
  echo "ERROR: nginx binary not found."
  exit 2
fi
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
if [ -f /etc/nginx/nginx.conf ]; then
  cp -a /etc/nginx/nginx.conf "$BACKUP_DIR/nginx.conf"
fi
if [ -d /etc/nginx/conf.d ]; then
  cp -a /etc/nginx/conf.d "$BACKUP_DIR/conf.d"
fi
mkdir -p "$REMOTE_INCLUDE_DIR"
if [ -f "$REMOTE_INCLUDE_PATH" ]; then
  cp -a "$REMOTE_INCLUDE_PATH" "$BACKUP_DIR/portal_headers.inc"
fi
mv "$REMOTE_TMP_SNIPPET" "$REMOTE_INCLUDE_PATH"
chmod 644 "$REMOTE_INCLUDE_PATH"
INCLUDE_LOADER=/etc/nginx/conf.d/hestia_portal_include.conf
if [ -f "$INCLUDE_LOADER" ]; then
  cp -a "$INCLUDE_LOADER" "$BACKUP_DIR/$(basename "$INCLUDE_LOADER")"
fi
cat > "$INCLUDE_LOADER" <<'INC'
include /usr/local/nginx/includes/portal_headers.inc;
INC
chmod 644 "$INCLUDE_LOADER"
if "$NGINX_BIN" -t; then
  if [ -f /var/run/nginx.pid ]; then
    kill -HUP "$(cat /var/run/nginx.pid 2>/dev/null || echo '')" 2>/dev/null || "$NGINX_BIN" -s reload || true
  else
    "$NGINX_BIN" -s reload || true
  fi
else
  if [ -f "$BACKUP_DIR/portal_headers.inc" ]; then
    mv "$BACKUP_DIR/portal_headers.inc" "$REMOTE_INCLUDE_PATH"
  fi
  exit 3
fi
echo "$BACKUP_DIR"
EOF

scp -P "${SSH_PORT}" "${LOCAL_HELPER}" "${USER}@${HOST}:/tmp/local_hestia_helper.sh"
ssh -p "${SSH_PORT}" "${USER}@${HOST}" "sudo sh /tmp/local_hestia_helper.sh '${TIMESTAMP}'"
ssh -p "${SSH_PORT}" "${USER}@${HOST}" "rm -f /tmp/local_hestia_helper.sh ${REMOTE_TMP_SNIPPET}"
rm -f "${LOCAL_HELPER}"
echo "Install finished. Verify with curl checks or run the acceptance tests."
