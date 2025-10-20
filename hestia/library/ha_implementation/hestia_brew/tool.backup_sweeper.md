---
id: HESTIA-TOOL-BACKUP-SWEEPER
title: "backup_sweeper — Workspace cleanup pipeline (index, naming, lifecycle, vault, report)"
version: "1.0.0"
created: "2025-10-20"
adrs: ["ADR-0018", "ADR-0024", "ADR-0027", "ADR-0008"]
artifact_kind: tool
entrypoint: "/config/hestia/tools/backup_sweeper.py"
reports_dir: "/config/hestia/reports"  # pipeline-level report index per existing docs
config_file: "/config/hestia/config/system/hestia.toml → [automation.sweeper]"
---

# backup_sweeper — operator guide

## What it does
- Orchestrates a 5-component cleanup pipeline to enforce workspace hygiene and retention:
  1) index.py — discover files and classify by patterns
  2) naming_convention.py — enforce naming rules and standardize
  3) sweeper.py — apply TTL and lifecycle deletions/moves
  4) vault_warden.py — prune vault artifacts by group/keep-N policy
  5) sweeper_report.py — emit comprehensive report and health score
- Produces structured reports and updates a reports index for monitoring.

## When to use it
- Routine workspace maintenance (scheduled or ad-hoc).
- Before backups or releases to minimize bloat and enforce naming.
- To monitor workspace health (health score in the reports index).

## Execution modes
- Full pipeline:
  - `python /config/hestia/tools/backup_sweeper.py` (execute)
  - `python /config/hestia/tools/backup_sweeper.py --dry-run` (preview)
  - `python /config/hestia/tools/backup_sweeper.py --validate-only` (validate config)
- Component-level (examples):
  - `python /config/hestia/tools/sweeper/index.py --help`
  - `python /config/hestia/tools/sweeper/naming_convention.py --help`
  - `python /config/hestia/tools/sweeper/sweeper.py --help`
  - `python /config/hestia/tools/sweeper/vault_warden.py --help`
  - `python /config/hestia/tools/sweeper/sweeper_report.py --help`

## Configuration (TOML)
Location: `/config/hestia/config/system/hestia.toml`

```toml
# Launcher script path used by wrappers
sweeper_script = "/config/hestia/tools/backup_sweeper.py"

[automation.sweeper]
# primary switches
apply = true              # controlled by CLI flags at runtime
index_root = "/config"   # scan root (honor ADR-0024)

[automation.sweeper.performance]
max_workers = 4
batch_size = 500

[automation.sweeper.components]
naming_standardizer = "naming_convention.py"
vault_manager = "vault_warden.py"
report_generator = "sweeper_report.py"

[automation.sweeper.naming_rules]
# Add glob->rename rules here (example)
# "**/*.bk.*": "retain"
```

Notes
- Use `/config`-absolute paths only (ADR-0024). Avoid `/Volumes` or host aliases.
- Reports index is maintained under `/config/hestia/reports/_index.jsonl` per current tooling docs.

## Paths & artifacts
- Reports index: `/config/hestia/reports/_index.jsonl`
- Recent reports: `/config/hestia/reports/<YYYY-MM-DD>/*` (tool-specific logs in files)
- Component logs may write to tool-local locations depending on CLI flags.

## How to run (quick)
- Full pipeline: `python /config/hestia/tools/backup_sweeper.py`
- Dry-run: `python /config/hestia/tools/backup_sweeper.py --dry-run`
- Validate-only: `python /config/hestia/tools/backup_sweeper.py --validate-only`

## Evidence & governance
- Adheres to ADR-0018 (workspace lifecycle) and ADR-0027 (file writing governance).
- Deterministic, structured outputs (JSON/JSONL). Maintains historical health scoring.
- Honors ADR-0024 path rules; CLI and scripts should not reference non-canonical mounts.

## Troubleshooting
- No report generated: check Python errors and permissions; run with `--dry-run` to isolate.
- Health score missing: test `cat /config/hestia/reports/_index.jsonl | jq -s '.[-1]'`.
- Component errors: run individual components with `--help` for usage; inspect their outputs.

## Change control
- Update TOML stanza and re-run. For component overrides, adjust `[automation.sweeper.components]`.
- Use VCS to track config evolution.
