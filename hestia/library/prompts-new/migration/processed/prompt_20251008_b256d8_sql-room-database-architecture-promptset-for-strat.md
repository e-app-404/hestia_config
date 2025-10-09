---
id: prompt_20251008_b256d8
slug: sql-room-database-architecture-promptset-for-strat
title: SQL Room Database Architecture Promptset for Strategos GPT
date: '2025-10-08'
tier: "\u03B1"
domain: operational
persona: promachos
status: deprecated
tags: []
version: '1.0'
source_path: sql_room_db/sql_room_db.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:26.993348'
redaction_log: []
---

# SQL Room Database Architecture Promptset for Strategos GPT
# Multi-phase reconstruction of Variable integration using SQL-based room databases
# Targets: Adaptive Motion Lighting + Valetudo Vacuum Control packages

promptset:
  id: sql-room-database-architecture.promptset
  version: 1.0
  created: "2025-10-08"
  description: |
    Comprehensive 5-phase promptset for Strategos GPT (ChatGPT-5 Extended Thinking) to architect
    and implement SQL-based room database solution replacing HACS Variable integration.
    Merges adaptive motion lighting and vacuum control into unified room-scoped data architecture
    achieving 70%+ entity reduction through dynamic database-backed configuration objects.
  legacy_compatibility: false
  persona: strategos_gpt
  purpose: |
    Transform Variable integration dependencies into production-grade SQL-based room database
    architecture. Create unified data layer for motion lighting and vacuum control with
    room-scoped configuration objects, maintaining all functionality while eliminating
    entity sprawl through strategic database design.
  schema_version: 1.0

  # Execution Context for Strategos GPT
  execution_context:
    model: "GPT-5 Extended Thinking"
    approach: "Sequential phase execution with thinking reinforcement"
    mandate: "Replace 70+ helper entities with <10 SQL sensors + room database architecture"
    success_criteria: "Production-ready packages with copy-paste YAML components"

  # Artifacts & Bindings
  artifacts:
      required:
        - description: "Complete adaptive motion lighting package with room configs, automations, and helper definitions"
          path: /mnt/data/adaptive_motion_lighting/
        - description: "Valetudo vacuum control package with room cleaning logic and state management"
          path: /mnt/data/valetudo/
        - description: "Official HA SQL integration documentation with schema patterns, query validation, and template integration"
          path: /mnt/data/homeassistant_sql_integration_guide.md
        - description: "SQLite usage patterns in HA ecosystem, performance considerations, and database design best practices"
          path: /mnt/data/sqlite_homeassistant_patterns.md
        - description: "YAML normalization rules and deterministic configuration patterns for package consistency"
          path: /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
        - description: "Motion/occupancy/presence signal handling requirements and tier progression standards"
          path: /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md
        - description: "Canonical workspace structure and file placement requirements"
          path: /mnt/data/ADR/ADR-0024-canonical-config-path.md
        - description: "Canonical area/room/zone mapping with hierarchical relationships"
          path: /mnt/data/architecture/area_mapping.yaml
        - description: "Presence detection architecture and entity relationship mapping"
          path: /mnt/data/architecture/presence_mapping.yaml
        - description: "Alpha/beta/eta tier progression rules for entity references"
          path: /mnt/data/architecture/tier_mapping.yaml

    consulted:
      # Extended context sources
      - path: /mnt/data/hestia_structure.md
        description: "Workspace organization principles and package placement conventions"
      - path: /mnt/data/draft_template.promptset
        description: "Template structure for promptset organization and phase management"
      - path: /mnt/data/enhanced-motion-lighting-config.promptset
        description: "Previous motion lighting architecture for feature preservation analysis"
      - path: /mnt/data/valetudo_optimization_comprehensive_v2.promptset
        description: "Previous vacuum optimization approach for integration pattern analysis"

  bindings:
      protocols:
        - sql_database_first_architecture
        - room_scoped_data_modeling
        - entity_reduction_optimization
        - production_grade_validation
        - adr_compliance_enforcement
      hard_guardrails:
        - Database schema MUST support JSON attributes for complex room configurations
        - SQL queries MUST use HA recorder database unless explicitly requiring external database
        - Room objects MUST consolidate 6+ entities into single queryable configuration
        - All YAML output MUST pass HA configuration validation
        - Package structure MUST follow ADR-0024 canonical path requirements
        - Entity references MUST use beta-tier entities per ADR-0021 progression rules
      persona: strategos_gpt

  retrieval_tags:
     - sql_architecture
     - room_database
     - entity_reduction
     - variable_replacement
     - motion_lighting
     - vacuum_control
     - home_assistant
     - database_design

  operational_modes:
     - research_mode
     - deconstruction_mode
     - architecture_mode
     - implementation_mode
     - validation_mode

  # 5-Phase Sequential Execution Plan
    prompts:
    # PHASE 1: Research Foundation
    - id: sql_room_db.research.foundation
      persona: strategos_gpt
      label: "Research — SQL Integration Patterns & Package Analysis"
      mode: research_mode
      protocols:
        - sql_database_first_architecture
        - production_grade_validation
      bindings:
        - /mnt/data/homeassistant_sql_integration_guide.md
        - /mnt/data/sqlite_homeassistant_patterns.md
        - /mnt/data/adaptive_motion_lighting/
        - /mnt/data/valetudo/
        - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
      prompt: |
        **STRATEGOS PHASE 1/5: RESEARCH FOUNDATION**
        
        You are Strategos GPT operating in Extended Thinking mode. Your objective: architect SQL-based room database solution to replace HACS Variable integration, achieving 70%+ entity reduction while preserving all functionality.

        ## Research Directives

        ### 1.1 SQL Integration Mastery
        **Absorb from \`/mnt/data/homeassistant_sql_integration_guide.md\`:**
        - SQL sensor configuration patterns and YAML schema requirements
        - Query validation rules and SELECT-only constraints
        - Template integration patterns for dynamic query generation
        - Database connection management (recorder vs external database)
        - JSON column support and nested attribute extraction
        - Performance considerations and query optimization

        ### 1.2 SQLite Architecture Patterns  
        **Extract from \`/mnt/data/sqlite_homeassistant_patterns.md\`:**
        - Room-scoped database design patterns
        - JSON storage vs normalized table approaches
        - Transaction handling and data consistency models
        - Integration with HA recorder database vs standalone SQLite
        - Query caching and performance optimization techniques

        ### 1.3 Package Component Analysis
        **Unpack and inventory \`/mnt/data/adaptive_motion_lighting/\`:**
        - Count total entities (helpers, sensors, automations)
        - Extract room configuration patterns and data structures
        - Identify dynamic data requirements (motion timeouts, bypass states)
        - Map entity interdependencies and automation triggers
        - Document GUI touchpoints and user-configurable elements

        **Unpack and inventory \`/mnt/data/valetudo/\`:**
        - Analyze vacuum control state management approach
        - Extract room-to-segment mapping patterns
        - Identify cleaning schedule and status tracking mechanisms
        - Document MQTT integration patterns and command structures

        ### 1.4 Governance Requirements
        **From ADR-0008 extract normalization requirements:**
        - YAML formatting standards (2-space indent, A→Z keys, UTF-8/LF)
        - Configuration determinism requirements
        - Package structure and naming conventions

        ## Required Output Structure
        ```yaml
        research_foundation:
          sql_capabilities:
            # SQL integration features and constraints
          sqlite_patterns:
            # Room database design patterns
          current_architecture:
            adaptive_lighting:
              entity_count: n
              room_configs: {}
              dependencies: []
            valetudo:
              entity_count: n  
              room_mappings: {}
              state_tracking: []
          consolidation_opportunities:
            # Specific entity reduction targets
          governance_constraints:
            # ADR compliance requirements
        ```

        **THINKING REQUIREMENT:** Use extended thinking to analyze interdependencies and architectural implications before outputting structured analysis.

        **CONFIDENCE ASSESSMENT:** [n]%

    # PHASE 2: Deconstruction Analysis
    - id: sql_room_db.deconstruction.objectives
      persona: strategos_gpt
      label: "Deconstruction — Feature Extraction & Requirements Mapping"
      mode: deconstruction_mode
    protocols:
    - room_scoped_data_modeling
    - entity_reduction_optimization
    bindings:
    - /mnt/data/adaptive_motion_lighting/
    - /mnt/data/valetudo/
    - /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md
    - /mnt/data/architecture/area_mapping.yaml
    prompt: |
    **STRATEGOS PHASE 2/5: DECONSTRUCTION ANALYSIS**

    Using research_foundation output, deconstruct both packages to extract core objectives and consolidation opportunities.

    ## Deconstruction Directives

    ### 2.1 Adaptive Motion Lighting Objective Extraction
    **From `/mnt/data/adaptive_motion_lighting/` extract:**
    - **Core automation logic**: Motion triggers → lighting activation patterns per room
    - **Room-specific configurations**: Timeouts, bypass states, illuminance thresholds, presence enhancements
    - **Entity interdependencies**: Helper relationships, automation triggers, template sensors
    - **GUI touchpoints**: Dashboard cards, manual overrides, notification templates
    - **Dynamic data requirements**: Per-room timeout variations, bypass toggles, last-triggered tracking
    - **Cross-room behaviors**: Sanctum complex propagation, hallway system coordination
    - **ADR-0021 compliance**: Beta-tier entity usage, presence asymmetric logic

    ### 2.2 Valetudo Control Objective Extraction  
    **From `/mnt/data/valetudo/` extract:**
    - **Room cleaning logic**: Segment mapping, cleaning schedules, state tracking mechanisms
    - **MQTT integration patterns**: Command structures, payload formats, topic hierarchies
    - **State management approach**: Last cleaned timestamps, cleaning frequency, error handling
    - **Script orchestration**: Room-specific cleaning sequences, notification workflows
    - **Sensor compositions**: Map segment sensors, composite status indicators
    - **GUI dependencies**: Dashboard integrations, manual cleaning controls

    ### 2.3 Entity Consolidation Mapping
    **Identify specific consolidation targets:**
    - **Motion lighting entities**: `input_datetime.motion_*`, `input_boolean.bypass_*`, `var.motion_*` → Single room config object
    - **Vacuum entities**: Room cleaning states, segment mappings, scheduling helpers → Unified room database
    - **Template sensors**: Convert template-heavy sensors to SQL-driven equivalents
    - **Cross-package synergies**: Shared room metadata, unified presence logic, coordinated timeouts

    ### 2.4 GUI Integration Inventory
    **Map all user-facing touchpoints:**
    - **Lovelace dependencies**: Cards requiring entity access, custom UI components
    - **Notification templates**: Message formats referencing entity attributes
    - **Manual controls**: User interaction points, override mechanisms
    - **Dashboard integrations**: Room status displays, cleaning controls, motion bypass toggles
    - **Template accessibility**: Jinja references that must remain functional

    ## Required Output Structure
    ```yaml
    deconstruction_analysis:
        adaptive_lighting_core:
        objectives: []
        room_configurations: {}
        gui_touchpoints: []
        entity_dependencies: {}
        data_requirements: {}
        valetudo_core:
        objectives: []
        state_tracking: {}
        mqtt_patterns: {}
        gui_dependencies: []
        room_mappings: {}
        consolidation_targets:
        motion_entities: {} # entity_id → room_config mapping
        vacuum_entities: {} # entity_id → room_config mapping
        template_sensors: [] # sensors to convert to SQL
        shared_metadata: {} # cross-package room data
        gui_compatibility_matrix:
        preserved_interfaces: []
        deprecated_entities: []
        new_sql_access_patterns: []
    ```

    **THINKING REQUIREMENT:** Analyze cross-package data dependencies and identify optimal consolidation strategies.

    **CONFIDENCE ASSESSMENT:** [n]%

    # PHASE 3: Architecture Design
    - id: sql_room_db.architecture.scaffold
    persona: strategos_gpt
    label: "Architecture — Room Database Schema & SQL Integration Design" 
    mode: architecture_mode
    protocols:
    - sql_database_first_architecture
    - room_scoped_data_modeling
    - adr_compliance_enforcement
    bindings:
    - /mnt/data/homeassistant_sql_integration_guide.md
    - /mnt/data/sqlite_homeassistant_patterns.md
    - /mnt/data/ADR/ADR-0024-canonical-config-path.md
    - /mnt/data/architecture/tier_mapping.yaml
    prompt: |
    **STRATEGOS PHASE 3/5: ARCHITECTURE DESIGN**

    Using research_foundation and deconstruction_analysis outputs, architect unified room database solution.

    ## Architecture Directives

    ### 3.1 Room Database Schema Design
    **Create unified SQLite schema supporting both packages:**
    ```sql
    -- Primary room configuration table
    CREATE TABLE room_configs (
        room_id TEXT NOT NULL,
        config_domain TEXT NOT NULL, -- 'motion_lighting', 'vacuum_control', 'shared'
        config_data JSON NOT NULL,
        version INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (room_id, config_domain)
    );

    -- Example data structures:
    -- motion_lighting: {"timeout": 120, "bypass": false, "illuminance_threshold": 10, "last_triggered": "", "presence_timeout_multiplier": 2.0}
    -- vacuum_control: {"segment_id": 1, "last_cleaned": "2025-01-01T00:00:00Z", "cleaning_frequency": 7, "needs_cleaning": false}
    -- shared: {"area_name": "Bedroom", "priority": 1, "related_areas": ["ensuite"], "occupancy_sensors": ["binary_sensor.bedroom_motion_beta"]}
    ```

    ### 3.2 SQL Integration Component Architecture
    **Design HA SQL sensors for data access:**
    - **Room Config Loader**: Dynamic queries with room/domain parameter templates
    - **Room Status Aggregator**: Cross-domain data synthesis for dashboard displays  
    - **Configuration Validator**: Data integrity checks and constraint enforcement
    - **Room Inventory Sensor**: Available rooms and capabilities enumeration
    - **Motion Timeout Calculator**: Dynamic timeout computation based on presence/occupancy
    - **Vacuum Schedule Sensor**: Room cleaning schedule and status indicators

    ### 3.3 Data Access Layer Design
    **Template functions for dynamic room data access:**
    - `{{ room_config('bedroom', 'motion_lighting') | from_json }}` → Complete JSON object access
    - `{{ room_status('kitchen', 'vacuum_control.last_cleaned') }}` → Specific nested attribute
    - `{{ rooms_needing_cleaning() | from_json }}` → Multi-room filtered queries
    - `{{ motion_config_for_area('sanctum_complex') | from_json }}` → Hierarchical area queries
    - `{{ room_presence_timeout('bedroom') }}` → Calculated timeout with presence multiplier

    ### 3.4 Update Mechanism Architecture  
    **Service layer for configuration updates (addressing SQL read-only limitations):**
    - **Custom Shell Commands**: SQLite UPDATE operations via shell_command integration
    - **Python Scripts**: Database update scripts with JSON manipulation
    - **Template-driven Updates**: Automation-triggered configuration changes
    - **Atomic Transaction Safety**: Rollback mechanisms and data validation
    - **Change Audit Trail**: Update logging and version tracking

    ### 3.5 Package Structure Architecture
    **Following ADR-0024 canonical paths:**
    ```
    /config/packages/
        room_database/
        sql_sensors.yaml          # Room config SQL sensors
        shell_commands.yaml       # Database update commands
        python_scripts.yaml       # Complex update logic
        database_init.sql         # Schema and initial data
        motion_lighting_v2/
        automations.yaml         # SQL-backed motion automations
        templates.yaml           # Room config template access
        blueprints.yaml          # Blueprint instantiations
        vacuum_control_v2/
        automations.yaml         # SQL-backed vacuum logic
        scripts.yaml             # Room cleaning orchestration
        mqtt_commands.yaml       # Valetudo MQTT integration
    ```

    ### 3.6 Integration Strategy Design
    **Addressing SQL sensor limitations:**
    - **Read Operations**: Native SQL sensors for configuration queries
    - **Write Operations**: Shell commands + Python scripts for updates
    - **Transaction Safety**: Validation queries before/after updates
    - **Performance Optimization**: Cached queries, minimal database hits
    - **Error Handling**: Fallback configurations, validation failures

    ## Required Output Structure
    ```yaml
    architecture_design:
        database_schema:
        tables: {}
        indexes: []
        sample_data: {}
        sql_sensors:
        room_config_loader: {}
        status_aggregators: {}
        inventory_sensors: {}
        update_mechanisms:
        shell_commands: {}
        python_scripts: {}
        validation_queries: {}
        template_functions:
        access_patterns: {}
        calculated_fields: {}
        package_structure:
        file_organization: {}
        component_placement: {}
        integration_strategy:
        read_patterns: {}
        write_patterns: {}
        error_handling: {}
        migration_strategy:
        variable_to_sql_mapping: {}
        data_migration_scripts: {}
        rollback_procedures: {}
    ```

    **THINKING REQUIREMENT:** Consider SQL sensor limitations and design hybrid read/write architecture.

    **CONFIDENCE ASSESSMENT:** [n]%

    # PHASE 4: Implementation Generation
    - id: sql_room_db.implementation.packages
    persona: strategos_gpt  
    label: "Implementation — Production-Ready Package Generation"
    mode: implementation_mode
    protocols:
    - production_grade_validation
    - adr_compliance_enforcement
    - entity_reduction_optimization
    bindings:
    - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
    - /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md
    - /mnt/data/hestia_structure.md
    prompt: |
    **STRATEGOS PHASE 4/5: IMPLEMENTATION GENERATION**

    Using architecture_design output, generate complete production-ready package implementations.

    ## Implementation Directives

    ### 4.1 Room Database Foundation Package
    **Create `/mnt/canvas/packages/room_database/`:**

    **File: `sql_sensors.yaml`**
    ```yaml
    # Room configuration SQL sensors
    sql:
        - name: "Room Config Motion Lighting"
        query: >
            SELECT config_data FROM room_configs 
            WHERE room_id = '{{ room_id }}' AND config_domain = 'motion_lighting'
        column: config_data
        value_template: >
            {{ value | from_json if value else {} }}
        attributes:
            room_id: "{{ room_id }}"
            domain: "motion_lighting"
            last_updated: "{{ now().isoformat() }}"

        - name: "Room Config Vacuum Control"  
        query: >
            SELECT config_data FROM room_configs 
            WHERE room_id = '{{ room_id }}' AND config_domain = 'vacuum_control'
        column: config_data
        value_template: >
            {{ value | from_json if value else {} }}

        - name: "Rooms Needing Cleaning"
        query: >
            SELECT json_group_array(room_id) as rooms
            FROM room_configs 
            WHERE config_domain = 'vacuum_control' 
            AND json_extract(config_data, '$.needs_cleaning') = 1
        column: rooms
        value_template: >
            {{ value | from_json if value else [] }}
    ```

    **File: `shell_commands.yaml`**
    ```yaml
    # Room database update commands
    shell_command:
        update_room_config: >
        sqlite3 /config/room_database.db "
        INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at) 
        VALUES ('{{ room_id }}', '{{ domain }}', '{{ config_data | to_json }}', datetime('now'));"
        
        update_motion_timeout: >
        sqlite3 /config/room_database.db "
        UPDATE room_configs 
        SET config_data = json_set(config_data, '$.timeout', {{ timeout }}, '$.updated_at', datetime('now'))
        WHERE room_id = '{{ room_id }}' AND config_domain = 'motion_lighting';"

        mark_room_cleaned: >
        sqlite3 /config/room_database.db "
        UPDATE room_configs 
        SET config_data = json_set(config_data, '$.last_cleaned', datetime('now'), '$.needs_cleaning', 0)
        WHERE room_id = '{{ room_id }}' AND config_domain = 'vacuum_control';"
    ```

    **File: `database_init.sql`**
    ```sql
    -- Initialize room database schema and seed data
    CREATE TABLE IF NOT EXISTS room_configs (
        room_id TEXT NOT NULL,
        config_domain TEXT NOT NULL, 
        config_data JSON NOT NULL,
        version INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (room_id, config_domain)
    );

    -- Seed initial room configurations (converted from existing Variable data)
    INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data) VALUES
    ('bedroom', 'motion_lighting', '{"timeout": 120, "bypass": false, "illuminance_threshold": 10, "last_triggered": "", "presence_timeout_multiplier": 2.0}'),
    ('bedroom', 'vacuum_control', '{"segment_id": 1, "last_cleaned": "2025-01-01T00:00:00Z", "cleaning_frequency": 7, "needs_cleaning": false}'),
    ('kitchen', 'motion_lighting', '{"timeout": 300, "bypass": false, "illuminance_threshold": 5, "last_triggered": "", "presence_timeout_multiplier": 1.5}'),
    ('kitchen', 'vacuum_control', '{"segment_id": 2, "last_cleaned": "2025-01-01T00:00:00Z", "cleaning_frequency": 3, "needs_cleaning": true}');
    ```

    ### 4.2 Motion Lighting V2 Package
    **Create `/mnt/canvas/packages/motion_lighting_v2/`:**

    **File: `automations.yaml`**
    ```yaml
    automation:
        - alias: "Motion Lights — Bedroom (SQL-driven)"
        id: motion_lights_bedroom_sql
        trigger:
            - platform: state
            entity_id: binary_sensor.bedroom_motion_beta
            to: 'on'
        variables:
            room_config: >
            {% set config = states('sensor.room_config_motion_lighting') %}
            {{ config | from_json if config not in ['unknown', 'unavailable', ''] else {} }}
            timeout: "{{ room_config.get('timeout', 120) | int }}"
            bypass: "{{ room_config.get('bypass', false) | bool }}"
            presence_multiplier: "{{ room_config.get('presence_timeout_multiplier', 1.0) | float }}"
            is_presence_detected: "{{ is_state('person.evert', 'home') }}"
            effective_timeout: "{{ (timeout * presence_multiplier) | int if is_presence_detected else timeout }}"
        condition:
            - condition: template
            value_template: "{{ not bypass }}"
            - condition: numeric_state
            entity_id: sensor.bedroom_illuminance_beta
            below: "{{ room_config.get('illuminance_threshold', 10) }}"
        action:
            - service: light.turn_on
            target:
                entity_id: light.adaptive_bedroom_light_group
            data:
                transition: 2
            - service: shell_command.update_room_config
            data:
                room_id: bedroom
                domain: motion_lighting
                config_data: >
                {{ dict(room_config, **{
                    'last_triggered': now().isoformat(),
                    'trigger_count': (room_config.get('trigger_count', 0) | int) + 1
                }) }}
            - delay:
                seconds: "{{ effective_timeout }}"
            - service: light.turn_off
            target:
                entity_id: light.adaptive_bedroom_light_group
            data:
                transition: 5
    ```

    ### 4.3 Vacuum Control V2 Package  
    **Create `/mnt/canvas/packages/vacuum_control_v2/`:**

    **File: `scripts.yaml`**
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
        sequence:
            - variables:
                room_config: >
                {% set config = states('sensor.room_config_vacuum_control') %}
                {{ config | from_json if config not in ['unknown', 'unavailable', ''] else {} }}
                segment_id: "{{ room_config.get('segment_id', 1) }}"
            - service: mqtt.publish
            data:
                topic: "valetudo/roborocks5/MapSegmentationCapability/action/start_segment_action"
                payload: >
                {
                    "action": "clean",
                    "segment_ids": [{{ segment_id }}],
                    "iterations": 1,
                    "customOrder": true
                }
            - service: shell_command.mark_room_cleaned
            data:
                room_id: "{{ room }}"
            - service: persistent_notification.create
            data:
                title: "Vacuum Control"
                message: "Started cleaning {{ room }} (segment {{ segment_id }})"
                notification_id: "vacuum_{{ room }}"
    ```

    ### 4.4 Template Integration Layer
    **Create backward compatibility templates:**
    ```yaml
    template:
        - sensor:
        - name: "Motion Timeout — {{ room }}"
            unique_id: "motion_timeout_{{ room }}_sql"
            state: >
            {% set config = states('sensor.room_config_motion_lighting') | from_json %}
            {{ config.get('timeout', 120) if config else 120 }}
            attributes:
            bypass: >
                {% set config = states('sensor.room_config_motion_lighting') | from_json %}
                {{ config.get('bypass', false) if config else false }}
            last_triggered: >
                {% set config = states('sensor.room_config_motion_lighting') | from_json %}
                {{ config.get('last_triggered', '') if config else '' }}
            room_id: "{{ room }}"
            source: "room_database_sql"
    ```

    ## Required Output Structure
    **Deliver production-ready YAML files organized by package:**
    - Complete SQL sensor configurations with error handling
    - Shell command definitions for database updates
    - Database initialization scripts with seed data
    - Migration-ready automation templates with SQL integration
    - Backward compatibility template layer
    - MQTT integration for Valetudo commands
    - Comprehensive error handling and validation

    **All output MUST be copy-paste ready with proper YAML formatting per ADR-0008.**

    **THINKING REQUIREMENT:** Validate each YAML block for HA compatibility and ensure SQL operations are atomic.

    **CONFIDENCE ASSESSMENT:** [n]%

    # PHASE 5: Validation Framework
    - id: sql_room_db.validation.comprehensive
    persona: strategos_gpt
    label: "Validation — Acceptance Criteria & Diagnostic Framework"
    mode: validation_mode
    protocols:
    - production_grade_validation
    - adr_compliance_enforcement
    bindings:
    - /mnt/data/draft_template.promptset
    - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
    prompt: |
    **STRATEGOS PHASE 5/5: VALIDATION FRAMEWORK**

    Using all previous outputs, create comprehensive validation and acceptance framework.

    ## Validation Directives

    ### 5.1 Acceptance Criteria Matrix
    **Define binary acceptance tests:**
    ```yaml
    acceptance_criteria:
        database_layer:
        - [ ] Room configs database initializes without errors
        - [ ] SQL sensors successfully query room data with proper JSON parsing
        - [ ] Shell commands execute database updates without corruption
        - [ ] Database schema supports all required room configuration patterns
        - [ ] Query performance remains under 100ms for typical operations
        
        functional_preservation:
        - [ ] Motion lighting triggers function identically to Variable-based original
        - [ ] Vacuum room cleaning maintains all original capabilities
        - [ ] Room-specific timeouts and bypass states work correctly
        - [ ] Presence-based timeout multipliers function as expected
        - [ ] Cross-room coordination (sanctum complex, hallway system) preserved
        
        entity_reduction:
        - [ ] Total entity count reduced by 70%+ from original Variable implementation
        - [ ] Room objects consolidate 6+ entities into single SQL-accessible configuration
        - [ ] No critical functionality lost in consolidation process
        - [ ] Template compatibility maintained for existing integrations
        
        gui_compatibility:
        - [ ] Dashboard cards continue to function with SQL-backed data
        - [ ] Manual override controls remain accessible
        - [ ] Notification templates reference correct entity attributes
        - [ ] Lovelace UI components display room status correctly
        
        performance_validation:
        - [ ] SQL queries execute within 100ms response time
        - [ ] Database updates don't block automation execution
        - [ ] Template rendering performance acceptable for UI responsiveness
        - [ ] Memory usage remains within acceptable bounds
        
        adr_compliance:
        - [ ] Package structure follows ADR-0024 canonical path requirements
        - [ ] Entity references use beta-tier entities per ADR-0021
        - [ ] YAML formatting adheres to ADR-0008 normalization rules
        - [ ] Motion/occupancy/presence signals handled per governance standards
    ```

    ### 5.2 Diagnostic Jinja Templates
    **Create validation and debugging templates:**
    ```jinja
    {# Room Database Health Check Template #}
    {% set rooms = ['bedroom', 'kitchen', 'ensuite', 'desk', 'hallway_downstairs'] %}
    {% set domains = ['motion_lighting', 'vacuum_control', 'shared'] %}

    ## Room Database Health Report
    Generated: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}

    {% for room in rooms %}
    ### Room: {{ room | title }}
    {% for domain in domains %}
    - **{{ domain }}**: {{ room_config(room, domain) is defined and room_config(room, domain) != {} }}
        {% if room_config(room, domain) %}
        - Config: {{ room_config(room, domain) | to_json }}
        {% endif %}
    {% endfor %}
    {% endfor %}

    ## Entity Reduction Analysis
    - **Original Entity Count**: {{ original_entity_count | default(70) }}
    - **Current Entity Count**: {{ current_entity_count | default(10) }}
    - **Reduction Percentage**: {{ ((original_entity_count - current_entity_count) / original_entity_count * 100) | round(1) }}%
    - **Target Met**: {{ 'YES' if ((original_entity_count - current_entity_count) / original_entity_count * 100) >= 70 else 'NO' }}

    ## SQL Sensor Status
    {% set sql_sensors = [
        'sensor.room_config_motion_lighting',
        'sensor.room_config_vacuum_control', 
        'sensor.rooms_needing_cleaning'
    ] %}
    {% for sensor in sql_sensors %}
    - **{{ sensor }}**: {{ 'OK' if states(sensor) not in ['unknown', 'unavailable', ''] else 'FAIL' }}
        - State: {{ states(sensor) }}
        - Last Updated: {{ state_attr(sensor, 'last_updated') }}
    {% endfor %}
    ```

    ### 5.3 Migration Validation Tokens
    **Create verification checkpoints:**
    - `MIGRATION_TOKEN_DATABASE_INITIALIZED`: Room database schema created and seeded
    - `MIGRATION_TOKEN_SQL_SENSORS_OPERATIONAL`: All SQL sensors querying successfully  
    - `MIGRATION_TOKEN_SHELL_COMMANDS_TESTED`: Database update commands validated
    - `MIGRATION_TOKEN_AUTOMATIONS_MIGRATED`: Motion/vacuum automations converted to SQL
    - `MIGRATION_TOKEN_TEMPLATES_COMPATIBLE`: Backward compatibility templates working
    - `MIGRATION_TOKEN_GUI_VERIFIED`: Dashboard and UI components functional
    - `MIGRATION_TOKEN_PERFORMANCE_ACCEPTABLE`: Query response times within limits
    - `MIGRATION_TOKEN_ENTITY_REDUCTION_ACHIEVED`: 70%+ reduction target met

    ### 5.4 Rollback Safety Mechanisms
    **Define comprehensive rollback procedures:**
    ```yaml
    rollback_procedures:
        database_rollback:
        - "Backup current room_database.db before any changes"
        - "Restore previous Variable integration package files"
        - "Re-enable Variable integration in HACS"
        - "Restart Home Assistant to reload Variable entities"
        
        configuration_rollback:
        - "Restore original automation files from backup"
        - "Re-enable Variable-based helper entities"
        - "Update entity references in templates and scripts"
        - "Verify all original functionality restored"
        
        validation_rollback:
        - "Run original package validation tests"
        - "Confirm entity counts match pre-migration state"  
        - "Verify GUI components function with original entities"
        - "Test motion lighting and vacuum control end-to-end"
    ```

    ### 5.5 Performance Benchmarks
    **Define measurable performance criteria:**
    ```yaml
    performance_benchmarks:
        query_response_times:
        room_config_query: "<50ms"
        bulk_room_status: "<100ms"
        cleaning_schedule_query: "<75ms"
        
        database_operations:
        config_update: "<200ms"
        bulk_insert: "<500ms"
        transaction_rollback: "<100ms"
        
        automation_execution:
        motion_trigger_to_light_on: "<2s"
        vacuum_script_execution: "<5s"
        template_rendering: "<100ms"
    ```

    ## Required Output Structure
    **Deliver complete validation framework:**
    - Binary acceptance test matrix with checkboxes
    - Diagnostic Jinja template collection for health monitoring
    - Migration token verification system with clear checkpoints
    - Comprehensive rollback safety procedures
    - Performance benchmark definitions with measurable criteria
    - Test automation scripts for continuous validation
    - Documentation for manual validation procedures

    **THINKING REQUIREMENT:** Consider failure modes, edge cases, and recovery scenarios for robust validation.

    **CONFIDENCE ASSESSMENT:** [n]%
  # Execution Summary for Strategos GPT
  execution_summary:
    objective: "Replace HACS Variable integration with SQL-based room database architecture"
    target_reduction: "70%+ entity reduction through room-scoped configuration objects"
    deliverables:
      - Research analysis of SQL integration patterns
      - Deconstructed feature requirements from both packages
      - Complete room database architecture design
      - Production-ready YAML package implementations  
      - Comprehensive validation and acceptance framework
    success_metrics:
      - Entity count: 70%+ reduction achieved
      - Functionality: 100% feature preservation
      - Performance: <100ms SQL query response times
      - Compliance: Full ADR-0008 and ADR-0021 adherence
      - Deployability: Copy-paste ready YAML components

  # Final Instructions for Strategos
  strategos_instructions: |
    Execute each phase sequentially, using Extended Thinking mode to analyze interdependencies
    and architectural implications. Each phase builds on previous outputs - maintain context
    continuity throughout execution.
    
    Your final deliverable should be production-ready Home Assistant packages that can be
    dropped directly into a /config/packages/ directory and function immediately, replacing
    the failed HACS Variable integration with superior SQL-based architecture.
    
    Focus on practical implementation over theoretical discussion. Every YAML block should
    be syntactically valid and functionally complete.

# Documentation  
documentation:
  - Reference: ADR-0021 for motion/presence signal requirements
  - See architecture/*.yaml files for canonical room/area mappings
  - SQL integration guide provides query optimization patterns
  - Package placement follows ADR-0024 canonical structure

    # PHASE 2: Deconstruction Analysis
    - id: sql_room_db.deconstruction.objectives
      persona: strategos_gpt
      label: "Deconstruction — Feature Extraction & Requirements Mapping"
      mode: deconstruction_mode
      protocols:
        - room_scoped_data_modeling
        - entity_reduction_optimization
      bindings:
        - /mnt/data/adaptive_motion_lighting/
        - /mnt/data/valetudo/
        - /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md
        - /mnt/data/architecture/area_mapping.yaml
      prompt: |
        **STRATEGOS PHASE 2/5: DECONSTRUCTION ANALYSIS**
        
        Using research_foundation output, deconstruct both packages to extract core objectives and consolidation opportunities.

        ## Deconstruction Directives

        ### 2.1 Adaptive Motion Lighting Objective Extraction
        **From `/mnt/data/adaptive_motion_lighting/` extract:**
        - **Core automation logic**: Motion triggers → lighting activation patterns per room
        - **Room-specific configurations**: Timeouts, bypass states, illuminance thresholds, presence enhancements
        - **Entity interdependencies**: Helper relationships, automation triggers, template sensors
        - **GUI touchpoints**: Dashboard cards, manual overrides, notification templates
        - **Dynamic data requirements**: Per-room timeout variations, bypass toggles, last-triggered tracking
        - **Cross-room behaviors**: Sanctum complex propagation, hallway system coordination
        - **ADR-0021 compliance**: Beta-tier entity usage, presence asymmetric logic

        ### 2.2 Valetudo Control Objective Extraction  
        **From `/mnt/data/valetudo/` extract:**
        - **Room cleaning logic**: Segment mapping, cleaning schedules, state tracking mechanisms
        - **MQTT integration patterns**: Command structures, payload formats, topic hierarchies
        - **State management approach**: Last cleaned timestamps, cleaning frequency, error handling
        - **Script orchestration**: Room-specific cleaning sequences, notification workflows
        - **Sensor compositions**: Map segment sensors, composite status indicators
        - **GUI dependencies**: Dashboard integrations, manual cleaning controls

        ### 2.3 Entity Consolidation Mapping
        **Identify specific consolidation targets:**
        - **Motion lighting entities**: `input_datetime.motion_*`, `input_boolean.bypass_*`, `var.motion_*` → Single room config object
        - **Vacuum entities**: Room cleaning states, segment mappings, scheduling helpers → Unified room database
        - **Template sensors**: Convert template-heavy sensors to SQL-driven equivalents
        - **Cross-package synergies**: Shared room metadata, unified presence logic, coordinated timeouts

        ### 2.4 GUI Integration Inventory
        **Map all user-facing touchpoints:**
        - **Lovelace dependencies**: Cards requiring entity access, custom UI components
        - **Notification templates**: Message formats referencing entity attributes
        - **Manual controls**: User interaction points, override mechanisms
        - **Dashboard integrations**: Room status displays, cleaning controls, motion bypass toggles
        - **Template accessibility**: Jinja references that must remain functional

        ## Required Output Structure
        ```yaml
        deconstruction_analysis:
          adaptive_lighting_core:
            objectives: []
            room_configurations: {}
            gui_touchpoints: []
            entity_dependencies: {}
            data_requirements: {}
          valetudo_core:
            objectives: []
            state_tracking: {}
            mqtt_patterns: {}
            gui_dependencies: []
            room_mappings: {}
          consolidation_targets:
            motion_entities: {} # entity_id → room_config mapping
            vacuum_entities: {} # entity_id → room_config mapping
            template_sensors: [] # sensors to convert to SQL
            shared_metadata: {} # cross-package room data
          gui_compatibility_matrix:
            preserved_interfaces: []
            deprecated_entities: []
            new_sql_access_patterns: []
        ```

        **THINKING REQUIREMENT:** Analyze cross-package data dependencies and identify optimal consolidation strategies.

        **CONFIDENCE ASSESSMENT:** [n]%

    # PHASE 3: Architecture Design
    - id: sql_room_db.architecture.scaffold
      persona: strategos_gpt
      label: "Architecture — Room Database Schema & SQL Integration Design" 
      mode: architecture_mode
      protocols:
        - sql_database_first_architecture
        - room_scoped_data_modeling
        - adr_compliance_enforcement
      bindings:
        - /mnt/data/homeassistant_sql_integration_guide.md
        - /mnt/data/sqlite_homeassistant_patterns.md
        - /mnt/data/ADR/ADR-0024-canonical-config-path.md
        - /mnt/data/architecture/tier_mapping.yaml
      prompt: |
        **STRATEGOS PHASE 3/5: ARCHITECTURE DESIGN**
        
        Using research_foundation and deconstruction_analysis outputs, architect unified room database solution.

        ## Architecture Directives

        ### 3.1 Room Database Schema Design
        **Create unified SQLite schema supporting both packages:**
        ```sql
        -- Primary room configuration table
        CREATE TABLE room_configs (
            room_id TEXT NOT NULL,
            config_domain TEXT NOT NULL, -- 'motion_lighting', 'vacuum_control', 'shared'
            config_data JSON NOT NULL,
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (room_id, config_domain)
        );
        
        -- Example data structures:
        -- motion_lighting: {"timeout": 120, "bypass": false, "illuminance_threshold": 10, "last_triggered": "", "presence_timeout_multiplier": 2.0}
        -- vacuum_control: {"segment_id": 1, "last_cleaned": "2025-01-01T00:00:00Z", "cleaning_frequency": 7, "needs_cleaning": false}
        -- shared: {"area_name": "Bedroom", "priority": 1, "related_areas": ["ensuite"], "occupancy_sensors": ["binary_sensor.bedroom_motion_beta"]}
        ```

        ### 3.2 SQL Integration Component Architecture
        **Design HA SQL sensors for data access:**
        - **Room Config Loader**: Dynamic queries with room/domain parameter templates
        - **Room Status Aggregator**: Cross-domain data synthesis for dashboard displays  
        - **Configuration Validator**: Data integrity checks and constraint enforcement
        - **Room Inventory Sensor**: Available rooms and capabilities enumeration
        - **Motion Timeout Calculator**: Dynamic timeout computation based on presence/occupancy
        - **Vacuum Schedule Sensor**: Room cleaning schedule and status indicators

        ### 3.3 Data Access Layer Design
        **Template functions for dynamic room data access:**
        - `{{ room_config('bedroom', 'motion_lighting') | from_json }}` → Complete JSON object access
        - `{{ room_status('kitchen', 'vacuum_control.last_cleaned') }}` → Specific nested attribute
        - `{{ rooms_needing_cleaning() | from_json }}` → Multi-room filtered queries
        - `{{ motion_config_for_area('sanctum_complex') | from_json }}` → Hierarchical area queries
        - `{{ room_presence_timeout('bedroom') }}` → Calculated timeout with presence multiplier

        ### 3.4 Update Mechanism Architecture  
        **Service layer for configuration updates (addressing SQL read-only limitations):**
        - **Custom Shell Commands**: SQLite UPDATE operations via shell_command integration
        - **Python Scripts**: Database update scripts with JSON manipulation
        - **Template-driven Updates**: Automation-triggered configuration changes
        - **Atomic Transaction Safety**: Rollback mechanisms and data validation
        - **Change Audit Trail**: Update logging and version tracking

        ### 3.5 Package Structure Architecture
        **Following ADR-0024 canonical paths:**
        ```
        /config/packages/
          room_database/
            sql_sensors.yaml          # Room config SQL sensors
            shell_commands.yaml       # Database update commands
            python_scripts.yaml       # Complex update logic
            database_init.sql         # Schema and initial data
          motion_lighting_v2/
            automations.yaml         # SQL-backed motion automations
            templates.yaml           # Room config template access
            blueprints.yaml          # Blueprint instantiations
          vacuum_control_v2/
            automations.yaml         # SQL-backed vacuum logic
            scripts.yaml             # Room cleaning orchestration
            mqtt_commands.yaml       # Valetudo MQTT integration
        ```

        ### 3.6 Integration Strategy Design
        **Addressing SQL sensor limitations:**
        - **Read Operations**: Native SQL sensors for configuration queries
        - **Write Operations**: Shell commands + Python scripts for updates
        - **Transaction Safety**: Validation queries before/after updates
        - **Performance Optimization**: Cached queries, minimal database hits
        - **Error Handling**: Fallback configurations, validation failures

        ## Required Output Structure
        ```yaml
        architecture_design:
          database_schema:
            tables: {}
            indexes: []
            sample_data: {}
          sql_sensors:
            room_config_loader: {}
            status_aggregators: {}
            inventory_sensors: {}
          update_mechanisms:
            shell_commands: {}
            python_scripts: {}
            validation_queries: {}
          template_functions:
            access_patterns: {}
            calculated_fields: {}
          package_structure:
            file_organization: {}
            component_placement: {}
          integration_strategy:
            read_patterns: {}
            write_patterns: {}
            error_handling: {}
          migration_strategy:
            variable_to_sql_mapping: {}
            data_migration_scripts: {}
            rollback_procedures: {}
        ```

        **THINKING REQUIREMENT:** Consider SQL sensor limitations and design hybrid read/write architecture.

        **CONFIDENCE ASSESSMENT:** [n]%

    # PHASE 4: Implementation Generation
    - id: sql_room_db.implementation.packages
      persona: strategos_gpt  
      label: "Implementation — Production-Ready Package Generation"
      mode: implementation_mode
      protocols:
        - production_grade_validation
        - adr_compliance_enforcement
        - entity_reduction_optimization
      bindings:
        - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
        - /mnt/data/ADR/ADR-0021-motion-occupancy-presence-signals.md
        - /mnt/data/hestia_structure.md
      prompt: |
        **STRATEGOS PHASE 4/5: IMPLEMENTATION GENERATION**
        
        Using architecture_design output, generate complete production-ready package implementations.

        ## Implementation Directives

        ### 4.1 Room Database Foundation Package
        **Create `/mnt/canvas/packages/room_database/`:**

        **File: `sql_sensors.yaml`**
        ```yaml
        # Room configuration SQL sensors
        sql:
          - name: "Room Config Motion Lighting"
            query: >
              SELECT config_data FROM room_configs 
              WHERE room_id = '{{ room_id }}' AND config_domain = 'motion_lighting'
            column: config_data
            value_template: >
              {{ value | from_json if value else {} }}
            attributes:
              room_id: "{{ room_id }}"
              domain: "motion_lighting"
              last_updated: "{{ now().isoformat() }}"
        
          - name: "Room Config Vacuum Control"  
            query: >
              SELECT config_data FROM room_configs 
              WHERE room_id = '{{ room_id }}' AND config_domain = 'vacuum_control'
            column: config_data
            value_template: >
              {{ value | from_json if value else {} }}
        
          - name: "Rooms Needing Cleaning"
            query: >
              SELECT json_group_array(room_id) as rooms
              FROM room_configs 
              WHERE config_domain = 'vacuum_control' 
              AND json_extract(config_data, '$.needs_cleaning') = 1
            column: rooms
            value_template: >
              {{ value | from_json if value else [] }}
        ```

        **File: `shell_commands.yaml`**
        ```yaml
        # Room database update commands
        shell_command:
          update_room_config: >
            sqlite3 /config/room_database.db "
            INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at) 
            VALUES ('{{ room_id }}', '{{ domain }}', '{{ config_data | to_json }}', datetime('now'));"
          
          update_motion_timeout: >
            sqlite3 /config/room_database.db "
            UPDATE room_configs 
            SET config_data = json_set(config_data, '$.timeout', {{ timeout }}, '$.updated_at', datetime('now'))
            WHERE room_id = '{{ room_id }}' AND config_domain = 'motion_lighting';"
        
          mark_room_cleaned: >
            sqlite3 /config/room_database.db "
            UPDATE room_configs 
            SET config_data = json_set(config_data, '$.last_cleaned', datetime('now'), '$.needs_cleaning', 0)
            WHERE room_id = '{{ room_id }}' AND config_domain = 'vacuum_control';"
        ```

        **File: `database_init.sql`**
        ```sql
        -- Initialize room database schema and seed data
        CREATE TABLE IF NOT EXISTS room_configs (
            room_id TEXT NOT NULL,
            config_domain TEXT NOT NULL, 
            config_data JSON NOT NULL,
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (room_id, config_domain)
        );
        
        -- Seed initial room configurations (converted from existing Variable data)
        INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data) VALUES
        ('bedroom', 'motion_lighting', '{"timeout": 120, "bypass": false, "illuminance_threshold": 10, "last_triggered": "", "presence_timeout_multiplier": 2.0}'),
        ('bedroom', 'vacuum_control', '{"segment_id": 1, "last_cleaned": "2025-01-01T00:00:00Z", "cleaning_frequency": 7, "needs_cleaning": false}'),
        ('kitchen', 'motion_lighting', '{"timeout": 300, "bypass": false, "illuminance_threshold": 5, "last_triggered": "", "presence_timeout_multiplier": 1.5}'),
        ('kitchen', 'vacuum_control', '{"segment_id": 2, "last_cleaned": "2025-01-01T00:00:00Z", "cleaning_frequency": 3, "needs_cleaning": true}');
        ```

        ### 4.2 Motion Lighting V2 Package
        **Create `/mnt/canvas/packages/motion_lighting_v2/`:**

        **File: `automations.yaml`**
        ```yaml
        automation:
          - alias: "Motion Lights — Bedroom (SQL-driven)"
            id: motion_lights_bedroom_sql
            trigger:
              - platform: state
                entity_id: binary_sensor.bedroom_motion_beta
                to: 'on'
            variables:
              room_config: >
                {% set config = states('sensor.room_config_motion_lighting') %}
                {{ config | from_json if config not in ['unknown', 'unavailable', ''] else {} }}
              timeout: "{{ room_config.get('timeout', 120) | int }}"
              bypass: "{{ room_config.get('bypass', false) | bool }}"
              presence_multiplier: "{{ room_config.get('presence_timeout_multiplier', 1.0) | float }}"
              is_presence_detected: "{{ is_state('person.evert', 'home') }}"
              effective_timeout: "{{ (timeout * presence_multiplier) | int if is_presence_detected else timeout }}"
            condition:
              - condition: template
                value_template: "{{ not bypass }}"
              - condition: numeric_state
                entity_id: sensor.bedroom_illuminance_beta
                below: "{{ room_config.get('illuminance_threshold', 10) }}"
            action:
              - service: light.turn_on
                target:
                  entity_id: light.adaptive_bedroom_light_group
                data:
                  transition: 2
              - service: shell_command.update_room_config
                data:
                  room_id: bedroom
                  domain: motion_lighting
                  config_data: >
                    {{ dict(room_config, **{
                      'last_triggered': now().isoformat(),
                      'trigger_count': (room_config.get('trigger_count', 0) | int) + 1
                    }) }}
              - delay:
                  seconds: "{{ effective_timeout }}"
              - service: light.turn_off
                target:
                  entity_id: light.adaptive_bedroom_light_group
                data:
                  transition: 5
        ```

        ### 4.3 Vacuum Control V2 Package  
        **Create `/mnt/canvas/packages/vacuum_control_v2/`:**

        **File: `scripts.yaml`**
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
            sequence:
              - variables:
                  room_config: >
                    {% set config = states('sensor.room_config_vacuum_control') %}
                    {{ config | from_json if config not in ['unknown', 'unavailable', ''] else {} }}
                  segment_id: "{{ room_config.get('segment_id', 1) }}"
              - service: mqtt.publish
                data:
                  topic: "valetudo/roborocks5/MapSegmentationCapability/action/start_segment_action"
                  payload: >
                    {
                      "action": "clean",
                      "segment_ids": [{{ segment_id }}],
                      "iterations": 1,
                      "customOrder": true
                    }
              - service: shell_command.mark_room_cleaned
                data:
                  room_id: "{{ room }}"
              - service: persistent_notification.create
                data:
                  title: "Vacuum Control"
                  message: "Started cleaning {{ room }} (segment {{ segment_id }})"
                  notification_id: "vacuum_{{ room }}"
        ```

        ### 4.4 Template Integration Layer
        **Create backward compatibility templates:**
        ```yaml
        template:
          - sensor:
            - name: "Motion Timeout — {{ room }}"
              unique_id: "motion_timeout_{{ room }}_sql"
              state: >
                {% set config = states('sensor.room_config_motion_lighting') | from_json %}
                {{ config.get('timeout', 120) if config else 120 }}
              attributes:
                bypass: >
                  {% set config = states('sensor.room_config_motion_lighting') | from_json %}
                  {{ config.get('bypass', false) if config else false }}
                last_triggered: >
                  {% set config = states('sensor.room_config_motion_lighting') | from_json %}
                  {{ config.get('last_triggered', '') if config else '' }}
                room_id: "{{ room }}"
                source: "room_database_sql"
        ```

        ## Required Output Structure
        **Deliver production-ready YAML files organized by package:**
        - Complete SQL sensor configurations with error handling
        - Shell command definitions for database updates
        - Database initialization scripts with seed data
        - Migration-ready automation templates with SQL integration
        - Backward compatibility template layer
        - MQTT integration for Valetudo commands
        - Comprehensive error handling and validation

        **All output MUST be copy-paste ready with proper YAML formatting per ADR-0008.**

        **THINKING REQUIREMENT:** Validate each YAML block for HA compatibility and ensure SQL operations are atomic.

        **CONFIDENCE ASSESSMENT:** [n]%

    # PHASE 5: Validation Framework
    - id: sql_room_db.validation.comprehensive
      persona: strategos_gpt
      label: "Validation — Acceptance Criteria & Diagnostic Framework"
      mode: validation_mode
      protocols:
        - production_grade_validation
        - adr_compliance_enforcement
      bindings:
        - /mnt/data/draft_template.promptset
        - /mnt/data/ADR/ADR-0008-normalization-and-determinism-rules.md
      prompt: |
        **STRATEGOS PHASE 5/5: VALIDATION FRAMEWORK**
        
        Using all previous outputs, create comprehensive validation and acceptance framework.

        ## Validation Directives

        ### 5.1 Acceptance Criteria Matrix
        **Define binary acceptance tests:**
        ```yaml
        acceptance_criteria:
          database_layer:
            - [ ] Room configs database initializes without errors
            - [ ] SQL sensors successfully query room data with proper JSON parsing
            - [ ] Shell commands execute database updates without corruption
            - [ ] Database schema supports all required room configuration patterns
            - [ ] Query performance remains under 100ms for typical operations
          
          functional_preservation:
            - [ ] Motion lighting triggers function identically to Variable-based original
            - [ ] Vacuum room cleaning maintains all original capabilities
            - [ ] Room-specific timeouts and bypass states work correctly
            - [ ] Presence-based timeout multipliers function as expected
            - [ ] Cross-room coordination (sanctum complex, hallway system) preserved
            
          entity_reduction:
            - [ ] Total entity count reduced by 70%+ from original Variable implementation
            - [ ] Room objects consolidate 6+ entities into single SQL-accessible configuration
            - [ ] No critical functionality lost in consolidation process
            - [ ] Template compatibility maintained for existing integrations
            
          gui_compatibility:
            - [ ] Dashboard cards continue to function with SQL-backed data
            - [ ] Manual override controls remain accessible
            - [ ] Notification templates reference correct entity attributes
            - [ ] Lovelace UI components display room status correctly
            
          performance_validation:
            - [ ] SQL queries execute within 100ms response time
            - [ ] Database updates don't block automation execution
            - [ ] Template rendering performance acceptable for UI responsiveness
            - [ ] Memory usage remains within acceptable bounds
            
          adr_compliance:
            - [ ] Package structure follows ADR-0024 canonical path requirements
            - [ ] Entity references use beta-tier entities per ADR-0021
            - [ ] YAML formatting adheres to ADR-0008 normalization rules
            - [ ] Motion/occupancy/presence signals handled per governance standards
        ```

        ### 5.2 Diagnostic Jinja Templates
        **Create validation and debugging templates:**
        ```jinja
        {# Room Database Health Check Template #}
        {% set rooms = ['bedroom', 'kitchen', 'ensuite', 'desk', 'hallway_downstairs'] %}
        {% set domains = ['motion_lighting', 'vacuum_control', 'shared'] %}

        ## Room Database Health Report
        Generated: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}

        {% for room in rooms %}
        ### Room: {{ room | title }}
        {% for domain in domains %}
        - **{{ domain }}**: {{ room_config(room, domain) is defined and room_config(room, domain) != {} }}
          {% if room_config(room, domain) %}
          - Config: {{ room_config(room, domain) | to_json }}
          {% endif %}
        {% endfor %}
        {% endfor %}

        ## Entity Reduction Analysis
        - **Original Entity Count**: {{ original_entity_count | default(70) }}
        - **Current Entity Count**: {{ current_entity_count | default(10) }}
        - **Reduction Percentage**: {{ ((original_entity_count - current_entity_count) / original_entity_count * 100) | round(1) }}%
        - **Target Met**: {{ 'YES' if ((original_entity_count - current_entity_count) / original_entity_count * 100) >= 70 else 'NO' }}

        ## SQL Sensor Status
        {% set sql_sensors = [
          'sensor.room_config_motion_lighting',
          'sensor.room_config_vacuum_control', 
          'sensor.rooms_needing_cleaning'
        ] %}
        {% for sensor in sql_sensors %}
        - **{{ sensor }}**: {{ 'OK' if states(sensor) not in ['unknown', 'unavailable', ''] else 'FAIL' }}
          - State: {{ states(sensor) }}
          - Last Updated: {{ state_attr(sensor, 'last_updated') }}
        {% endfor %}
        ```

        ### 5.3 Migration Validation Tokens
        **Create verification checkpoints:**
        - `MIGRATION_TOKEN_DATABASE_INITIALIZED`: Room database schema created and seeded
        - `MIGRATION_TOKEN_SQL_SENSORS_OPERATIONAL`: All SQL sensors querying successfully  
        - `MIGRATION_TOKEN_SHELL_COMMANDS_TESTED`: Database update commands validated
        - `MIGRATION_TOKEN_AUTOMATIONS_MIGRATED`: Motion/vacuum automations converted to SQL
        - `MIGRATION_TOKEN_TEMPLATES_COMPATIBLE`: Backward compatibility templates working
        - `MIGRATION_TOKEN_GUI_VERIFIED`: Dashboard and UI components functional
        - `MIGRATION_TOKEN_PERFORMANCE_ACCEPTABLE`: Query response times within limits
        - `MIGRATION_TOKEN_ENTITY_REDUCTION_ACHIEVED`: 70%+ reduction target met

        ### 5.4 Rollback Safety Mechanisms
        **Define comprehensive rollback procedures:**
        ```yaml
        rollback_procedures:
          database_rollback:
            - "Backup current room_database.db before any changes"
            - "Restore previous Variable integration package files"
            - "Re-enable Variable integration in HACS"
            - "Restart Home Assistant to reload Variable entities"
            
          configuration_rollback:
            - "Restore original automation files from backup"
            - "Re-enable Variable-based helper entities"
            - "Update entity references in templates and scripts"
            - "Verify all original functionality restored"
            
          validation_rollback:
            - "Run original package validation tests"
            - "Confirm entity counts match pre-migration state"  
            - "Verify GUI components function with original entities"
            - "Test motion lighting and vacuum control end-to-end"
        ```

        ### 5.5 Performance Benchmarks
        **Define measurable performance criteria:**
        ```yaml
        performance_benchmarks:
          query_response_times:
            room_config_query: "<50ms"
            bulk_room_status: "<100ms"
            cleaning_schedule_query: "<75ms"
            
          database_operations:
            config_update: "<200ms"
            bulk_insert: "<500ms"
            transaction_rollback: "<100ms"
            
          automation_execution:
            motion_trigger_to_light_on: "<2s"
            vacuum_script_execution: "<5s"
            template_rendering: "<100ms"
        ```

        ## Required Output Structure
        **Deliver complete validation framework:**
        - Binary acceptance test matrix with checkboxes
        - Diagnostic Jinja template collection for health monitoring
        - Migration token verification system with clear checkpoints
        - Comprehensive rollback safety procedures
        - Performance benchmark definitions with measurable criteria
        - Test automation scripts for continuous validation
        - Documentation for manual validation procedures

        **THINKING REQUIREMENT:** Consider failure modes, edge cases, and recovery scenarios for robust validation.

        **CONFIDENCE ASSESSMENT:** [n]%

