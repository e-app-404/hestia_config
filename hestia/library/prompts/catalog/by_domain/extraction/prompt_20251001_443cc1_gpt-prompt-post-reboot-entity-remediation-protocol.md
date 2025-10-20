---
id: prompt_20251001_443cc1
slug: gpt-prompt-post-reboot-entity-remediation-protocol
title: "\U0001F9E0 GPT Prompt: Post-Reboot Entity Remediation Protocol (v2)"
date: '2025-10-01'
tier: "α"
domain: extraction
persona: promachos
status: approved
tags: []
version: '1.0'
source_path: batch6_mac-import_Post-Reboot Entity Remediation Protocol.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:24.517714'
redaction_log: []
---

<!-- start prompt -->
# 🧠 GPT Prompt: Post-Reboot Entity Remediation Protocol (v2)

## 🎯 Objective

Reconcile entity ID drift caused by Home Assistant reintegration. Update all canonical mappings, tiered YAML logic, and doctrinal references to reflect new post-reboot `entity_id`s while retaining `canonical_id` traceability.

---

## 📋 Input Artifacts

- `25-06-10_post-reboot_entity_registry.json`: Extracted `core.entity_registry` from live `.storage/`
- `25-06-08_pre-reboot_entity_registry.json`: Extracted `core.entity_registry` from backup `.storage/`
- `architecture_doctrine.yaml`: Doctrine with `canonical_id`, `derived_from`, and `tier_origin`
- `alpha_sensor_registry.json`, `omega_device_registry.json`: Canonical registries
- All tiered YAML logic in `/config/hestia/**` referencing stale `entity_id`s

---

## 🧩 Task Breakdown

### Phase 1: Entity Drift Mapping

Match pre → post `entity_id` transitions by comparing:

- `unique_id`
- `device_id`
- `name` → `original_name`
- Optional: `canonical_id`, `platform`

Emit:

```yaml
- old_id: binary_sensor.foxy_motion_β
  new_id: binary_sensor.foxy_motion_β_v2
  match_type: direct | fuzzy | derived_via_canonical_id | alias
  confidence_score: 0.94
```

### Phase 2: Patch Propagation

Rewrite all references to stale `entity_id`s, including:

- `architecture_doctrine.yaml` (`derived_from`, `canonical_id`)
- Logic tiers `_β` → `_ζ` (`/config/hestia/{sensors,inference,logic,automation}`)
- Canonical registries: `alpha_sensor_registry.json`, `omega_device_registry.json`

Preserve:

- YAML metadata (`created`, `contributors`, `confidence_metrics`)
- Existing canonical anchors where still valid

### Phase 3: Validator Trace + Rebuild

- Run trace against updated logic
- Validate full tier fanout
- Emit `validator_log.json`
- Emit `logic_path_index.yaml` for post-drift signal verification

Emit drift reconciliation report with:

- Rewritten entries
- Unmatched signals (with `severity`)
- Tier violations (if introduced)

### Phase 4: Doctrinal + Dev Documentation Update

- Rewrite all doctrinal examples using outdated entity IDs
- Patch `developer_guidelines.md` with a new section:
  **"Handling Entity Drift After System Rebuilds"**
- (Optional) Inject `canonical_id:` into active HA entities via script (annotated)

---

## 📦 Expected Outputs

- `entity_id_drift_report.yaml`
- Updated `architecture_doctrine.yaml`
- Patched logic files (`patch_manifest.yaml`)
- Updated canonical registries (`alpha_*.json`, `omega_*.json`)
- `validator_log.json`
- `logic_path_index.yaml`

**additional requirements**

- Add a `schema_version` to the YAML emitted (useful for chain auditing).
- Inclusion of `legacy_id:` is required if match is fuzzy to help future reverse-tracing.

---

## 🔒 Constraints

- Only map entities with ≥ 0.88 confidence
- Never overwrite `canonical_id` unless `unique_id` match is exact
- Preserve YAML formatting, inline docs, and structured comments
- If ambiguity detected: annotate match with `match_type: fuzzy` and emit in `reconciliation_candidates.yaml`

## 🛡 Fail-Safe Enforcement

Fail mapping if:

- confidence_score is missing
- any match_type = ambiguous
- `entity_id` is reused across multiple `device_id`s with different `unique_id`s

Every emitted mapping must include:

- `confidence_explanation`: human-readable trust rationale
- `action_flag`: patch_safe | review | reject

Block downstream YAML output unless:

- `validator_log.json` contains zero errors
- `confidence_manifest.yaml` confirms ≥ 95% of matches are patch_safe
- `manifest.sha256` validates all patch files

---

## 🧪 Execution Mode

```yaml
execution_mode: enforce_recompletion
```

---

## ▶️ Activation Phrase

```plaintext
"Start entity reconciliation from 25-06-10_post-reboot_entity_registry.json and apply to architecture_doctrine.yaml."
```
<!-- end prompt -->

