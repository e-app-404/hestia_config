---
title: ADR-0003: Canonical Tier Definitions for Home Assistant Entity Architecture
date: 2025-09-11
status: Draft
---

# ADR-0003: Canonical Tier Definitions for Home Assistant Entity Architecture

## Table of Contents
1. Context
2. Decision
3. Enforcement
4. Tokens
5. Last updated

## 1. Context
Home Assistant entity architecture benefits from a tiered model to organize, validate, and reason about entities and their relationships. This ADR formalizes canonical tier definitions, rules, and validation logic for robust, maintainable automations and integrations.

## 2. Decision
The following canonical tiers are defined:

### α: Signal Plane Tier
- **Symbol:** α
- **Function:** Raw, direct input from devices
- **Canonical Rule:**
  If entity_category is not set or is "None" AND platform is not "template", "group", "sensor aggregation" AND entity is registered in core.entity_registry with a valid device_id → assign tier = α
- **Match:**
  - registry: core.entity_registry
  - device_id: [".+"]
  - platform: ["mqtt", "command_line", "rest", "sun", "backup", "hassio", "sonos"]
  - entity_category: [null, "None"]
- **Required Fields:** ["device_id"]
- **Feeds From:** []
- **Feeds Into:** ["β", "η"]
- **Annotations:** ["tier", "canonical_id", "subsystem"]
- **Validation:**
  - directionality: terminal_source
  - regression_guard: true
  - override_aware: false

### β: Abstraction Tier
- **Symbol:** β
- **Function:** Canonicalized signal abstraction
- **Canonical Rule:**
  If platform is "template" or "derivative" OR entity references other entities in attributes (e.g. entity_id, source) → assign tier = β
- **Match:**
  - platform: ["template", "derivative"]
  - references_entities: true
  - entity_id: ".*_β$"
- **Required Fields:** ["tier", "canonical_id", "alpha_source"]
- **Feeds From:** ["α"]
- **Feeds Into:** ["γ", "δ", "ζ"]
- **Annotations:** ["tier", "canonical_id", "upstream_sources"]
- **Validation:**
  - directionality: unidirectional
  - regression_guard: true
  - override_aware: true

### μ: Diagnostics Tier
- **Symbol:** μ
- **Function:** Tier integrity and drift diagnostics
- **Canonical Rule:**
  If entity_category: diagnostic OR entity_id contains *_percent, *_load, *_uptime → assign tier = μ
- **Match:**
  - entity_category: diagnostic
  - entity_id: ["*_percent*", "*_load*", "*_uptime*"]
  - attributes_include: ["diagnostic_type", "target_tier"]
- **Required Fields:** ["tier", "target_tier"]
- **Feeds From:** ["*"]
- **Feeds Into:** []
- **Annotations:** ["tier", "health_scope"]
- **Validation:**
  - alert_on_failure: true
  - audit_log_required: true

### σ: System Configuration Tier
- **Symbol:** σ
- **Function:** Mode settings, scenario switches, configuration overrides
- **Canonical Rule:**
  If domain in input_* OR entity_id matches *_override, *_setting, *_mode → assign tier = σ
- **Match:**
  - domains: ["input_boolean", "input_text", "input_number"]
  - entity_id: ["*_override*", "*_setting*", "*_mode*"]
  - attributes_include: ["mode", "override_target"]
- **Required Fields:** ["tier", "scenario_id", "config_scope"]
- **Feeds From:** []
- **Feeds Into:** ["γ", "ζ", "μ"]
- **Annotations:** ["tier", "override_scope", "config_context"]
- **Validation:**
  - override_tracing: true
  - impact_graph_enabled: true
  - loopback_guard: true

### η: Formatting / Merge Tier
- **Symbol:** η
- **Function:** Data synthesis across domains or protocols
- **Canonical Rule:**
  If attributes include "merge_logic" and upstream_sources reference more than one entity → assign tier = η
- **Match:**
  - attributes_include: ["merge_logic", "upstream_sources"]
  - upstream_sources_count: ">1"
  - entity_id: ".*_η$"
  - file_path: "**/eta/**/*.yaml"
- **Required Fields:** ["tier", "upstream_sources", "merge_logic"]
- **Feeds From:** ["α", "β"]
- **Feeds Into:** ["γ", "δ"]
- **Annotations:** ["tier", "merge_strategy"]
- **Validation:**
  - directionality: unidirectional
  - override_aware: true
  - aggregation_mandatory: true
  - traceability: true
  - _meta.tier_inference_origin: η.canonical_rule

### γ: Computation / Scoring Tier
- **Symbol:** γ
- **Function:** Weighted inference logic
- **Canonical Rule:**
  If attributes include "score_weight", "formula_type", or computation logic (e.g., gain_score, prediction_outcome) → assign tier = γ
- **Match:**
  - attributes_include: ["score_weight", "formula_type", "gain_score", "prediction_outcome"]
  - entity_id: ".*_γ$"
  - file_path: "**/sensors/gamma/**/*.yaml"
- **Required Fields:** ["tier", "source_entity", "formula_type"]
- **Feeds From:** ["β", "η"]
- **Feeds Into:** ["δ", "ε", "ζ"]
- **Annotations:** ["tier", "score_model", "confidence"]
- **Validation:**
  - bounded: true
  - regression_guard: true
  - override_aware: true
  - traceability: true
  - _meta.tier_inference_origin: γ.canonical_rule
  - disambiguation:
      tier_priority: 2
      conflict_resolution_hint: "Prefer γ if computation attributes present."

### δ: Temporal Memory Tier
- **Symbol:** δ
- **Function:** Decay, smoothing, and signal persistence
- **Canonical Rule:**
  If attributes include "decay_rate" or entity_id matches ".*_δ$" → assign tier = δ
- **Match:**
  - attributes_include: ["decay_rate"]
  - entity_id: ".*_δ$"
  - file_path: "**/sensors/delta/**/*.yaml"
- **Required Fields:** ["tier", "source_entity", "decay_type"]
- **Feeds From:** ["γ", "β"]
- **Feeds Into:** ["ε", "ζ"]
- **Annotations:** ["tier", "decay_strategy"]
- **Validation:**
  - decay_bounds: true
  - regression_guard: true
  - override_aware: true
  - traceability: true
  - _meta.tier_inference_origin: δ.canonical_rule
  - disambiguation:
      tier_priority: 3
      conflict_resolution_hint: "Prefer δ if decay attributes present."

### ε: Validation Tier
- **Symbol:** ε
- **Function:** Validation, thresholding, suppression
- **Canonical Rule:**
  If attributes include "threshold" or entity_id matches ".*_ε$" → assign tier = ε
- **Match:**
  - attributes_include: ["threshold"]
  - entity_id: ".*_ε$"
  - file_path: "**/sensors/epsilon/**/*.yaml"
- **Required Fields:** ["tier", "source_entity", "threshold", "validation_type"]
- **Feeds From:** ["δ", "γ"]
- **Feeds Into:** ["ζ"]
- **Annotations:** ["tier", "validator_id"]
- **Validation:**
  - threshold_required: true
  - fallback_required: true
  - traceability: true
  - _meta.tier_inference_origin: ε.canonical_rule
  - disambiguation:
      tier_priority: 4
      conflict_resolution_hint: "Prefer ε if threshold attributes present."

### ζ: Decision Tier
- **Symbol:** ζ
- **Function:** Final high-level automations or room states
- **Canonical Rule:**
  If entity_id matches ".*_ζ$" or file_path matches "**/sensors/zeta/**/*.yaml" → assign tier = ζ
- **Match:**
  - entity_id: ".*_ζ$"
  - file_path: "**/sensors/zeta/**/*.yaml"
- **Required Fields:** ["tier", "primary_source", "fallback_behavior"]
- **Feeds From:** ["ε", "δ", "β"]
- **Feeds Into:** []
- **Annotations:** ["tier", "decision_path"]
- **Validation:**
  - fallback_required: true
  - silence_protection: true
  - override_support: true
  - traceability: true
  - _meta.tier_inference_origin: ζ.canonical_rule
  - disambiguation:
      tier_priority: 5
      conflict_resolution_hint: "Prefer ζ if decision/automation attributes present."

## 3. Enforcement
- All entities should be assigned a canonical tier according to the above rules.
- Validation logic and required fields must be enforced for each tier.
- Tier feeds and annotations must be maintained for traceability and reasoning.

## 4. Tokens
- `tier`: Canonical tier assignment (α, β, μ, σ, η, γ, δ, ε, ζ)
- `entity_id`, `platform`, `attributes_include`, `required_fields`, `feeds_from`, `feeds_into`, `annotations`, `validation`
- `_meta.tier_inference_origin`: Source of tier assignment logic

---
_Last updated: 2025-09-11_
