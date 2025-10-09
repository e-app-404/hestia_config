---
id: prompt_20251008_6e0dad
slug: sql-room-database-architecture-promptset-v12-strat
title: "SQL Room Database Architecture \u2014 Promptset v1.2 (Strategos)"
date: '2025-10-08'
tier: "\u03B1"
domain: governance
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: sql_room_db/sql_room_db_v1.2.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.026602'
redaction_log: []
---

# SQL Room Database Architecture — Promptset v1.2 (Strategos)

> Applied diffs from v1.1 review: two-column SQL results with attribute payloads, JSON1 preflight, heredoc transactional writes, platform-level scan interval, recorder hygiene, canonical topic + room ID, strengthened self-checks.

```yaml
promptset:
  id: sql-room-database-architecture.promptset
  version: 1.2
  created: "2025-10-08"
  description: >
    Production-grade, 5-phase execution plan to replace HACS Variable with a
    SQL-backed room database for Adaptive Motion Lighting + Valetudo Vacuum Control.
    Enforces HA state-size limits, attribute-based JSON payloads, transaction-safe writes,
    JSON1 preflight, and ADR compliance. Target: ≥70% entity reduction with zero feature loss.

  persona: strategos_gpt
  legacy_compatibility: false
  schema_version: 1.0

  execution_context:
    model: "GPT-5 Extended Thinking"
    mandate: "Replace 70+ helper entities with <10 SQL-backed access points"
    success_criteria:
      - "Copy-paste deployable packages; config check passes"
      - "≥70% entity reduction; identical behavior preserved"
      - "SQL query p50 < 100ms; updates < 200ms"
      - "ADR-0008 / ADR-0021 / ADR-0024 compliant"

  globals:
    timezone: "Europe/London"
    ha_state_char_limit: 255
    naming:
      sql_sensors:
        motion: "sensor.room_configs_motion_lighting"       # plural 'room_configs'
        vacuum: "sensor.room_configs_vacuum_control"
        cleaning_need: "sensor.rooms_needing_cleaning"
    recorder_db_default: false              # Use dedicated /config/room_database.db
    scan_interval_seconds: 30               # Bound DB load (platform-level)
    json1_required_functions: ["json_extract", "json_group_object", "json_group_array", "json_valid"]
    valetudo_base_topic_var: "valetudo_base_topic"  # single source of truth (secret or input_text)
    room_id_pattern: "^[a-z0-9_]+$"               # slugified room IDs

  artifacts:
    required:
      - { description: "Adaptive motion lighting package", path: /mnt/data/adaptive_motion_lighting/ }
      - { description: "Valetudo vacuum control package", path: /mnt/data/valetudo/ }
      - { description: "HA SQL integration guide", path: /mnt/data/homeassistant_sql_integration_guide.md }
      - { description: "SQLite usage & performance", path: /mnt/data/sqlite_homeassistant_patterns.md }
      - { description: "Normalization & determinism rules", path: /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md }
      - { description: "Motion/occupancy/presence governance", path: /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md }
      - { description: "Canonical path requirements", path: /mnt/data/ADR/ADR-0024-canonical-config-path.md }
      - { description: "Canonical mappings", path: /mnt/data/architecture/{area_mapping.yaml,presence_mapping.yaml,tier_mapping.yaml} }
    consulted:
      - { path: /mnt/data/hestia_structure.md, description: "Package placement conventions" }
      - { path: /mnt/data/enhanced-motion-lighting-config.promptset, description: "Prior motion architecture" }
      - { path: /mnt/data/valetudo_optimization_comprehensive_v2.promptset, description: "Vacuum integration patterns" }

  bindings:
    protocols:
      - sql_database_first_architecture
      - room_scoped_data_modeling
      - entity_reduction_optimization
      - production_grade_validation
      - adr_compliance_enforcement
    hard_guardrails:
      - "Every SQL query MUST return two columns: a short STATE column ('state' or 'count') and a JSON ATTRIBUTE column named 'payload'."
      - "For each query, 'column:' MUST select 'state' (or 'count'); JSON MUST be exposed only via attribute 'payload' using the SQL sensor 'attributes' mapping."
      - "DO NOT store JSON in sensor state; JSON must be an ATTRIBUTE named 'payload'."
      - "Numeric_state conditions MUST NOT template thresholds; use template condition instead."
      - "Writes MUST NOT target recorder DB; use /config/room_database.db (unless explicitly toggled)."
      - "All write paths MUST be transactional (BEGIN IMMEDIATE…COMMIT) and shell-quoting safe."
      - "Shell fallback MUST use a heredoc to pass JSON (no nested quoting); preferred path is AppDaemon/Node-RED/Python service."
      - "Sensors MUST specify platform-level scan_interval: {{ scan_interval_seconds }}."
      - "Names MUST match globals.naming.* exactly."
      - "If SQLite JSON1 is missing, generate a normalized schema fallback and switch queries."
      - "room_id MUST be slugified: {{ room_id_pattern }} and sourced from a canonical mapping file."
      - "Valetudo MQTT base topic MUST be defined once as {{ valetudo_base_topic_var }} and referenced everywhere."

  retrieval_tags: [sql_architecture, room_database, entity_reduction, motion_lighting, vacuum_control, home_assistant, database_design]
  operational_modes: [research_mode, deconstruction_mode, architecture_mode, implementation_mode, validation_mode]

  response_contracts:
    research_foundation_shape:
      keys: [sql_capabilities, sqlite_patterns, current_architecture, consolidation_opportunities, governance_constraints]
    deconstruction_shape:
      keys: [adaptive_lighting_core, valetudo_core, consolidation_targets, gui_compatibility_matrix]
    architecture_shape:
      keys: [database_schema, sql_sensors, update_mechanisms, template_functions, package_structure, integration_strategy, migration_strategy]
    implementation_outputs:
      files:
        - "/config/packages/room_database/sql_sensors.yaml"
        - "/config/packages/room_database/shell_commands.yaml"
        - "/config/packages/room_database/database_init.sql"
        - "/config/packages/motion_lighting_v2/automations.yaml"
        - "/config/packages/motion_lighting_v2/templates.yaml"
        - "/config/packages/vacuum_control_v2/scripts.yaml"
        - "/config/packages/vacuum_control_v2/mqtt_commands.yaml"
    validation_shape:
      keys: [acceptance_criteria, diagnostics_templates, migration_tokens, rollback_procedures, performance_benchmarks]

  non_negotiables:
    - "SQL sensors return: short state ('ok' or int 'count') + attribute 'payload' JSON; additional 'count' where relevant."
    - "Read via state_attr('…','payload') | from_json only."
    - "Valetudo topics are configurable; expose a single macro/variable for the base topic."
    - "Presence modulates timeouts (ADR-0021), never blocks activation."
    - "All write paths escape JSON with tojson; avoid bash-only constructs; prefer /bin/sh or AppDaemon/Node-RED."

  prompts:

    - id: sql_room_db.research.foundation
      persona: strategos_gpt
      label: "Research — SQL Patterns & Package Inventory"
      mode: research_mode
      protocols: [sql_database_first_architecture, production_grade_validation]
      bindings:
        - /mnt/data/homeassistant_sql_integration_guide.md
        - /mnt/data/sqlite_homeassistant_patterns.md
        - /mnt/data/adaptive_motion_lighting/
        - /mnt/data/valetudo/
        - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
      prompt: |
        Produce `research_foundation` strictly matching response_contracts.research_foundation_shape.
        Explicitly list SQL integration SELECT-only constraints, JSON1 functions used, and recorder-vs-dedicated DB tradeoffs.
        Identify Variable-based entities that are clear SQL consolidation targets.
        CONFIDENCE: [n]%

    - id: sql_room_db.deconstruction.objectives
      persona: strategos_gpt
      label: "Deconstruction — Feature Extraction & Mapping"
      mode: deconstruction_mode
      protocols: [room_scoped_data_modeling, entity_reduction_optimization]
      bindings:
        - /mnt/data/adaptive_motion_lighting/
        - /mnt/data/valetudo/
        - /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md
        - /mnt/data/architecture/area_mapping.yaml
      prompt: |
        Produce `deconstruction_analysis` matching response_contracts.deconstruction_shape.
        Include lists of per-room timeouts, bypasses, illuminance thresholds (if discoverable), and MQTT topics/payload shapes for Valetudo.
        Flag any GUI dependencies that require attribute payloads (no JSON in state).
        CONFIDENCE: [n]%

    - id: sql_room_db.architecture.scaffold
      persona: strategos_gpt
      label: "Architecture — Unified Schema & Integration"
      mode: architecture_mode
      protocols: [sql_database_first_architecture, room_scoped_data_modeling, adr_compliance_enforcement]
      bindings:
        - /mnt/data/homeassistant_sql_integration_guide.md
        - /mnt/data/sqlite_homeassistant_patterns.md
        - /mnt/data/ADR/ADR-0024-canonical-config-path.md
        - /mnt/data/architecture/tier_mapping.yaml
      prompt: |
        Deliver `architecture_design` matching response_contracts.architecture_shape with:
        - Schema: `room_configs` table + index; PRAGMAs (WAL/NORMAL) and `schema_version` meta table.
        - JSON1-first design AND a normalized fallback (if preflight fails).
        - Preflight (NOT a sensor): run `sqlite3 /config/room_database.db "PRAGMA compile_options;"` and assert 'JSON1' present (case-insensitive). If absent, switch to normalized schema and alternate sensors.
        - SQL sensors: platform-level `scan_interval: {{ scan_interval_seconds }}`. Each query returns `state`/`count` and `payload` columns; `column:` points to the short column; map `payload` via `attributes`.
        - Update mechanisms:
          * Preferred: AppDaemon/Node-RED/Python endpoint (transactional, validation, logging).
          * Fallback: /bin/sh shell_command using heredoc with `BEGIN IMMEDIATE; ...; COMMIT;` and `tojson`.
        - Template accessors use `state_attr(...,'payload')` only.
        - Package structure under /config/packages in ADR-0024 layout.
        - Integration strategy noting `scan_interval`, error handling, and `recorder_policy` below.
        - recorder_policy:
            include:
              entities: []
            exclude:
              entity_globs:
                - sensor.room_configs_*
                - sensor.rooms_needing_cleaning
            note: "Avoid recorder bloat from large attribute payloads."
        CONFIDENCE: [n]%

    - id: sql_room_db.implementation.packages
      persona: strategos_gpt
      label: "Implementation — Production Packages"
      mode: implementation_mode
      protocols: [production_grade_validation, adr_compliance_enforcement, entity_reduction_optimization]
      bindings:
        - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
        - /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md
        - /mnt/data/hestia_structure.md
      prompt: |
        Emit the files listed in response_contracts.implementation_outputs with these rules:
        - **room_database/sql_sensors.yaml** (single platform entry):
          * `db_url: sqlite:////config/room_database.db`
          * `scan_interval: {{ scan_interval_seconds }}` (platform-level)
          * Three queries:
            - {{ globals.naming.sql_sensors.motion }}: `SELECT 'ok' AS state, json_group_object(room_id, config_data) AS payload ...`; `column: state`; `attributes: { payload: payload }`.
            - {{ globals.naming.sql_sensors.vacuum }}: same shape as above for `vacuum_control`.
            - {{ globals.naming.sql_sensors.cleaning_need }}: `SELECT COALESCE(json_group_array(room_id),'[]') AS payload, json_array_length(COALESCE(json_group_array(room_id),'[]')) AS count ...`; `column: count`; `attributes: { payload: payload }`.
        - **room_database/shell_commands.yaml**:
          * Use `/bin/sh` heredoc; wrap updates in `BEGIN IMMEDIATE; ...; COMMIT;`; JSON via `tojson`; no templated SQL keywords.
        - **room_database/database_init.sql**:
          * CREATE TABLE + INDEX + PRAGMAs; optional `schema_version` table; seed minimal rooms; comment block for normalized fallback schema.
        - **motion_lighting_v2/automations.yaml**:
          * Replace numeric_state threshold with template condition.
          * Read configs via `state_attr('{{ globals.naming.sql_sensors.motion }}','payload')`.
        - **motion_lighting_v2/templates.yaml**:
          * Compatibility sensors reading attributes only.
        - **vacuum_control_v2/scripts.yaml**:
          * MQTT payload built with `tojson`; base topic pulled from `!secret {{ valetudo_base_topic_var }}` or `input_text.{{ valetudo_base_topic_var }}`; mark_room_cleaned via shell_command.
        - **vacuum_control_v2/mqtt_commands.yaml**:
          * Document topic variable; keep deterministic.
        Ensure ADR-0008 formatting and deterministic key order.
        CONFIDENCE: [n]%

    - id: sql_room_db.validation.comprehensive
      persona: strategos_gpt
      label: "Validation — Acceptance & Diagnostics"
      mode: validation_mode
      protocols: [production_grade_validation, adr_compliance_enforcement]
      bindings:
        - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
      prompt: |
        Produce `validation_pack` with:
        - acceptance_criteria: checkbox matrix covering DB init, JSON1 preflight, SQL sensors (attribute payloads), transactional writes, performance budgets, ADR checks, recorder_policy applied.
        - diagnostics_templates: Jinja to verify JSON1 availability (via token), presence of `payload` attributes, and entity reduction math.
        - migration_tokens: sequential tokens for gating (e.g., MIGRATION_TOKEN_JSON1_OK, MIGRATION_TOKEN_SCHEMA_1_APPLIED, ...).
        - rollback_procedures and performance_benchmarks with concrete targets.
        CONFIDENCE: [n]%

  self_checks:
    - "Assert each SQL query SELECTs 'state'|'count' AND 'payload', with column: state|count."
    - "Assert attributes mapping includes payload → payload (and count where applicable)."
    - "Assert no JSON is placed in sensor state; attributes only."
    - "Assert no numeric_state uses templated thresholds."
    - "Assert platform-level scan_interval present on SQL sensor."
    - "Assert names match globals.naming.* everywhere."
    - "Verify JSON1 availability via preflight (not a sensor). If missing, emit normalized fallback + alternate sensors."
    - "Assert write path uses BEGIN IMMEDIATE/COMMIT and passes JSON via heredoc with tojson."
    - "Assert recorder excludes or retention policy applied to bulk JSON sensors."
    - "Assert room_id matches {{ room_id_pattern }} and is sourced from canonical mapping."
    - "Assert all MQTT topics reference the single {{ valetudo_base_topic_var }} value."
```

