---
id: ADR-0017
title: "ADR-0017: Fallback local logging path for HA tooling (non-repo, cross-platform)"
date: 2025-09-25
author: "Evert Appels"
status: Proposed
deciders: [platform, ops]
supersedes: []
amends: []
related: [ADR-0016, ADR-0008, ADR-0009]
decision:
  summary: "When ${HA_MOUNT} is not writable, tooling writes to an OS-specific local path outside the repo, with strict perms."
  precedence: "Logs MUST NOT be written under ${HA_MOUNT} or the repo root."
policy:
  macOS: "$HOME/Library/Logs/Hestia"
  linux: "${XDG_STATE_HOME:-$HOME/.local/state}/hestia/logs"
  windows: "%LOCALAPPDATA%\\Hestia\\Logs"
security:
  perms: "0700 (owner-only) on POSIX; private ACL on Windows"
acceptance:
  - "Simulate mount-down; tooling writes to the OS path and creates it with correct perms."
  - "CI packaging proves logs are excluded from artifacts."
enforcement_protocols: [validation_first_design, hestia_config_protocols, file_delivery_integrity_v2, include_scan_v2]
---

# ADR-0017 — Fallback local logging path for Home Assistant tooling (non-repo, cross-platform)

The ADR proposing `/Users/evertappels/Projects/HomeAssistant/logs` as a last-resort local log path has been created in `/tmp/adr_fallback_logpath.md`. Move or copy this file to your repository ADR directory (for example `docs/adr/`) when file access to the repo is available.

Commands to move into repo once mount is healthy:

sudo mkdir -p /n/ha/path/to/repo/docs/adr
sudo mv /tmp/adr_fallback_logpath.md /n/ha/path/to/repo/docs/adr/XXX-fallback-logpath.md

## Context

The Home Assistant configuration workspace is normally mounted from network storage (the NAS) at `/n/ha` or `/Volumes/ha`. In the event of network mount failures, automount placeholders (auto_smb) or lock issues, the tooling that writes logs or temporary operational files may be unable to persist data to the canonical config path. This causes diagnostic gaps and impedes incident response.

## Decision

When the primary Home Assistant config mount (the operator's `root config` mount) is unavailable, tooling and scripts MUST write fallback logs to the operator's local directory:

`/Users/evertappels/Projects/HomeAssistant/logs`

This location is to be used only as a last-resort fallback when the canonical logging or config locations are unreachable.

## Rationale

- Local storage in the operator's home directory ensures logs survive network outages and are available for diagnostics.
- Using a consistent fallback path across tooling simplifies developer expectations and automation for collection.
- The path is operator-specific and reduces risk of accidentally placing logs on other systems.

## Consequences

- Scripts must detect mount readiness (e.g., verify `/n/ha` or configured `root config` path is mounted and writable) before writing to canonical locations; otherwise they should write to the fallback path.
- The fallback path is not a replacement for central persistent logging; teams must still ensure logs are copied to central storage or attached to incident reports.
- Access control and rotation must be implemented for the fallback path if it is used in production for extended durations.

## Implementation

- Add helper `ensure_log_path()` used by scripts which:
  - verifies primary mount is writable; if not, ensures the fallback directory exists with 0700 permissions and returns its path.

- Update `ha_autofs_hardened.sh` to write logs to `/var/log/ha_autofs_hardened.log` when possible, but fall back to `/Users/evertappels/Projects/HomeAssistant/logs/ha_autofs_hardened.log` if the mount is unavailable or unwritable.

## Follow-ups

- Confirm canonical `root config` path once mounting issue is resolved and update ADR accordingly.
- Add retention/rotation policy for fallback logs in operations runbook.
- Review any tooling that currently writes to `/tmp` or other ephemeral locations and update to use `ensure_log_path()`.

## Token Blocks

```
# mount readiness probe (example)
test -w "${HA_MOUNT:-$HOME/hass}" || echo "mount not writable"

# fallback path chosen (macOS example)
EXPECTED="$HOME/Library/Logs/Hestia"
mkdir -p "$EXPECTED"; chmod 700 "$EXPECTED"
test -d "$EXPECTED" && test "$(stat -f %Op "$EXPECTED")" = "drwx------"

# guard: ensure repo contains no logs
git ls-files | grep -E '/(logs|log)/' && { echo "❌ logs in repo"; exit 1; } || :
echo "✅ no logs in repo"
```