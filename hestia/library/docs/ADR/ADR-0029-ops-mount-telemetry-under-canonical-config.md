---
id: ADR-0029
slug: ops-mount-telemetry-under-canonical-config
title: Operational Mount & Telemetry under Canonical /config
status: Accepted
created: 2025-10-20
author: "e-app-404"
context: production
amends:
  - ADR-0024
last_updated: 2025-10-20
decision: "Operationalize ADR-0024 on macOS using synthetic mapping, LaunchAgent mounts, Keychain-backed SMB auth, and local-only mount telemetry."
date: 2025-10-20
related:
  - ADR-0024
last_updated: 2025-10-22

# 1) Decision

Operationalize ADR-0024 on macOS using:
- APFS synthetic mapping so `/config` resolves to `/System/Volumes/Data/homeassistant`.
- User-level LaunchAgent to mount the HA Samba `config` share to the Data path.
- Keychain-backed, non-interactive SMB authentication (hostname **and** IP entries; trusted apps).
- Local-only mount telemetry with a strict, minimal schema.
All tools, scripts, docs, and automation **MUST** reference `/config` exclusively.

# 2) Rationale

Separates policy (ADR-0024) from runbook. Removes legacy path drift, ensures deterministic mounting, and provides binary health signals without leaking secrets.

# 3) Scope

Covers macOS operator host behavior, logging/telemetry, and integration points with CI and HA runtime that depend on the canonical path. Does not alter HA network/export settings.

# 4) Normative Rules

**Canonical Interface**
1. `/config` is the sole public interface path (see ADR-0024). No `$HOME`, `~/hass`, `/Volumes/...`, `/n/ha`, or actions-runner paths in code/docs.

**Mount Target**
2. The only mount target is `/System/Volumes/Data/homeassistant` (the "Data path"). `/config` must not be used as a mountpoint.

**SMB & Auth**
3. Credentials MUST exist in Keychain for both `homeassistant.local` and the active IP (e.g., `192.168.0.129`), protocol `smb`.
4. Trusted applications MUST include:
   - `/sbin/mount_smbfs`
   - `/usr/bin/smbutil`
   - `/System/Library/CoreServices/NetAuthAgent.app/Contents/MacOS/NetAuthAgent`
   - `/System/Applications/Utilities/Terminal.app/Contents/MacOS/Terminal`
5. Mounts MUST be non-interactive. If a prompt appears, the Keychain is out of policy and MUST be remediated.

**LaunchAgent**
6. Runs as the user, with `KeepAlive.NetworkState=true`, `StartInterval=60`, and logs to `~/Library/Logs/Hestia`.
7. The agent MUST mount onto the Data path and **never** onto `/config`.
8. The agent MUST implement bounded retry/backoff and safe unmount on logout/shutdown.

**Permissions & Modes**
9. Present file/dir modes via client options: files `0644`, dirs `0755`. The mountpoint directory owner MUST be `${USER}:staff`.

**Spotlight & Watchers**
10. Spotlight indexing MUST be disabled on the Data path mount to avoid churn.
11. Editor/file-watcher limits SHOULD be tuned to avoid polling overload on SMB volumes.

**Telemetry**
12. Telemetry is local-only, JSON lines, no secrets. Schema defined in §7. Retention ≤ 30 days or 50 MB, whichever first.

**Compliance**
13. Guard scripts MUST pass in RO/RW contexts; CI MUST set `REQUIRE_CONFIG_WRITABLE=0` for read-only jobs.
14. Linter MUST reject: `\$HOME/`, `~/hass`, `/Volumes/`, `/n/ha`, `actions-runner/.+?/hass`; with exclusions for `ADR/deprecated/**` and `library/docs/ADR-imports/**`.

# 5) Implementation Summary (Authoritative)

- `/etc/synthetic.conf` contains: `config\thomeassistant`.
- Data path exists: `/System/Volumes/Data/homeassistant`, owned by `${USER}:staff`.
- LaunchAgent `com.hestia.mount.homeassistant.plist` executes `~/bin/ha-mount.sh`.
- `ha-mount.sh` mounts `//${USER}@<host-or-ip>/config` to the Data path using Keychain (no prompts), applies modes, disables Spotlight, emits telemetry.
- Health tools: `bin/require-config-root`, `bin/config-health`, `tools/lint_paths.sh`.

# 6) Validation (Binary)

Must pass:
- `stat -f '%HT' /config` → directory or symlink resolving to Data path.
- `python3 -c 'import os;print(os.path.realpath("/config"))'` → `/System/Volumes/Data/homeassistant`.
- `mount | grep ' /System/Volumes/Data/homeassistant .*smbfs'` → exactly one mount active.
- `REQUIRE_CONFIG_WRITABLE=0 bin/require-config-root` → exit 0.
- `tools/lint_paths.sh` → no findings.
- Telemetry file updated on each (re)mount with schema in §7.

# 7) Telemetry Schema (Local-only)

```json
{
  "ts": "RFC3339",
  "host": "macbook",
  "iface": "/config",
  "realpath": "/System/Volumes/Data/homeassistant",
  "mounted": true,
  "mount_fs": "smbfs",
  "mount_src": "//evertappels@homeassistant.local/config",
  "ip": "192.168.0.129",
  "write_ok": true,
  "agent_loaded": true,
  "agent_pid": 12345,
  "agent_exit_code": 0,
  "last_error": "",
  "keychain_host_entry": true,
  "keychain_ip_entry": true
}
```

Retention policy: rotate daily, keep ≤ 30 days or ≤ 50 MB total.

# 8) Migration

* **Supersede ADR-0022**. Move to `ADR/deprecated/` with `status: Superseded` and `superseded_by: ADR-0029`.
* Replace any `ha_mount_*` scripts from ADR-0022 with `~/bin/ha-mount.sh`.
* Re-issue Keychain entries for both hostname and IP, with trusted apps (§4).

# 9) Risks & Mitigations

* **Host/IP drift** → maintain both Keychain entries; agent retries on DNS failure.
* **Interactive prompts** → Keychain trust missing; remediate entries or reset and re-add.
* **Editor watcher load** → disable Spotlight; constrain watcher settings for SMB paths.
* **Stale mounts** → agent unmounts on logout/shutdown; health check alerts in logs.

# 10) Backout

Temporary allowance: `/homeassistant -> /config` symlink may be enabled to maintain continuity during incident response. Policy remains `/config` (ADR-0024).

## Assumptions

* macOS operator host runs current macOS with LaunchAgents supported in `~/Library/LaunchAgents`.
* The Samba add-on on Home Assistant exposes the `config` share and authenticates with username/password stored in macOS Keychain (entries for both `homeassistant.local` and its current IP).
* `/config` resolves to `/System/Volumes/Data/homeassistant` via synthetic mapping; `/config` must be treated as the only public interface path.
* CI can operate in read-only mode when `REQUIRE_CONFIG_WRITABLE=0`.

## Touchpoints Checklist

* macOS filesystem interface (`/config` synthetic → Data path).
* SMB mount policy (hostname/IP, non-interactive auth, permissions modes).
* LaunchAgent (user scope, retry/backoff, sleep/wake/network awareness, logging).
* Keychain governance (creation, rotation, auto-trust for required binaries).
* Telemetry & logs (schema, retention, location).
* Guards, linters, fixers (RO/RW, exclusions for ADR imports).
* Home Assistant references (`shell_command`, backups, recorder paths) pinned to `/config`.
* VS Code/devcontainer/compose/CI mounting to `/config`.
* Spotlight & watcher behavior on network share.
* Backout and recovery procedures.
