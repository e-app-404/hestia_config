# Network files index

This file is a lightly opinionated index of canonical network configuration artifacts in this workspace. It is intended to make it easier to find the single source of truth for specific concerns and to document the expected consumers for each file.

Canonical files (read-only/authoritative unless noted):

- `tailscale_machines.topology.json` — Canonical list of Tailscale devices and metadata (IPs split into `ipv4`/`ipv6`). Used by automation scripts and audits.
- `cloudflare.conf` — Cloudflare tunnel and proxy configuration documentation (human-authored). Contains operational notes and verification steps.
- `dns.topology.json` — Compact DNS topology (apex + subdomains) used for quick reference.
- `nas.conf` — Synology DSM operational configuration and deployment notes (contains secrets in placeholders; do not commit tokens).
- `network.conf.yaml` — Higher-level network configuration and Tailscale devices inventory. Consider migrating authoritative fields to `tailscale_machines.topology.json` and using `network.conf.yaml` as a runtime summary.
- `network.topology.json` / `network.runtime.yaml` / `network.extract.yaml` — Runtime topology extracts used for orchestration and ad-hoc queries.
- `netgear.conf` — Switch as-built and port/VLAN mapping.

Guidance:
- Treat `tailscale_machines.topology.json` as the authoritative device metadata for Tailscale-managed devices. When updating devices, prefer editing that file (or the source CSV/automation that generates it), and then propagate to other summaries.
- Secrets (API tokens, private keys, node keys) must not be committed. Use your vault or environment variable references instead.
- Add a JSON Schema (`tailscale_machines.schema.json`) to validate topology files in CI.

Maintenance tasks:
- Run `python3 -m json.tool tailscale_machines.topology.json` to validate JSON syntax.
- Use `tools/check_tailscale_consistency.py` (present in this folder) to detect IP drift between `network.conf.yaml` and `tailscale_machines.topology.json`.

(End of file)


# TEMPLATE: Preview Configuration Files
#
# This directory contains generated configuration previews that may include:
# - SMB/CIFS share configurations
# - Generated service configurations  
# - Preview configurations with embedded credentials
# - Network service configurations
#
# These files are excluded from git tracking as they may contain:
# - Generated credentials
# - Network paths and shares
# - Service-specific configuration with PII
#
# Template structure for preview configs:
# [global]
# server_string = "__SERVER_NAME__"
# workgroup = "__WORKGROUP__"
# 
# [share_name]
# browseable = true
# path = "__SHARE_PATH__"
# valid_users = "__USER_LIST__"
#
# Replace __PLACEHOLDER__ values with actual configuration.
# These files contain generated credentials and are excluded from git tracking.

# Example preview configuration files:
# - smb.conf (Samba/SMB share configuration)