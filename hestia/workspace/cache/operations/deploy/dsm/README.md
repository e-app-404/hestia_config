DSM deployment artifacts for nas.xplab.io

Purpose: provide operator-friendly, dry-run-safe files to converge Web Station to a single Web Service, add reverse-proxy notes, and deploy app assets to `/volume1/web`.

Files included:
- .htaccess.template  — recommended headers & options (use only if DSM UI does not manage headers)
- public/index.html   — example public page (references fingerprinted assets under /_assets)
- portal/index.html   — portal page; MUST be served with Cache-Control: no-store
- _assets/app.js      — resilient config fetch with AbortController + exponential backoff
- _assets/portal.config.json — example portal manifest (relative URLs)
- portal/ping.html    — tiny auth-check ping endpoint
- apply_portal_changes.sh — deploy script (dry-run by default; --apply to copy to /volume1/web)
- acceptance_tests.sh — curl-based checks to validate endpoints/headers
- reverse_proxy_notes.md — explicit DSM UI steps for reverse proxy rules

Safety:
- deploy script is dry-run by default and requires `--apply` to make changes.
- It will not alter system services or restart anything.

Usage (example dry-run):
  bash hestia/deploy/dsm/apply_portal_changes.sh

Usage (apply):
  sudo bash hestia/deploy/dsm/apply_portal_changes.sh --apply
