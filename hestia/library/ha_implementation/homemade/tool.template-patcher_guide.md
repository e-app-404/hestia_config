---
id: DOCS-TEMPLATE-PATCHER-001
title: "template_patcher — Jinja template validation and automated fixes"
slug: template-patcher-guide
version: 1.0.0
created: 2025-10-20
author: "e-app-404"
adrs: ["ADR-0002", "ADR-0020", "ADR-0024"]
content_type: manual
last_updated: 2025-10-21
hot_links:
- entrypoint: "/config/hestia/tools/template_patcher/patch_jinja_templates.sh"
---

# template_patcher — operator guide

## What it does
- Validates and auto-patches Jinja templates to conform to Hestia patterns (ADR-0002 & ADR-0020):
  - Guards on datetime parsing (`as_datetime`) and state normalization (`unknown/unavailable`).
  - Fixes common filter/function usage mismatches (e.g., `abs()` vs `| abs`).
  - Normalizes whitespace and prevents template-empty-string glitches.

## When to use it
- Before committing changes to `custom_templates/` or template-bearing YAML.
- After bulk edits or merges that might introduce template drift.

## How to run
- VS Code task: “Hestia: Patch HA templates”
  - Runs: `bash /config/hestia/tools/template_patcher/patch_jinja_templates.sh`
- Command line (equivalent):
  - `/config/hestia/tools/template_patcher/patch_jinja_templates.sh`

## Behavior & outputs
- Operates in place under `/config` following path hygiene rules.
- Backs up changed files with `.bak-<UTC>` suffix and `.sha256` checksum.
- Emits a brief report to the terminal; pair with config-validate afterwards.

## Safety & governance
- Read-only unless patch candidates are detected and confirmed.
- Conforms to ADR-0024 (paths) and ADR-0020 (error canonicalization).

## Troubleshooting
- No patches applied: templates already compliant.
- Invalid YAML after patch: run config validation and inspect backups.
- Excessive diffs: narrow the scope or run in a feature branch first.

## Change control
- Keep backups until changes are verified by HA.
- Consider adding CI hooks to run the patcher for PRs touching templates.
