---
title: "ADR-0015: Symlink Policy for Hestia Config Workspace"
date: 2025-09-21
status: Proposed
author:

 - "Evert Appels"
 - "GPT-5 Thinking"
  related:
 - ADR-0001
 - ADR-0004
 - ADR-0008
 - ADR-0009
 - ADR-0010
 - ADR-0012
 - ADR-0013
 - ADR-0014
  supersedes: \[]
  last\_updated: 2025-09-21
---

# ADR-0015: Symlink Policy for Hestia Config Workspace

## Table of Contents

1. Context
2. Decision
3. Scope
4. Rationale
5. Rules & Guardrails
6. Enforcement & Automation
7. Migration & Remediation Plan
8. Consequences
9. Redaction & Governance Notes
10. Machine-Parseable Blocks

---

## 1. Context

Historic attempts to use filesystem symlinks inside the Home Assistant (HA) `/config` tree (especially at the repo root or HA-loaded directories) have repeatedly caused issues with HA’s file watcher, backup/snapshot integrity, Samba/NAS clients, and cross-platform tooling. We also maintain a strict separation between **authoring/tooling* - and **runtime-loaded configuration**. This ADR formalizes a project-wide symlink policy, defaulting to **no symlinks in HA-loaded config paths**, with narrowly-defined exceptions elsewhere.

A specific driver for this ADR is the desire to reference shared Jinja macros without creating a root-level symlink. The **canonical* - macro library is:

 - `/config/custom_templates/template.library.jinja`

…and **MUST** - be imported directly from that path rather than via symlinks.

## 2. Decision

 - Disallow symlinks in the HA runtime configuration tree (the **deny-list** - below), including the config root.
 - Require direct, canonical imports/paths for any HA-loaded artifacts (e.g., Jinja, packages, Lovelace), with the canonical macro location set to `/config/custom_templates/template.library.jinja`.
 - Allow symlinks **only** - in designated non-runtime areas (the **allow-list** - below) for developer workflows and large-data artifacts, subject to guardrails.
 - Provide automated enforcement in pre-commit and CI to block prohibited symlinks and to verify canonical imports for templates.

## 3. Scope

**In scope**: Repository layout, HA config tree, developer tooling, backups/snapshots, and cross-platform access (Samba/NAS, macOS/Linux/Windows).

**Out of scope**: OS-level or Docker-level mounts/binds controlled outside of the repo (handled by deployment tooling separately).

## 4. Rationale

 - **Stability**: HA’s file watcher and reload mechanisms behave inconsistently with symlinks.
 - **Integrity**: Snapshots/tarballs and Samba shares may dereference or miss symlinked content, leading to broken backups or duplicate material.
 - **Determinism**: Symlinks blur boundaries between authoring and runtime config, undermining auditability and normalization rules (see ADR-0008).
 - **Portability**: Cross-platform paths and ACLs differ; symlinks often degrade the experience on NAS/SMB clients.

## 5. Rules & Guardrails

### 5.1 Deny-list (no symlinks permitted)

- `/config` (root) and all HA-loaded subtrees, including but not limited to:

  - `/config/custom_templates/`
  - `/config/templates/`
  - `/config/packages/`
  - `/config/includes/`
  - `/config/lovelace/` and `/config/ui-lovelace*/`
  - `/config/automations*/`, `/config/scripts*/`, `/config/scenes*/`
  - Any directory referenced by HA `!include` or `template:` loaders
- `/vault` (including `backups/`, `tarballs/`, and `storage/`) to preserve archival integrity

### 5.2 Allow-list (symlinks permitted with guardrails)

- `/tools/**`, `/deploy/**`, `/work/**`, `/docs/**`, `/diagnostics/**`, `/config/meta/**`
- Guardrails for allowed locations:

  - Symlinks must be **relative* - (no absolute paths) and must not escape the repository root.
  - No symlinks may point into any deny-listed path.
  - No symlink chains > 1 hop (no nested chains).
  - Do not symlink files that are consumed by HA at runtime, even if placed in an allow-listed folder.

### 5.3 Canonical paths & imports

- **Jinja macro library (canonical):** - `/config/custom_templates/template.library.jinja`
- **Jinja import rule:**

  ```jinja
  {%- from 'custom_templates/template.library.jinja' import <macro_a>, <macro_b> -%}
  ```
 - No alternate symlinked entry points (e.g., root-level `template.library.jinja`) are allowed.

### 5.4 Exception process

 - Exceptions are rare and **time-bound**. A PR seeking an exception must include a fenced YAML **`SYMLINK_EXCEPTION`* - block (see Machine-Parseable Blocks) describing justification, duration, and rollback plan. Approval by repository maintainers is required. Exceptions are logged and expire automatically.

## 6. Enforcement & Automation

- **Pre-commit hook** - (mandatory): fail on any git-added symlink under deny-listed paths; fail on absolute-path symlinks; flag multi-hop chains.

  - Reference implementation sketch:

    ```bash
    #!/usr/bin/env bash
    set -euo pipefail
    deny_roots=("config" "vault")
    status=0
    while read -r mode _ _ _ path; do
      [[ $mode != 120000 ]] && continue  # only symlinks
      top=${path%%/*}
      for d in "${deny_roots[@]}"; do
        if [[ $top == "$d" ]]; then
          echo "ERROR: Symlink in deny-listed path: $path" >&2
          status=1
        fi
      done
      target=$(git show :"$path" | tr -d '\r')
      if [[ $target = / - ]]; then
        echo "ERROR: Absolute symlink target: $path -> $target" >&2
        status=1
      fi
    done < <(git ls-files -s)
    exit $status
    ```
- **CI check**: replicate pre-commit logic; additionally verify that no symlink target points into a deny-listed subtree.
- **Template import linter**: scan for imports of `template.library.jinja` and ensure they use `custom_templates/template.library.jinja`.

## 7. Migration & Remediation Plan

1. **Inventory**: Detect existing symlinks and their targets.

   ```bash
   git ls-files -s | awk '$1==120000{print $4}'
   ```
2. **Remove** - symlinks found under deny-listed paths; replace with real files where needed.
3. **Rewrite Jinja imports**  - to the canonical path:

   ```bash
   rg -l "template\.library\.jinja" config | xargs sd \
     "from '.*template\.library\.jinja'" \
     "from 'custom_templates/template.library.jinja'"
   ```
4. **Add pre-commit/CI hooks** - and re-run to confirm no violations.

## 8. Consequences

 - Slight duplication in authoring workflows (copy over symlink) in exchange for higher determinism and safer snapshots.
 - Clear separation of authoring vs runtime config simplifies audits, diffs, and incident response.

## 9. Redaction & Governance Notes

 - This ADR follows `ADR-0009` governance and formatting. No sensitive material is included. Any future exception blocks will be time-bound and machine-parseable for automated redaction/export.

## 10. Machine-Parseable Blocks

```yaml
SYMLINK_POLICY:
  version: 1
  canonical_files:
    - path: /config/custom_templates/template.library.jinja
      purpose: jinja_macro_library
  deny_roots:
    - /config
    - /vault
  deny_globs:
    - /config/**
    - /vault/**
  allow_roots:
    - /tools
    - /deploy
    - /work
    - /docs
    - /diagnostics
    - /config/meta
  guardrails:
    - relative_only
    - no_multi_hop
    - no_target_into_deny_roots
    - no_runtime_consumption_of_symlinked_files
  jinja_import_rule:
    import: "from 'custom_templates/template.library.jinja'"

SYMLINK_EXCEPTION:
  required_fields:
    - id
    - justification
    - expires
    - owner
    - rollback_plan
```

```yaml
TOKEN_BLOCK:
  accepted:
    - SYMLINK_POLICY_OK
    - NO_SYMLINKS_IN_CONFIG
    - CANONICAL_TEMPLATE_PATH_OK
    - TOKEN_BLOCK_OK
  requires:
    - ADR_SCHEMA_V1
  drift:
    - DRIFT: symlink_in_config_root
    - DRIFT: symlink_in_ha_loaded_dir
    - DRIFT: absolute_symlink_target
    - DRIFT: multi_hop_symlink
    - DRIFT: canonical_template_missing
    - DRIFT: import_uses_root_symlink
```
