---
id: prompt_20250612_e4f3be
slug: batch6-mac-import-gpt-prompt-post-reboot-canonical-registry-reconciliation-runtime-hardened-match-ordered-v2-yaml-copy-edit
title: '>'
date: '2025-06-12'
tier: "α"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch6_mac-import_GPT Prompt- Post-Reboot Canonical Registry Reconciliation
  (Runtime-Hardened, Match-Ordered v2) yaml Copy Edit .md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:23.212185'
redaction_log: []
---

prompt:
- id: 20250612_canonical_registry_reconciliated
  version: 2.1
  variant: match_ordered_execution
  objective: >
    'Reconcile post-reboot entity ID drift and propagate high-confidence mappings into artifacts listed.
    Do so while preserving canonical traceability and enforcing drift confidence gates.'

  artifacts:
  - `alpha_sensor_registry.json`
  - `alpha_light_registry.json`
  - `omega_device_registry.json`
  - `omega_room_registry.json`

  inputs:
  - `25-06-08_pre-reboot_core.entity_registry.json`
  - `25-06-12_post-reboot_core.entity_registry.json`
  - `entity_map.json` (optional, enrich canonical lineage)
  - [alpha/omega]_registry.json files

  phases:
  - id: entity_drift_mapping
    nr: 1
    anchor_perspective: post_reboot
    description: >
      'Entity drift detection is performed using the **post-reboot entity registry as the source of truth**.'
    match_precedence:
    - method: device_id + entity_id similarity
      label: primary
      confidence_range: 0.94–1.00

    - method: unique_id match
      label: secondary
      confidence_range: 0.90–0.98

    - method: fuzzy name + area + platform/device_class
      label: fallback
      confidence_range: 0.70–0.88
      action_flag: review

    output_contract:
    - old_id: binary_sensor.foxy_motion_β
      new_id: binary_sensor.foxy_motion_β_v2
      match_type: primary | secondary | fallback
      confidence_score: 0.94
      confidence_explanation: "device_id match + entity_id token alignment"
      canonical_id: foxy_motion_canonical
      action_flag: patch_safe | review

    deliverables:
    - `entity_id_drift_report.yaml`
    - `confidence_manifest.yaml`
    - `unmatched_entities.yaml` (optional)

  - id: canonical_registry_propagation
    nr: 2
    action: >
      'For each `action_flag: patch_safe`, replace stale entity_id in `prompt.artifacts`'
    rules:
    - Do not overwrite `canonical_id` unless match\_type: primary or secondary with exact UID
    - Preserve `confidence_metrics`, metadata (`created`, `contributor`, `tier_origin`)
    - Annotate with: >
        last_updated: 2025-06-12_phase2_rebuild
      lang: yaml
    outputs:
    - Updated `*_registry.json`
    - `patch_manifest.yaml`
    - One inline diff preview per file
    example: |
      '```diff'
      '#Example: omega_device_registry.json'
      '- entity_id: binary_sensor.foxy_motion_β'
      '+ entity_id: binary_sensor.foxy_motion_β_v2'
      '```'
    - protocols:
      ids: evaluation_protocol_v1
    - safeguards:
      validation_gates:
        - validator_log.json must contain 0 errors
        - manifest.sha256 must match emitted files
        - 95%+ matches must be marked patch_safe
        - If any confidence_score missing: abort and emit reason
      fail_mode_enforcement:
        - fail_if_confidence_missing: true
        - halt_on_ambiguous_match: true
        - emit_if_patch_manifest_unavailable: false

    activation_phrase: >
      'Begin canonical registry reconciliation from 25-06-12_post-reboot_core.entity_registry.json'

