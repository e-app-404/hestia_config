# Notes — session capture

- **SMB vs HTTP**: SMB mounts (TCP 445/139) work remotely via Tailscale without an explicit port; the HA web UI runs on TCP **8123** and requires the port unless you proxy 443→8123.
- **Tailscale**: MagicDNS is functioning; overlay IP `100.105.130.99` belongs to `homeassistant.reverse-beta.ts.net`. HTTP access to `:8123` from remote currently fails until HA binds to all interfaces.
- **Binding**: Add the `http:` block to `configuration.yaml` with `server_host: 0.0.0.0`, `trusted_proxies` covering Tailscale CGNAT `100.64.0.0/10` and LAN `192.168.0.0/16`, then restart Core.
- **OOM history**: Prior incidents were linked to unbounded echo workload; responder now has bounded inflight threads and optional rate limiting. Keep `enable_echo: false` by default.
- **Ops cadence**: For telemetry attestation (STP5), enable echo only during the window; collect receipts; then disable again.

## File map
- `config/hestia/core/state/transient_state.conf` — rolling runtime signals.
- `config/hestia/core/config/relationships.conf` — device/service graph.
- `config/hestia/core/ops/suggested_commands.conf` — repeatable commands.
- `config/hestia/core/notes/README.md` — human context.