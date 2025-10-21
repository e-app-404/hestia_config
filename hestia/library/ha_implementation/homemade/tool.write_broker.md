---
id: DOCS-WRITE-BROKER-001
title: "write-broker — governed, atomic file modifications"
created: 2025-10-20
version: 1.0.0
adrs: ["ADR-0027", "ADR-0024", "ADR-0008", "ADR-0009"]
content_type: manual
author: "e-app-404"
hot_links:
- entrypoint: "/config/bin/write-broker"
- logs_dir: "/config/hestia/workspace/operations/logs"
last_updated: 2025-10-21
---

# write-broker — operator guide

## What it does
- Provides a single, governed entrypoint for file modifications under `/config`.
- Enforces ADR-0027: validation → atomic replace → audit trail (logs).
- Supports replace/rewrite operations with search/replace or file swap semantics.

## When to use it
- Any automation or operator action that modifies tracked files under `/config`.
- Prefer over ad-hoc `sed`/`mv` to retain atomicity, backups, and audit logs.

## Commands
- replace
  - `write-broker replace --file <path> --search <old> --replace <new> [--commit] --msg <message>`
- rewrite
  - `write-broker rewrite --file <path> --from <temp_file> [--commit] --msg <message>`

Notes
- Use `--dry-run` first to preview changes without applying.
- `--commit` persists changes; omitting it leaves a preview.
- All operations are constrained to `/config` (ADR-0024 path policy).

## Audit & logs
- Audit JSON logs written under `/config/hestia/workspace/operations/logs/` (see ADR-0027 examples: `write_broker_*.json`).
- Include timestamp, operation, file path, checks, and result status.

## Safety & governance
- Validation: ensures path is within allowed root; content checks can be applied.
- Atomic ops: writes go to a temp file and replace via `os.replace()`.
- Audit trail: JSON logs support post-mortem and CI compliance checks.

## Examples
- Replace a token:
  - `write-broker replace --file /config/custom_templates/template.library.jinja --search '__TOKEN__' --replace 'value' --commit --msg 'Inject token'`
- Rewrite from a temp file:
  - `write-broker rewrite --file /config/custom_templates/template.library.jinja --from /tmp/new.jinja --commit --msg 'Update template (normalized)'`

## Troubleshooting
- Permission denied: ensure the path is under `/config` and writable.
- No audit log: verify logs directory exists; tool will create it if missing.
- Dry-run shows changes but not applied: add `--commit`.

## Change control
- Use VCS to track file changes; audit logs provide additional provenance.
