# Hestia Workspace AI Assistant Guide

**Governance Preamble**: When assisting in this workspace, always consult [governance index](/config/.workspace/governance_index.md) first and treat its rules as authoritative. Cite the specific ADR(s) and section(s) when recommending changes. If a proposed action conflicts with ADR-0024 (canonical /config mount) or ADR-0022 (mount management), stop and ask for approval.

## Workspace Overview & Context

This repository (Hestia) is a collection of operator tooling, configuration artifacts, and small utilities that live alongside a Home Assistant installation. Use the notes below to be productive quickly and avoid unsafe changes.

## Canonical Path Standards (ADR-0024) 🏛️

### Edit Root

- **CANONICAL PATH**: `/config` (only writable config mount)
- **Python paths**: Always use `/config` directly: `Path('/config/...')`
- **VS Code**: Use workspace-relative paths (`${workspaceFolder}`) in configs

### Path Precedence Rules

- **VS Code configs**: prefer `${workspaceFolder}` for portability
- **Runtime scripts & HA paths**: use absolute `/config/...` for correctness
- **Never mix styles** within the same script

### ❌ DEPRECATED PATHS (DO NOT USE)

- `~/hass`, `/n/ha`, `/private/var/ha_real` (legacy paths)
- `hestia/reports/` → use `hestia/workspace/reports/` instead
- `hestia/core/` → use `hestia/config/` instead
- `hestia/docs/ADR/` → use `hestia/library/docs/ADR/` instead
- `/tmp` → use `tmp/` instead
- `/Volumes/HA/**` → blocked by readonly settings (use `/config` only)

## Workspace Structure & Navigation

### Key Areas (per hestia_structure.md)

- `hestia/config/` — Runtime YAML only (devices, network, preferences, registry, diagnostics)
- `hestia/library/docs/ADR/` — Architecture Decision Records (follow ADR-0009 formatting)
- `hestia/tools/` — Scripts, validators, pipelines (Mac-safe paths)
- `hestia/workspace/archive/vault/` — Long-term backups and bundles
- `hestia/workspace/operations/logs/` — Generated ops logs (use-case/timestamp structured)
- `.trash/` — Temporary files (auto-swept, gitignored)
- `artifacts/` — Reproducible release bundles (gitignored)

### File Management & Hygiene (ADR-0018)

- **Backups**: Use pattern `<name>.bk.<YYYYMMDDTHHMMSSZ>` (UTC timestamps)
- **Never commit**: `.storage/`, `.venv*/`, `deps/`, caches, secrets, runtime state
- **Reports**: Write to `hestia/workspace/reports/<use-case>/<UTC>__<tool>__<label>.log`
- **Atomic operations**: Use `os.replace()` for safe file updates

## Workspace Index & Discovery System 📋

### Automated Indices (/.workspace/)

- **governance_index.json** — ADR governance with hot rules and compliance tracking
- **config_index.json** — Configuration artifact scanning and categorization
- **knowledge_base_index.json** — Documentation and guide discovery with 79+ documents

### Manual Indices (/hestia/config/index/)

- **manifest.yaml** — Core workspace artifact registry with tools, diagnostics, network configs
- **appdaemon_index.yaml** — AppDaemon component tracking and endpoint management

### Index Usage Patterns

- **ADR lookup**: Query `governance_index.json` for current hot rules and compliance requirements
- **Config discovery**: Use `config_index.json` for finding configuration artifacts by category
- **Documentation search**: Browse `knowledge_base_index.json` by category (guides, automation, integration)
- **Tool inventory**: Reference `manifest.yaml` tools section for available workspace utilities

### Discovery Strategies

- **Problem-solving**: Start with governance_index for ADR constraints, then config_index for artifacts
- **Integration work**: Use knowledge_base_index for HA integration docs and guides
- **Tool development**: Check manifest.yaml for existing tools and avoid duplication
- **Cross-referencing**: Automated indices complement manual indices for comprehensive coverage

## Reporting & Monitoring Infrastructure 📊

### Report Structure

- **Location**: `/config/hestia/reports/<YYYY-MM-DD>/<tool>__<timestamp>__<type>.log`
- **Format**: Frontmatter+JSON structured logging with metadata and compliance tracking
- **Index**: Automatic catalog maintenance in `/config/hestia/reports/_index.jsonl`

### Report Types

- **Execution logs**: Tool runtime with input/output tracking and error details
- **Health reports**: Workspace health scoring with executive summaries and recommendations
- **Compliance reports**: ADR compliance validation with governance metadata
- **Comprehensive reports**: Full pipeline results with metrics and operational insights

### Health Scoring System

- **Workspace health**: Numerical score (0-100) based on file organization and compliance
- **Success rates**: Tool execution success tracking with failure analysis
- **Recommendations**: Actionable suggestions for workspace improvement
- **Trend tracking**: Historical health metrics via report index querying

### Monitoring Patterns

- **Query recent reports**: `cat /config/hestia/reports/_index.jsonl | jq -s 'sort_by(.created_at) | .[-5:]'`
- **Health monitoring**: Regular backup sweeper dry-runs for workspace health assessment
- **Compliance tracking**: ADR compliance validation in all tool outputs
- **Executive summaries**: High-level workspace status in comprehensive reports

## Patch Operation Workflow (ADR-0032)

When the operator submits a patch request (pastes a diff, drops a patch file, or links patch instructions), follow this mandatory workflow:

1) Create or update a todo
- Path: `/config/hestia/workspace/todo/`
- Use `TODO_TEMPLATE.md` and include `agent: copilot` and a `human_owner:`
- Link any provided patch instructions and include a brief proposed_patch snippet when safe

2) Stage the patch artifact
- Path: `/config/hestia/workspace/staging/`
- Filename pattern: `<UTC>__<tool|agent>__<label>.<ext>`
- Do not modify runtime configs at this step

3) Append to the patch ledger
- Path: `/config/hestia/workspace/operations/logs/patch-ledger.jsonl`
- Format: JSONL with fields like `timestamp_utc`, `id`, `source`, `actor`, `title`, `status`, `todo_path`, `staging_paths`, `plan_path`, `pr_url`, `notes`

4) Link or create a patch plan (optional)
- Path: `/config/hestia/workspace/operations/patch_plans/`
- Plans must include scope guards, validation steps, and ADR references

5) Migrate approved artifacts
- Move from `staging/` to `patches/` and update the ledger status
- Use governed writes (ADR‑0027) for any changes to runtime configs; avoid direct in-place edits

Guardrails
- Honor ADR‑0024 canonical path `/config`
- No secrets in todos or artifacts; reference vault URIs when needed

Reference: ADR‑0032 — Patch Operation Workflow

## Code Quality & Formatting Standards

### YAML/Config Normalization (ADR-0008)

- **Encoding**: UTF-8 with LF line endings
- **Indentation**: 2 spaces (no tabs)
- **YAML**: Sort keys A→Z, use `key: value` format
- **JSON**: Pretty print with 2-space indent, sort keys recursively
- **Trailing**: Exactly one newline at EOF, no trailing spaces

### Jinja Templates (ADR-0002, ADR-0020)

- **Always gate datetime operations**: `{% set t = as_datetime(x) %}{{ t is not none and ... }}`
- **State normalization**: Check `raw not in ['unknown','unavailable','']`
- **Whitespace control**: Use `{%-` and `-%}` in macros to prevent empty string returns
- **Template errors**: Use filter syntax `{{ delta | abs }}` not `{{ abs(delta) }}`

### Python Code Standards

- **Version**: Python >= 3.10
- **Style**: Follow ruff settings in `pyproject.toml` (line-length 100)
- **Path expansion**: Use `/config` directly, no expansion needed
- **AI output compliance**: Must use Python ≥ 3.10 syntax; no outdated patterns

### Python Environment Management

- **Workspace venv**: `/config/.venv` (primary development environment)
- **Package availability**: `toml` package installed for configuration parsing
- **Environment setup**: Use `configure_python_environment` for workspace initialization
- **Tool dependencies**: Individual tools specify their interpreter requirements in documentation
- **Configuration parsing**: All tools can access `hestia.toml` via `import toml`

### Prompt Library Tooling (ADR-0018, ADR-0026)

- **Two environments by design**:
  - **HA code & dev inside this repo**: `/config/.venv` (workspace interpreter)
  - **Prompt library / operator CLIs**: `~/hestia_venv` (home venv, reproducible)
- **Wrappers**: Scripts under this repo that call prompt tooling must use `~/hestia_venv/bin/python` (not `/config/.venv`)
- **Dependencies**: Ensure `pyyaml` et al. are installed in `~/hestia_venv`
- **Documentation**: Clearly state interpreter per tool in READMEs

## Configuration Management System (hestia.toml) ⚙️

### Centralized Configuration

- **Primary config**: `/config/hestia/config/system/hestia.toml`
- **Schema versioning**: `config_schema_version` with update tracking
- **ADR compliance**: Built-in compliance metadata and validation
- **Tool integration**: All automation tools read from hestia.toml sections

### Configuration Sections

- **[meta]**: Version control, schema tracking, and compliance ADRs
- **[paths]**: Canonical path definitions and workspace roots
- **[sweeper]**: Backup sweeper configuration (patterns, retention, reports)
- **[maintenance]**: Automated maintenance schedules and policies
- **[compliance]**: ADR tracking and governance validation

### Usage Patterns

- **Tool configuration**: Tools read their config sections via `toml.load()`
- **Path management**: All tools use `paths.config_root` for consistency
- **Compliance tracking**: Automated ADR compliance validation in tool outputs
- **Version control**: Schema evolution with backward compatibility

### Integration Requirements

- **All new tools** must integrate with hestia.toml configuration
- **Configuration changes** must update schema version
- **ADR compliance** must be declared in tool metadata
- **Path references** must use canonical paths from config

## Security & Vault Management (CRITICAL) 🔒

### Secret Handling Rules

- **NEVER commit**: Real credentials, tokens, private keys
- **Placeholders**: Use `__REPLACE_ME__` in vault templates
- **Preview vs provisioning**: Files under `hestia/config` are previews only
- **Flag requirement**: Any modification introducing plaintext secrets requires human maintainer action

### Vault URI Conventions

- **Format**: `vault://secret/hestia/...` with fragment notation
- **Fragment convention**: After `#` (such as `#credentials`) is a **schema requirement**
- **No speculation**: Do not invent or alter vault URI patterns; use existing exactly as defined
- **Examples**: `vault://secret/hestia/storage/samba#credentials`

### Vault Schema Integrity

- All vault URIs follow existing fragment convention; no new fragments without schema approval
- Do not remove vault placeholders or alter `vault://` schema
- All secret paths and patterns must remain exactly as defined by the codebase

### File Writing Governance (ADR-0027) 🔒

#### Write-Broker System

- **Governed operations**: Use `/config/bin/write-broker` for all file modifications
- **Atomic operations**: All file changes must use atomic replace patterns (`os.replace()`)
- **Backup-before-modify**: Required for all configuration changes
- **Path enforcement**: Three-layer governance (validation, atomic ops, audit trails)

#### Usage Patterns

- **Replace operation**: `write-broker replace --file <path> --search <old> --replace <new> --commit --msg <message>`
- **Validation mode**: Add `--dry-run` flag to preview changes
- **Rollback support**: All changes create automatic backups for restoration
- **Audit trail**: Complete operation logging with commit messages and timestamps

#### Governance Layers

1. **Validation Layer**: Pre-flight path and content validation
2. **Atomic Operations**: Guaranteed atomic file modifications
3. **Audit Trail**: Complete operation history with rollback capabilities

#### Integration Requirements

- **All automation tools** must use write-broker for file modifications
- **Manual edits** should follow atomic operation patterns
- **Backup verification** required before destructive operations
- **Path compliance** with ADR-0024 canonical path standards

## Development Workflows & CLI Tools

### Python CLIs & Entrypoints

- **Published in**: `pyproject.toml` (e.g. `hestia-adr-lint`)
- **Development**: Create venv under `~` (not under HA mount)
- **ADR Linter**: Run from venv outside HA mount: `hestia-adr-lint hestia/library/docs/ADR --format human`

### Deployment & Script Patterns

- **Dry-run default**: Check `--help` for `--apply`/`--execute` flags before making changes
- **Scripts assumed non-destructive** unless explicitly documented with `--apply`/`--execute`
- **Examples**: `hestia/deploy/dsm/apply_portal_changes.sh` uses `--apply` to perform changes

### Error Patterns & References

- **Error patterns**: Reference `hestia/library/error_patterns.yml` for known issues
- **Template abs()**: Use `{{ value | abs }}` not `{{ abs(value) }}`
- **Shell script paths**: Use `bash -lc '/config/tools/script.sh'` format
- **Missing files**: Use `package_*` prefix for package files
- **Registry errors**: Ensure `deleted_entities` exists in entity registry

## Backup Sweeper Automation System (ADR-0018, ADR-0024, ADR-0027) 🧹

### Architecture Overview

- **Main orchestrator**: `/config/hestia/tools/backup_sweeper.py`
- **5-component modular pipeline**: Sequential execution with shared log communication
- **Configuration-driven**: All parameters from `/config/hestia/config/system/hestia.toml`
- **Safety-first**: Atomic operations, dry-run validation, backup-before-modify

### Component Pipeline

1. **index.py** — Workspace scanner with pattern-based file discovery and classification
2. **naming_convention.py** — Naming standards enforcement with regex guardrails
3. **sweeper.py** — TTL-based file lifecycle management with configurable retention
4. **vault_warden.py** — Vault retention manager with basename grouping and keep-N-latest
5. **sweeper_report.py** — Comprehensive reporting with health scoring and ADR compliance

### Usage Patterns

- **Preview operations**: `python /config/hestia/tools/backup_sweeper.py --dry-run`
- **Execute cleanup**: `python /config/hestia/tools/backup_sweeper.py`
- **Validate setup**: `python /config/hestia/tools/backup_sweeper.py --validate-only`
- **Component help**: `python /config/hestia/tools/sweeper/<component>.py --help`

### Key Features

- **Pipeline orchestration**: Subprocess management with graceful failure recovery
- **Structured logging**: Frontmatter+JSON format with batch tracking and compliance metadata
- **Health scoring**: Workspace health metrics with executive summaries and recommendations
- **Report indexing**: Automatic catalog maintenance in `/config/hestia/reports/_index.jsonl`
- **Configuration validation**: Pre-flight checks for all components and settings

### Safety Guardrails

- **Atomic file operations**: All modifications use atomic replace patterns
- **Backup-before-modify**: Creates backups before any file changes
- **Dry-run validation**: Complete preview mode without file modifications
- **Component isolation**: Independent component execution with isolated error handling
- **Rollback support**: All operations reversible via backup restoration

## Home Assistant Integration Patterns

### Configuration Management

- **Mount validation**: Scripts should check `/config` exists using `tools/lib/require-config-root.sh`
- **Config validation**: Run config checks after template/automation changes
- **Recorder Policy**: Follow ADR-0014 for OOM guard and retention policies

### Integration Points

- **Tailscale/Network**: Configs under `hestia/config/network`
- **Custom components**: Located in `custom_components/`
- **Templates**: Located in `custom_templates/` with backup patterns
- **Packages**: Use `package_*` prefix for modular configurations

### Network & Storage

- **Network artifacts**: Under `hestia/config/network/` support preview and deployment scripts
- **Storage configs**: Reference vault URIs for credentials (never hardcode)
- **Diagnostics**: Configurations under `hestia/config/diagnostics/`

## Architecture Decision Records (ADR) 📋

### ADR Compliance (ADR-0009)

- **Formatting**: Follow ADR-0009 (YAML front-matter, TOKEN_BLOCK)
- **Governance**: All ADRs must be indexed in governance system
- **References**: Always cite specific ADR(s) and section(s) when recommending changes

### Current Hot Rules (from governance index)

- **ADR-0024**: Single canonical config mount → `/config` only; no dual SMB mounts
- **ADR-0022**: Mount management via LaunchAgent; preflight before writes
- **Path contracts**: Prefer container paths over host aliases; avoid `/Volumes/...` in tooling

### Key ADRs for Reference

- **ADR-0002**: Jinja pattern normalization
- **ADR-0008**: Syntax-aware normalization & determinism rules
- **ADR-0009**: ADR governance and formatting policy
- **ADR-0014**: Recorder policy, OOM guard & repo guardrails
- **ADR-0018**: Workspace lifecycle policy (backup sweeper compliance)
- **ADR-0020**: HA configuration error canonicalization
- **ADR-0022**: Mount keychain credentials and telemetry system
- **ADR-0024**: Canonical config path (supersedes ADR-0016)
- **ADR-0026**: Workspace environment operations
- **ADR-0027**: File writing governance and path enforcement system
- **ADR-0028**: AppDaemon & Room-DB canonicalization (proposed)

## AI Assistant Safety Guidelines 🛡️

### Preferred Actions

- **Non-destructive refactors**: Tests, documentation, code quality improvements
- **Atomic updates**: Create backups before modifying critical configs
- **Validation**: Run config checks after template/automation changes
- **Project structure integrity**: No relocation of critical files or breaking of entrypoints

### Flag Conditions (Require Human Approval)

- Any changes introducing secrets or system service modifications
- Modifications to vault placeholders or `vault://` schema
- Changes that conflict with ADR-0024 (canonical /config mount) or ADR-0022 (mount management)
- System service modifications or deployment steps

### Operational Guidelines

- When unsure, ask for clarification (e.g., "vault templates", "ADR linter", "deploy/dsm") before generating code
- **ACK tokens**: Scripts may require environment variables (per ADR governance)
- Prefer changes that add tests, docs, or non-destructive refactors

### Maintenance Session Tracking

- **Session logs**: `/config/hestia/config/system/maintenance_log.conf`
- **Structured documentation**: Actions, metrics, knowledge capture, and confidence levels
- **Historical audit**: Complete trail of major workspace changes and tool creation
- **Operational context**: Reference previous sessions for understanding system evolution
- **Tool genealogy**: Track creation and evolution of workspace utilities
- **Confidence tracking**: Technical, operational, and documentation confidence per session

## Quick Reference Files 📚

### Essential Reading

- `README.md` — Dev setup and run instructions
- `pyproject.toml` — Packaging and CLI entrypoints
- [ADR Library](/config/hestia/library/docs/ADR/) — Architecture decisions and patterns
- [Governance Index](/config/.workspace/governance_index.md) — Current rules and hot ADRs
- `hestia/library/error_patterns.yml` — Known error patterns and fixes

### Workspace Index Files

- **Automated Indices** (`/.workspace/`):
  - `governance_index.json` — 25 ADRs with hot rules and compliance tracking
  - `config_index.json` — Configuration artifact discovery and categorization
  - `knowledge_base_index.json` — 79 documents across guides, automation, integration
- **Manual Indices** (`/hestia/config/index/`):
  - `manifest.yaml` — Core workspace registry (tools, diagnostics, network)
  - `appdaemon_index.yaml` — AppDaemon components and endpoints (pending enhancement)

### Configuration & System Files

- `/config/hestia/config/system/hestia.toml` — Central configuration with ADR compliance
- `/config/hestia/config/system/maintenance_log.conf` — Session tracking and operational history
- `/config/hestia/reports/_index.jsonl` — Report catalog with health scoring and metrics

### Vault & Secret Management

- `hestia/workspace/archive/vault/templates/` — Secret template patterns
- `hestia/tools/utils/vault_manager/README.md` — Secret naming conventions

### Tools & Utilities

#### Core Workspace Tools

- **write-broker** — File writing governance enforcement with atomic operations
- **backup_sweeper.py** — Automated backup cleanup with 5-component modular pipeline
- **phantom_entity_cleanup.sh** — Entity registry maintenance and orphan resolution
- **template_patcher/** — Jinja template validation and automated fixes
- **adr/** — ADR governance, formatting validation, and compliance checking
- **workspace_manager.sh** — Complete workspace lifecycle management

#### Specialized Utilities

- **entity_duplicate_cleaner.sh** — Mobile device entity deduplication and takeover
- **backup_validator.sh** — Backup integrity checking and validation
- **lint_paths.sh** — Path compliance validation per ADR-0024
- **fix_path_drift.sh** — Automated path standardization and drift correction

#### Legacy & Development Tools

- `hestia/tools/*` — CLI helpers; test in venv before edits
- `bin/` — Workspace executables and validation tools
- `tools/legacy/` — Deprecated tools maintained for reference

If anything here is unclear or you need more detail on a subcomponent, specify the area (e.g. `vault templates`, `jinja patterns`, `workspace structure`, `ADR linter`) and I will provide file-level examples and expanded guidance.
