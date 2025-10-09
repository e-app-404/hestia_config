---
id: prompt_20251004_b5858d
slug: enhanced-motion-lighting-configuration-promptset
title: Enhanced Motion-Lighting Configuration Promptset
date: '2025-10-04'
tier: "\u03B1"
domain: governance
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: ha-config/enhanced-motion-lighting-config.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.172655'
redaction_log: []
---

# Enhanced Motion-Lighting Configuration Promptset
# Comprehensive Home Assistant lighting automation with hierarchical area behavior
# Supports area-specific behaviors, presence enhancement, and blueprint integration

promptset:
  id: enhanced-motion-lighting-config.promptset
  version: 1.0
  created: "2025-10-04"
  description: |
    Comprehensive promptset for implementing area-specific lighting automation that respects spatial relationships and occupancy patterns in Home Assistant. Supports hierarchical behavior, presence enhancement, and blueprint integration with ADR-0021 compliance.
  persona: home_automation_architect
  purpose: |
    Generate working, validated, and intuitive lighting configurations for complex area hierarchies with motion/occupancy/presence integration. Focuses on three key area groups: Sanctum Complex, Kitchen Complex, and Hallway System.
  legacy_compatibility: false
  schema_version: 1.0

  # Artifacts & Bindings
  artifacts:
    required:
      # Input package drafts to be evaluated and migrated
      - path: hestia/workspace/cache/canvas/package_motion_lights-1a.yaml
        description: "One of the two generated package drafts to be evaluated and migrated; contains automation aliases, helper declarations and informs safety pass and mapping decisions"
      - path: hestia/workspace/cache/canvas/package_motion_lights-2a.yaml
        description: "Second generated package draft to be evaluated; contains additional alias lists and VAR sync automations; used to identify missing helpers and consolidation opportunities"
      
      # Core blueprints for instantiation
      - path: library/blueprints/sensor-light.yaml
        description: "Chosen core blueprint for motion lighting; execution plan instantiates this blueprint for each area (referenced as the canonical blueprint)"
      
      # Entity mapping sources
      - path: config/devices/presence.conf
        description: "Source of person and presence entity ids to map presence-related blueprint inputs in the mapping pass"
      - path: config/devices/motion.conf
        description: "Source of motion/occupancy sensor entity ids — used to populate blueprint inputs for triggers"
      - path: config/devices/lighting.conf
        description: "Source of light entity ids and group targets to map blueprint light_target inputs"
      - path: config/preferences/motion_timeout.conf
        description: "Provides recommended timeout profiles to centralize into var or input_number entries during helper consolidation"
      
      # Target destination
      - path: packages/motion_lighting/
        description: "Where the new per-area package files, helpers and VALIDATION.md will live (execution plan step 3 & 4)"
    
    consulted:
      # Source promptsets and generation rules
      - path: hestia/library/prompts/catalog/ha-config/enhanced-motion-lighting-config.promptset
        description: "Primary promptset that defines the desired behavior, blueprint selection, household policy, and constraints used to craft optimized prompt2 and the execution plan"
      - path: hestia/library/prompts/catalog/ha-config/motion_automation_blueprint.promptset
        description: "Provides constraints and deliverables (variables, packages, blueprint mapping) — used to shape mapping pass in execution plan"
      
      # Additional blueprints
      - path: library/blueprints/sensor-light-add-on.yaml
        description: "Used for add-on behaviors and advanced features where appropriate; included in plan for potential instantiation"
      - path: library/blueprints/motion_lights.yaml
        description: "Blueprint collection that informs trigger/condition patterns and parameter expectations; useful for advanced mapping and avoiding duplicated automations"
      - path: library/blueprints/ha-blueprint-linked-entities.yaml
        description: "For linked entities patterns and considerations about not duplicating automations that control the same target"
      
      # Optional entity sources
      - path: config/devices/illuminance.conf
        description: "Optional — used for dynamic lighting / lux gating inputs where available"
      
      # Area and registry mapping
      - path: config/registry/room_registry.yaml
        description: "Area -> sensor -> lighting mapping guide; used to ensure entity mapping uses canonical area ids and adheres to ADR naming"
      - path: library/docs/ADR/area_hierarchy.yaml
        description: "Area relationship contract (v1.1 with registry alignment)"
      
      # Usage guides and policy
      - path: library/helpers/motion_lights/blueprint_usage_guide.md
        description: "Operational guidance for presence policy (asymmetric), validation checklist and recommended defaults — used to craft validation steps and default require_presence_for_activation=false"
      - path: library/helpers/motion_lights/presence_sensors.yaml
        description: "Template sensors and area_presence_map to inform presence input assignments and # TODO placeholders"
      
      # ADR governance and policy
      - path: library/docs/ADR/ADR-0021-motion-occupancy-presence-signals.md
        description: "ADR requirements for motion/occupancy/presence handling used in both prompt2 and execution steps to avoid violating workspace policies"
      - path: library/docs/ADR/ADR-0016-canonical-ha-smb-mount.md
        description: "Minor reference for workspace structure and placement of helpers (ensures consistent package locations)"
      - path: library/docs/ADR/ADR-0023-operator-priority-merge-resolution.md
        description: "Informs merge and branching strategy (create backup branch before mass edits) — included in execution plan step 1"
      
      # Validation tools
      - path: .yamllint.yaml
        description: "Ensures lint rules align with repo standards (2-space indent, etc.) before running Yamllint as validation"
    
    rationale: |
      Files labeled "required" are necessary inputs the execution plan relies on to produce correct blueprint instantiations and helper definitions.
      Files labeled "consulted" are important for policy, naming, and optional features; they influence defaults, validation steps and hardening decisions.
      Destination folder packages/motion_lighting/ is listed as required because the execution plan creates per-area YAML files there.

  bindings:
    protocols:
      - entity_validation_first
      - hierarchical_behavior_modeling
      - adr_compliance_enforcement
      - presence_enhancement_without_blocking
    hard_guardrails:
      - "Do not substitute alpha-tier entities when a beta-tier entity is missing; emit blank input with '# TODO'."
      - "Map concrete entities from device config files FIRST; only use TODO for genuinely missing beta composites."
      - "Every automation MUST have complete use_blueprint block; no alias-only entries allowed."
      - "All helper blocks (input_boolean, var) MUST have concrete initial values, not empty declarations."
      - "DO NOT gate essential lighting behind unmeasurable helpers (cooking_mode, sleep_mode, etc.); use sensor-driven logic only."
      - "DO NOT gate essential lighting behind unmeasurable helpers (cooking_mode, sleep_mode, etc.); use sensor-driven logic only."
    persona: home_automation_architect

  retrieval_tags:
    - home_assistant
    - motion_lighting
    - area_hierarchy
    - presence_detection
    - blueprint_automation
    - adr_compliance

  operational_modes:
    - entity_validation_mode
    - configuration_generation_mode
    - critical_analysis_mode
    - deployment_validation_mode

  # Target Areas Configuration
  target_areas:
    sanctum_complex:
      description: "Upstairs private space"
      container: sanctum
      main_area: bedroom
      subareas: [desk, wardrobe, ottoman, hifi_configuration]
      connected_areas: [ensuite]
      cross_area_triggers:
        wardrobe_to_bedroom: "wardrobe motion/occupancy contributes to bedroom aggregate (unidirectional)"
        wardrobe_to_ottoman: "wardrobe motion triggers ottoman lightstrip activation"
      behaviors:
        desk: "Extended timeout for work sessions, presence-enhanced brightness, independence from bedroom main lighting (uses occupancy_beta if available)"
        wardrobe: "30-second timeout lightstrip automation; contributes to bedroom motion/occupancy but not vice versa; triggers ottoman lightstrip"
        ottoman: "Vibration sensor integration with wardrobe motion trigger for lightstrip activation"
        ensuite: "Privacy-aware timing, shower occupancy detection integration"

    kitchen_complex:
      description: "Downstairs utility"
      main_area: kitchen
      connected_areas: [laundry_room]
      behaviors:
        kitchen: "Standard motion lighting with appropriate timeout for food prep and cleanup activities"

    hallway_system:
      description: "Circulation spaces"
      main_area: hallway_downstairs
      proxy_areas: [entrance]  # motion sensor proxy only - no direct lighting
      connected_areas: [upstairs]
      behaviors:
        hallways: "Motion-triggered transit lighting with area-to-area propagation logic (beta-only sensors, per-level groups)"
      propagation:
        enabled: true
        source: hallway_downstairs
        targets: [upstairs]
        decay_rate: 0.7
        window_seconds: 20

  # Blueprint Selection Matrix
  blueprint_matrix:
    core_executor: library/blueprints/sensor-light.yaml
    add_on: library/blueprints/sensor-light-add-on.yaml
    link_entities: library/blueprints/ha-blueprint-linked-entities.yaml
    rules:
      bedroom: [core_executor]
      desk: [core_executor, link_entities]           # task lighting coherence
      wardrobe: [core_executor, link_entities]       # 30s timeout + ottoman lightstrip trigger
      ottoman: [link_entities]                       # vibration sensor + wardrobe motion linkage
      kitchen: [core_executor]                       # standard motion lighting
      ensuite: [core_executor]                       # privacy timing
      hallway_downstairs: [core_executor]
      hallway_upstairs: [core_executor]

  # Household Policy
  household_policy:
    tracked_persons: 1  # person.evert
    untracked_housemates: 1
    presence_policy: "asymmetric"  # Presence enhances, absence never blocks
    motion_activation: "independent"  # Must work for untracked occupant
    presence_generation_rules:
      require_presence_for_activation_default: false
      presence_entity_pattern: "binary_sensor.*_presence_beta"
      enhancement_examples:
        - "timeout_seconds += 120 when presence on"
        - "brighter scene when presence on; neutral otherwise"

  # Technical Constraints
  technical_constraints:
    adr_compliance: "ADR-0021"
    tier_progression: "alpha → beta → eta"
    propagation_decay_rate: 0.7
    entity_patterns:
      motion_sensors: "binary_sensor.*_motion_beta"
      occupancy_sensors: "binary_sensor.*_occupancy_beta"
      illuminance_sensors: "sensor.*_illuminance_beta"
      vibration_sensors: "binary_sensor.*_vibration"
      presence_entity: "person.evert"

  # Prompts Section
  prompts:
    - id: enhanced_lighting.entity_validation.v1
      persona: home_automation_architect
      label: "Entity Inventory Validation"
      mode: entity_validation_mode
      protocols:
        - entity_validation_first
        - hierarchical_behavior_modeling
      bindings:
        - config/devices/motion.conf
        - config/devices/lighting.conf
        - config/devices/illuminance.conf
        - config/devices/presence.conf
      prompt: |
        version: 1.0
        
        ## Context & Prerequisites
        I'm working with a comprehensive Home Assistant setup that includes motion-lighting blueprints, device configurations, and area hierarchy documentation. I need to implement area-specific lighting automation that respects spatial relationships and occupancy patterns.

        ## Phase 1: Entity Inventory Validation
        
        Please validate all required entities exist and are correctly mapped for the target areas:
        
        ### Target Areas for Validation:
        1. **Sanctum Complex** (upstairs private space)
           - sanctum (container) → bedroom (main area) → desk, wardrobe, ottoman, hifi_configuration (subareas)
           - ensuite (connected area)

        2. **Kitchen Complex** (downstairs utility)
           - kitchen (main area) + laundry_room (connected utility space)

        3. **Hallway System** (circulation spaces)
           - hallway_downstairs (main circulation) + entrance (motion proxy only) + upstairs (upper circulation)

        ### Validation Requirements:
        - Motion sensors per area (from motion.conf)
        - Light entities and groups (from lighting.conf)  
        - Illuminance sensors (from illuminance.conf)
        - Presence sensors (from presence.conf integration)

        ### Output Required:
        Generate a comprehensive entity inventory report showing:
        - ✅ Available entities per area
        - ❌ Missing entities or gaps
        - ⚠️ Potential mapping issues
        - 📋 Entity relationship validation

        Proceed to Phase 2 only after validation is complete.

      phases:
        - name: entity_inventory
          persona: home_automation_architect
          instructions: |
            Parse all device configuration files and generate comprehensive entity inventory.
            Cross-reference with target areas and identify any gaps or inconsistencies.
            Flag entities that don't follow ADR-0021 naming conventions.
          outputs:
            - name: entity_validation_report.md
              required: true
              content: |
                # Entity Validation Report
                
                ## Beta Compliance Gates (fail if any ❌)
                - Motion beta present for all targeted areas: [...]
                - Occupancy beta present where specified in behaviors: [...]
                - Illuminance beta present for areas with lux gating; others flagged TODO: [...]
                
                ## Target Area Coverage Analysis
                [Detailed entity mapping per area]
                
                ## Missing Entities Report
                [List of required but missing entities]
                
                ## ADR-0021 Compliance Check
                [Entity naming convention validation]

    - id: enhanced_lighting.configuration_generation.v1
      persona: home_automation_architect
      label: "Blueprint Configuration Generation"
      mode: configuration_generation_mode
      protocols:
        - hierarchical_behavior_modeling
        - adr_compliance_enforcement
        - presence_enhancement_without_blocking
      bindings:
        - library/blueprints/
        - config/preferences/motion_timeout.conf
        - library/docs/ADR/area_hierarchy.yaml
      prompt: |
        version: 1.0
        
        ## Phase 2: Blueprint Configuration Generation
        
        Based on the validated entity inventory, generate COMPLETE, DEPLOYABLE YAML configurations using appropriate blueprints from the blueprint collection.
        
        CRITICAL: Generate full automation bodies with `use_blueprint:` blocks, NOT alias-only lists.

        ### Configuration Requirements:
        
        #### Area-Specific Behaviors:
        - **Desk subarea:** Extended timeout for work sessions, presence-enhanced brightness, independence from bedroom main lighting
        - **Wardrobe subarea:** 30-second timeout lightstrip; contributes to bedroom motion aggregate (unidirectional); triggers ottoman lightstrip
        - **Ottoman subarea:** Vibration sensor (bedroom_ottoman_alpha_vibration) integration with wardrobe motion trigger for lightstrip
        - **Kitchen:** Standard motion lighting with appropriate timeout for food prep and cleanup activities
        - **Ensuite:** Privacy-aware timing, shower occupancy detection integration
        - **Hallways:** Motion-triggered transit lighting with area-to-area propagation logic

        #### Hierarchical Constraints:
        - Floor → Area → Subarea inheritance with override capability
        - Presence enhancement for tracked person (person.evert) without blocking untracked housemate
        - Propagation rules following area_hierarchy.yaml contract (decay_rate: 0.7)
        - Timeout profiles per motion_timeout.conf matrix

        #### Technical Specifications:
        - Use existing blueprint patterns from library/blueprints/
        - Integrate with binary_sensor.*_motion_beta and binary_sensor.*_occupancy_beta entities
        - Respect illuminance thresholds from sensor.*_illuminance_beta
        - Follow ADR-0021 signal standardization (alpha→beta→eta progression)

        #### Generation Contract:
        inputs_required:
          - motion_sensors: ["binary_sensor.<area>_motion_beta"]
        inputs_optional:
          - occupancy_sensors: ["binary_sensor.<area>_occupancy_beta"]
          - vibration_sensors: ["binary_sensor.<area>_vibration"]
          - ambient_lux_entity: ["sensor.<area>_illuminance_beta"]
          - presence_entity: ["binary_sensor.<area>_presence_beta"]
        policy:
          - "If optional inputs missing, set to '' and add '# TODO'."
          - "Always use eta-tier group lights as targets."
        
        #### MANDATORY OUTPUT FORMAT:
        ```yaml
        # Complete automation with blueprint instantiation - NOT alias-only
        automation:
          - alias: "Motion Lights — Bedroom"
            use_blueprint:
              path: library/blueprints/sensor-light.yaml
            input:
              motion_trigger: binary_sensor.bedroom_motion_beta
              light_switch: light.group_bedroom_lights_eta
              time_delay: 300
              presence_entity: '# TODO: binary_sensor.bedroom_presence_beta'
              require_presence_for_activation: false
        ```
        
        #### ANTI-PATTERNS TO AVOID:
        - ❌ `- alias: "Motion Lights — Bedroom"` (incomplete)
        - ❌ Empty `var:` blocks without definitions
        - ❌ Helper declarations without initial values
        - ✅ Complete `use_blueprint:` blocks with all inputs

        ### Output Required:
        Generate complete, working blueprint configurations for each target area with:
        - Area-specific parameter tuning
        - Hierarchical behavior implementation  
        - Context-aware timeout application
        - Presence enhancement integration

      phases:
        - name: blueprint_configuration
          persona: home_automation_architect
          instructions: |
            Generate working YAML configurations using validated entities and appropriate blueprints.
            Implement hierarchical behavior patterns with proper inheritance and overrides.
            Ensure ADR-0021 compliance throughout all configurations.
          outputs:
            - name: sanctum_complex_config.yaml
              required: true
              content: |
                # COMPLETE package file with:
                input_boolean:
                  motion_bypass_bedroom: {initial: false, icon: mdi:motion-sensor-off}
                  motion_bypass_desk: {initial: false, icon: mdi:motion-sensor-off}
                  motion_bypass_wardrobe: {initial: false, icon: mdi:motion-sensor-off}
                
                var:
                  motion_timeout_bedroom: 300
                  motion_timeout_desk: 180
                  motion_timeout_wardrobe: 30
                  motion_timeout_ensuite: 600
                
                automation:
                  - alias: "Motion Lights — Bedroom"
                    use_blueprint:
                      path: library/blueprints/sensor-light.yaml
                    input:
                      motion_trigger: binary_sensor.bedroom_motion_beta
                      light_switch: light.group_bedroom_lights_eta
                  - alias: "Motion Lights — Wardrobe"
                    use_blueprint:
                      path: library/blueprints/sensor-light.yaml
                    input:
                      motion_trigger: binary_sensor.wardrobe_motion_beta
                      light_switch: light.bedroom_ottoman_lightstrip_alpha_matter
                      time_delay: 30
                  - alias: "Linked — Wardrobe to Ottoman Lightstrip"
                    use_blueprint:
                      path: library/blueprints/ha-blueprint-linked-entities.yaml
                    input:
                      linked_entity: 
                        - binary_sensor.wardrobe_motion_beta
                        - binary_sensor.bedroom_ottoman_alpha_vibration
                      target_entity: light.bedroom_ottoman_lightstrip_alpha_matter
            - name: kitchen_complex_config.yaml
              required: true
              content: |
                # COMPLETE package with standard motion lighting (no unmeasurable cooking mode gates)
                input_boolean:
                  motion_bypass_kitchen: {initial: false, icon: mdi:motion-sensor-off}
                  motion_bypass_laundry_room: {initial: false, icon: mdi:motion-sensor-off}
                
                var:
                  motion_timeout_kitchen: 180
                  motion_timeout_laundry_room: 120
            - name: hallway_system_config.yaml
              required: true
              content: |
                # COMPLETE package with propagation logic and circulation automation

    - id: enhanced_lighting.critical_analysis.v1
      persona: home_automation_architect
      label: "Critical Analysis & Optimization"
      mode: critical_analysis_mode
      protocols:
        - adr_compliance_enforcement
        - presence_enhancement_without_blocking
      bindings:
        - library/docs/ADR/ADR-0021-motion-occupancy-presence-signals.md
      prompt: |
        version: 1.0
        
        ## Phase 3: Critical Analysis
        
        Perform comprehensive analysis of the generated configurations to identify optimization opportunities and potential issues.

        ### Analysis Framework:
        
        #### Areas of Opportunity:
        - Identify automation gaps or optimization potential
        - Suggest improvements to existing blueprint patterns
        - Highlight entity relationship improvements
        - Performance optimization recommendations

        #### Uncertainty/Machine-Friendliness Issues:
        - Flag ambiguous sensor mappings or missing entities
        - Identify complex logic that needs template sensors
        - Point out blueprint limitations requiring custom automation
        - Highlight potential maintenance challenges

        #### Validation Checklist:
        - [ ] All target areas have complete sensor coverage
        - [ ] Hierarchical relationships properly implemented
        - [ ] Presence enhancement works without blocking untracked housemate
        - [ ] Timeout profiles match expected usage patterns
        - [ ] Blueprint parameters align with ADR-0021 standards

        ### Questions for User Validation:
        1. Do the assumed area-specific behaviors match your actual usage patterns?
        2. Are there additional context sensors (time of day, activity modes) to consider?
        3. Should any areas have manual override capabilities or scheduling exceptions?
        4. Are there specific brightness or color temperature preferences per area?
        5. Do the timeout profiles in motion_timeout.conf align with your experience?

      phases:
        - name: critical_analysis
          persona: home_automation_architect
          instructions: |
            Analyze generated configurations for gaps, optimization opportunities, and compliance issues.
            Generate actionable recommendations and validation questions for user feedback.
          outputs:
            - name: critical_analysis_report.md
              required: true
              content: |
                # Critical Analysis Report
                
                ## Optimization Opportunities
                [Detailed recommendations for improvements]
                
                ## Uncertainty & Risk Assessment
                [Potential issues and mitigation strategies]
                
                ## Validation Checklist Results
                [Compliance and functionality verification]
                
                ## User Validation Questions
                [Questions requiring user confirmation]

  # Migration Guidance
  migration:
    strategy: |
      This promptset replaces the previous enhanced-lighting-prompt.md with structured, multi-phase workflow.
      Legacy single-prompt approach migrated to three-phase validation → generation → analysis pattern.
      All original requirements preserved with enhanced structure and governance.

  # Extensibility & Documentation
  extensibility:
    - Add new target areas by extending target_areas configuration
    - Implement additional analysis phases for specialized requirements
    - Extend household_policy for different occupancy patterns
    - Add custom operational modes for specific use cases
  
  documentation:
    - Reference: ADR-0021 for signal standardization requirements
    - See library/blueprints/ for available automation patterns
    - Consult area_hierarchy.yaml for spatial relationship rules
    - Motion timeout profiles defined in motion_timeout.conf

  # Execution Mandate for Next GPT
  execution_mandate:
    target_paths:
      - "library/blueprints/"
      - "config/devices/presence.conf"
      - "config/devices/motion.conf"
      - "config/devices/lighting.conf"
      - "config/devices/illuminance.conf"
      - "library/docs/ADR/area_hierarchy.yaml"
      - "config/registry/room_registry.yaml"
      - "config/preferences/motion_timeout.conf"
      - "helpers/motion_lights/"
    objective: "Emit deploy-ready motion-lighting packages using beta abstractions for motion/occupancy/illuminance, eta-tier group lights, and asymmetric presence enhancements. Apply hierarchical behaviors for Sanctum Complex, Kitchen Complex, and Hallway System."
    acceptance:
      - "All packages reference only *_beta sensors; no alpha entities appear"
      - "Illuminance uses sensor.<room>_illuminance_beta or is '' with # TODO"
      - "Desk and both hallways are fully implemented; Wardrobe only if explicitly requested"
      - "Presence never blocks activation; enhancements implemented where presence betas exist"
      - "Blueprint selection follows blueprint_matrix and no duplicate logic across add-ons"
      - "Timeouts follow config/preferences/motion_timeout.conf profiles"
      - "YAML passes ha core check; two-space indent; A→Z keys"
      - "NO ALIAS-ONLY AUTOMATIONS: Every automation has complete use_blueprint block"
      - "NO EMPTY BLOCKS: All var:, input_boolean:, automation: sections populated"
      - "DEPLOYABLE STATE: Files load in HA without syntax errors or missing references"
    risk:
      - "Missing beta composites in certain rooms (emit TODO blanks)"
      - "Propagation tuning could over/under-trigger; use decay_rate 0.7 and 20s window"
    rollback: "Revert to previous stable packages; disable new packages by setting initial_state: 'off'."
