# Hestia — Lineage Guardian (Copilot Bundle)

> Validate and correct entity lineage metadata across Home Assistant template YAML files.

## Quick Start

1. Merge `config/snippets/hestia.toml.patch` into your real config:
   `/config/hestia/config/system/hestia.toml`
2. (Optional) Create venv & install:
   ```bash
   cd /config/hestia/tools/lineage_guardian
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the pipeline (dry-run safe):
   ```bash
   cd /config/hestia/tools/lineage_guardian
   python lineage_guardian/graph_scanner.py --output ./.artifacts/graph.json --template-dir /config/domain/templates/ --verbose
   python lineage_guardian/lineage_validator.py --graph-file ./.artifacts/graph.json --output ./.artifacts/violations.json --verbose
   python lineage_guardian/lineage_corrector.py --violations-file ./.artifacts/violations.json --plan-dir ./.artifacts/_plan
   python lineage_guardian/graph_integrity_checker.py --graph-file ./.artifacts/graph.json --output ./.artifacts/integrity.json
   python lineage_guardian/lineage_report.py --graph ./.artifacts/graph.json --violations ./.artifacts/violations.json --integrity ./.artifacts/integrity.json --outdir ./.artifacts/report
   ```
4. Or open `/config/hestia/tools/lineage_guardian` in VSCode: **Terminal → Run Task → Lineage: Full Pipeline (dry-run)**

## What's inside

* `lineage_guardian/` — modular components
  * `graph_scanner.py` (build graph)
  * `lineage_validator.py` (check vs declared metadata)
  * `lineage_corrector.py` (non-destructive plan; ruamel-based merge placeholder)
  * `graph_integrity_checker.py` (post-checks)
  * `lineage_report.py` (markdown + JSON summary)
  * `models.py`, `utils.py`, `lineage_guardian.py` (orchestrator)
* `.vscode/` — tasks & launch
* `prompts/COPILOT_GUIDE.md` — paste into Copilot Chat
* `config/snippets/hestia.toml.patch` — config extension

## Safety & Guardrails

* **Dry-run by default** (only writes plan files under `./.artifacts/_plan`)
* **Backups + atomic writes** (when you implement ruamel merges)
* **Scope validation** to `/config/domain/templates/` only
* Idempotent; no destructive edits.

