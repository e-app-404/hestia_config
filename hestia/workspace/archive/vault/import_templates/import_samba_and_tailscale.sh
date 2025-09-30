#!/usr/bin/env bash
# Simple import helper for vault templates (non-destructive; prints commands)
# Usage: ./import_samba_and_tailscale.sh [--vault-cli vault write] (dry-run)

set -euo pipefail

TEMPLATES_DIR="$(dirname "$0")/../templates"

echo "Templates directory: $TEMPLATES_DIR"

for f in "$TEMPLATES_DIR"/samba_*.yaml; do
  name="$(basename "$f" .yaml)"
  share="${name#samba_}"
  echo "# Importing $f -> vault://hestia/samba/$share#credentials"
  echo "# Example (HashiCorp Vault):"
  echo "# vault kv put secret/hestia/samba/$share username=\\"<user>\\" password=\\"<pass>\\""
done

echo "# Tailscale placeholders"
echo "# vault kv put secret/hestia/tailscale/acl acl=@acl.json"
echo "# vault kv put secret/hestia/tailscale/keys keys=@keys.json"

echo "Done (dry-run). Replace with actual vault CLI commands as appropriate."
