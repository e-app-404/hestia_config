---
Title: Meta-Capture Processing Pipeline — Architecture Proposal
Slug: meta-capture-pipeline-architecture
Status: Draft
Authors:
  - Workspace Engineering
  - GitHub Copilot (assisted)
Last_Updated: 2025-10-19
Related_ADRs:
  - ADR-0013: Source→Core Config Merge via extracted_config (Meta-Capture Pipeline)
  - ADR-0008: Syntax-Aware Normalization & Determinism Rules
  - ADR-0018: Workspace lifecycle policy (backup sweeper compliance)
  - ADR-0024: Canonical config path (/config)
  - ADR-0027: File writing governance & write-broker
---

# Meta-Capture Processing Pipeline — Architecture Proposal

## Executive Summary

Design a modular, multi-modal tool (inspired by Sweeper and Lineage Guardian) that ingests meta-capture YAML documents from a staging area, validates and classifies content by top-level keys, splits them into atomic patch updates for the canonical config repo under `/config/hestia/config`, gates merges with a traffic-light validation system, and disposes of processed inputs safely. Periodic scheduler + ad-hoc CLI modes.

## Goals & Non-Goals

- Goals:
  - Config-driven intake (hestia.toml) and repeatable pipeline runs (cron + on-demand)
  - Deterministic routing and split into atomic updates (per ADR-0013)
  - Safety-first governance (ADR-0027): backups, atomic writes, audit logs
  - Human-centric UX: clear status, dry-run previews, review queues
- Non-Goals:
  - Direct service restarts/deployments (left to existing HA flows)
  - Replacing ADR-0013 domain merge scripts (we orchestrate them)

## High-Level Architecture

- Orchestrator CLI: `meta_capture.py` (planned: `/config/hestia/tools/meta_capture/meta_capture.py`)
- Components:
  1) Intake Scanner — discovers new files in `paths.workspace.staging` (hestia.toml)
  2) Schema Validator — enforces meta-capture schema (min: `extracted_config` OR `exports` OR `transient_state`)
  3) Classifier — identifies present top-level keys: `exports`, `extracted_config`, `transient_state`, `relationships`, `suggested_commands`, `notes`
  4) Router — maps sections to canonical target files (per ADR-0013 routing table + topics_index)
  5) Atomizer — splits into atomic patch units (per target file), with provenance metadata
  6) Validator — evaluates conflicts vs canonical data → traffic light (red/orange/yellow/green)
  7) Merger — applies green/yellow (with alert) via write-broker; queues orange/red for review
  8) Disposer — moves processed inputs to archive/quarantine per outcome
  9) Reporter — emits frontmatter+JSON logs and audits under `/config/hestia/reports/`

- Modes:
  - Periodic (cron) — reads schedule from hestia.toml
  - Ad-hoc (CLI) — `--dry-run`, `--validate-only`, `--since`, `--file path.yaml`, `--topics` filters

## Configuration (hestia.toml)

Add a new section:

```toml
[automation.meta_capture]
enabled = true
schedule_cron = "*/10 * * * *"  # every 10 minutes
intake_paths = ["/config/hestia/workspace/staging"]
quarantine_path = "/config/.quarantine/meta_capture"
archive_path = "/config/hestia/workspace/archive/meta_capture"
dry_run_default = true
verbose_logging = true

[automation.meta_capture.routing]
# ADR-0013 domain routing (core config files)
core_homeassistant = "/config/hestia/config/core/homeassistant.yaml"
core_mqtt = "/config/hestia/config/core/mqtt.yaml"
core_zigbee2mqtt = "/config/hestia/config/core/zigbee2mqtt.yaml"
core_addons = "/config/hestia/config/core/addons.yaml"
core_devices = "/config/hestia/config/core/devices.yaml"
core_repo = "/config/hestia/config/core/repo.yaml"
# Topics → path mapping (per updated meta-capture prompt)
system = "/config/hestia/config/system/system.conf"
storage = "/config/hestia/config/storage/storage.conf"
network = "/config/hestia/config/network/network.conf"
devices = "/config/hestia/config/devices/devices.conf"
diagnostics = "/config/hestia/config/diagnostics/diagnostics.conf"
preferences = "/config/hestia/config/preferences/preferences.conf"
cli = "/config/hestia/config/system/cli.conf"
transient_state = "/config/hestia/config/system/transient_state.conf"
relationships = "/config/hestia/config/system/relationships.conf"
suggested_commands = "/config/hestia/config/system/cli.conf"  # append section
notes = "/config/hestia/config/system/notes.conf"

[automation.meta_capture.validation]
conflict_policy = "traffic_light"
secret_detection = true
stable_paths_required = true
pin_guard = true

[automation.meta_capture.write]
use_write_broker = true
backup_before_modify = true
atomic_writes = true
```

## Data Contracts

- Intake file: YAML with any of the following top-level keys:
  - `exports` (Claude exporter format)
  - `extracted_config`, `transient_state`, `relationships`, `suggested_commands`, `notes`
- Atomic Patch Unit (APU):
  ```yaml
  apu:
    id: "<hash>"
    target_path: "<canonical file>"
    section: "<topic or domain>"
    operation: "append|merge|upsert|replace"
    content: <yaml-node>
    provenance:
      source_file: "/config/hestia/workspace/staging/…"
      x-origin.timestamp: "2025-10-19T14:30:52Z"
      x-origin.source: "meta-capture"
  ```

## Validation (Traffic Light)

- Green — auto-merge: no conflicts, schema-valid, no pins touched, no secrets, stable paths
- Yellow — auto-merge + alert: minor conflicts or new sections; low risk
- Orange — manual review: touches pinned keys, ambiguous merges, partial contradictions
- Red — block: contradicts canonical info, secrets leakage, unstable device paths, schema violation

Validation checks:
- Schema presence (for each top-level section)
- ADR-0013 routing rules compliance
- Secrets detection per ADR-0027
- Pin guard (`# @pin`) detection
- Stable device path rewrite opportunities (prefer `/dev/serial/by-id/...`)
- Duplicate keys and list keyed-upsert integrity (x-merge.key)

## Merge Strategy

- Use `/config/bin/write-broker` for all file updates
- Merge modes:
  - append: for logs/notes/transient_state entries
  - upsert: for maps/lists with `x-merge.key`
  - replace: only when flagged and safe
- Always create before/after diff + rollback bundle

## Disposition of Source Files

- On success (all APUs green/yellow): move to `archive_path` with suffix `.processed.{timestamp}`
- On partial success/failure: move to `quarantine_path` with suffix `.error.{timestamp}` and an error report
- Never re-ingest the same file (archive/quarantine scanning excluded)

## UX & Usability

- CLI flags: `--dry-run`, `--files`, `--topics`, `--since`, `--output-report`
- Human-readable summary + JSONL log entry per run
- Clear mapping of APUs → targets, with traffic-light badges
- Safety banners when yellow/orange/red present; suggested next steps

## Inspiration & Parallels

- Sweeper: orchestrator + modular components, shared log, ADR-0018 reporting
- Lineage Guardian: scanner/validator/corrector/report pattern, VSCode tasks, hestia.toml integration

## Acceptance Criteria

- DRY-RUN over the three provided samples produces:
  - Classified APUs with target paths
  - Traffic-light classification with reasons
  - A single consolidated report under `/config/hestia/reports/<date>/meta_capture__<ts>__dry_run.log`
- No file writes in DRY-RUN

## Open Questions

- Should `transient_state` be consolidated by timestamp as log entries or normalized by entity keys?
- How strict should we be on `exports` content schemas per topic?
- How to de-duplicate suggested_commands across sessions?
