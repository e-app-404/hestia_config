# xplab Dual-surface Portal — DSM Setup (concise)

## 1) Web Station docroot

- Public:  `/volume1/web/public`  → served at `/`
- Private: `/volume1/web/portal`  → served at `/portal`

## 2) DSM Reverse Proxy (Control Panel → Login Portal → Advanced → Reverse Proxy)

Create rules:

- Location: `/portal` → Destination: `http://127.0.0.1:80/portal`
  - Access control: Enable authentication (DSM account) and restrict source IPs to Tailscale CIDRs or specific devices.
- Location: `/ha` → Destination: `http://192.168.0.129:8123` (strip prefix)
  - Optional Header: inject `Authorization: Bearer <HA_Long_Lived_Access_Token>` (limits to requests under `/portal` if supported).
- Location: `/grafana` → Destination: `http://<grafana-host>:3000` (strip prefix)
  - Prefer a view‑only/anonymous org or rely on DSM auth.

## 3) Cloudflare

- Keep Tunnel/Proxy for `nas.xplab.io`.
- Cache rules: Bypass for `/portal/*` and `/ha/*`.

## 4) Security notes

- UI hides private tiles, but **enforcement lives in DSM reverse proxy**.
- Rotate HA tokens periodically if you inject headers.
- Consider separate subdomains if you later split public/private surfaces.

## 5) Test

- Public landing: `https://nas.xplab.io/`
- Private: `https://nas.xplab.io/portal/` (should require DSM auth/IP allowlist)
- Badges: confirm Tailscale/Cloudflare/NAS entities exist in HA or adjust IDs in `_assets/portal.config.json`.
