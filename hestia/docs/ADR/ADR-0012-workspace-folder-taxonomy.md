---
id: ADR-0012
title: "Workspace Folder Taxonomy & ADR Methodology"
date: 2025-09-19
last_updated: 2025-09-25
status: Pending validation
related: ["ADR-0009", "ADR-0008", "ADR-0010", "ADR-0016"]
path_convention: "${HA_MOUNT:-$HOME/hass}"
tags: ["meta-capture", "configuration", "governance", "secrets", "taxonomy"]
author: "Evert Appels"
supersedes: []
notes: |
  This ADR consolidates and normalizes the earlier "hestia_structure" notes into a single, machine-enforceable policy.
  Source notes are retained under docs/source_notes/structure-notes.md for historical context.
---

# ADR-0012: Workspace folder taxonomy and assignation rules

> **Decision summary*- — Define a canonical workspace taxonomy with programmatic file assignation rules so that runtime code, operational tooling, documentation, machine-discovered artifacts, and authoritative records are cleanly separated. Provide binary acceptance checks and CI enforcement hooks to prevent drift.

## 1. Context

Historical drift produced duplicate or misplaced trees (e.g., `bb8_core/`, `services.d/`, and `tools/` at repo root). This ADR introduces a strict taxonomy and programmatic rules so automation can keep the workspace deterministic.

## 2. Decision

### 2.1 Canonical roots (repository pillars)

- `addon/` — **Runtime code for the Home Assistant add-on**

  - `addon/bb8_core/` — Python package used exclusively at runtime inside the add-on.
  - `addon/services.d/` — s6-overlay services shipped in the container (`<service>/run`, optional `<service>/log/run`).
  - `addon/tests/` — tests for `bb8_core` and services.
  - `addon/tools/` — runtime utilities bundled into the add-on image.
- `ops/` — **Operations, QA, audits, release tooling (never imported at runtime)**

  - Suggested subfolders: `ops/audit/`, `ops/diagnostics/`, `ops/qa/`, `ops/release/`, `ops/evidence/`, `ops/guardrails/`, `ops/tools/`.
- `scripts/` — **Developer scripts*- (bootstrap, repo maintenance; short, gluey). Not imported by runtime.
- `docs/` — **Documentation*- (ADRs, guides, prompts, patches, legacy). ADRs for this project live under `hestia/docs/ADR/` (see 2.2).
- `reports/` — **Generated artifacts only*- (logs, coverage, audits, evidence exports produced by CI or local runs). No source files.
- **Forbidden at repo root**:

  - `services.d/` (must live under `addon/services.d/`).
  - `tools/` (rehomed under `addon/tools/` or `ops/tools/`).

> **Path convention*- — All scripts and tools must honor `${HA_MOUNT:-$HOME/hass}` per ADR-0016. Hard-coding `/n/ha` is prohibited.

### 2.2 Knowledge & configuration tree ("hestia" space)

- `hestia/core/config/` — **Machine-discovered artifacts*- (extracts, runtime configs, topology) destined for machine consumption.

  - Naming:

    - `*.extract.yaml` — point-in-time extracted snapshots (from discovery/import).
    - `*.runtime.yaml` — intended/observed runtime configuration.
    - `*.topology.json` — network/device topology for tooling.
  - Indexing: each artifact **must** be referenced from `hestia/core/config/index/hades_config_index.yaml`.
- `hestia/core/devices/` — **Authoritative records** (`as_built` YAML). Allowed top-level keys:

  - `as_built` (required), `validation`, `notes`, `ha_integration`, `moved_note`, `transient_state`, `relationships`, `group`.
- `hestia/docs/ADR/` — **ADRs and governance docs** (Markdown with machine-parseable front-matter and a `TOKEN_BLOCK`).
- `hestia/vault/` — **Archives & backups**. Never consumed directly by runtime; excluded from packaging.

### 2.3 Programmatic assignation rules

- Python importing `addon.bb8_core` ⇒ **`addon/`**.
- Python performing audits/releases or using docker, paho, git, HA CLI, cloud SDKs ⇒ **`ops/`**.
- Python with CLI entrypoint and **no** runtime imports:

  - operational tooling ⇒ `ops/tools/`
  - developer convenience ⇒ `scripts/`
- s6 service trees (`<name>/run`, optional `log/run`) ⇒ **`addon/services.d/`**.
- Generated outputs (logs, coverage, dumps) ⇒ **`reports/`** - only.

### 2.4 Front-matter schema (ADR files)

- Canonical key order: `title`, `date`, `last_updated`, `status`, `author`, `related`, `requires`, `path_convention`, `tags`, `notes`.
- Indentation: spaces only; YAML must parse with `yaml.safe_load`.
- Each ADR ends with a fenced YAML `TOKEN_BLOCK` (see §6).

### 2.5 Index schema (hades_config_index.yaml, v1 minimal)

```yaml
version: 1
artifacts:
  - path: "hestia/core/config/network.runtime.yaml"
    type: "runtime_config"
    owner: "platform"
    tags: ["network", "routing"]
```

## 3. Enforcement

### 3.1 Pre-commit (local)

Reject commits that contain:

- `services.d/` at the repo root.
- Python modules importing `bb8_core` without the `addon.` prefix.
- Python under root `tools/` (must be rehomed to `addon/tools/` or `ops/tools/`).
- ADR files with tabs in front-matter or missing `TOKEN_BLOCK`.

### 3.2 CI gates (per ADR-0009 schedule)

- **Repo shape audit**: ensures taxonomy compliance and assignation rules.
- **ADR schema check**: validates front-matter order + required keys + `TOKEN_BLOCK` presence.
- **Config parsing**: `yaml.safe_load/json.load` for all files under `hestia/core/config/`.
- **Index completeness**: every `hestia/core/config/*` file has an entry in `hades_config_index.yaml`.
- **Include-scan**: deny root `tools/`, root `services.d/`, misplaced generated files, and logs under repo/hestia trees.
- **Deterministic packaging** (per ADR-0008): manifests + stable sha256 across reruns.

## 4. Binary acceptance criteria (must all pass)

1. **Taxonomy pass** — No files violate the folder policy (root `services.d/`, root `tools/`, incorrect imports).
2. **ADR compliance** — All ADRs parse; keys in canonical order; exactly one `TOKEN_BLOCK` per ADR.
3. **Config validity** — All artifacts in `hestia/core/config/` parse and are **indexed**.
4. **Determinism** — Two consecutive packaging runs produce identical sha256 for the release bundle.
5. **Path convention** — No scripts contain hard-coded `/n/ha`; all respect `${HA_MOUNT:-$HOME/hass}`.

### 4.1 Suggested CI snippets

```bash
# 1) root services.d/ forbidden
[ -d services.d ] && { echo "forbidden: root services.d"; exit 1; } || :

# 2) bare bb8_core import detector
rg -n "^\s*from\s+bb8_core|^\s*import\s+bb8_core" -g '!addon/**' && {
  echo "forbidden: bare bb8_core import outside addon/"; exit 1; } || :

# 3) ADR front-matter + TOKEN_BLOCK
./tools/adr_validate.py --path hestia/docs/ADR --require-token-block --order title,date,last_updated,status,author,related,requires,path_convention,tags,notes

# 4) Config parse + index completeness
python - <<'PY'
import sys, yaml, json, pathlib
root=pathlib.Path('hestia/core/config')
idx=yaml.safe_load(open('hestia/core/config/index/hades_config_index.yaml'))
indexed={a['path'] for a in idx.get('artifacts', [])}
for p in root.rglob('*'):
  if p.is_dir():
    continue
  if p.suffix in ('.yaml', '.yml'):
    yaml.safe_load(open(p))
  elif p.suffix == '.json':
    json.load(open(p))
  else:
    print(f"unsupported extension: {p}"); sys.exit(1)
  if str(p) not in indexed:
    print(f"unindexed artifact: {p}"); sys.exit(1)
print("OK")
PY

# 5) Deterministic packaging probe
old=$(sha256sum artifacts/release.tar.gz | awk '{print $1}')
# ... rerun the packager ...
new=$(sha256sum artifacts/release.tar.gz | awk '{print $1}')
[ "$old" = "$new" ] || { echo "non-deterministic packaging"; exit 1; }

# 6) Path convention guard
rg -n "/n/ha" --hidden --glob '!*vendor/*' && { echo "hard-coded /n/ha found"; exit 1; } || :
```

## 5. Consequences

- **Positive**: deterministic structure, clearer ownership, easier reviews, lower CI noise, and safer packaging.
- **Trade-offs**: some churn to rehome legacy folders and add indexing; minimal maintenance of index and ADR tokens.

## 6. TOKEN_BLOCK (for this ADR)

```yaml
TOKEN_BLOCK:
  accepted:
    - WORKSPACE_TAXONOMY_DEFINED
    - ASSIGNATION_RULES_DEFINED
    - TOKEN_BLOCK_OK
  requires:
    - ADR_SCHEMA_V1
    - DETERMINISTIC_PACKAGING
    - INCLUDE_SCAN_ENFORCED
  drift:
    - DRIFT: root_services_d_present
    - DRIFT: bare_bb8_core_import
    - DRIFT: python_tools_root
    - DRIFT: folder_taxonomy_violation
    - DRIFT: unindexed_config_artifact
```

## 7. Rollout & relationships

- Rollout schedule and gate states are governed by **ADR-0009**. This ADR supplies the taxonomy and checks those gates enforce.
- This ADR depends on **ADR-0016** (path convention) and amends **ADR-0010** (workspace shape) by clarifying forbidden roots and hestia subtrees.

## 8. Changelog

- 2025-09-25 — Reassembled ADR for clarity; unified naming conventions; added binary acceptance criteria and CI snippets; formalized index schema; merged "hestia_structure" content; retained source notes under `docs/source_notes/structure-notes.md`.
