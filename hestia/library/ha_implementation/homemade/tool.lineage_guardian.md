---
id: HESTIA-TOOL-LINEAGE-GUARDIAN
title: "lineage_guardian — Template lineage scanner, validator, and reporter"
version: "1.0.0"
created: "2025-10-20"
adrs: ["ADR-0009", "ADR-0020", "ADR-0024"]
artifact_kind: tool
entrypoint: "/config/hestia/tools/lineage_guardian/lineage_guardian_cli.py"
artifacts_dir: "/config/hestia/tools/lineage_guardian/.artifacts"
config_file: "/config/hestia/config/system/hestia.toml → [automation.lineage_guardian] (optional)"
---

# lineage_guardian — operator guide

## What it does
- Scans Jinja templates and related configuration to derive a dependency graph (lineage) across entities, sensors, and macros.
- Validates lineage invariants and detects structural issues (missing references, cycles, integrity errors).
- Produces machine-consumable artifacts (graph, violations, integrity, report) for review and CI automation.

## When to use it
- Before deploying template changes to catch broken references or cycles.
- During refactors to visualize deps and ensure invariants remain satisfied.
- As part of CI/commit hooks or manual preflight on large template edits.

## Pipeline components
- graph_scanner.py → builds a lineage graph from templates.
- lineage_validator.py → checks contract rules, emits violations.
- graph_integrity_checker.py → low-level graph integrity checks.
- lineage_corrector.py → generates an optional correction/plan directory.
- lineage_report.py → summarizes findings to a compact report.

## Execution modes (CLI)
- Full pipeline (wrapper):
  - `cd /config/hestia/tools/lineage_guardian && python lineage_guardian_cli.py --verbose`
- Individual components (examples):
  - Scanner: `python lineage_guardian/graph_scanner.py --output ./.artifacts/graph.json --template-dir /config/domain/templates/ --verbose`
  - Validator: `python lineage_guardian/lineage_validator.py --graph-file ./.artifacts/graph.json --output ./.artifacts/violations.json --verbose`
  - Corrector: `python lineage_guardian/lineage_corrector.py --violations-file ./.artifacts/violations.json --plan-dir ./.artifacts/_plan`
  - Integrity: `python lineage_guardian/graph_integrity_checker.py --graph-file ./.artifacts/graph.json --output ./.artifacts/integrity.json`
  - Report: `python lineage_guardian/lineage_report.py --graph ./.artifacts/graph.json --violations ./.artifacts/violations.json --integrity ./.artifacts/integrity.json --outdir ./.artifacts/report`

## Configuration
- Primary control via CLI flags (paths shown above).
- Optional TOML section: `[automation.lineage_guardian]` in `/config/hestia/config/system/hestia.toml` (if present) for defaults such as template directories and output locations.
- Use canonical paths only (`/config`); avoid host aliases (ADR-0024).

## Paths & artifacts
- Templates input: typically `/config/domain/templates/`.
- Artifacts output dir: `/config/hestia/tools/lineage_guardian/.artifacts/`.
  - graph.json — dependency graph
  - violations.json — rule violations
  - integrity.json — structural integrity summary
  - report/ — human-readable summary exports
  - _plan/ — optional correction plan

## How to run (quick)
- Wrapper: `cd /config/hestia/tools/lineage_guardian && python lineage_guardian_cli.py --verbose`
- After running, inspect `.artifacts/` outputs; iterate on templates and re-run as needed.

## Evidence & governance
- Artifacts are deterministic JSON/JSONL/dir trees suitable for CI inspection.
- Path policy: ADR-0024 (use `/config` only). No external mounts in commands or outputs.
- Pair with ADR-0020 (config error canonicalization) for consistent diagnosis.

## Troubleshooting
- No artifacts produced: ensure template dir exists and is readable.
- Empty graph: check that template files match the scanner's discovery patterns.
- Many missing references: run validator with `--verbose` and verify entity IDs and macros are correctly named.
- Permission errors: ensure `.artifacts/` is writable by the current user.

## Change control
- Safe to run repeatedly; re-generates `.artifacts/` content.
- Use VCS to track graph/violations deltas across refactors.
