Operator Checklist — DSM Web Station consolidation

Prechecks
- [ ] Confirm DSM >= 7.2 with Web Station, Apache 2.4, PHP 8.2 installed.
- [ ] Ensure valid TLS cert bound to nas.xplab.io in Security → Certificate.
- [ ] Ensure /volume1/web/{public,portal,_assets} exist and contain expected content.

UI Steps
- [ ] In Web Station → Web Service: ensure `xplab-public` exists with document root `/volume1/web`. If a `xplab-portal` service exists, migrate content and remove the extra service.
- [ ] In Web Station → Web Portal: bind `nas.xplab.io` to `xplab-public`, enable HTTP/2 and HSTS, bind TLS cert.
- [ ] In Control Panel → Application Portal → Reverse Proxy: add rules per `reverse_proxy_notes.md` for `/portal`, `/ha`, `/grafana`.

Files to copy (optional)
- Use `hestia/deploy/dsm/apply_portal_changes.sh --apply` to copy example files to `/volume1/web`. The script is dry-run by default.

Acceptance
- Run `hestia/deploy/dsm/acceptance_tests.sh nas.xplab.io` from a machine that can reach the NAS to verify endpoints and headers.

Evidence
- Save screenshots into `hestia/deploy/dsm/screenshots/`:
  - web_services.png
  - web_portal.png
  - reverse_proxy_portal.png
  - reverse_proxy_ha.png
  - reverse_proxy_grafana.png

Notes
- If headers are already managed via DSM UI or a fronting CDN, avoid duplicating them in `.htaccess`.
- For Cloudflare/Tunnel users: only cache `/_assets/*` and set `Cache-Control` appropriately. Ensure `/portal` is not cached.
