# Hestia — Lineage Guardian

> Validate and correct entity lineage metadata across Home Assistant template YAML files.

## Quick Start

**✅ Configuration is already integrated into `/config/hestia/config/system/hestia.toml`**

### Option 1: CLI (Recommended)
```bash
cd /config/hestia/tools/lineage_guardian
python lineage_guardian_cli.py --verbose
```

### Option 2: VSCode Tasks
From **any workspace location**:
- **Terminal → Run Task → "Lineage Guardian: Full Pipeline (dry-run)"**
- **Terminal → Run Task → "Lineage Guardian: Scanner Only"**
- **Terminal → Run Task → "Lineage Guardian: Open Documentation"**

### Option 3: Manual Components
```bash
cd /config/hestia/tools/lineage_guardian
python lineage_guardian/graph_scanner.py --output ./.artifacts/graph.json --template-dir /config/domain/templates/ --verbose
python lineage_guardian/lineage_validator.py --graph-file ./.artifacts/graph.json --output ./.artifacts/violations.json --verbose
python lineage_guardian/lineage_corrector.py --violations-file ./.artifacts/violations.json --plan-dir ./.artifacts/_plan
python lineage_guardian/graph_integrity_checker.py --graph-file ./.artifacts/graph.json --output ./.artifacts/integrity.json
python lineage_guardian/lineage_report.py --graph ./.artifacts/graph.json --violations ./.artifacts/violations.json --integrity ./.artifacts/integrity.json --outdir ./.artifacts/report
```

## Architecture

### Core Components
- **`lineage_guardian_cli.py`** — ADR-compliant CLI wrapper with proper logging
- **`lineage_guardian/`** — modular pipeline components:
  - `graph_scanner.py` — extract entity relationships from YAML templates
  - `lineage_validator.py` — validate declared vs actual metadata
  - `lineage_corrector.py` — generate non-destructive correction plans
  - `graph_integrity_checker.py` — bidirectional consistency checks
  - `lineage_report.py` — comprehensive markdown + JSON reporting
  - `models.py`, `utils.py` — data structures and utilities

### Integration Points
- **Configuration**: `/config/hestia/config/system/hestia.toml` → `[automation.lineage_guardian]`
- **Documentation**: `/config/hestia/library/docs/guides/development/lineage_guardian_copilot_guide.md`
- **VSCode Tasks**: Integrated into main workspace `/.vscode/tasks.json`
- **Workspace Index**: Tracked in `/config/hestia/config/index/manifest.yaml`
- **Logging**: Follows ADR-0018 patterns → `/config/hestia/workspace/operations/logs/lineage/`

## Safety & Guardrails

- **Dry-run by default** — only writes plan files under `./.artifacts/_plan`
- **ADR-0024 compliant** — uses canonical `/config` paths
- **ADR-0018 compliant** — structured logging and backup patterns
- **Scope validation** — restricted to `/config/domain/templates/` only
- **Atomic operations** — backup-before-modify when implementing ruamel merges
- **Idempotent** — no destructive edits

## Development

**Copilot Enhancement Guide**: `/config/hestia/library/docs/guides/development/lineage_guardian_copilot_guide.md`

Use this guide to:
- Harden regex patterns in `utils.py`
- Implement ruamel.yaml-based safe merges in `lineage_corrector.py`
- Add comprehensive unit tests
- Expand entity parsing capabilities
