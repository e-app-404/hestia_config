---
id: prompt_20250916_f2cc56
slug: ha-log-analysis
title: '|'
date: '2025-09-16'
tier: "α"
domain: operational
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: diag/ha_log_analysis.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.889565'
redaction_log: []
---

promptset:
  id: homeassistant.log_analysis.v1
  version: 1.0
  created: "2025-09-16"
  description: |
    Structured promptset for Home Assistant log analysis and error-driven debugging. Supports multi-phase workflows, governance, and technical changelog modes. Designed for use with Copilot/GPT-4.1.
  persona: ha_debug_persona
  purpose: |
    Enable systematic parsing, synthesis, and resolution of Home Assistant log errors. Prioritize issues, scaffold patch plans, and guide operator-driven hardening.
  legacy_compatibility: true
  schema_version: 1.0

  artifacts:
    required:
      - path: /Volumes/HA/config/home-assistant.log
      - path: /Volumes/HA/config/home-assistant.log.1
    optional:
      - path: /Volumes/HA/config/domain/templates/**/*.yaml
      - path: /Volumes/HA/config/custom_components/**/*.py
      - path: /Volumes/HA/config/hestia/workspace/prompt_registry/catalog/draft_template.promptset
    # Use glob patterns for extensibility

  bindings:
    protocols:
      - prompt_optimization_first
      - confidence_scoring_always
      - phase_context_memory
    persona: ha_debug_persona

  retrieval_tags:
    - log_analysis
    - error_audit
    - patch_plan
    - governance
    - changelog

  operational_modes:
    - governance_review_mode
    - technical_changelog_mode
    - custom_mode

  prompts:
    - id: ha.log_analysis.multi_phase
      persona: ha_debug_persona
      label: "Home Assistant Log Analysis — Multi-Phase"
      mode: technical_changelog_mode
      protocols:
        - prompt_optimization_first
        - confidence_scoring_always
        - phase_context_memory
      bindings:
        - /Volumes/HA/config/home-assistant.log
        - /Volumes/HA/config/home-assistant.log.1
      prompt: |
        version: 1.0
        Parse all home-assistant.log* files, focusing on entries from the last hour, 24 hours, and up to one week (adjusting the time window based on error frequency and Home Assistant restart events).

        1. **Methodology:**  
           - Parse and group log entries by error/warning type, component, and timestamp.
           - Synthesize recurring errors into main "Issues" (an Issue may consist of multiple related error instances).
           - For each Issue, provide:
             - Impact assessment (effect on HA runtime, data loss, integration failures, etc.)
             - Debugging difficulty (simple config, code patch, multi-component, etc.)
             - Coding language(s) and components involved.
             - Frequency and recency of occurrence.
           - Flag configuration errors (e.g., duplicate IDs, invalid YAML) separately from code errors.
           - Ignore warnings about untested custom integrations unless they directly impact runtime or stability.
           - For complex or multi-component errors, visualize dependencies (e.g., recorder → history/logbook/energy) in the output.
           - Include links to relevant documentation or error references for complex issues.

        2. **Prioritization:**  
           - Rank Issues by severity, runtime impact, and complexity.
           - Note dependencies (e.g., recorder errors blocking history/logbook/energy).

        3. **Patch Plan Scaffold:**  
           - For each prioritized Issue, outline a patch plan:
             - Identify referenced code/config files.
             - Retrieve and inspect relevant code snippets.
             - Propose targeted fixes or configuration changes.
             - Note any required follow-up (e.g., integration updates, dependency checks).
             - Recommend automated tests or validation steps after patching.

        4. **Mini-Prompt for Operator:**  
           - “Using the synthesized error audit and patch plan, walk the workspace to retrieve and inspect the referenced code/config files. For each Issue, propose and apply a targeted fix, then validate resolution in the logs. Suggest further hardening steps if needed.”

        5. **Final Output:**  
           - Present a fully resolved patch plan, referencing actual code/config changes, ready for operator review and implementation.

      phases:
        - name: log_audit
          persona: ha_debug_persona
          instructions: |
            Parse log files, group and synthesize errors, reconstruct main Issues, and score for runtime impact.
          outputs:
            - name: error_audit.md
              required: true
              content: |
                # Error Audit (Phase 1)
                ...
        - name: patch_scaffold
          persona: ha_debug_persona
          instructions: |
            For each Issue, walk the workspace, retrieve referenced code/config files, and scaffold a patch plan.
          outputs:
            - name: patch_plan.md
              required: true
              content: |
                # Patch Plan (Phase 2)
                ...
        - name: operator_hardening
          persona: ha_debug_persona
          instructions: |
            Guide operator through targeted fixes, validation, and further hardening.
          outputs:
            - name: operator_guidance.md
              required: true
              content: |
                # Operator Guidance (Phase 3)
                ...

  migration:
    strategy: |
      - Map legacy log parsing and error grouping to new multi-phase structure.
      - Use legacy_compatibility: true to signal support.
      - Reference canonical schema for validation.

  extensibility:
    - To add new prompt types, phases, or operational modes, copy and adapt the relevant example block.
    - Link new artifacts, protocols, and outputs as needed.
    - Specify artifact resolution order: required > optional > globs.

  documentation:
    - Reference: /mnt/data/promptset_schema.yaml
    - For extended guidance, see /mnt/data/promptset_docs.md
    - Comments are limited to essential guidance; maintain extended docs separately.
