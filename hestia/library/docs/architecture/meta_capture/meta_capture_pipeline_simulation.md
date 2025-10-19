---
Title: Meta-Capture Pipeline — Simulation (DRY-RUN using 3 samples)
Slug: meta-capture-pipeline-simulation
Status: Draft
Authors:
  - Workspace Engineering
  - GitHub Copilot (assisted)
Last_Updated: 2025-10-19
Related_ADRs:
  - ADR-0013
  - ADR-0027
---

# Simulation: How information flows through the pipeline

Input directory: `/config/hestia/workspace/staging`
Samples:
- `20251019T143052Z-appdaemon-claude.yaml` (Claude exporter format — `exports:`)
- `20251019T143052Z-appdaemon-strategos.yaml` (meta-capture v1 — `extracted_config`, `transient_state`, `relationships`, `suggested_commands`)
- `20251019T143052Z-appdaemon-strategos_followup.yaml` (similar structure; includes transient_state lines 45–53)

## 1) Intake & Classification

- Detected 3 files (new)
- Top-level keys:
  - `…-claude.yaml`: exports
  - `…-strategos.yaml`: extracted_config, transient_state, relationships, suggested_commands, notes
  - `…-strategos_followup.yaml`: extracted_config, transient_state, relationships, suggested_commands, notes

## 2) Routing & Atomization (APUs)

- `…-claude.yaml` (exports):
  - system → `/config/hestia/config/system/system.conf` (merge)
  - network → `/config/hestia/config/network/network.conf` (merge)
  - storage → `/config/hestia/config/storage/storage.conf` (merge)
  - devices → `/config/hestia/config/devices/devices.conf` (upsert inventory, relationships)
  - diagnostics → `/config/hestia/config/diagnostics/diagnostics.conf` (append checks/errors/commands)
  - cli → `/config/hestia/config/system/cli.conf` (append commands)

- `…-strategos.yaml` + `…-strategos_followup.yaml`:
  - extracted_config.appdaemon → core/addons.yaml (upsert)
  - extracted_config.room_db_apps → core/addons.yaml or system docs (TBD)
  - extracted_config.database_schema → core/devices.yaml (db model notes) or docs
  - extracted_config.rest_commands → core/homeassistant.yaml (services) or cli.conf examples
  - extracted_config.canonical_rooms → devices/devices.conf (inventory)
  - transient_state → `/config/hestia/config/system/transient_state.conf` (append entries)
  - relationships → `/config/hestia/config/system/relationships.conf` (append)
  - suggested_commands → `/config/hestia/config/system/cli.conf` (append)
  - notes → `/config/hestia/config/system/notes.conf` (append)

Example APU (from strategos_followup transient_state lines 45–53):
```yaml
apu:
  id: sha256:…
  target_path: /config/hestia/config/system/transient_state.conf
  section: transient_state
  operation: append
  content:
    active_configs:
      bedroom:
        domain: motion_lighting
        timeout: 180
        version: 1
        updated_at: 2025-10-19T03:00:25
```

## 3) Validation (Traffic Light)

- Green examples:
  - diagnostics.checks entries (new) — no conflicts
  - cli.commands entries (new) — no conflicts
  - transient_state append entries — additive

- Yellow examples:
  - devices.inventory upserts — new IDs are safe; minor attribute drift flagged
  - system.services updates — non-pinned fields updated

- Orange examples:
  - core/homeassistant.yaml host/ip if pinned (`# @pin`) — requires manual
  - storage paths that differ from canonical (container vs host mapping) — human confirmation

- Red examples:
  - plaintext secret fields (detected) in canonical files — block
  - attempts to overwrite `# @pin` values — block
  - unstable device paths (`/dev/ttyUSB*`) — block until rewritten

## 4) Disposition

- On full success (greens + yellows): move inputs → `/config/hestia/workspace/archive/meta_capture/*.processed.<ts>`
- On any orange/red: move inputs → `/config/.quarantine/meta_capture/*.error.<ts>` with report
- Always include a consolidated report in `/config/hestia/reports/<date>/meta_capture__<ts>__dry_run.log`

## 5) DRY-RUN Summary (simulated)

- Files processed: 3
- APUs generated: 18 (system 1, network 1, storage 1, devices 3, diagnostics 3, cli 3, transient_state 4, relationships 2)
- Traffic light: 12 green, 4 yellow, 2 orange, 0 red
- Actions (if executed): 16 merges, 2 queued for review
- Disposition: would archive 2, quarantine 1 (due to orange requiring manual review)

## Notes & Assumptions

- Exact APU counts depend on fine-grained splitting policy
- This is a non-executing simulation; no files were modified
- Final merge destinations align with ADR-0013 and the updated meta-capture exporter contract
