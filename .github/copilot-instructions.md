<!-- Copilot instructions for Hestia (Home Assistant workspace) -->
# Quick guide for AI coding assistants

This repository (Hestia) is a collection of operator tooling, config artifacts
and small utilities that live alongside a Home Assistant installation. Use the
notes below to be productive quickly and avoid unsafe changes.

## Canonical Workspace Structure (ADR-0016)

- **Edit root**: `~/hass` (canonical path for all operations)
- **NEVER** use `/n/ha` or `/private/var/ha_real` (deprecated legacy paths)
- **Python paths**: Always use `.expanduser()` with tilde paths: `Path('~/hass/...').expanduser()`
- **VS Code**: Use workspace-relative paths (`${workspaceFolder}`) in configs

## Key Workspace Areas (per hestia_structure.md)

- `hestia/config/` — Runtime YAML only (devices, network, preferences, registry, diagnostics)
- `hestia/library/docs/ADR/` — Architecture Decision Records (follow ADR-0009 formatting)
- `hestia/tools/` — Scripts, validators, pipelines (Mac-safe paths)
- `hestia/workspace/archive/vault/` — Long-term backups and bundles
- `hestia/workspace/operations/logs/` — Generated outputs and logs (use-case/timestamp structured)
- `.trash/` — Temporary files (auto-swept, gitignored)
- `artifacts/` — Reproducible release bundles (gitignored)

## File Management & Hygiene (ADR-0018)

- **Backups**: Use pattern `<name>.bk.<YYYYMMDDTHHMMSSZ>` (UTC timestamps)
- **Never commit**: `.storage/`, `.venv*/`, `deps/`, caches, secrets, runtime state
- **Reports**: Write to `hestia/workspace/operations/logs/<use-case>/<UTC>__<tool>__<label>.log`
- **Atomic operations**: Use `os.replace()` for safe file updates

## Code Quality Standards

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

### Python Code
- **Version**: Python >= 3.10
- **Style**: Ruff settings in `pyproject.toml` (line-length 100)
- **Path expansion**: `Path('~/hass/...').expanduser()` for tilde paths

## Workflows and Commands

- **Python CLIs**: Published in `pyproject.toml` (e.g. `hestia-adr-lint`)
- **Development**: Create venv under `~` (not under HA mount)
- **Dry-run default**: Check `--help` for `--apply`/`--execute` flags before making changes
- **Error patterns**: Reference `hestia/tools/error_patterns.yml` for known issues

## Security & Secrets (Critical)

- **Never commit**: Real credentials, tokens, private keys
- **Placeholders**: Use `__REPLACE_ME__` in vault templates
- **Vault URIs**: Use vault://secret/hestia/... format with fragment notation
- **Preview vs provisioning**: Files under `hestia/config` are previews only

## Integration Points

- **Tailscale/Network**: Configs under `hestia/config/network`
- **ADR compliance**: Follow ADR-0009 formatting (YAML front-matter, TOKEN_BLOCK)
- **Mount validation**: Scripts should check `${HA_MOUNT:-$HOME/hass}` exists
- **Git hooks**: Pre-commit validates paths, prevents banned file tracking

## Safety Guidelines for AI Agents

- **Prefer**: Non-destructive refactors, tests, documentation
- **Atomic updates**: Create backups before modifying critical configs
- **Validation**: Run config checks after template/automation changes
- **Flag**: Any changes introducing secrets or system service modifications
- **ACK tokens**: Scripts may require environment variables (ADR-0016)

## Common Error Patterns (ADR-0020)

- **Template abs()**: Use `{{ value | abs }}` not `{{ abs(value) }}`
- **Shell script paths**: Use `bash -lc '/config/tools/script.sh'` format
- **Missing files**: Use `package_*` prefix for package files
- **Registry errors**: Ensure `deleted_entities` exists in entity registry

## Quick Reference Files

- `pyproject.toml` — Packaging and CLI entrypoints
- `README.md` — Dev setup and run instructions  
- `hestia/library/docs/ADR/` — Architecture decisions and patterns
- `hestia/tools/error_patterns.yml` — Known error patterns and fixes

## Deprecated Paths (DO NOT USE)

- `hestia/reports/` — DEPRECATED, use `hestia/workspace/operations/logs/` instead
- `/n/ha` — DEPRECATED, use `~/hass` instead
- `hestia/core/` — DEPRECATED, use `hestia/config/` instead
- `hestia/docs/ADR/` — DEPRECATED, use `hestia/library/docs/ADR/` instead

If anything here is unclear or you need more detail on a subcomponent, say which
area (e.g. `vault templates`, `jinja patterns`, `workspace structure`) and I will expand
the instructions with file-level examples.

