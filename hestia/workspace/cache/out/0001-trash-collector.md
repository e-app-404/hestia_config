---
status: open
created_at: 2025-10-03T00:00:00Z
updated_at: 2025-10-03T00:00:00Z
author: copilot
agent: copilot
human_owner: __REPLACE_ME__
priority: medium
labels: [maintenance, housekeeping, config]
---

# Auto-sweep root `.trash/` folder (Trash Collector)

## Description

Introduce a configurable, safe auto-sweeper that removes or archives files in the repository root `.trash/` folder based on settings stored in `hestia/config/system/trash-collector.conf` (TBC). This reduces clutter, enforces retention policies, and provides auditable cleanup runs.

## Proposed change / patch

- Add a configuration template `hestia/config/system/trash-collector.conf.example` describing options (enabled, retention_days, dry_run, exclude_patterns, archive_path, run_interval_cron).
- Implement a small idempotent Python script `hestia/tools/trash_collector/collect_trash.py` that:
  - Reads config from `hestia/config/system/trash-collector.conf` (YAML or INI; example provided).
  - Supports `dry_run` mode that reports files that would be removed/archived.
  - Moves files older than `retention_days` to `archive_path` or deletes them when `archive_path` is null.
  - Emits structured JSON logs to `hestia/workspace/operations/logs/trash_collector/<UTC>__collect.json`.
  - Exposes an exit code: 0=ok, 1=warning (some files matched but not removed due to dry_run), 2=error.
- Add documentation `hestia/library/docs/operations/trash_collector.md` explaining setup, config fields, and failure modes.
- Add a lightweight GitHub Actions workflow `.github/workflows/trash-collector.yml` (optional) that runs the collector on schedule when enabled.

## Files changed

- Add: `hestia/config/system/trash-collector.conf.example`
- Add: `hestia/tools/trash_collector/collect_trash.py`
- Add: `hestia/library/docs/operations/trash_collector.md`
- Optional: `.github/workflows/trash-collector.yml`

## Test plan

- Unit tests for `collect_trash.py` validating `dry_run`, `archive_path`, `exclude_patterns`, and retention logic using temporary directories.
- Manual test: create test files in `.trash/` with varied timestamps and run `python hestia/tools/trash_collector/collect_trash.py --config hestia/config/system/trash-collector.conf.example --dry-run`.
- Validate logs are created in `hestia/workspace/operations/logs/trash_collector/` and that exit codes match expectations.

## Security / validation tokens

No validation tokens required for local runs. For automated runs that modify repository (archive or delete), require a short-lived validation token to allow non-interactive deletions (TBC in ADR).

## Notes / references

- Follow the workspace automation contract: always source `ha_path.sh` in scripts and use `$HESTIA_CONFIG`.
- This todo is intentionally conservative: default `dry_run: true` and `enabled: false` to avoid accidental deletions.

## Change log

- 2025-10-03: created by copilot
