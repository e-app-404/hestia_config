---
id: prompt_20250906_08abb7
slug: meta-capture
title: 'Promptset for capturing and organizing system/network/device configuration'
date: '2025-09-06'
tier: "α"
domain: config
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: archivist/meta_capture.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.973382'
redaction_log: []
---

promptset:
  id: meta_capture.promptset.v1
  version: 1
  version_semver: 1.0.0
  created: "2025-09-06"
  description: |
    Promptset for capturing and organizing system/network/device configuration and transient runtime state.
    Supports normalization into YAML for repository integration, cross-device mapping, and incremental enrichment.
  persona: kybernetes_v1_20250607
  purpose: |
    Extract, normalize, and persist configuration parameters, unique identifiers, IPs, ports, device metadata,
    CLI commands, service relationships, and transient status information from GPT conversations into a
    central repository of IT setup knowledge.
  legacy_compatibility: false
  schema_version: 1.0

  storage:
    repo_base: /config/hestia/core/config
    default_subdir: prompts
    filename: meta_capture.promptset.v1.yaml

  artifacts:
    required:
      - path: /mnt/data/system_instruction.yaml
    optional:
      - path: /mnt/data/prompt_registry.md
      - path: /mnt/data/persona_registry.yaml
      - path: /mnt/data/prompt_tests.yaml

  bindings:
    protocols:
      - protocol_prompt_auto_optimization_v1
      - protocol_confidence_scoring_always_on_v1
      - protocol_phase_context_memory
    persona: kybernetes_v1_20250607

  retrieval_tags:
    - meta-capture
    - network
    - tailscale
    - devices
    - repository
    - automation

  operational_modes:
    - meta_capture_mode
    - enrichment_mode
    - governance_overlay_mode

  prompts:
    - id: meta_capture.session_seed.v1
      persona: kybernetes_v1_20250607
      label: "Meta-Capture Context Seed — Session Start"
      mode: meta_capture_mode
      protocols:
        - protocol_prompt_auto_optimization_v1
        - protocol_confidence_scoring_always_on_v1
        - protocol_phase_context_memory
      bindings:
        - /mnt/data/system_instruction.yaml
      prompt: |
        version: 1.0
        Activate meta-capture mode. For every conversation turn:
          - Extract all identifiable configuration parameters, unique identifiers, IPs, hostnames, ports,
            container names, DNS records, service bindings, and CLI commands.
          - Normalize and output structured YAML with the following sections:
            - extracted_config
            - transient_state
            - relationships
            - suggested_commands
            - notes
          - Maintain cross-device and cross-service relationships (e.g., device → service → port).
          - Ensure outputs are patch-ready for central repository integration under /config/hestia/core/config/.
      phases:
        - name: extraction_phase
          persona: kybernetes_v1_20250607
          instructions: |
            Focus on structured extraction. Capture config/state data from user queries and responses.
          outputs:
            - name: extracted_config.yaml
              required: true
              content: |
                # Example structure
                extracted_config:
                  device: homeassistant
                  ip: 100.105.130.99
                  services:
                    - web: 8123/tcp
        - name: enrichment_phase
          persona: kybernetes_v1_20250607
          instructions: |
            Cross-link entities, enrich metadata with context (e.g., Tailscale status, DNS mappings, service health).
          outputs:
            - name: enriched_context.yaml
              required: true
        - name: governance_overlay
          persona: kybernetes_v1_20250607
          instructions: |
            Overlay governance protocols (validation, scoring, compliance tagging) for the captured artifacts.
          outputs:
            - name: governance_overlay_report.md
              required: false

    - id: meta_capture.session_seed.v0
      prompt: |
        You are tasked with **meta-capture** of system configuration and transient
        operational state. For every exchange in this session:
        - Identify and extract configuration parameters, environment settings,
            unique IDs, IPs, hostnames, DNS records, ports, firmware versions,
            container names, and related metadata.
        - Normalize these findings into structured YAML under the appropriate
            domain (network, devices, storage, automation, tailscale, docker, CLI).
        - Preserve relationships (e.g., device → service → port, container →
            image → volume mount).
        - Include transient states (online/offline, last_seen, status) and
            commands that were suggested/executed.
        - Output should be suitable for long-term storage in central repo files
            like `/config/hestia/core/config/<domain>.conf`.

        Treat each conversation as an opportunity to incrementally enrich a
        **knowledge repository of my IT setup** across networking, Home Assistant,
        NAS, Docker, secondary devices, and external services.

    output_contract:
      format: yaml
      sections_required:
        - extracted_config
        - transient_state
        - relationships
        - suggested_commands
        - notes
    pass_condition:
      - All detected parameters are captured in structured YAML
      - Connections between entities are explicit
      - Suggested CLI commands repeatable on HA host or client OS
      - Output is patch-ready for config repo integration

  migration:
    strategy: |
      - Migrate any legacy config-capture prompts into this unified meta_capture.promptset.v1.
      - Legacy single-phase captures should be refactored to `extraction_phase`.
      - Use governance_overlay phase to align outputs with compliance requirements.

  extensibility:
    - Extend with domain-specific promptsets (e.g., `networking.promptset`, `storage.promptset`) that inherit
      from meta_capture.promptset.
    - Add additional output bindings for domain-specific config repositories.

  documentation:
    - Reference: /config/hestia/library/prompts/_meta/promptset_schema.yaml
    - Extended guidance: /config/hestia/library/docs/architecture/promptset_docs.md

