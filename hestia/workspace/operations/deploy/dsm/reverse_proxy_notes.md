Reverse Proxy UI instructions (DSM Control Panel)

These are step-by-step notes to configure the reverse proxy rules in DSM (Control Panel → Application Portal → Reverse Proxy / Advanced).

1) Portal: /portal
- Location: /portal
- Destination: http://127.0.0.1:80/portal
- Preserve Host: enabled
- WebSocket: enabled
- X-Forwarded-For / X-Forwarded-Proto: enabled
- Access Control: select "Require login" (DSM account) or configure "Allow from" specific DSM groups
- IP Allowlist: restrict to Tailnet CIDR 100.64.0.0/10 via firewall (if DSM UI supports CIDR allowlisting). If DSM doesn't support CIDR directly, use DSM group policies or a firewall rule.

2) Home Assistant: /ha
- Location: /ha
- Destination: http://192.168.0.129:8123
- Strip prefix: yes (so upstream sees /)
- Preserve Host: enabled
- WebSocket: enabled
- X-Forwarded-For / X-Forwarded-Proto: enabled
- No auth injection: leave authentication unchecked (HA handles auth)

3) Grafana: /grafana
- Location: /grafana
- Destination: http://<grafana-host>:3000
- Strip prefix: yes
- Preserve Host: enabled
- WebSocket: enabled
- X-Forwarded-For / X-Forwarded-Proto: enabled

Notes:
- Bind these reverse proxy rules to the Web Portal `nas.xplab.io` which must be configured under Web Station → Web Portal and use a valid TLS certificate.
- Enable HTTP/2 and HSTS in the Web Portal settings for improved security. Consider preload only if you control all subdomains and understand implications.

Screenshots: place under `hestia/deploy/dsm/screenshots/` after applying changes.
