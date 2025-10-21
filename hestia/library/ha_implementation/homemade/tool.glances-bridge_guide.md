---
id: DOCS-GLANCES-BRIDGE-001
title: "glances_bridge — Glances normalizer & optional Tailscale proxy"
slug: glances-bridge-guide
version: 1.0
author: "e-app-404"
created: 2025-10-20
adrs: ["ADR-0031", "ADR-0024", "ADR-0027", "ADR-0008"]
content_type: manual
last_updated: 2025-10-21
installation: hestia/tools/glances_bridge
entrypoint: "/config/hestia/tools/glances_bridge/glances_bridge.py"
- reports_dir: "/config/hestia/workspace/reports/glances_bridge"
- logs_dir: "/config/hestia/workspace/operations/logs/glances_bridge"
ledger: /config/hestia/workspace/.hestia/index/glances_bridge__index.jsonl
configuration: "/config/hestia/config/system/hestia.toml"
---

# glances_bridge — operator guide

## What it does
- Probes a Glances instance and installs a small HTTP normalizer that proxies the Glances API.
- Normalizes disk I/O payloads by injecting `time_since_update` where missing for:
  - GET `/api/4/all` (diskio in object) → adds `time_since_update` to each disk entry
  - GET `/api/4/diskio` (list shape) → adds `time_since_update` to each item
- Optionally exposes the normalizer via Tailscale `serve tcp` (if enabled).
- Emits evidence (JSON reports + JSONL ledger) and prunes them per retention policy.

## When to use it
- Glances is running locally but returns disk I/O payloads that break downstream consumers due to missing `time_since_update`.
- You need a safe, idempotent operator tool that can be `dry-run` checked, audited, and rolled forward without side-effects.
- You want optional remote access using Tailscale TCP forwarding without modifying Glances itself.

## Execution modes

### `dry-run` mode
  - Probes upstream, samples responses, previews normalization counts.
  - Writes a report and ledger entry (no file writes or service changes).
  - Exit code: 0 on success; 2 when upstream is unreachable or validation fails.

### `apply` mode
  - Writes/updates the normalizer script under `<repo_root>/bin/glances-normalize.py` using atomic or brokered writes.
  - Starts the normalizer process and optionally configures Tailscale TCP mapping.
  - Idempotent: skips install if content SHA matches previous or on-disk version.
  - Exit code: 0 on success; 3 on failure to install/start.

## Configuration (TOML)
Location: `/config/hestia/config/system/hestia.toml`

```toml
[automation.glances_bridge]
repo_root    = "/config"
config_root  = "/config/hestia/config"
allowed_root = "/config/hestia"
report_dir   = "/config/hestia/workspace/reports/glances_bridge"
index_dir    = "/config/hestia/workspace/.hestia/index"

[automation.glances_bridge.runtime]
upstream_url    = "http://127.0.0.1:61208"  # Glances API base URL
listen_host     = "127.0.0.1"               # Normalizer bind host
normalizer_port = 61209                      # Normalizer bind port
tailscale_host  = ""                         # Optional hostname for context only
tailscale_port  = 61208                      # Exposed TCP port (tailscale serve)

[automation.glances_bridge.apply]
use_write_broker = false                     # true → use write-broker for file writes
write_broker_cmd = "/config/bin/write-broker"
write_broker_mode= ""                        # e.g. "replace" or "rewrite"

[automation.glances_bridge.retention]
reports_days = 14
ledger_lines = 20000
```

Notes
- `use_write_broker=false` by default (atomic write used). Enable to route writes via broker (ADR-0027).
- Reports path is under `workspace/reports/glances_bridge` (ADR-0031 evidence pattern). Runtime logs stay under `operations/logs/glances_bridge`.

## Paths & artifacts
- Reports: `/config/hestia/workspace/reports/glances_bridge/*__{dry_run|apply}.json`
- Ops logs: `/config/hestia/workspace/operations/logs/glances_bridge/*.out|*.err`
- Ledger: `/config/hestia/workspace/.hestia/index/glances_bridge__index.jsonl`
- Installed script: `<repo_root>/bin/glances-normalize.py` (default repo_root `/config`)

## How to run
- Using configured CLI entries (see `config/system/cli.conf`):
  - Dry-run: `/config/.venv/bin/python /config/hestia/tools/glances_bridge/glances_bridge.py dry-run`
  - Apply:   `/config/.venv/bin/python /config/hestia/tools/glances_bridge/glances_bridge.py apply`

## Behavior details
- The embedded normalizer is a tiny HTTP proxy that forwards all requests to `runtime.upstream_url` and rewrites only the disk I/O payloads:
  - Adds `time_since_update: 1.0` when the key is not present.
  - Leaves all other endpoints and fields untouched.
- Listen host/port are configurable via TOML; the process is started detached and health-checked via a TCP connect to 127.0.0.1:`normalizer_port`.

## Tailscale integration (optional)
- If `tailscale` CLI is available and `runtime.tailscale_host` is non-empty:
  - `tailscale serve reset`
  - `tailscale serve tcp <tailscale_port> 127.0.0.1:<normalizer_port>`
- No changes if `tailscale_host` is empty or CLI is missing.

## Evidence & retention
- Each run writes a timestamped JSON report and appends a JSONL entry to the ledger.
- Retention:
  - Reports older than `retention.reports_days` are deleted.
  - Ledger is truncated to the last `retention.ledger_lines` entries.

## Safety & governance
- Paths follow ADR-0024 (single canonical mount: `/config`).
- Writes use atomic replace; optional `write-broker` integration follows ADR-0027.
- Idempotency:
  - Content SHA is compared against last applied (ledger) and on-disk file before writing.
  - Apply mode uses a run-lock to prevent concurrent installs.

## Troubleshooting
- Upstream probe fails (dry-run exit 2): Ensure Glances is running and reachable at `runtime.upstream_url`.
- Port not listening after apply: Check ops logs in `operations/logs/glances_bridge/` and verify `normalizer_port` is free.
- Tailscale not configured: Set `runtime.tailscale_host` and ensure `tailscale` CLI is installed.
- Reports/ledger missing: Verify directory permissions and TOML `report_dir`/`index_dir` values.
- Broker errors: If `use_write_broker=true`, confirm `write_broker_cmd` exists and `write_broker_mode` is valid.

## Change control
- Update TOML under `[automation.glances_bridge]` then re-run `apply`.
- To revert a bad install, re-run `apply` after correcting config or disable the tool.
