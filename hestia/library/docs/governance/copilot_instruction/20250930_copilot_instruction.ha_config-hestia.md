<!-- Copilot instructions for Hestia (Home Assistant workspace) -->

# Hestia AI Coding Assistant Guide (Governance‑Grade)

You are assisting inside the Hestia repository — a collection of operator tooling, configuration artifacts, and utilities running alongside Home Assistant. Follow these directives exactly.

## 📂 Repository Topology
- `hestia/config/` — runtime configs (devices, network, services)
- `hestia/tools/` — Python CLIs & utilities (e.g. ADR linter)
- `hestia/workspace/archive/vault/` — **secret templates only** (placeholders, never real secrets)
- Network artifacts under `hestia/config/network/` support preview and deployment scripts

## ⚙️ Workflows & Commands
- ADR Linter: defined in `pyproject.toml` (entry `hestia-adr-lint`).  
  Run from a venv **outside** the HA mount:
  ```bash
  hestia-adr-lint hestia/library/docs/ADR --format human
````

* Deployment scripts default to **dry‑run**.
  Always check `--help` for `--apply` / `--execute` before performing changes.

## ✅ Conventions to Preserve

* **Never** commit or generate real credentials. Vault templates use `__REPLACE_ME__` placeholders.
* Maintain **preview vs provisioning** separation: no hardcoded secrets in templates or renderers.
* Python ≥ 3.10, ruff line length 100 per `pyproject.toml`.

## 🔒 Secret & Vault Handling

* `vault://` URIs in YAML (e.g. `hestia/config/storage/samba.yaml`) map to Vault paths like `secret/hestia/...`.
* The fragment convention after `#` (such as `#credentials`) is a **schema requirement**. Do not invent or alter it.
* All secret paths and patterns must remain exactly as defined by the codebase; no speculative generation.

## 📚 Files to Read First

* `README.md` (repo root) — dev/run instructions
* `pyproject.toml` — packaging & CLI entrypoints
* `hestia/tools/*` — CLI helpers; test in venv before edits
* `vault_manager/README.md` — secret naming & template rules

## 📝 Examples of Patterns

* ADR linter: `hestia/tools/utils/validators/adr_lint` CLI → `hestia.tools.adr_lint.cli:main`
* Dry‑run deploy: `hestia/deploy/dsm/apply_portal_changes.sh` uses `--apply` to perform changes

## 🛡️ AI Agent Safety Rules

* Prefer changes that add tests, docs, or **non‑destructive refactors**.
* **Flag** any modification introducing plaintext secrets or system service changes — these require human maintainer action.
* Do not remove vault placeholders or alter `vault://` schema.
* When unsure, ask for clarification (e.g., “vault templates”, “ADR linter”, “deploy/dsm”) before generating code.

## 🧩 Operational Assumptions (Hardened)

* All vault URIs follow the existing fragment convention; no new fragments should be proposed without schema approval.
* Scripts are assumed **non‑destructive** unless explicitly documented with `--apply`/`--execute`.
* AI output must comply with Python ≥ 3.10 and ruff config; no outdated syntax.
* Copilot suggestions must keep project structure intact; no relocation of critical files or breaking of entrypoints.
