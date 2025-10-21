---
id: DOCS-GLANCES-BRIDGE-002
title: "glances_bridge — Glances normalizer & optional Tailscale proxy"
slug: glances-bridge-readme
version: 1.0
author: "e-app-404"
created: 2025-10-20
adrs: ["ADR-0024", "ADR-0027", "ADR-0031"]
content_type: readme
last_updated: 2025-10-21
hot_links:
- reports: /config/hestia/workspace/reports/glances_bridge/
- reports: /config/hestia/workspace/.hestia/index/glances_bridge__index.jsonl
- process_logs: /config/hestia/workspace/operations/logs/glances_bridge/
---

# glances_bridge — ADR-0031-Compliant Glances Normalizer & Tailscale Proxy

## Overview

`glances_bridge.py` is a TOML-driven, idempotent tool for normalizing Glances API output and optionally exposing it via Tailscale TCP forwarding. It is designed for safe, evidence-rich automation in Home Assistant environments, following ADR-0031 doctrine.

- **Config:** Reads from `/config/hestia/config/system/hestia.toml` under `[automation.glances_bridge]`.
- **Modes:**
  - `dry-run`: Probes upstream, simulates normalization, emits a mode-suffixed report and ledger entry (no writes).
  - `apply`: Installs/updates the normalizer script, starts the service, configures Tailscale (if enabled), emits report and ledger.
- **Reports:** Written to `/config/hestia/workspace/reports/glances_bridge/` as `*__dry_run.json` or `*__apply.json`.
- **Ledger:** Append-only JSONL at `/config/hestia/workspace/.hestia/index/glances_bridge__index.jsonl`.
- **Retention:** Prunes old reports and trims ledger per TOML settings.

## Usage

### Dry-run

```bash
/config/.venv/bin/python /config/hestia/tools/glances_bridge/glances_bridge.py dry-run
```
- Probes Glances upstream (`runtime.upstream_url`), simulates normalization, writes a report and ledger entry.
- No changes made to the system.

### Apply

```bash
/config/.venv/bin/python /config/hestia/tools/glances_bridge/glances_bridge.py apply
```

- Installs/updates the normalizer script at `<repo_root>/bin/glances-normalize.py`.
- Starts the normalizer as a background process.
- Optionally configures Tailscale TCP forwarding if `runtime.tailscale_host` is set and `tailscale` CLI is available.
- Idempotent: skips install if content SHA matches last-applied or on-disk version.

## Configuration

Add this block to `/config/hestia/config/system/hestia.toml`:

```toml
[automation.glances_bridge]
repo_root    = "/config"
config_root  = "/config/hestia/config"
allowed_root = "/config/hestia"
report_dir   = "/config/hestia/workspace/reports/glances_bridge"
index_dir    = "/config/hestia/workspace/.hestia/index"

[automation.glances_bridge.runtime]
upstream_url    = "http://127.0.0.1:61208"
listen_host     = "127.0.0.1"
normalizer_port = 61209
tailscale_host  = "" # set to enable tailscale wiring
tailscale_port  = 61208

[automation.glances_bridge.apply]
use_write_broker = false
write_broker_cmd = "/config/bin/write-broker"
write_broker_mode= ""

[automation.glances_bridge.retention]
reports_days = 14
ledger_lines = 20000
```

## Troubleshooting
- **Upstream probe fails:** Ensure Glances is running and reachable at `runtime.upstream_url`.
- **Tailscale not configured:** Set `runtime.tailscale_host` and ensure `tailscale` CLI is installed if you want TCP forwarding.
- **Idempotency skips install:** If the script is unchanged, apply will skip re-install and mark the ledger with `skip_reason: idempotent`.
- **Reports/ledger not updating:** Check file permissions and retention settings in TOML.

## Evidence & Governance
- All actions are logged in the ledger and reports for auditability.
- Retention and atomic operations follow ADR-0024, ADR-0027, and ADR-0031.
- No secrets or vault URIs are ever written by this tool.

<!-- ADR-0031/0024 canonical section -->
## Canonical Paths & Evidence (ADR-0031 / ADR-0024)

- Reports: `/config/hestia/workspace/reports/glances_bridge/…`
- Ops logs: `/config/hestia/workspace/operations/logs/glances_bridge/…`
- Ledger (JSONL): `/config/hestia/workspace/.hestia/index/glances_bridge__index.jsonl`

Path compliance: No $HOME, ~/hass, /Volumes, /n/ha, or actions-runner paths in code or docs. Use /config only (ADR-0024). The repo path-linter enforces this policy.

Write broker: Default use_write_broker=false. Set to true to route file writes through the broker; ensure broker_cmd and mode are configured when enabled.

## Support
For config or runtime issues, see:
- Reports: `/config/hestia/workspace/reports/glances_bridge/`
- `/config/hestia/workspace/.hestia/index/glances_bridge__index.jsonl`
- Process logs (normalizer stdout/err): `/config/hestia/workspace/operations/logs/glances_bridge/`
