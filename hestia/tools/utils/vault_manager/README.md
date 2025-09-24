# Vault Manager (hestia/tools/utils/vault_manager)

This directory contains guidance, templates and small helper scripts to
manage secrets for the Hestia workspace. The goal is to provide a
predictable, auditable mapping between repository artifacts (Samba
shares, Tailscale ACLs/keys, Glances credentials, etc.) and secret
backend entries so credentials never live in plaintext in the repo.

This README documents the local conventions, templates and recommended
commands for importing secrets into a vault-like secret store (for
example HashiCorp Vault's KV store). It is intentionally implementation
agnostic — the provided import helpers are dry-run by default and show
the CLI commands you should run against your secret backend.

## Layout

- `templates/` - example secret payloads (YAML) that show the expected
	key names and values. These are safe to store in the repository because
	they contain placeholders (e.g. `__REPLACE_ME__`).
- `import_templates/` - small helper scripts and README that demonstrate
	how to import the templates into a vault. The scripts are dry-run by
	default and print example commands.
- `README.md` - this document.

## Naming conventions

Use a predictable vault path convention so automation can look up
credentials reliably. Recommended paths:

- Samba shares: `secret/hestia/samba/<share>`
	- stored keys: `username`, `password`, optional `smbpasswd`, `samba_extra_opts`
- Tailscale ACLs: `secret/hestia/tailscale/acl` (store ACL JSON or YAML)
- Tailscale Keys: `secret/hestia/tailscale/keys` (store auth key list)
- Glances credentials: `secret/hestia/glances/<host>` (username/password)

The repository YAMLs reference secrets using a `vault://` URI scheme; for
example in `hestia/core/config/storage/samba.yaml`:

```yaml
credentials: "vault://hestia/samba/config_share#credentials"
```

The `#credentials` fragment is a simple convention to indicate the
payload to use; when importing into a real vault this maps to the
secret stored at `secret/hestia/samba/config_share`.

## Templates and examples

Example templates live under `hestia/vault/templates/` and look like:

```yaml
username: homeassistant
password: __REPLACE_ME__
```

These templates are intentionally minimal and show the canonical keys
that code and renderers expect when generating `smb.conf` or other
consumers.

## Import helper (dry-run)

`hestia/vault/import_templates/import_samba_and_tailscale.sh` prints
example vault CLI commands. It is a dry-run and will not modify any
secret backend unless you replace the `echo` lines with your vault CLI
commands (for example `vault kv put` for HashiCorp Vault).

Example HashiCorp Vault commands (manual)

```bash
# Samba share
vault kv put secret/hestia/samba/config_share username="homeassistant" password="<secret>"

# Tailscale ACLs (upload a JSON/YAML file)
vault kv put secret/hestia/tailscale/acl @tailscale-acl.json
vault kv put secret/hestia/tailscale/keys @tailscale-keys.json
```

If your secret backend is not HashiCorp Vault, map the `secret/hestia/...`
path to the equivalent location in your backend.

## Security best-practices

- Never commit real credentials to the repository. Use the templates with
	placeholder values only.
- Use access controls on your vault (ACLs/policies) so only automation or
	operators with a business need can read the secret paths.
- Rotate Tailscale auth keys and Samba passwords periodically and record
	rotation events in your audit logs.
- Prefer short-lived credentials where supported by your secret backend
	(e.g., dynamic secrets or tokens).

## Integration with Hestia tooling

- `hestia/core/config/storage/samba.yaml` references vault URIs for
	Samba share credentials. The preview tooling (`apply_strategos`) will
	render `smb.conf` previews only — credential injection happens at
	provisioning time and should be done by an operator or a secure
	provisioning agent that can access the vault.
- The `hestia/tools/*` scripts include a lightweight preview runner and
	the `import_templates` helper which together let you validate the
	configuration shape and prepare secret import commands.

## Example workflow

1. Edit `hestia/core/config/storage/samba.yaml` to define shares and
	 reference vault URIs for credentials.
2. Create secret entries in your vault per the naming convention using
	 `import_templates/import_samba_and_tailscale.sh` as a guide, or using
	 the appropriate CLI for your backend.
3. Validate `smb.conf` preview with `hestia/tools/apply_strategos/samba_preview_runner.py`.
4. Provision the service and inject credentials at runtime using a
	 secure provisioning agent (outside of this repository).

## Troubleshooting

- If previews fail linting, check `hestia/core/preview/notes/SAMBA_LINT.json`.
- The import helper is intentionally a dry-run. Replace the `echo`
	placeholders with your vault CLI to perform actual imports.

## Contact / Maintainers

If you need changes to the vault layout or additional templates, open a
PR against the repository or contact the Hestia maintainers listed in
the repository documentation.

