---
id: prompt_20250605_7737a6
slug: batch6-mac-import-id-full-scope-execution-refactor
title: Batch6 Mac Import Id Full Scope Execution Refactor Motion Occupancy Presence
date: '2025-06-05'
tier: "\u03B2"
domain: operational
persona: nomia
status: candidate
tags: []
version: '1.0'
source_path: batch6_mac-import_id-full_scope_execution_refactor_motion-occupancy-presence.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:22.747032'
redaction_log: []
---

Begin **full-scope execution** of motion, occupancy, and presence sensor refactoring using validated source artifacts and canonicalized directory structure under `/config/hestia`.

**Execution Mode:** `generate`
**Signoff Policy:** `auto_affirm_with_prompt`
**Directory Context:** Fully aligned to:
- `sensor: !include_dir_merge_named hestia/sensors/alpha`
- `template: !include_dir_merge_named hestia/inference`
- `binary_sensor: !include_dir_merge_named hestia/logic`

---

**Directives:**

1. **Do not pause or await confirmation.**
   - Proceed until:
     - All refactoring goals are completed
     - OR failure/oversight is fully documented in `tools/validation_tools/validator_log.json` with phase markers.

2. **Logging & Monitoring:**
   - Emit inline execution logs after every 3 files.
   - Track and append:
     - `confidence_metrics` block (structural, operational, semantic)
     - `hallucination_probability` (`p`) per file

3. **Auto-Recalibration Rules:**
   - If `confidence.structural < 0.85` OR remains `< 0.90` over 2 files:
     - Halt briefly to re-read the motion refactoring doctrine
     - Re-align execution stack with latest `motion_sensor_refactoring_POA_2025-06-05.md`

4. **Hallucination Threshold:**
   - `p < 0.10` is strictly enforced. Escalate violations to `validator_log.json`.

---

Upon completion, validate that the following files exist and are correctly placed:

- `sensors/alpha/motion.yaml`
- `inference/motion_inference.yaml`
- `inference/occupancy_inference.yaml`
- `logic/presence_logic.yaml`
- `logic/climate_zone.yaml`
- `logic/automation_triggers.yaml`
- `templates/template.library.jinja`

Trigger `configuration.yaml` stub export if post-placement success is confirmed.

