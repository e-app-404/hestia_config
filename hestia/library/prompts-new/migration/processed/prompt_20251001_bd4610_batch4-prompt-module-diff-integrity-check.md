---
id: prompt_20251001_bd4610
slug: batch4-prompt-module-diff-integrity-check
title: Batch4 Prompt Module Diff Integrity Check
date: '2025-10-01'
tier: "\u03B2"
domain: validation
persona: nomia
status: candidate
tags: []
version: '1.0'
source_path: batch 4/batch4-prompt_module-diff_integrity_check.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.916099'
redaction_log: []
---

phase: diff_integrity_check
action: audit_refactor_information_integrity
validation_status: pending
goals:
  - Ensure that all semantically meaningful components from the original YAML are accounted for in the refactor
  - Detect and flag information loss or silent omission of operational logic
  - Confirm that each retained or modified block adds clarity, abstraction, or structural improvement
evaluation_criteria:
  - Any removed entity must be justified with a design rationale
  - Any renamed or refactored element must preserve functional equivalence or improve role expressiveness
  - New elements must be additive or consolidative, not duplicative
required_inputs:
  - source_file: ha-networking-configuration.yaml
  - refactored_file: <refactored_output>.yaml
next_steps:
  - Run semantic diff between source and refactored sensor blocks
  - Identify tier shifts, role migrations, or deleted logic
  - Emit lineage map: source_id → refactored_id with change reason
affirmation_template:
  proceed: Proceed to source-to-refactor lineage mapping and data flow traceability audit.
  pause: Pause and surface justification for removed or transformed components.

