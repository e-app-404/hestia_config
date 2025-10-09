---
id: prompt_20251001_bfa275
slug: gpt-prompt-post-reboot-entity-remediation-protocol
title: "\U0001F9E0 GPT Prompt: Post-Reboot Entity Remediation Protocol"
date: '2025-10-01'
tier: "\u03B1"
domain: instructional
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: Post-Reboot Entity Remediation Protocol.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:22.482832'
redaction_log: []
---

# 🧠 GPT Prompt: Post-Reboot Entity Remediation Protocol

## 🎯 Objective
Reconcile entity ID changes between pre-reboot documentation and the current Home Assistant state. Update tiered YAML logic, canonical registries, and doctrinal entries to reflect actual post-reboot entity identifiers.

---

## 📋 Input Artifacts

- `post_reboot_entity_snapshot.json`: JSON export of current HA entities
- `pre_reboot_entity_registry.csv`: Canonical CSV export of pre-reboot registry
- `architecture_doctrine.yaml`: Current doctrinal structure (includes `derived_from` and `canonical_id`)
- `alpha_sensor_registry.json`, `omega_device_registry.json`: Canonical device + sensor mappings
- Any YAML logic files from `/config/hestia/` containing tiered logic referencing outdated entity_ids

---

## 🧩 Task Breakdown

### Phase 1: Entity Drift Mapping
- Match `pre_reboot_entity_registry.csv` to `post_reboot_entity_snapshot.json`
- Output a mapping YAML with fields:
  - `old_id: binary_sensor.foxy_motion_β`
  - `new_id: binary_sensor.foxy_motion_β_v2`
  - `match_type: fuzzy | alias | direct`
  - `confidence_score: float`

### Phase 2: Propagate Fixes
- Patch `derived_from:` and `canonical_id:` fields across:
  - `architecture_doctrine.yaml`
  - All tiered logic YAMLs (`_β`, `_γ`, `_δ`, `_ε`, `_ζ`)
  - Sensor registry files (json/yaml)

### Phase 3: Validate and Confirm
- Rebuild and validate `logic_path_index.yaml`
- Run validator trace across updated logic
- Emit report of:
  - Rewritten entries
  - Unmatched references (if any)
  - Tier integrity violations (if introduced)

### Phase 4: Documentation Reconciliation
- Rewrite doctrinal examples that contain outdated entity IDs
- Update `developer_guidelines.md` with a section on:
  - "Handling Entity Drift After System Rebuild"
- Optional: inject `canonical_id` attributes into live HA entities

---

## 📌 Output Expectations

- `entity_id_drift_report.yaml`
- Updated `architecture_doctrine.yaml` with realigned `derived_from`
- Patched YAML logic files (inline or listed in `patch_manifest.yaml`)
- Updated canonical registries (`alpha_*.json`, `omega_*.json`)
- Drift summary and patch audit log

---

## 📢 Constraints

- Do not assume `entity_id` renames unless verified by match in snapshot
- Do not patch registries or doctrine unless changes are traceable and high-confidence
- Retain original metadata (`created`, `contributors`) when updating YAMLs
- Use `canonical_id` as ground truth where available; otherwise fallback to `unique_id`

---

## 🧪 Activation Phrase

Respond to:
**"Start entity reconciliation from post_reboot_entity_snapshot.json and apply to architecture_doctrine.yaml."**


