#!/usr/bin/env bash
# Import templates into a HashiCorp Vault KV v2 path (dry-run by default)

set -euo pipefail

TEMPLATES_DIR="$(dirname "$0")/../templates"
APPLY=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) APPLY=true; shift;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

for f in "$TEMPLATES_DIR"/samba_*.yaml; do
  name="$(basename "$f" .yaml)"
  share="${name#samba_}"
  echo "Processing template $f -> secret/hestia/samba/$share"
  username=$(sed -n "s/^username: \(.*\)$/\1/p" "$f" || true)
  password=$(sed -n "s/^password: \(.*\)$/\1/p" "$f" || true)
  if [ -z "$password" ] || [ "$password" = "__REPLACE_ME__" ]; then
    echo "Please enter password for $share (will not be echoed):"
    read -rs PW
    password="$PW"
  fi
  if [ "$APPLY" = true ]; then
    echo "vault kv put secret/hestia/samba/$share username=\"$username\" password=\"$password\""
    vault kv put secret/hestia/samba/$share username="$username" password="$password"
  else
    echo "DRY-RUN: vault kv put secret/hestia/samba/$share username=\"$username\" password=\"<hidden>\""
  fi
done

echo "Processing tailscale placeholders"
ACL_FILE="/n/ha/hestia/vault/templates/tailscale_acl.json"
KEYS_FILE="/n/ha/hestia/vault/templates/tailscale_keys.json"
if [ -f "$ACL_FILE" ]; then
  if [ "$APPLY" = true ]; then
    vault kv put secret/hestia/tailscale/acl @"$ACL_FILE"
  else
    echo "DRY-RUN: vault kv put secret/hestia/tailscale/acl @$ACL_FILE"
  fi
else
  echo "No tailscale ACL template found at $ACL_FILE"
fi

if [ -f "$KEYS_FILE" ]; then
  if [ "$APPLY" = true ]; then
    vault kv put secret/hestia/tailscale/keys @"$KEYS_FILE"
  else
    echo "DRY-RUN: vault kv put secret/hestia/tailscale/keys @$KEYS_FILE"
  fi
else
  echo "No tailscale keys template found at $KEYS_FILE"
fi

echo "Done (apply=$APPLY)."
