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
- `hestia/reports/` → use `hestia/workspace/operations/logs/` instead
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
- `hestia/workspace/operations/logs/` — Generated outputs and logs (use-case/timestamp structured)
- `.trash/` — Temporary files (auto-swept, gitignored)
- `artifacts/` — Reproducible release bundles (gitignored)

### File Management & Hygiene (ADR-0018)

- **Backups**: Use pattern `<name>.bk.<YYYYMMDDTHHMMSSZ>` (UTC timestamps)
- **Never commit**: `.storage/`, `.venv*/`, `deps/`, caches, secrets, runtime state
- **Reports**: Write to `hestia/workspace/operations/logs/<use-case>/<UTC>__<tool>__<label>.log`
- **Atomic operations**: Use `os.replace()` for safe file updates

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

### Prompt Library Tooling (ADR-0018, ADR-0026)

- **Two environments by design**:
  - **HA code & dev inside this repo**: `/config/.venv` (workspace interpreter)
  - **Prompt library / operator CLIs**: `~/hestia_venv` (home venv, reproducible)
- **Wrappers**: Scripts under this repo that call prompt tooling must use `~/hestia_venv/bin/python` (not `/config/.venv`)
- **Dependencies**: Ensure `pyyaml` et al. are installed in `~/hestia_venv`
- **Documentation**: Clearly state interpreter per tool in READMEs

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
- **ADR-0018**: Workspace lifecycle policy
- **ADR-0020**: HA configuration error canonicalization
- **ADR-0024**: Canonical config path (supersedes ADR-0016)
- **ADR-0026**: Workspace environment operations

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

## Quick Reference Files 📚

### Essential Reading

- `README.md` — Dev setup and run instructions
- `pyproject.toml` — Packaging and CLI entrypoints
- [ADR Library](/config/hestia/library/docs/ADR/) — Architecture decisions and patterns
- [Governance Index](/config/.workspace/governance_index.md) — Current rules and hot ADRs
- `hestia/library/error_patterns.yml` — Known error patterns and fixes

### Vault & Secret Management

- `hestia/workspace/archive/vault/templates/` — Secret template patterns
- `hestia/tools/utils/vault_manager/README.md` — Secret naming conventions

### Tools & Utilities

- `hestia/tools/*` — CLI helpers; test in venv before edits
- `bin/` — Workspace executables and validation tools

If anything here is unclear or you need more detail on a subcomponent, specify the area (e.g. `vault templates`, `jinja patterns`, `workspace structure`, `ADR linter`) and I will provide file-level examples and expanded guidance.
