NX1: DSM + Portal Reverse Proxy

This folder contains the DSM-specific deployment artifacts and operational notes for converging Synology DSM to a single Web Service with a hardened reverse proxy for /portal, /ha, and /grafana.

What is included
- apply_portal_changes.sh — safe deploy script (dry-run default; --apply to execute)
- .htaccess.template — recommended headers (install with --write-htaccess)
- acceptance_tests.sh — acceptance checks for portal and assets (enhanced, strict)
- snippets/ — reverse-proxy snippets for DSM Web Station

Quick operator steps
1. Deploy assets to NAS (dry-run, then apply):
   hestia/deploy/dsm/apply_portal_changes.sh --apply --write-htaccess
2. If Cloudflare Tunnel is used, ensure the tunnel ingress maps nas.xplab.io to http://192.168.0.104:80
   — Change in Cloudflare Zero Trust → Tunnels if necessary.
3. Run acceptance tests:
   hestia/deploy/dsm/acceptance_tests.sh nas.xplab.io

Where to look for backups
- When apply_portal_changes.sh runs with --apply it creates a timestamped backup directory on the NAS (see script output).

Notes
- Prefer scoped Cloudflare API tokens for automation (Account:Tunnels:Edit + Zone:Cache Purge:Edit).
- If DSM UI or reverse-proxy already sets headers, avoid duplicating in .htaccess.
