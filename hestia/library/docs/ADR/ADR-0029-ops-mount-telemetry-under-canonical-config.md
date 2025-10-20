---
id: ADR-0029
slug: ops-mount-telemetry-under-canonical-config
title: Operational Mount & Telemetry under Canonical /config
status: Accepted
created: 2025-10-20
amends:
  - ADR-0024
supersedes:
  - ADR-0022
---

# Decision
Implement ADR-0024 operationally on macOS via APFS synthetic `/config` → `/System/Volumes/Data/homeassistant`, user-level LaunchAgent, Keychain-backed non-interactive SMB mounts (hostname + IP entries), and local-only mount telemetry. All tools, scripts, and docs MUST reference `/config`.

# Rationale
Separates policy (ADR-0024) from operational implementation. Eliminates legacy path drift, ensures predictable mounting, and provides binary health signals.

# Normative Rules
- `/config` is the sole public interface (per ADR-0024).
- Mount target is `/System/Volumes/Data/homeassistant` only.
- Keychain entries MUST exist for `homeassistant.local` and active IP, with trusted apps: `/sbin/mount_smbfs`, `/usr/bin/smbutil`, NetAuthAgent, Terminal.
- LaunchAgent runs as user, logs to `~/Library/Logs/Hestia`.
- Telemetry is local-only; payload includes `realpath(/config)`, `mounted`, `write_ok`, `agent_loaded`, `agent_exit_code`; no secrets.

# Compliance & Validation
- Guard scripts pass in RO/RW contexts.
- Linter rejects `$HOME/`, `~/hass`, `/Volumes/`, `/n/ha`, `actions-runner/.+?/hass`, excluding `ADR/deprecated/**` and `library/docs/ADR-imports/**`.
- Binary health checks green on macOS, containers, and CI.

# Consequences
Removes ambiguity from ADR-0022; establishes a single operational reference.

# Backout
Re-enable transitional `/homeassistant -> /config` symlink only as a temporary measure; policy remains ADR-0024.
