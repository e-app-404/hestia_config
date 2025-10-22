---
id: ADR-0014
title: OOM Mitigation & Recorder Policy
slug: oom-mitigation-recorder-policy
status: Accepted
related: []
last_updated: '2025-10-22'
date: 2025-09-18
decision: Adopt a **single, canonical recorder configuration** with short retention
  and strict excludes, enforce **OOM sentinel**, and implement **repo-level guardrails**
  to make the policy machine-checkable.
version: v2 (canonical-path + guardrails)
tags:
- performance
- memory
- oom
- recorder
- database
- policy
- automation
- guardrails
- ci
- hestia
- configuration
- sql
references:
- .github/workflows/ha-governance.yml
author: Strategos (governance)
---

# ADR-0014: Recorder Policy, OOM Guard & Repo Guardrails (v2)

## Context

- Repeated OOM kills of the Home Assistant python process under memory pressure.
- Excessive recorder churn dominated by high-frequency sensors (time/date/device_time/signal_strength/etc.).
- Duplicate top-level `recorder:` definitions previously existed in the workspace, producing ambiguous effective config.
- Need for **idempotent**, **programmatically enforced** repo sanity and integration configuration.

## Decision

Adopt a **single, canonical recorder configuration** with short retention and strict excludes, enforce **OOM sentinel**, and implement **repo-level guardrails** to make the policy machine-checkable.

## Scope

- Workspace repository only (configuration-as-code); runtime host actions are covered by a separate operational runbook/delta contract.

## Canonical Paths & Tokens

- **Canonical recorder path:** `packages/integrations/recorder.yaml`
- **Documentation-only mirror:** `packages/recorder_policy.yaml` (commented out; no active config)
- **Guardrails path:** `hestia/tools/guardrails/`
- **ADR ID:** `ADR-0014.v2`
- **Enforcement tokens:** `single_recorder`, `idempotent_includes`, `no_dup_keys`, `oom_guard_present`, `no_symlinks`, `unique_automation_ids`, `unique_unique_ids`, `config_syntax_ok`
- **Artifact paths (CI):** `.github/workflows/ha-governance.yml`, `hestia/tools/guardrails/*`

## Invariants (Machine‑checkable)

1. **Single recorder:** Exactly one top-level `recorder:` exists across HA-loaded trees and it resides at `packages/integrations/recorder.yaml`.
2. **Idempotent packages:** No duplicate YAML keys; helpers/sensors/automations use unique identifiers; no symlinks under HA-loaded trees.
3. **Config is syntactically valid:** Containerized `check_config` passes for the repo.
4. **OOM guard present:** OOM notice automation and threshold helper exist (unique IDs) without creating duplicates.

## Programmatic Enforcement (CI)

- **Workflow:** `.github/workflows/ha-governance.yml`
- **Checks:**

  - `hestia/tools/guardrails/check_recorder_uniqueness.sh` — count=1 and at canonical path.
  - `hestia/tools/guardrails/check_duplicate_keys.py` — deny duplicate YAML keys.
  - `hestia/tools/guardrails/check_no_symlinks.sh` — deny symlinks in HA-loaded trees.
  - `hestia/tools/guardrails/check_unique_automation_ids.py` — unique automation `id:` across repo.
  - `hestia/tools/guardrails/check_unique_unique_ids.py` — unique `unique_id` across repo.
  - `hestia/tools/guardrails/validate_config.sh --syntax-only` — YAML parse sanity.
  - **Containerized HA**: `python -m homeassistant --script check_config -c /config` via the Home Assistant stable container with repo mounted at `/config`.

## Operational Policy (Effective YAML)

_This YAML **lives only** at `packages/integrations/recorder.yaml`._

```yaml
recorder:
  purge_keep_days: 7
  auto_purge: true
  commit_interval: 30
  exclude:
    domains:
      - automation
      - camera
      - event
      - group
      - logbook
      - media_player
      - persistent_notification
      - recorder
      - update
      - updater
      - zone
    event_types:
      - call_service # keep 'automation_triggered' (DO NOT exclude)
    entity_globs:
      - sensor.sun*
      - sensor.time*
      - sensor.date*
      - sensor.*_uptime*
      - sensor.*_entity_list
      - sensor.*failover_summary
      - sensor.*_minutes_since_*
      - sensor.*_device_time*
      - sensor.*_signal_strength*
      - sensor.*_rssi*
      - sensor.*_memory*
      - sensor.*_swap*
      - sensor.*_load_*
      - weather.*
      - binary_sensor.*day
    entities:
      - sensor.current_date_natural
      - sensor.current_date_description
      - sensor.current_time_legacy
      - sensor.current_time
      - sensor.schedule_status
      - sensor.disabled_device_entities
      - group.unavailable_entities
      - group.smartthings_entities
      - input_text.plex_tv_index
      - input_text.plex_movie_index
      - input_number.plex_tv_episode_count
      - input_number.plex_movie_count
      # Migrated from HACS Variable (var.*) to native HA helpers 2025-10-10
  include:
    domains:
      - binary_sensor
      - sensor
      - switch
      - light
```

## Runbook (Post‑merge, Host Execution — summarized)

1. **Preflight:** Confirm CI green; snapshot `/config/home-assistant_v2.db` and `/config/.storage/core.entity_registry` to `/tmp`, compress.
2. **Recorder purge:** Call `recorder.purge` with `keep_days: 7`; monitor HA logs.
3. **Observe churn for 24h:** Capture top entities and domain counts via SQL on a DB copy (joins with `states_meta`).
4. **Compact:** Stop core, `VACUUM` the DB, restart core.
5. **OOM sentinel test:** Temporarily lower threshold by 1% and wait ≤6 min for persistent notification; restore.
6. **Evidence bundle:** Save SQL outputs, HA check logs, DB sizes and deltas into `evidence/recorder/`.

## Acceptance Criteria (Binary)

- **AC-REC-01:** `check_recorder_uniqueness.sh` exits 0 and finds the block at `packages/integrations/recorder.yaml`.
- **AC-REC-02:** Duplicate-key scan and YAML lint exit 0.
- **AC-REC-03:** No symlinks in HA-loaded trees.
- **AC-REC-04:** Unique automation `id:` and unique `unique_id` across repo.
- **AC-REC-05:** Containerized `check_config` exits 0.
- **AC-OPS-01:** In 24h post-change, total new `states` rows ≤ target and top-entity counts drop (thresholds defined in the delta contract).
- **AC-OPS-02:** Post‑VACUUM DB size reduced by ≥25% vs. pre‑VACUUM snapshot (after churn stabilizes).
- **AC-OPS-03:** OOM sentinel fires during controlled test and auto-clears when below threshold.

## Drivers

- HA stability; avoid memory exhaustion and unclean shutdowns.
- Deterministic, reviewable configuration with guardrails preventing drift.

## Considered Alternatives

- Immediate migration to MariaDB (deferred until config sanity is enforced).
- Rely solely on excludes without includes (rejected; reduces control and clarity).

## Consequences

- Shorter historical retention window (7 days) in exchange for stability.
- CI will intentionally block PRs that add duplicate recorder blocks or non-idempotent content.

## Rollback Strategy

- Revert the last change set in git to restore previous recorder policy.
- Restore `/config/home-assistant_v2.db.copy` backup if necessary and restart core.

## Notes

- Keep OOM guard in `packages/package_oom_guard.yaml` with unique IDs; guard CI ensures no duplicates are introduced.
- The documentation mirror at `packages/recorder_policy.yaml` remains fully commented to avoid duplicate keys.

## Token Blocks

```yaml
TOKEN_BLOCK:
  accepted:
    - RECORDER_SINGLE_BLOCK_OK
    - OOM_SENTINEL_PRESENT
    - YAML_SYNTAX_OK
  requires:
    - ADR_SCHEMA_V1
  drift:
    - DRIFT: duplicate_recorder_blocks
    - DRIFT: oom_guard_missing
    - DRIFT: yaml_syntax_error
```
