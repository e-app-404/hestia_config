---
id: prompt_20250906_08abb7
slug: meta-capture
title: 'Promptset for capturing and organizing system/network/device configuration'
date: '2025-09-06'
tier: "α"
domain: config
persona: none
status: active
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
  persona: none
  purpose: |
    Extract, normalize, and persist configuration parameters, unique identifiers, IPs, ports, device metadata,
  CLI commands, service relationships, and transient status information from conversations into a
    central repository of IT setup knowledge.
  legacy_compatibility: false
  schema_version: 1.0

  storage:
    # Use canonical hestia/config location (ADR-0024 compliance)
    repo_base: /config/hestia/config
    default_subdir: prompts
    filename: meta_capture.promptset.v1.yaml

  artifacts:
    required: []
    optional:
      - path: /mnt/data/prompt_registry.md
      - path: /mnt/data/persona_registry.yaml
      - path: /mnt/data/prompt_tests.yaml

  bindings:
    protocols: []
    persona: none

  topics_index:
    - topic: system
      path: /config/hestia/config/system/system.conf
    - topic: storage
      path: /config/hestia/config/storage/storage.conf
    - topic: network
      path: /config/hestia/config/network/network.conf
    - topic: devices
      path: /config/hestia/config/devices/devices.conf
    - topic: diagnostics
      path: /config/hestia/config/diagnostics/diagnostics.conf
    - topic: preferences
      path: /config/hestia/config/preferences/preferences.conf
    - topic: cli
      path: /config/hestia/config/system/cli.conf

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
      persona: none
      label: "Meta-Capture Context Seed — Session Start"
      mode: meta_capture_mode
      protocols: []
      bindings: []
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
          - Ensure outputs are patch-ready for central repository integration under /config/hestia/config/.
      phases:
        - name: extraction_phase
          persona: none
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
          persona: none
          instructions: |
            Cross-link entities, enrich metadata with context (e.g., Tailscale status, DNS mappings, service health).
          outputs:
            - name: enriched_context.yaml
              required: true
        - name: governance_overlay
          persona: none
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
            like `/config/hestia/config/<domain>.conf`.

    - id: meta_capture.exporter.claude.v1
      label: "Claude Exporter — Topics → YAML files"
      mode: meta_capture_mode
      protocols: []
      bindings: []
      prompt: |
        Produce a deterministic YAML export of all stored/session knowledge for the requested topics
        (any of: system, storage, network, devices, diagnostics, preferences, cli).

        Path mapping (authoritative):
          - system → /config/hestia/config/system/system.conf
          - storage → /config/hestia/config/storage/storage.conf
          - network → /config/hestia/config/network/network.conf
          - devices → /config/hestia/config/devices/devices.conf
          - diagnostics → /config/hestia/config/diagnostics/diagnostics.conf
          - preferences → /config/hestia/config/preferences/preferences.conf
          - cli → /config/hestia/config/system/cli.conf

        Output contract (single YAML document):
          exports:
            - topic: <one of above>
              target_path: <canonical path from mapping>
              file_format: yaml
              content: |
                # topic-specific schema follows
        Schemas:
          system.system.conf:
            system:
              hostnames: []
              services: {}
              env: {}
              notes: []
          storage.storage.conf:
            storage:
              volumes: []
              backups: []
              notes: []
          network.network.conf:
            network:
              interfaces: []
              addresses: []
              dns: []
              routes: []
              notes: []
          devices.devices.conf:
            devices:
              inventory: []
              relationships: []
              notes: []
          diagnostics.diagnostics.conf:
            diagnostics:
              checks: []
              recent_errors: []
              notes: []
          preferences.preferences.conf:
            preferences:
              ui: {}
              automations: {}
              notes: []
          system.cli.conf:
            cli:
              commands: []  # {name, command, purpose, related: [topics]}

        Rules:
          - No external personas or files are required; this prompt is self-contained for Claude.
          - If a field is unknown, omit it or set to empty list/map.
          - Use 2-space indent, LF line endings, and valid YAML.
          - Do not fabricate secrets; redacted placeholders are allowed (e.g., __REDACTED__).
          - If user specifies topics, export only those; otherwise export all topics you can populate.

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
  - Output is patch-ready for config repo integration under /config/hestia/config/

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

