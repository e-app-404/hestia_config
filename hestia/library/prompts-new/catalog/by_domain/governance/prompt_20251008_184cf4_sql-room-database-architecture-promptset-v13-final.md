---
id: prompt_20251008_184cf4
slug: sql-room-database-architecture-promptset-v13-final
title: "SQL Room Database Architecture \u2014 Promptset v1.3 (Final, Strategos)"
date: '2025-10-08'
tier: "\u03B1"
domain: governance
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: sql_room_db/sql_room_db_v1.3.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:26.861870'
redaction_log: []
---

# SQL Room Database Architecture — Promptset v1.3 (Final, Strategos)

> **Final hardened promptset**: operator‑proof, ADR‑compliant, and robust to HA/SQLite quirks. This version bakes in all remaining risk controls: JSON-in-attributes only, JSON1 preflight with tokens, transactional heredoc writes, schema version enforcement, canonical room mapping validation (via preferred AppDaemon path), deterministic naming, recorder hygiene, and explicit self‑checks.

````yaml
promptset:
  id: sql-room-database-architecture.promptset
  version: 1.3
  created: "2025-10-08"
  description: >
    Five-phase, production-grade plan to replace HACS Variable with a SQL-backed room database
    for Adaptive Motion Lighting + Valetudo Vacuum Control. Prevents HA state overflows, enforces
    transactional writes, and guarantees deterministic, ADR-compliant outputs. Target: ≥70% entity
    reduction with zero feature loss.

  persona: strategos_gpt
  legacy_compatibility: false
  schema_version: 1.0

  execution_context:
    model: "GPT-5 Extended Thinking"
    mandate: "Replace 70+ helper entities with <10 SQL-backed access points"
    success_criteria:
      - "Copy-paste deployable packages; `ha core check` passes"
      - "≥70% entity reduction; identical behavior preserved"
      - "SQL query p50 < 100ms; update p50 < 200ms"
      - "ADR-0008 / ADR-0021 / ADR-0024 compliant"

  globals:
    timezone: "Europe/London"
    ha_state_char_limit: 255
    naming:
      sql_sensors:
        motion: "sensor.room_configs_motion_lighting"      # plural 'room_configs'
        vacuum: "sensor.room_configs_vacuum_control"
        cleaning_need: "sensor.rooms_needing_cleaning"
    recorder_db_default: false                      # Use dedicated /config/room_database.db
    scan_interval_seconds: 30                       # Platform-level cadence
    json1_required_functions: ["json_extract", "json_group_object", "json_group_array", "json_valid"]
    valetudo_base_topic_var: "valetudo_base_topic"  # One source of truth (secrets or input_text)
    room_id_pattern: "^[a-z0-9_]+$"                 # Slugified room IDs
    tokens_dir: "/config/.sql_room_db_tokens"      # Preflight/migration tokens directory
    schema_expected: 1                               # Expected DB schema_version
    canonical_mapping_file: "/config/architecture/area_mapping.yaml"

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

  bindings:
    protocols:
      - sql_database_first_architecture
      - room_scoped_data_modeling
      - entity_reduction_optimization
      - production_grade_validation
      - adr_compliance_enforcement

    hard_guardrails:
      # HA/SQL Sensor safety
      - "Every SQL query MUST return two columns: a short column named 'state' (or 'count') and a JSON column named 'payload'."
      - "The SQL sensor 'column:' MUST select 'state' (or 'count'). The additional 'payload' column becomes an attribute automatically."
      - "JSON MUST NOT be placed in sensor state; read via state_attr('…','payload') | from_json only."
      - "Numeric_state conditions MUST NOT template thresholds; use template condition instead."
      - "Sensors MUST specify platform-level scan_interval: {{ scan_interval_seconds }}."
      - "Names MUST match globals.naming.* exactly."

      # DB/write safety
      - "Writes MUST NOT target recorder DB (unless explicitly toggled); default is /config/room_database.db."
      - "All write paths MUST be transactional (BEGIN IMMEDIATE…COMMIT)."
      - "Preferred write path: AppDaemon/Node-RED/Python service with validation + logging. Fallback shell MUST use /bin/sh heredoc and `tojson`."
      - "Writes MUST verify schema version == {{ schema_expected }} before mutating data; else abort and notify."
      - "room_id MUST match {{ room_id_pattern }} and MUST exist in {{ canonical_mapping_file }} before writes (validate in preferred path)."

      # Environment & portability
      - "Before creating sensors, run JSON1 preflight (not a sensor). If JSON1 unavailable, generate normalized schema + alternate sensors."
      - "If `sqlite3` binary is absent, generate the preferred AppDaemon/Node-RED path and disable shell fallback."

      # Recorder hygiene & secrets
      - "Recorder excludes MUST be provided to prevent bloat from bulk JSON attributes."
      - "Valetudo topic MUST come from a single value {{ valetudo_base_topic_var }} (prefer !secret)."

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
        - "/config/packages/room_database/shell_commands.yaml"          # shell fallback (disabled if no sqlite3)
        - "/config/packages/room_database/database_init.sql"
        - "/config/packages/room_database/preflight.yaml"              # startup automation + shell_command preflights
        - "/config/packages/room_database/recorder_policy.yaml"        # excludes for bulk sensors
        - "/config/packages/motion_lighting_v2/automations.yaml"
        - "/config/packages/motion_lighting_v2/templates.yaml"
        - "/config/packages/vacuum_control_v2/scripts.yaml"
        - "/config/packages/vacuum_control_v2/mqtt_commands.yaml"
        - "/config/appdaemon/apps/room_db_updater/app.yaml"            # preferred path
        - "/config/appdaemon/apps/room_db_updater/room_db_updater.py"  # preferred path (validation + writes)
        - "/config/.sql_room_db_tokens/README.txt"                     # token semantics
        - "/config/secrets.example.yaml"                               # valetudo_base_topic stub
    validation_shape:
      keys: [acceptance_criteria, diagnostics_templates, migration_tokens, rollback_procedures, performance_benchmarks]

  non_negotiables:
    - "Platform-level `scan_interval` on SQL sensor; three queries only (motion, vacuum, cleaning_need)."
    - "Two-column SELECT with 'state'/'count' + 'payload' always; 'column:' is 'state' or 'count'."
    - "Template access uses state_attr('…','payload') | from_json exclusively."
    - "Presence modulates timeouts (ADR-0021), never blocks activation."
    - "Writes are transactional and schema-guarded; failures raise persistent_notification and DO NOT mutate data."
    - "Recorder excludes applied for sensor.room_configs_* and sensor.rooms_needing_cleaning."

  prompts:

    # PHASE 1 — Research
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
        Produce `research_foundation` matching response_contracts.research_foundation_shape.
        Include: SELECT-only constraints; JSON1 functions; recorder vs dedicated DB tradeoffs; obvious Variable → SQL consolidation targets.
        CONFIDENCE: [n]%

    # PHASE 2 — Deconstruction
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
        Produce `deconstruction_analysis` per response_contracts.deconstruction_shape.
        List per-room timeouts/bypasses/illuminance thresholds (if discoverable) and Valetudo topics/payload shapes.
        Flag GUI dependencies needing attribute payloads (no JSON in state).
        CONFIDENCE: [n]%

    # PHASE 3 — Architecture
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
        Deliver `architecture_design` per response_contracts.architecture_shape with:
        - DB schema:
          * `room_configs(room_id, config_domain, config_data TEXT, version INT, created_at, updated_at)`; PK(room_id, config_domain)
          * Index: (config_domain, room_id)
          * PRAGMAs: WAL; synchronous=NORMAL
          * `schema_version(version INT NOT NULL)` with initial value {{ schema_expected }}
        - JSON1 preflight (NOT a sensor):
          * Create {{ tokens_dir }} if missing
          * Run: `sqlite3 /config/room_database.db "PRAGMA compile_options;"` and check for 'JSON1' case-insensitive
          * If present → touch `{{ tokens_dir }}/MIGRATION_TOKEN_JSON1_OK`
          * If absent → touch `{{ tokens_dir }}/MIGRATION_TOKEN_JSON1_MISSING` and generate normalized fallback schema + alternate sensors (no JSON functions)
        - SQL sensors (single platform entry):
          * `db_url: sqlite:////config/room_database.db`
          * `scan_interval: {{ scan_interval_seconds }}`
          * Three queries, each returning 'state'/'count' + 'payload'; `column:` selects the short column.
          * Note: extra 'payload' column automatically becomes an attribute in HA.
        - Update mechanisms:
          * Preferred: AppDaemon app `room_db_updater` providing services to read/validate canonical mapping ({{ canonical_mapping_file }}), verify schema_version, and perform writes under one transaction; logs failures and raises notifications.
          * Fallback: /bin/sh `shell_command` heredoc with BEGIN IMMEDIATE/COMMIT; checks `sqlite3 --version` and aborts if missing; schema_version check included.
        - Template accessors: ONLY use `state_attr(...,'payload')`.
        - Recorder policy: exclude `sensor.room_configs_*` and `sensor.rooms_needing_cleaning`.
        - Package structure: under /config/packages per ADR-0024.
        CONFIDENCE: [n]%

    # PHASE 4 — Implementation
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
        Emit the files in response_contracts.implementation_outputs with these rules and examples:

        **/config/packages/room_database/sql_sensors.yaml** (single platform):
        ```yaml
        sensor:
          - platform: sql
            db_url: sqlite:////config/room_database.db
            scan_interval: {{ scan_interval_seconds }}
            queries:
              - name: "Room Configs — Motion Lighting"
                query: >
                  SELECT 'ok' AS state,
                         json_group_object(room_id, config_data) AS payload
                  FROM room_configs
                  WHERE config_domain = 'motion_lighting';
                column: state
              - name: "Room Configs — Vacuum Control"
                query: >
                  SELECT 'ok' AS state,
                         json_group_object(room_id, config_data) AS payload
                  FROM room_configs
                  WHERE config_domain = 'vacuum_control';
                column: state
              - name: "Rooms Needing Cleaning"
                query: >
                  SELECT COALESCE(json_group_array(room_id),'[]') AS payload,
                         json_array_length(COALESCE(json_group_array(room_id),'[]')) AS count
                  FROM room_configs
                  WHERE config_domain = 'vacuum_control'
                    AND json_extract(config_data, '$.needs_cleaning') = 1;
                column: count
        ```

        **/config/packages/room_database/shell_commands.yaml** (fallback only):
        ```yaml
        shell_command:
          update_room_config: >-
            /bin/sh -c 'command -v sqlite3 >/dev/null 2>&1 || exit 123; sqlite3 /config/room_database.db <<"SQL"\nBEGIN IMMEDIATE;\nSELECT CASE WHEN (SELECT version FROM schema_version)={{ schema_expected }} THEN 1 ELSE RAISE(ABORT,"SCHEMA_VERSION_MISMATCH") END;\nINSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at)\nVALUES ("{{ room_id }}","{{ domain }}","{{ config_data | tojson }}", datetime("now"));\nCOMMIT;\nSQL'
          update_motion_timeout: >-
            /bin/sh -c 'command -v sqlite3 >/dev/null 2>&1 || exit 123; sqlite3 /config/room_database.db <<"SQL"\nBEGIN IMMEDIATE;\nSELECT CASE WHEN (SELECT version FROM schema_version)={{ schema_expected }} THEN 1 ELSE RAISE(ABORT,"SCHEMA_VERSION_MISMATCH") END;\nUPDATE room_configs\nSET config_data = json_set(config_data, "$.timeout", {{ timeout }}), updated_at = datetime("now")\nWHERE room_id="{{ room_id }}" AND config_domain="motion_lighting";\nCOMMIT;\nSQL'
          mark_room_cleaned: >-
            /bin/sh -c 'command -v sqlite3 >/dev/null 2>&1 || exit 123; sqlite3 /config/room_database.db <<"SQL"\nBEGIN IMMEDIATE;\nSELECT CASE WHEN (SELECT version FROM schema_version)={{ schema_expected }} THEN 1 ELSE RAISE(ABORT,"SCHEMA_VERSION_MISMATCH") END;\nUPDATE room_configs\nSET config_data = json_set(config_data, "$.last_cleaned", datetime("now"), "$.needs_cleaning", 0), updated_at = datetime("now")\nWHERE room_id="{{ room_id }}" AND config_domain="vacuum_control";\nCOMMIT;\nSQL'
        ```

        **/config/packages/room_database/database_init.sql**:
        ```sql
        PRAGMA journal_mode=WAL;\nPRAGMA synchronous=NORMAL;\nCREATE TABLE IF NOT EXISTS room_configs (\n  room_id TEXT NOT NULL,\n  config_domain TEXT NOT NULL,\n  config_data TEXT NOT NULL,\n  version INTEGER DEFAULT 1,\n  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n  PRIMARY KEY (room_id, config_domain)\n);\nCREATE INDEX IF NOT EXISTS idx_room_configs_domain_room ON room_configs(config_domain, room_id);\nCREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);\nINSERT OR IGNORE INTO schema_version(version) VALUES({{ schema_expected }});
        ```

        **/config/packages/room_database/preflight.yaml** (startup preflights + tokens + notifications):
        ```yaml
        shell_command:
          room_db_json1_preflight: >-
            /bin/sh -c 'mkdir -p {{ tokens_dir }}; rm -f {{ tokens_dir }}/MIGRATION_TOKEN_JSON1_*; if sqlite3 /config/room_database.db "PRAGMA compile_options;" | grep -i JSON1 >/dev/null; then touch {{ tokens_dir }}/MIGRATION_TOKEN_JSON1_OK; else touch {{ tokens_dir }}/MIGRATION_TOKEN_JSON1_MISSING; fi'
          room_db_sqlite_presence: >-
            /bin/sh -c 'mkdir -p {{ tokens_dir }}; rm -f {{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_*; if command -v sqlite3 >/dev/null 2>&1; then touch {{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_OK; else touch {{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_MISSING; fi'
        automation:
          - alias: "Room DB Preflight — On Start"
            id: room_db_preflight_on_start
            trigger:
              - platform: homeassistant
                event: start
            action:
              - service: shell_command.room_db_sqlite_presence
              - service: shell_command.room_db_json1_preflight
              - choose:
                  - conditions: "{{ not path_exists('{{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_OK') }}"
                    sequence:
                      - service: persistent_notification.create
                        data:
                          title: "Room DB Preflight"
                          message: "> sqlite3 not found — shell fallback disabled; AppDaemon/Node-RED path required."
                  - conditions: "{{ path_exists('{{ tokens_dir }}/MIGRATION_TOKEN_JSON1_MISSING') }}"
                    sequence:
                      - service: persistent_notification.create
                        data:
                          title: "Room DB Preflight"
                          message: "> SQLite JSON1 missing — using normalized schema + alternate sensors."
        ```

        **/config/packages/room_database/recorder_policy.yaml**:
        ```yaml
        recorder:
          exclude:
            entity_globs:
              - sensor.room_configs_*
              - sensor.rooms_needing_cleaning
        ```

        **/config/appdaemon/apps/room_db_updater/app.yaml** (preferred path):
        ```yaml
        room_db_updater:
          module: room_db_updater
          class: RoomDbUpdater
          db_path: /config/room_database.db
          schema_expected: {{ schema_expected }}
          canonical_mapping_file: {{ canonical_mapping_file }}
        ```

        **/config/appdaemon/apps/room_db_updater/room_db_updater.py** (preferred path skeleton):
        ```python
        import appdaemon.plugins.hass.hassapi as hass
        import json, sqlite3, yaml, re, time

        ROOM_ID_RE = re.compile(r"{{ room_id_pattern }}")

        class RoomDbUpdater(hass.Hass):
            def initialize(self):
                self.register_endpoint(self.update_config, "room_db/update_config")
                self.log("RoomDbUpdater initialized")

            def _validate_room(self, room_id):
                if not ROOM_ID_RE.match(room_id or ""):
                    raise ValueError("Invalid room_id slug")
                with open(self.args.get("canonical_mapping_file"), "r") as f:
                    amap = yaml.safe_load(f) or {}
                if room_id not in amap.get("rooms", {}):
                    raise ValueError("room_id not in canonical mapping")

            def _schema_ok(self, cur, expected):
                cur.execute("SELECT version FROM schema_version")
                v = cur.fetchone()[0]
                if int(v) != int(expected):
                    raise RuntimeError("SCHEMA_VERSION_MISMATCH")

            def update_config(self, data):
                try:
                    room_id = data.get("room_id")
                    domain = data.get("domain")
                    cfg = data.get("config_data")
                    self._validate_room(room_id)
                    conn = sqlite3.connect(self.args.get("db_path"))
                    cur = conn.cursor()
                    try:
                        self._schema_ok(cur, self.args.get("schema_expected"))
                        conn.execute("BEGIN IMMEDIATE")
                        cur.execute(
                            "INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at) VALUES (?,?,?, datetime('now'))",
                            (room_id, domain, json.dumps(cfg))
                        )
                        conn.commit()
                    except Exception:
                        conn.rollback()
                        raise
                    finally:
                        conn.close()
                    return {"status": "ok"}
                except Exception as e:
                    self.error(str(e))
                    self.call_service("persistent_notification/create", title="Room DB Update Failed", message=str(e))
                    return {"status": "error", "error": str(e)}
        ```

        **/config/packages/motion_lighting_v2/automations.yaml** (attribute reads + template condition):
        ```yaml
        automation:
          - alias: "Motion Lights — Bedroom (SQL-driven)"
            id: motion_lights_bedroom_sql
            trigger:
              - platform: state
                entity_id: binary_sensor.bedroom_motion_beta
                to: "on"
            variables:
              _raw: "{{ state_attr('sensor.room_configs_motion_lighting','payload') }}"
              _cfgs: "{{ _raw | from_json if _raw else {} }}"
              room_config: "{{ _cfgs.get('bedroom', {}) }}"
              timeout: "{{ room_config.get('timeout', 120) | int }}"
              bypass: "{{ room_config.get('bypass', false) | bool }}"
              presence_multiplier: "{{ room_config.get('presence_timeout_multiplier', 1.0) | float }}"
              is_presence_detected: "{{ is_state('person.evert','home') }}"
              effective_timeout: "{{ (timeout * presence_multiplier) | int if is_presence_detected else timeout }}"
              illuminance_threshold: "{{ room_config.get('illuminance_threshold', 10) | int }}"
            condition:
              - condition: template
                value_template: "{{ not bypass }}"
              - condition: template
                value_template: >
                  {{ (states('sensor.bedroom_illuminance_beta') | float(9999)) < illuminance_threshold }}
            action:
              - service: light.turn_on
                target:
                  entity_id: light.adaptive_bedroom_light_group
                data:
                  transition: 2
              - service: persistent_notification.create
                data:
                  title: "Motion Light Trigger"
                  message: "Bedroom SQL-driven activation at {{ now() }}"
              - choose:
                  - conditions: "{{ path_exists('{{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_OK') }}"
                    sequence:
                      - service: shell_command.update_room_config
                        data:
                          room_id: "bedroom"
                          domain: "motion_lighting"
                          config_data: >-
                            {{ dict(room_config, **{'last_triggered': now().isoformat(), 'trigger_count': (room_config.get('trigger_count', 0) | int) + 1}) }}
                  - conditions: "{{ not path_exists('{{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_OK') }}"
                    sequence:
                      - service: rest_command.room_db_update_config    # if user maps AppDaemon endpoint to rest_command
                        data:
                          room_id: "bedroom"
                          domain: "motion_lighting"
                          config_data: >-
                            {{ dict(room_config, **{'last_triggered': now().isoformat(), 'trigger_count': (room_config.get('trigger_count', 0) | int) + 1}) }}
              - delay:
                  seconds: "{{ effective_timeout }}"
              - service: light.turn_off
                target:
                  entity_id: light.adaptive_bedroom_light_group
                data:
                  transition: 5
        ```

        **/config/packages/motion_lighting_v2/templates.yaml** (compatibility):
        ```yaml
        template:
          - sensor:
              - name: "Motion Timeout — Bedroom (SQL)"
                unique_id: "motion_timeout_bedroom_sql"
                state: >-
                  {% set raw = state_attr('sensor.room_configs_motion_lighting','payload') %}
                  {% set cfg = (raw | from_json).get('bedroom', {}) if raw else {} %}
                  {{ cfg.get('timeout', 120) }}
                attributes:
                  bypass: >-
                    {% set raw = state_attr('sensor.room_configs_motion_lighting','payload') %}
                    {% set cfg = (raw | from_json).get('bedroom', {}) if raw else {} %}
                    {{ cfg.get('bypass', false) }}
                  last_triggered: >-
                    {% set raw = state_attr('sensor.room_configs_motion_lighting','payload') %}
                    {% set cfg = (raw | from_json).get('bedroom', {}) if raw else {} %}
                    {{ cfg.get('last_triggered', '') }}
                  room_id: "bedroom"
                  source: "room_database_sql"
        ```

        **/config/packages/vacuum_control_v2/scripts.yaml** (tojson payload + topic from secret):
        ```yaml
        script:
          clean_room_with_sql_tracking:
            alias: "Clean Room with SQL Database Tracking"
            fields:
              room:
                description: "Room to clean"
                required: true
                selector:
                  text:
            variables:
              _raw: "{{ state_attr('sensor.room_configs_vacuum_control','payload') }}"
              _cfgs: "{{ _raw | from_json if _raw else {} }}"
              room_config: "{{ _cfgs.get(room, {}) }}"
              segment_id: "{{ room_config.get('segment_id', 1) | int }}"
              base_topic: "{{ secret('{{ valetudo_base_topic_var }}') if has_value('secret', '{{ valetudo_base_topic_var }}') else states('input_text.{{ valetudo_base_topic_var }}') }}"
            sequence:
              - service: mqtt.publish
                data:
                  topic: "{{ base_topic }}/MapSegmentationCapability/action/start_segment_action"
                  payload: "{{ {'action':'clean','segment_ids':[segment_id],'iterations':1,'customOrder':True} | tojson }}"
              - choose:
                  - conditions: "{{ path_exists('{{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_OK') }}"
                    sequence:
                      - service: shell_command.mark_room_cleaned
                        data:
                          room_id: "{{ room }}"
                  - conditions: "{{ not path_exists('{{ tokens_dir }}/MIGRATION_TOKEN_SQLITE3_OK') }}"
                    sequence:
                      - service: rest_command.room_db_update_config
                        data:
                          room_id: "{{ room }}"
                          domain: "vacuum_control"
                          config_data: "{{ dict(room_config, **{'last_cleaned': now().isoformat(), 'needs_cleaning': false}) }}"
              - service: persistent_notification.create
                data:
                  title: "Vacuum Control"
                  message: "Started cleaning {{ room }} (segment {{ segment_id }})"
                  notification_id: "vacuum_{{ room }}"
        ```

        **/config/packages/vacuum_control_v2/mqtt_commands.yaml**:
        ```yaml
        # Valetudo base topic variable
        input_text:
          {{ valetudo_base_topic_var }}:
            name: "Valetudo Base Topic"
            min: 1
            max: 128
            initial: "valetudo/robot"
        ```

        **/config/.sql_room_db_tokens/README.txt** (token semantics):
        - MIGRATION_TOKEN_SQLITE3_OK|MISSING
        - MIGRATION_TOKEN_JSON1_OK|MISSING

        **/config/secrets.example.yaml**:
        ```yaml
        {{ valetudo_base_topic_var }}: "valetudo/robot"
        ```

        Ensure ADR-0008 formatting and deterministic key order.
        CONFIDENCE: [n]%

    # PHASE 5 — Validation
    - id: sql_room_db.validation.comprehensive
      persona: strategos_gpt
      label: "Validation — Acceptance & Diagnostics"
      mode: validation_mode
      protocols: [production_grade_validation, adr_compliance_enforcement]
      bindings:
        - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
      prompt: |
        Produce `validation_pack` including:
        - acceptance_criteria: checkboxes for DB init, JSON1 preflight tokens, SQL sensors (payload attribute present), transactional writes, schema_version guard, performance budgets, recorder excludes, ADR checks.
        - diagnostics_templates: Jinja verifying presence/contents of tokens, payload attributes readable, and entity reduction math.
        - migration_tokens: list and order with operator steps and expected file presence in {{ tokens_dir }}.
        - rollback_procedures and performance_benchmarks with concrete targets.
        CONFIDENCE: [n]%

  self_checks:
    - "Assert each SQL query SELECTs 'state'|'count' AND 'payload', with column: state|count (no JSON in state)."
    - "Assert platform-level scan_interval present and equals {{ scan_interval_seconds }}."
    - "Assert names match globals.naming.* across all files."
    - "Verify JSON1 preflight tokens exist; if missing JSON1, alternate schema/sensors are generated."
    - "Assert write paths are transactional; shell fallback uses heredoc + BEGIN IMMEDIATE/COMMIT + tojson."
    - "Assert schema_version table exists and enforced == {{ schema_expected }} before writes."
    - "Assert recorder excludes include sensor.room_configs_* and sensor.rooms_needing_cleaning."
    - "Assert room_id pattern {{ room_id_pattern }} and mapping validation is implemented in preferred (AppDaemon) path."
    - "Assert MQTT topics reference a single {{ valetudo_base_topic_var }} value (secret or input_text)."
````

