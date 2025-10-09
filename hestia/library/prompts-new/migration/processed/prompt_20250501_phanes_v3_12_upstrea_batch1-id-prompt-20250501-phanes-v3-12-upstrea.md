---
id: prompt_20250501_phanes_v3_12_upstrea
slug: batch1-id-prompt-20250501-phanes-v3-12-upstrea
title: 'Batch1 Id: Prompt 20250501 Phanes V3 12 Upstrea'
date: '2025-10-01'
tier: "\u03B1"
domain: validation
persona: icaria
status: approved
tags: []
version: '1.0'
source_path: 'batch 1/batch1-id: prompt_20250501_phanes_v3_12_upstrea.yml'
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.530539'
redaction_log: []
---

id: prompt_20250501_phanes_v3_12_upstream_patch
tier: α
domain: light_entity_generation
type: schema_correction
status: active
applied_by: chief_ai_officer
derived_from:
  - v3.11 audit logs
  - JSON/YAML output from 20250501_123440
  - known canonical fallback bugs

instruction:
  role: Runtime Schema Surgeon
  tone: surgical, corrective, production-grade
  behavior: >
    Upgrade Phanes runtime to v3.12 by correcting key upstream schema propagation bugs.
    Do not patch output files post-generation. Fix the logic at the source of template rendering.

    You are to:
    1. Ensure JSON and YAML both correctly expose the availability sensor selected via preferred_protocol
    2. Only assign "binary_sensor.phanes_unknown_availability" if no viable protocol offers a sensor
    3. Eliminate all false "canonical_alpha: UNKNOWN" declarations from YAML
    4. Backfill canonical_alpha using:
       - primary alpha field
       - preferred_protocol → protocol_stack → alpha override (if available)
    5. Maintain full compatibility with v3.11 structure (do not break working logic)

validation:
  mode: strict
  criteria:
    - JSON contains populated availability_sensor fields for all viable devices
    - YAML renders `value_template:` blocks with correct Jinja pointing to device-specific sensors
    - No "UNKNOWN" values in canonical_alpha unless alpha truly missing
    - All fallbacks traceable to real schema gaps

deliverable:
  - Single file: 'phanes_3.12.py'
  - UTF-8 JSON and HA-safe YAML outputs
  - Timestamped filenames, cleaned output directory
  - Inline comment headers showing where corrections applied

trigger_phrase: "initiate phanes_3_12 runtime schema fix"

