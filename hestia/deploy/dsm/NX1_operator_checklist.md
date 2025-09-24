NX1 Operator Checklist

Pre-deploy
- Verify backup of /volume1/web or ensure apply_portal_changes.sh backup location is reachable.
- Ensure you have a Cloudflare token or dashboard access to update tunnel ingress.

Deploy
- Run dry-run first:
  hestia/deploy/dsm/apply_portal_changes.sh
- When satisfied, apply with htaccess:
  hestia/deploy/dsm/apply_portal_changes.sh --apply --write-htaccess

Cloudflare
- If tunnel is token-managed and remote_config=true, update via Cloudflare dashboard: Zero Trust → Tunnels → [synology-dsm] → Edit ingress
  - Ensure nas.xplab.io → http://192.168.0.104:80
  - Preserve plex mapping
- Purge zone cache after changes if assets don't show up immediately.

Verify
- Run acceptance tests:
  hestia/deploy/dsm/acceptance_tests.sh nas.xplab.io
- Confirm:
  - /portal/ returns 200 and is served with Cache-Control: no-store
  - /_assets/app.js returns 200 with Cache-Control: max-age=14400 (or appropriate max-age)
  - CSP header is present on root or portal

Rollback
- apply_portal_changes.sh creates a timestamped backup dir on the NAS — restore files from there if needed.

Security
- Rotate tokens after use and use scoped tokens where possible.

Contacts
- Who to contact if Cloudflare changes fail: admin@yourdomain.example
