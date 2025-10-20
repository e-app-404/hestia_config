# Hestia — Lineage Guardian

> Validate and correct entity lineage metadata across Home Assistant template YAML files.

## Quick Start

**✅ Configuration is fully integrated into `/config/hestia/config/system/hestia.toml`**  
**✅ VSCode Tasks are available workspace-wide**  
**✅ CLI commands documented in `/config/hestia/config/system/cli.conf`**  
**✅ Tracked in workspace manifest and relationship graph**

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
- **CLI Commands**: Documented in `/config/hestia/config/system/cli.conf` → `lineage_guardian_management`
- **Service Registry**: Mapped in `/config/hestia/config/system/relationships.conf`
- **Workspace Allocation**: Defined in `/config/hestia/config/system/hestia_workspace.conf`
- **Logging**: Follows ADR-0018 patterns → `/config/hestia/workspace/operations/logs/lineage/`

### Workspace Integration Status

**✅ Fully Integrated** — All components are now in canonical locations:

- **Tool Location**: `/config/hestia/tools/lineage_guardian/` (ADR-0024 compliant)
- **Configuration**: Centralized in `hestia.toml` with comprehensive settings
- **CLI Access**: Direct CLI wrapper + VSCode tasks + documented commands
- **Governance**: Tracked in workspace manifest and service relationships
- **Content Allocation**: Proper workspace rules in `hestia_workspace.conf`

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

## Recent Workspace Changes (2025-10-16)

- **Configuration Integration**: Complete `hestia.toml` configuration with scheduler settings
- **VSCode Tasks**: Added workspace-wide tasks for full pipeline, scanner-only, and documentation
- **CLI Documentation**: Added comprehensive `lineage_guardian_management` section to `cli.conf`
- **Service Mapping**: Added to `relationships.conf` with integration points tracking
- **Workspace Allocation**: Defined content allocation rules in `hestia_workspace.conf`
- **Manifest Tracking**: All components registered in workspace `manifest.yaml`
