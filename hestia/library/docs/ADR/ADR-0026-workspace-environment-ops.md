---
id: ADR-0026
title: Workspace Operations & Environment Management
slug: workspace-environment-ops
status: Accepted
related:
- ADR-0009
- ADR-0024
- ADR-0030
supersedes: []
last_updated: 2025-10-21
date: 2025-10-06
version: 1.0
decision: Architectural decision documented in this ADR.
author:
- "e-app-404"
- Strategos (Executive Project Strategist)
tags: ["operations", "workspace", "home-assistant", "ha", "environment", "venv", "governance", "security", "recovery", "tooling", "macos", "ci-cd", "diagnostics", "ssh", "requirements", "ops"]
---

## ADR-0026 — Workspace Operations & Environment Management

## 1. Context

Operational knowledge for the HA workspace has grown organically and is fragmented across scripts, READMEs, and commit messages. Critical patterns—such as the dual virtual environment strategy, governance tooling isolation, and safety gates—exist in implementation but lack a single authoritative reference.

**Problem**: Without a canonical operational ADR, teams risk drift, misconfigurations, and unsafe changes deployed to the live Home Assistant (HA) configuration.

**Goal**: Establish a governed, reproducible, and auditable model for:

- Environment setup and isolation
- Secrets handling
- Safety/rollback
- Platform integration (incl. macOS specifics)
- CI/CD alignment
- Diagnostics and maintenance workflows

## 2. Decision

Adopt a **Workspace Operations & Environment Management** standard with the following pillars:

1. **Dual-venv strategy**: Separate execution contexts for product code vs. governance/ops tooling.
2. **Tooling isolation**: Makefile entry points and path discipline to keep runtime config clean.
3. **Safety first**: Backups, validation gates, and binary acceptance checks precede mutating actions.
4. **Secrets hygiene**: Clear separation of credentials, least privilege, and vault-based resolution.
5. **Platform-aware ops**: macOS mount handling, cross-platform task shims, and VS Code tasks.
6. **Observability & diagnostics**: Lightweight, structured evidence and standardized logs under workspace paths.

## 3. Architecture Overview

```text
/config
├── configuration.yaml (HA runtime)
├── includes/ (HA declarative includes)
├── hestia/
│   ├── tools/              # ops + diagnostics (iso from HA runtime)
│   │   ├── system/
│   │   ├── utils/{backup,validators}
│   │   ├── python_scripts/
│   │   ├── evidence/
│   │   └── ci/
│   └── workspace/
│       ├── reports/
│       │   └── checkpoints/
│       ├── archive/
│       │   ├── tarballs/<YYYY-Www>/
│       │   ├── backups/<YYYY-Www>/
│       │   ├── dev_envs/<TS>/
│       │   ├── bleedthrough/<TS>/
│       │   └── adr/deprecated/
│       ├── cache/{python,tmp,scanner}/
│       └── ops/{lint,ci,playbooks,runbooks}/
├── .venv                   # product/dev venv (optional for local dev)
├── .venv_ha_governance     # governance venv (validators, hygiene tools)
└── www/assets/             # web assets (e.g., worker-portal-no-store.js)
```

## 4. Core Infrastructure

## 4.1 Dual Virtual Environment Strategy

- **`.venv`** — product-facing development; libraries required by add-ons/custom components and local dev tooling
- **`.venv_ha_governance`** — governance & ops tools only: linters, schema validators, hygiene/ADR lint, diagnostic collectors

**Rationale**: Prevents governance dependencies from leaking into HA runtime or add-on images; simplifies SBOM and troubleshooting.

### Creation & Activation

```bash
# product/dev venv (optional for local development)
python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip
pip install -r requirements-dev.txt

# governance venv (primary operational environment)
python3 -m venv .venv_ha_governance && source .venv_ha_governance/bin/activate
pip install --upgrade pip && pip install -r requirements-dev.txt

# OR use Makefile integration
make venv  # Creates and configures .venv_ha_governance automatically
```

## 4.2 Makefile Integration & Tooling Isolation

**Principles**:

- No scripts write to `/config` root; mutating outputs go to `hestia/workspace/{reports,archive,cache}`
- Makefile targets are **pure interfaces** with dry-run first, APPLY gated for mutation

### Reference Makefile

```makefile
VENV=.venv_ha_governance
ACTIVATE=. $(VENV)/bin/activate
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: hygiene backup tarball lint validate adr-validate config-validate

## Root hygiene check (governance compliance)
hygiene:
  @bash hestia/tools/root_hygiene_check.sh

## Create workspace backup
backup tarball:
  @bash hestia/tools/utils/backup/hestia_tarball.sh

## YAML linting
lint: venv
  @$(VENV)/bin/yamllint -f colored -s .

## ADR validation
adr-validate: venv
  @for adr in $$(find hestia/library/docs/ADR -name "*.md" -not -name "*template*"); do \
    echo "Validating $$adr..."; \
    $(PY) hestia/tools/utils/validators/adr_validator.py "$$adr" || exit 1; \
  done

## Comprehensive config validation
config-validate: adr-validate template-validate
  @echo "✅ All configuration validation checks passed"
```

## 4.3 Python Environment Management

**Dependencies Strategy**:

- **Pin interpreter**: Python 3.11+ (3.13.7 currently active)
- **Shared requirements**: Both venvs use `requirements-dev.txt` containing governance tools:
  - `yamllint==1.*` - YAML validation
  - `jsonschema==4.*` - Schema validation
  - `ruamel.yaml==0.18.*` - YAML processing
  - `pre-commit==3.*` - Git hooks
  - `isort==5.*`, `black==23.*` - Code formatting
  - `pytest==7.*`, `coverage==7.*` - Testing
  - Additional: `pandas`, `click`, `requests`, `cryptography`

**Installation Practices**:

- Prefer wheels; never use `sudo pip`
- Use `pip install --upgrade pip` before installing requirements
- For HA add-ons, dependencies live in Docker image builds; **never** couple to host venvs
- ADR linter installed separately: `pip install -e hestia/tools/utils/validators/adr_lint/[test]`

## 5. Security & Secrets

## 5.1 SSH Key Management

- Keys stored in `/config/.ssh/` with `0600` permissions; `authorized_keys` curated
- No private keys in VCS; CI uses deploy keys or OIDC

## 5.2 Vault Integration & Secret Resolution

- Secret values referenced via HA `!secret` or environment expansion (`!env_var`)
- For ops scripts, resolve secrets via vault client (or `.evidence.env` **read-only** runtime file) and avoid persisting secrets in artifacts

## 5.3 Credential Isolation

- `.venv_ha_governance` reads minimalist `.env.adr0024` for hygiene paths
- Network credentials for diagnostics passed by env at call time; not stored

## 6. Safety & Recovery

## 6.1 Safety Mechanisms & Validation Gates

- **Dry-run by default**: require `APPLY=1` to mutate
- **Preflight checks**: root hygiene, YAML schema validation, `hass --script check_config`
- **Binary acceptance**: pass/fail with machine-readable JSON summaries

## 6.2 Backup Strategy

**Dual Tarball System**:

- **Standard backups**: `make tarball` (excludes `.storage` directory)
- **Complete backups**: `make storage-tarball` (includes runtime state)
- **Location**: `hestia/workspace/archive/backups/<YYYY-Www>/`
- **Event-driven**: Automatic backups before migrations via ADR-0024 implementation

### Tarball Implementation (hestia/tools/utils/backup/hestia_tarball.sh)

```bash
# Environment variable controls inclusion
INCLUDE_STORAGE="${INCLUDE_STORAGE:-false}"
DATE=$(date -u +%Y%m%dT%H%M%SZ)
WEEK=$(date +%G-W%V)
OUT_DIR="/config/hestia/workspace/archive/backups/$WEEK"

# Comprehensive exclusion patterns (37+ patterns)
if [[ "$INCLUDE_STORAGE" == "true" ]]; then
  EXCLUDE_ARGS=(--exclude='.venv*/' --exclude='deps/' --exclude='.mypy_cache/')
else
  EXCLUDE_ARGS=(--exclude='.storage/' --exclude='.venv*/' --exclude='deps/')
fi

tar -czf "$OUT_DIR/hestia_backup_$DATE.tar.gz" "${EXCLUDE_ARGS[@]}" -C "$BASE_DIR" config/
```

## 6.3 Rollback Procedures

- Each migration emits a timestamped backup in `archive/backups/<TS>.tar.gz`
- Rollback uses `restore` target with **explicit confirmation** and validation after restore

## 7. Platform Integration

## 7.1 macOS-Specific Tooling & Mounts

- Prefer absolute path: `/System/Volumes/Data/homeassistant` for the HA data root
- Neutralize legacy mounts (`/n/ha`, `/Volumes/HA`) to `/config` via `hestia_neutralize_runner.sh`

## 7.2 Cross-Platform Considerations

- Use POSIX shell; avoid GNU-only flags when possible
- Provide Python fallbacks for platform quirks (stat, date parsing)

## 7.3 VS Code Workspace Configuration

Single authoritative `.code-workspace` with:

- canonical `terminal.integrated.cwd` to HA root
- YAML schemas for HA
- watcher/search excludes for archive/cache/tmp
- python interpreters pinned to venvs

## 8. Technology Stack

## 8.1 Core Tools & Dependencies

- **Linters**: `yamllint==1.*`, `ruff` (configured via `pyproject.toml`)
- **Schema Validation**: `jsonschema==4.*` for HA configuration validation
- **Python Tools**: `ruamel.yaml==0.18.*`, `pandas==2.*`, `click==8.*` for data processing
- **Testing**: `pytest==7.*`, `coverage==7.*` for validation testing
- **Code Quality**: `isort==5.*`, `black==23.*`, `pre-commit==3.*`
- **Security**: `cryptography==46.*` for secret handling

## 8.2 Integration Architecture

- **CI/CD**: GitHub Actions for hygiene checks, tarball rotation, ADR link validation (ADR-0030)
- **Home Assistant Integration**: Shell commands migrated from `domain/shell_commands/` executable scripts to declarative YAML in `packages/integrations/shell_command.yaml`
- **Monitoring/Diagnostics**: Lightweight scripts under `hestia/tools/{system,ops,evidence}/` with evidence under `workspace/operations/reports/`
- **Package Management**: Python entry points via `pyproject.toml` (e.g., `hestia-adr-lint`)

## 9. Operational Procedures

## 9.1 Environment Bootstrap

**Governance Environment Setup:**

```bash
# Automated via Makefile (recommended)
make venv  # Creates .venv_ha_governance and installs requirements
make hygiene  # Verify clean state

# Manual setup (alternative)
python3 -m venv .venv_ha_governance
source .venv_ha_governance/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

**ADR Linter Setup (External Venv):**

```bash
# Install in user home (NOT under /config)
python3 -m venv ~/.venv/hestia-adr
source ~/.venv/hestia-adr/bin/activate
cd /config/hestia/tools/utils/validators/adr_lint
pip install -e .[test]

# Usage
hestia-adr-lint /config/hestia/library/docs/ADR --format human
```

**VS Code Integration**:

- Use canonical terminal cwd: `/System/Volumes/Data/homeassistant`
- Python interpreter paths: `.venv_ha_governance/bin/python`
- Exclude patterns: `.storage/**`, `.venv*/**`, `hestia/workspace/cache/**`

## 9.2 Troubleshooting

**Common Issues & Solutions:**

- **Virtual Environment Activation Errors**:
  - **Problem**: `command not found: uname` or PATH corruption
  - **Root Cause**: Virtual environment created with legacy paths during ADR-0024 migration
  - **Solution**: Fix activation script paths:
    ```bash
    # Edit .venv/bin/activate (or .venv_ha_governance/bin/activate)
    # Change: case "$(uname)" in
    # To: case "$(/usr/bin/uname)" in
    # Change: export VIRTUAL_ENV=/Volumes/config/.venv
    # To: export VIRTUAL_ENV=/System/Volumes/Data/homeassistant/.venv_ha_governance
    ```

- **Broken add-on deps**: Rebuild container; ensure `requirements.txt` copied into build context
- **Schema errors**: Run `yamllint` and HA config check via `make lint config-validate`
- **Path drift**: Run `hestia_neutralize_runner.sh` and `root_hygiene_check.sh`
- **ADR linter issues**: Ensure installed in external venv (`~/.venv/hestia-adr`), not under `/config`
- **Makefile target failures**: Verify `.venv_ha_governance` exists and is properly configured

## 9.3 Maintenance & Hygiene Automation

- Nightly hygiene job: root check, diagnostics snapshot, archive rotation
- Weekly rollups under `archive/<YYYY-Www>/`

## 10. Governance & Enforcement

## 10.1 Root Hygiene System

**Guards**: `hestia/tools/root_hygiene_check.sh` with comprehensive allow-lists:

```bash
# Core HA runtime files and directories
ALLOWED_DIRS="blueprints custom_components domain packages python_scripts themes www tts hestia includes entities appdaemon zigbee2mqtt ps5-mqtt glances bin scripts image custom_templates tmp"

# Runtime/build directories
ALLOWED_RUNTIME=".storage .ssh .venv .venv_ha_governance .mypy_cache .cloud .trash .quarantine artifacts deps .git .github .githooks .vscode .ci-config .devcontainer"

# Core configuration files
ALLOWED_FILES="configuration.yaml scenes.yaml scripts.yaml automations.yaml customize.yaml secrets.yaml .HA_VERSION Makefile requirements*.txt worker-portal-no-store.js"
```

**Evidence & Reporting**:

- Hygiene violations logged with specific file/directory names
- Results stored under `workspace/operations/reports/`
- CI integration via GitHub Actions for automated enforcement

**Review Requirements**:

- Operational PRs must include: preflight output, backup artifact link, hygiene check results
- Binary pass/fail with machine-readable summaries

## 11. Risks & Mitigations

- **Tool leakage into runtime** → Strict path discipline; CI guard
- **Secrets exposure** → Vault patterns and `.env` minimization
- **Rollback gaps** → Mandatory pre-mutation backups + manifests

## 12. Acceptance Criteria (Binary)

1. Two venvs exist and activate successfully; governance tools run from `.venv_ha_governance`.
2. Makefile targets `hygiene`, `diag`, `backup`, `restore` work; `hygiene` is read-only.
3. Mutating tools require `APPLY=1` and emit artifacts to `workspace/…` only.
4. Backups appear in `archive/tarballs/<YYYY-Www>/` with manifest.
5. CI job fails on root hygiene violations.

## 13. Implementation Plan

- **Phase 1**: ✅ **COMPLETED** - Governance venv + Makefile integration + hygiene scripts deployed
- **Phase 2**: ✅ **COMPLETED** - Shell commands migration from executable scripts to declarative YAML
- **Phase 3**: ✅ **COMPLETED** - Virtual environment path resolution fixes and backup system integration
- **Phase 4**: 🔄 **IN PROGRESS** - CI integration (root hygiene, ADR validation, tarball automation)

## 13.1 Shell Commands Migration (Completed October 2025)

**Migration Pattern**: Executable scripts in `domain/shell_commands/` → Declarative YAML in `packages/integrations/shell_command.yaml`

**Benefits Achieved**:

- **Canonical Path Compliance**: All commands use `/config/hestia/tools/` paths per ADR-0024
- **Configuration as Code**: Shell commands now follow Home Assistant declarative patterns
- **Simplified Maintenance**: Single YAML file vs. scattered executable scripts
- **Backup Integration**: Commands included in standard backup/restore procedures

**Implementation Template**:

```yaml
# packages/integrations/shell_command.yaml
shell_command:
  # System tools
  git_push_logger: "/config/hestia/tools/system/git_push_logger.sh"

  # Operations tools
  addons_runtime_fetch: "/config/hestia/tools/ops/addons_runtime_fetch.sh"

  # Evidence/verification tools
  ha_bb8_verification: "/config/hestia/tools/evidence/ha_bb8_verification.sh"
```

## TOKEN_BLOCK

```yaml
TOKEN_BLOCK:
  accepted:
    - DUAL_VENV_STRATEGY_OK
    - TOOLING_ISOLATION_OK
    - SAFETY_GATES_OK
    - SECRETS_HYGIENE_OK
    - WORKSPACE_EVIDENCE_OK
    - CI_ROOT_HYGIENE_OK
    - MAKEFILE_GOVERNANCE_INTEGRATION_OK
    - ADR_LINTER_EXTERNAL_VENV_OK
    - BACKUP_DUAL_TARBALL_OK
    - ROOT_HYGIENE_ALLOWLISTS_OK
  requires:
    - ADR_SCHEMA_V1
    - ADR_0024_CANONICAL_PATHS
    - VSCODE_WORKSPACE_UPDATED
    - MAKEFILE_TARGETS_PRESENT
    - GOVERNANCE_VENV_READY
    - REQUIREMENTS_DEV_UNIFIED
    - SHELL_COMMANDS_MIGRATED
  drift:
    - DRIFT: governance_tools_in_runtime
    - DRIFT: missing_backups_or_manifests
    - DRIFT: secrets_in_artifacts
    - DRIFT: yaml_schema_regressions
    - DRIFT: ci_root_hygiene_disabled
    - DRIFT: adr_linter_under_config_mount
    - DRIFT: venv_path_resolution_errors
    - DRIFT: makefile_venv_target_missing
```

## 14. References

- ADR-0009 Governance format
- ADR-0024 Canonical paths & workspace hygiene
- ADR-0030 Cross-repository ADR alignment
