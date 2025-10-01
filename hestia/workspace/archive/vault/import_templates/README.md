Vault import templates
======================

This folder contains small YAML templates and a helper script to guide importing
secrets for Samba shares and Tailscale artifacts into your secret backend.

Files:
- `samba_*.yaml` - example payloads for Samba shares (username/password placeholders).
- `import_samba_and_tailscale.sh` - a dry-run helper that prints the vault commands you
  should run. Replace the echo lines with your vault CLI commands (e.g., `vault kv put`).

Guidance:
- Use the naming convention: `secret/hestia/samba/<share>` and store `username` and
  `password` as key/value pairs.
- For Tailscale ACLs and keys, use `secret/hestia/tailscale/acl` and
  `secret/hestia/tailscale/keys` and store the exported ACL JSON/YAML and key lists.
