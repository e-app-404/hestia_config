---
title: "ADR-0012: Workspace Folder Taxonomy & ADR Methodology"
date: 2025-09-19
status: Draft
author:
  - "Evert Appels"
last_updated: 2025-09-19
related:
  - ADR-0009
  - ADR-0008
tags: ["meta-capture", "configuration", "governance", "secrets"]
---

# ADR-0012: Workspace Folder Taxonomy & ADR Methodology

This ADR formalizes the methodology used to consolidate and normalize configuration artifacts (extracted snapshots, runtime configs, authoritative as-built records), defines expected I/O shapes, file/folder mappings, hard requirements, and validation tokens. It also documents TODOs for undefined items.

## Summary of methodology applied

- Discover artifacts (manual capture or automated discovery).
- Canonicalize machine-discovered artifacts into `hestia/core/config/` as `*.extract.yaml`, `*.runtime.yaml`, or `*.topology.json`.
- Keep authoritative human-curated `as_built` records in `hestia/core/devices/` as `*.conf` (YAML-like).
- Archive duplicates or historical snapshots into `hestia/vault/duplicates/` or `hestia/vault/backups/` before deleting to avoid accidental data loss.
- Normalize ADRs and governance docs into `hestia/docs/ADR/` following ADR-0009 front-matter schema and ensuring `TOKEN_BLOCK` exists.

## Expected I/O (contract)

- Inputs:
  - discovery artifacts (raw): JSON/YAML snippets from devices or network scans.
  - user-supplied ADRs (Markdown with front-matter).

- Outputs:
  - canonical artifacts under `hestia/core/config/` (YAML/JSON) for machine consumption.
  - authoritative device records under `hestia/core/devices/` (YAML with `as_built`).
  - ADRs under `hestia/docs/ADR/` with validated front-matter and `TOKEN_BLOCK`.

## Shape of deliverable files (examples)

- Extracted device snapshot (YAML): `hestia/core/config/<device>.extract.cfg`
  - root: `extracted_config` (mapping)
  - keys: `device`, `role`, `mgmt_ip`, `mac`, `dns_servers` (list), `ntp_servers` (list), `snmp` (mapping)

- Runtime network config (YAML): `hestia/core/config/network.runtime.yaml`
  - root: mapping with `modem`, `router`, `tailnet_routing`, `local_gateway_domain`

- Topology JSON: `hestia/core/config/network.topology.json`
  - mirror of runtime network config in JSON; consumed by topology tools.

- Authoritative device record (YAML): `hestia/core/devices/<device>.conf`
  - root: `as_built` (mapping)
  - other allowed blocks: `validation`, `notes`, `ha_integration`, `moved_note`, `transient_state`, `relationships`, `group`

- ADRs: `hestia/docs/ADR/ADR-XXXX-<slug>.md`
  - front-matter keys (in order): `title`, `date`, `status`, `author`, `related`, `supersedes`, `last_updated`
  - must include a fenced YAML `TOKEN_BLOCK:` with `accepted`, `requires`, and `drift` lists.

## Folder -> Content categorization mapping

- `hestia/core/config/` → machine-discovered artifacts (extracts, runtime configs, topology), indexed by `hades_config_index.yaml`.
- `hestia/core/devices/` → authoritative `as_built` records and curated device notes.
- `hestia/docs/ADR/` → ADRs and governance docs (machine-parseable front-matter + tokens).
- `hestia/vault/` → archives, backups, duplicates (never consumed directly by runtime).

## Hard requirements (enforced by CI)

- All ADR front-matter must match Schema v1 and keys must be in the canonical order.
- ADRs must include a `TOKEN_BLOCK` YAML fenced block at the end.
- `hestia/core/config/` artifacts must parse with `yaml.safe_load` or `json.load`.
- No tabs in YAML front-matter; spaces-only indentation.
- Files in `core/config/` should be referenced in `hestia/core/config/index/hades_config_index.yaml`.

## Validation tokens

- TOKEN_BLOCK schema (v1):
  - `accepted`: list of UPPER_SNAKE tokens describing what the ADR/file complies with.
  - `requires`: list of prerequisite schema tokens.
  - `drift`: list of DRIFT codes for issues to surface.

Example token block (append to ADR files):

```yaml
TOKEN_BLOCK:
  accepted:
    - ADR_FORMAT_OK
    - ADR_REDACTION_OK
    - ADR_GENERATION_OK
    - TOKEN_BLOCK_OK
  requires:
    - ADR_SCHEMA_V1
  drift:
    - DRIFT: adr_format_invalid
    - DRIFT: missing_token_block
```

## Normalization performed for ADR-0009 and ADR-0012

- Normalized ADR-0009 front-matter key order per Schema v1 and normalized workspace references from the other project into the local layout (`/n/ha/hestia/...`).
- Ensured ADR-0009 includes a `TOKEN_BLOCK` so automation can consume it.

## TODOs / Open items (needs attention)

- [TODO] Define the retention policy and TTL for `hestia/core/config/*.extract.*` snapshots (e.g., 30 days by default).
- [TODO] Decide canonical naming conventions for `*.extract.cfg` vs `*.extract.yaml` (consistency currently mixed).
- [TODO] Formalize the exact JSON Schema / metadata_schema.yaml for `hades_config_index.yaml` tags and enforce the `tag_policy` list.
- [TODO] Implement CI scripts to run `ci_checks` (yaml_load, path_exists, tag_policy) — currently only manual validation performed.
- [TODO] Confirm whether `group` HA snippets in device files should be extracted into `hestia/core/devices/ha/` or kept inline.

## Enforcement & automation notes

- CI should run on PRs that touch `hestia/core/*` and `hestia/docs/ADR/*`.
- Automation should extract `TOKEN_BLOCK` from ADRs and publish governance reports.

---

TOKEN_BLOCK:
  accepted:
    - ADR_FORMAT_OK
    - ADR_NORMALIZATION_OK
    - ADR_INDEXED_OK
  requires:
    - ADR_SCHEMA_V1
  drift:
    - DRIFT: adr_missing_retention_policy
    - DRIFT: adr_ambiguous_extract_extension
---
title: "ADR-0012: Workspace folder taxonomy and assignation rules"
date: 2025-09-14
status: Accepted
author:
  - Evert Appels
  - Github Copilot
related:
  - HA-BB8.ADR-0001
  - HA-BB8.ADR-0004
  - HA-BB8.ADR-0008
  - HA-BB8.ADR-0009
  - HA-BB8.ADR-0017
  - HA-BB8.ADR-0018
last_updated: 2025-09-14
supersedes: []
---

# ADR-0012: Workspace folder taxonomy and assignation rules

## Table of Contents
1. Context
2. Decision
3. Canonical roots
4. Assignation Rules (programmatic)
5. Enforcement
6. Consequences
7. Token Block

## 1. Context
This project maintains a canonical add-on code root at `addon/`. Prior drift produced duplicate or misplaced content at the repository root (e.g., `bb8_core/`, `services.d/`, and `tools/`). This ADR defines categorical purposes and programmatic assignation rules per folder to prevent drift.

## 2. Decision

### Canonical roots
- `addon/`: **Runtime code for the Home Assistant add-on**
  - `addon/bb8_core/` — Python package for runtime code only.
  - `addon/services.d/` — s6-overlay services shipped in the container (`<service>/run`, optional `<service>/log/run`).
  - `addon/tests/` — tests for the runtime package.
  - `addon/tools/` — runtime utilities bundled into the container (may be invoked by services or operators).
- `ops/`: **Operations, QA, audits, release tooling**
  - Subfolders: `ops/audit`, `ops/diagnostics`, `ops/qa`, `ops/release`, `ops/evidence`, `ops/guardrails`, etc.
  - `ops/tools/` — operator-facing tools (docker, git, CI helpers, data audits); **never imported at runtime**.
- `scripts/`: **Repo developer scripts** (small glue, bootstrap, repo maintenance; no runtime semantics).
- `reports/`: **Generated artifacts only** (logs, coverage, audits, evidence). No source files.
- `docs/`: **Documentation** (ADR, guides, prompts, patches, legacy).
- `services.d/` at repo root: **FORBIDDEN**. All services must live under `addon/services.d/`.
- `tools/` at repo root: **Discouraged**. Code tools must be rehomed:
  - add-on utilities → `addon/tools/`
  - ops tooling → `ops/tools/`
  - otherwise → `scripts/`

## 3. Assignation Rules (programmatic)
- Python files importing `addon.bb8_core` → **`addon/`** (runtime or add-on bundled tools).
- Python files importing docker, paho, git, HA CLI, cloud SDKs, or performing audits/releases → **`ops/`**.
- Python files with CLI `if __name__ == "__main__"` but no runtime imports:
  - operational CLIs → `ops/tools/`
  - developer convenience → `scripts/`
- s6 services (`<name>/run` [+ `log/run`]) → **`addon/services.d/`** (executable).
- Generated outputs, logs, coverage, dumps → **`reports/`** only.

## 4. Enforcement
- Pre-commit hook rejects:
  - root `services.d/`
  - bare `bb8_core` imports (must be `addon.bb8_core`)
  - Python under `tools/` at repo root (must be rehomed)
- CI job runs repo-shape audit and fails on violations.

## 5. Consequences
- No duplicate code trees.
- Clear separation of runtime vs ops/dev artifacts.
- Automated guardrails prevent regression.

## 6. Token Block
```yaml
TOKEN_BLOCK:
  accepted:
    - WORKSPACE_TAXONOMY_OK
    - FOLDER_ASSIGNATION_OK
    - TOKEN_BLOCK_OK
  requires:
    - ADR_SCHEMA_V1
    - ADR_FORMAT_OK
    - ADR_GENERATION_OK
    - ADR_REDACTION_OK
  drift:
    - DRIFT: root_services_d_present
    - DRIFT: bare_bb8_core_import
    - DRIFT: python_tools_root
    - DRIFT: folder_taxonomy_violation
```
