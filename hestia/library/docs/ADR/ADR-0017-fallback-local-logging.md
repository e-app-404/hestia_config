---
id: ADR-0017
title: "Fallback local logging path for HA tooling (non-repo, cross-platform)"
slug: fallback-local-logging-path-for-ha-tooling-non-repo-cross-platform
status: "Proposed"
related:
- ADR-0008
- ADR-0009
- ADR-0024
- ADR-0026
supersedes: []
last_updated: '2025-10-22'
date: '2025-09-25'
decision: "When ${HA_MOUNT} is not writable, tooling writes to a platform-specific local path outside the repo with strict perms."
author: "e-app-404"
security_perms: "0700 (owner-only) on POSIX."
acceptance:
- Simulate mount-down; tooling writes to the OS path and creates it with correct perms.
- CI packaging proves logs are excluded from artifacts.
enforcement_protocols:
- validation_first_design
- hestia_config_protocols
- file_delivery_integrity_v2
- include_scan_v2
---

## ADR-0017 — Fallback local logging path for Home Assistant tooling (non-repo, cross-platform)

## Context

Per ADR-0024, the canonical Home Assistant config path is `/config` (single canonical mount). If `/config` is unavailable or not writable, tooling that writes logs or temporary operational files may be unable to persist data to the canonical location. This causes diagnostic gaps and impedes incident response. This ADR defines a platform-specific fallback path outside the repo to preserve diagnostic logs safely when `/config` is not writable.

## Decision

When the primary Home Assistant config mount (`/config`) is unavailable, tooling and scripts MUST write fallback logs to the operator's local directory:

`~/Library/Logs/Hestia`

This location is to be used only as a last-resort fallback when the canonical logging or config locations are unreachable.

## Rationale

- Local storage in the operator's home directory ensures logs survive network outages and are available for diagnostics.
- Using a consistent fallback path across tooling simplifies developer expectations and automation for collection.
- The path is operator-specific and reduces risk of accidentally placing logs on other systems.

## Consequences

- Scripts must detect mount readiness (e.g., verify `/config` is mounted and writable) before writing to canonical locations; otherwise they should write to the fallback path.
- The fallback path is not a replacement for central persistent logging; teams must still ensure logs are copied to central storage or attached to incident reports.
- Access control and rotation must be implemented for the fallback path if it is used in production for extended durations.

## Implementation

- Add helper `ensure_log_path()` used by scripts which:
  - verifies primary mount is writable; if not, ensures the fallback directory exists with 0700 permissions and returns its path.

- Update `ha_autofs_hardened.sh` (or successor) to write logs to `/var/log/ha_autofs_hardened.log` when possible, but fall back to the platform-specific path above if `/config` is unavailable or unwritable.

## Follow-ups

- Confirm canonical `root config` path once mounting issue is resolved and update ADR accordingly.
- Add retention/rotation policy for fallback logs in operations runbook.
- Review any tooling that currently writes to `/tmp` or other ephemeral locations and update to use `ensure_log_path()`.

## Token Blocks

```yaml
TOKEN_BLOCK:
  notes: fallback logging contract validation snippets
  checks:
    - name: mount-writability
      cmd: "test -w /config || echo 'mount not writable'"
    - name: macos-fallback-perms
      cmd: "EXPECTED=\"$HOME/Library/Logs/Hestia\"; mkdir -p \"$EXPECTED\"; chmod 700 \"$EXPECTED\"; test -d \"$EXPECTED\""
    - name: repo-guard-no-logs
      cmd: "! git ls-files | grep -E '/(logs|log)/'"
```
