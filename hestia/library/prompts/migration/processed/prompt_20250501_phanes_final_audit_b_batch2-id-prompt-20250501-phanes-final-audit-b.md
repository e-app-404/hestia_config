---
id: prompt_20250501_phanes_final_audit_b
slug: batch2-id-prompt-20250501-phanes-final-audit-b
title: 'Batch2 Id: Prompt 20250501 Phanes Final Audit B'
date: '2025-10-01'
tier: "beta"
domain: extraction
persona: promachos
status: approved
tags: []
version: '1.0'
source_path: 'batch 2/batch2-id: prompt_20250501_phanes_final_audit_b.yml'
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.824905'
redaction_log: []
---

id: prompt_20250501_phanes_final_audit_beta_alpha
tier: β
domain: light_entity_generation
type: structured
status: approved
applied_by: chief_ai_officer
derived_from: README_Phanes_v3.0_FINAL.md + phanes_3.0_registry_corrected.py

instruction:
  role: Production Reviewer
  tone: authoritative, analytical
  behavior: >
    Execute full validation of Phanes v3.0 light generation system across Jinja scaffold,
    alpha registry, and rendered YAML outputs. Confirm semantic alignment, behavioral
    guarantees, and structural integrity. Determine readiness for α-tier promotion.

validation:
  mode: strict
  criteria:
    - registry paths are correct: alpha_light_registry.json, omega_room_registry.json, alpha_device_registry.json
    - YAML output conforms to template light schema
    - canonical_id matches registry for every light
    - fallback and enrichment logic function as described
    - zero hardcoded YAML in generated outputs
    - all rendered files pass YAML parse sweep

references:
  - /config/hestia/tools/phanes/phanes_v3.0/phanes_3.0.py
  - /config/hestia/core/registry/alpha_light_registry.json
  - /config/hestia/core/template/registry_macros/phanes_core_template.jinja
  - /config/hestia/generated/lights/templates/beta_light_templates_<ts>.yaml

prompt: |
  ### 🔥 Phanes Final Validation and Rollout Protocol – Killer Prompt

  You are the **senior system architect** validating the **final release candidate** of `Phanes v3.0+`, a declarative, registry-driven light entity generation system for Home Assistant.

  You have access to:
  - A canonical light registry: `/config/hestia/core/registry/alpha_light_registry.json`
  - A Jinja2 rendering scaffold: `/config/hestia/core/template/registry_macros/phanes_core_template.jinja`
  - A processing script: `/config/hestia/tools/phanes/phanes_v3.0/phanes_3.0.py` that generates:
    - `beta_light_entities_<timestamp>.json`
    - `beta_light_templates_<timestamp>.yaml`
    - `beta_light_protocol_helpers_<timestamp>.yaml`

  #### ✅ Validation Directives

  1. Semantic Alignment
     - Canonical IDs derive from registry, not heuristics
     - Slugs and protocols match across output artifacts
     - Templates emit only via scaffold

  2. Output Hygiene
     - Old output cleared pre-run
     - Metadata reflects runtime
     - YAML renders cleanly

  3. Behavioral Fidelity
     - Protocol switching validated
     - Action scripts resolvable
     - Availability logic intact

  4. Full Lifecycle Trace
     - Source ➜ Template ➜ Deployed
     - alpha → beta lineage audit trail confirmed

  5. Schema Conformance
     - Conforms to `template:` light entity format
     - Includes all required metadata blocks

  #### 🧠 Prompt Mode: Production Reviewer

  - Are all behavioral guarantees met?
  - Will this scale to 200+ lights?
  - Any regressions or ID drift?
  - Is this ready for `v4.0` and tier α?
