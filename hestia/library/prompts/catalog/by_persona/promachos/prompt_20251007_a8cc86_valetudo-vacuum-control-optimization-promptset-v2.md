---
id: prompt_20251007_a8cc86
slug: valetudo-vacuum-control-optimization-promptset-v2
title: Valetudo Vacuum Control Optimization Promptset v2
date: '2025-10-07'
tier: "\u03B1"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: valetudo_optimization_comprehensive_v2.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:26.810417'
redaction_log: []
---

# Valetudo Vacuum Control Optimization Promptset v2
# Multi-prompt sequential execution with bundle artifact mapping

promptset:
  id: valetudo-vacuum-optimization.promptset.v2
  version: 2.0
  created: "2025-10-07"
  description: |
    Enhanced promptset for optimizing Valetudo vacuum control package using sequential prompt execution.
    Maps bundle artifacts to /mnt/data/* paths and breaks optimization into discrete, manageable prompts
    for ChatGPT-5 Thinking model execution.
  persona: strategos_gpt
  purpose: |
    Generate a complete, production-ready Valetudo vacuum control package through sequential prompt
    execution. Each prompt handles a specific optimization aspect with clear inputs and outputs,
    building toward comprehensive MQTT-based vacuum control with HACS Variable optimization.
  legacy_compatibility: false
  schema_version: 1.0

  # Artifacts & Bindings (Bundle Contents Mapped)
  artifacts:
    required:
      - path: /mnt/data/package_control_vacuum.yaml
        description: "Current vacuum package with reliability issues and incorrect command syntax"
      - path: /mnt/data/valetudo.conf
        description: "Valetudo robot configuration with MQTT settings and segment mapping"
      - path: /mnt/data/hacs.variable.md
        description: "HACS Variable component documentation for optimized state management"
      - path: /mnt/data/integration.vacuum.md
        description: "Home Assistant vacuum integration reference"
      - path: /mnt/data/integration.valetudo.md
        description: "Valetudo-specific integration patterns and MQTT commands"
      - path: /mnt/data/mqtt_discovery_comprehensive_analysis.md
        description: "MQTT discovery analysis and troubleshooting reference"
    optional:
      - path: /mnt/data/valetudo-notifications.yaml
        description: "Reference blueprint for Valetudo notifications"
      - path: /mnt/data/valetudo-clean-rooms.yaml
        description: "Reference blueprint for room cleaning scripts"
      - path: /mnt/data/valetudo-send-vacuum-command.yaml
        description: "Reference blueprint for vacuum command patterns"
      - path: /mnt/data/README.md
        description: "Bundle documentation with optimization objectives and robot configuration"

  bindings:
    protocols:
      - production_ready_first
      - mqtt_command_validation
      - variable_optimization_analysis
      - comprehensive_error_handling
      - sequential_prompt_execution
    persona: strategos_gpt

  retrieval_tags:
    - valetudo
    - vacuum
    - mqtt
    - hacs-variable
    - optimization
    - production-grade
    - home-assistant
    - sequential-execution

  operational_modes:
    - analysis_mode
    - design_mode
    - implementation_mode
    - validation_mode

  # Sequential Prompts for Optimization
  prompts:
    # Phase 1: Current State Analysis
    - id: valetudo.analysis.current_state
      persona: strategos_gpt
      label: "Current State Analysis — Entity Inventory & Problem Assessment"
      mode: analysis_mode
      protocols:
        - production_ready_first
        - comprehensive_error_handling
      bindings:
        - /mnt/data/package_control_vacuum.yaml
        - /mnt/data/valetudo.conf
        - /mnt/data/README.md
      prompt: |
        **PROMPT 1/8: CURRENT STATE ANALYSIS**

        **You are Strategos GPT (model: GPT-5 Thinking). Analyze the current Valetudo vacuum control package and provide structured assessment.**

        ## Inputs Available
        - Current package: `/mnt/data/package_control_vacuum.yaml`
        - Robot config: `/mnt/data/valetudo.conf`
        - Bundle overview: `/mnt/data/README.md`

        ## Analysis Tasks

        ### 1. Entity Inventory Assessment
        **Count and categorize all entities in current package:**
        - Input helpers (datetime/boolean breakdown)
        - Template sensors 
        - Automations (by trigger type)
        - Scripts (by functionality)
        - Total entity count for baseline

        ### 2. Command Pattern Analysis
        **Identify all vacuum.send_command usage:**
        - Extract command types and parameters
        - Map segment cleaning patterns
        - Document reliability issues and failure modes

        ### 3. MQTT Configuration Review
        **From valetudo.conf, extract:**
        - MQTT broker settings (host, port, credentials)
        - Topic prefix and robot identifier
        - Available capabilities and segment mapping

        ### 4. Problem Classification
        **Categorize issues by severity:**
        - Critical: Command failures, state inconsistencies
        - High: Performance bottlenecks, missing error handling
        - Medium: Notification gaps, maintainability issues

        ## Required Output Structure
        ```yaml
        current_state_analysis:
          entity_inventory:
            input_helpers: {datetime: N, boolean: N, total: N}
            template_sensors: N
            automations: N
            scripts: N
            total_entities: N
          
          command_patterns:
            vacuum_send_command_usage: [list of commands]
            segment_cleaning_patterns: [room -> segment mapping]
            reliability_issues: [documented problems]
          
          mqtt_configuration:
            broker: {host: "", port: N, credentials: ""}
            topic_prefix: ""
            robot_identifier: ""
            capabilities: [list]
          
          problem_classification:
            critical: [list]
            high: [list]
            medium: [list]
        ```

        **END: CONFIDENCE ASSESSMENT: [n]%**

    # Phase 1: Variable Component Analysis
    - id: valetudo.analysis.variable_optimization
      persona: strategos_gpt
      label: "Variable Component Analysis — HACS Variable Consolidation Opportunities"
      mode: analysis_mode
      protocols:
        - variable_optimization_analysis
        - production_ready_first
      bindings:
        - /mnt/data/hacs.variable.md
        - /mnt/data/package_control_vacuum.yaml
      prompt: |
        **PROMPT 2/8: VARIABLE COMPONENT ANALYSIS**

        **Using output from PROMPT 1 and HACS Variable documentation, analyze consolidation opportunities.**

        ## Inputs Required
        - Previous output: `current_state_analysis`
        - HACS Variable docs: `/mnt/data/hacs.variable.md`
        - Current package entities for reference

        ## Analysis Tasks

        ### 1. Consolidation Opportunities
        **Map current input helpers to Variable potential:**
        - Room cleaning timestamps (6 datetime helpers)
        - Room cleaning flags (6 boolean helpers)
        - Identify consolidation patterns using Variable attributes

        ### 2. Performance Impact Assessment
        **Compare approaches:**
        - Current: Individual helper entity state changes
        - Variable: Attribute updates within single entity
        - Automation trigger frequency implications
        - Database query optimization potential

        ### 3. Feature Benefit Analysis
        **Evaluate Variable-specific benefits:**
        - SQL query capabilities for historical analysis
        - Template-based attribute updates
        - Persistence advantages over input helpers
        - Reduced entity namespace pollution

        ### 4. Migration Strategy Design
        **Plan transition approach:**
        - Parallel running period requirements
        - Data migration procedures
        - Rollback safety mechanisms
        - Validation checkpoints

        ## Required Output Structure
        ```yaml
        variable_optimization_analysis:
          consolidation_opportunities:
            room_cleaning_state:
              current_entities: [list of helper entities]
              variable_attributes: [proposed attribute structure]
              entity_reduction: {from: N, to: N, percentage: N}
          
          performance_impact:
            automation_triggers: {current: N, optimized: N}
            state_changes: {current: "frequent", optimized: "reduced"}
            database_queries: [optimization opportunities]
          
          feature_benefits:
            sql_capabilities: [specific use cases]
            template_advantages: [automation simplifications]
            persistence_gains: [reliability improvements]
          
          migration_strategy:
            transition_phases: [ordered steps]
            validation_points: [checkpoint criteria]
            rollback_procedures: [safety mechanisms]
        ```

        **END: CONFIDENCE ASSESSMENT: [n]%**

    # Phase 2: MQTT Command Design
    - id: valetudo.design.mqtt_commands
      persona: strategos_gpt
      label: "MQTT Command Design — Proper Valetudo Integration Patterns"
      mode: design_mode
      protocols:
        - mqtt_command_validation
        - production_ready_first
      bindings:
        - /mnt/data/integration.valetudo.md
        - /mnt/data/mqtt_discovery_comprehensive_analysis.md
        - /mnt/data/valetudo-send-vacuum-command.yaml
      prompt: |
        **PROMPT 3/8: MQTT COMMAND DESIGN**

        **Design proper MQTT command patterns to replace vacuum.send_command usage.**

        ## Inputs Required
        - Previous outputs: `current_state_analysis`, `variable_optimization_analysis`
        - Valetudo integration guide: `/mnt/data/integration.valetudo.md`
        - MQTT analysis: `/mnt/data/mqtt_discovery_comprehensive_analysis.md`
        - Blueprint reference: `/mnt/data/valetudo-send-vacuum-command.yaml`

        ## Design Tasks

        ### 1. Topic Structure Definition
        **Design MQTT topic hierarchy:**
        - Base topic from robot configuration
        - Capability-specific topic patterns
        - Command vs status topic separation
        - Discovery compatibility requirements

        ### 2. Payload Structure Design
        **Define JSON payload schemas:**
        - Segment cleaning command structure
        - Iteration and customOrder parameters
        - Error handling payload formats
        - Status confirmation patterns

        ### 3. Room-to-Segment Mapping
        **Create room configuration structure:**
        - Room names to segment ID mapping
        - Flexible configuration for easy updates
        - Multi-segment room support
        - Validation mechanisms

        ### 4. Command Validation Framework
        **Design payload validation:**
        - JSON schema validation patterns
        - MQTT connectivity verification
        - Command acknowledgment handling
        - Timeout and retry mechanisms

        ## Required Output Structure
        ```yaml
        mqtt_command_design:
          topic_structure:
            base_topic: "Valetudo/RoboRockS5"
            command_topics:
              segment_clean: "MapSegmentationCapability/clean/set"
              status: "MapSegmentationCapability/clean"
            discovery_topics: [autodiscovery patterns]
          
          payload_schemas:
            segment_clean:
              action: "start_segment_action"
              required_fields: [segment_ids, iterations, customOrder]
              optional_fields: [custom parameters]
            status_confirmation: [expected response structure]
          
          room_segment_mapping:
            living_room: {segment_id: 1, name: "Living Room"}
            kitchen: {segment_id: 2, name: "Kitchen"}
            # ... other rooms
          
          validation_framework:
            payload_validation: [JSON schema patterns]
            connectivity_checks: [MQTT broker validation]
            acknowledgment_handling: [confirmation mechanisms]
        ```

        **END: CONFIDENCE ASSESSMENT: [n]%**

    # Phase 2: Error Handling Design
    - id: valetudo.design.error_handling
      persona: strategos_gpt
      label: "Error Handling Design — Comprehensive Failure Recovery"
      mode: design_mode
      protocols:
        - comprehensive_error_handling
        - production_ready_first
      bindings:
        - /mnt/data/integration.vacuum.md
        - /mnt/data/valetudo-notifications.yaml
      prompt: |
        **PROMPT 4/8: ERROR HANDLING DESIGN**

        **Design comprehensive error handling and recovery mechanisms.**

        ## Inputs Required
        - Previous outputs: All previous analysis and design outputs
        - Vacuum integration reference: `/mnt/data/integration.vacuum.md`
        - Notification blueprint: `/mnt/data/valetudo-notifications.yaml`

        ## Design Tasks

        ### 1. Failure Mode Classification
        **Identify and categorize failure scenarios:**
        - MQTT broker connectivity issues
        - Robot hardware errors and states
        - Segment cleaning failures
        - Timeout and communication errors

        ### 2. Detection Mechanisms
        **Design error detection systems:**
        - Real-time status monitoring
        - Cleaning verification procedures
        - Connectivity health checks
        - State consistency validation

        ### 3. Recovery Procedures
        **Define automated recovery actions:**
        - Retry mechanisms with backoff
        - Fallback cleaning strategies
        - Manual intervention triggers
        - Safe state restoration

        ### 4. Notification Framework
        **Design user notification system:**
        - Error severity classification
        - Actionable notification content
        - Escalation procedures
        - Status dashboard integration

        ## Required Output Structure
        ```yaml
        error_handling_design:
          failure_modes:
            mqtt_connectivity: [connection failures, authentication errors]
            robot_hardware: [error states, battery issues, blockages]
            cleaning_operations: [segment failures, timeout conditions]
            communication: [payload errors, acknowledgment timeouts]
          
          detection_mechanisms:
            real_time_monitoring: [sensor patterns, automation triggers]
            verification_procedures: [cleaning completion checks]
            health_checks: [connectivity validation, robot status]
          
          recovery_procedures:
            retry_mechanisms: [backoff strategies, attempt limits]
            fallback_strategies: [alternative cleaning approaches]
            manual_intervention: [escalation triggers, human override]
          
          notification_framework:
            severity_levels: [critical, warning, info]
            notification_content: [actionable message templates]
            delivery_methods: [push, persistent, dashboard]
        ```

        **END: CONFIDENCE ASSESSMENT: [n]%**

    # Phase 3: Implementation - Variable Component
    - id: valetudo.implementation.variables
      persona: strategos_gpt
      label: "Variable Implementation — HACS Variable Component Configuration"
      mode: implementation_mode
      protocols:
        - production_ready_first
        - variable_optimization_analysis
      bindings:
        - /mnt/data/hacs.variable.md
      prompt: |
        **PROMPT 5/8: VARIABLE IMPLEMENTATION**

        **Implement complete HACS Variable configuration based on previous analysis.**

        ## Inputs Required
        - All previous analysis and design outputs
        - Variable component documentation for syntax reference

        ## Implementation Tasks

        ### 1. Variable Definitions File
        **Create `domain/variables/vacuum_variables.yaml`:**
        - Room cleaning state consolidated variable
        - Job status tracking variable
        - Configuration and metadata variables
        - Proper attribute structure and initial values

        ### 2. Template Integration
        **Design template sensors for compatibility:**
        - Backward compatibility with existing automations
        - Days-since-cleaned calculations using Variable attributes
        - Status aggregation and reporting sensors

        ### 3. Migration Procedures
        **Document data migration:**
        - Current helper values to Variable attributes
        - Automation trigger updates
        - Template reference updates

        ## Required Output Structure
        ```yaml
        variable_implementation:
          file_content:
            domain_variables_vacuum_variables_yaml: |
              # Complete YAML content for Variable definitions
          
          template_sensors:
            compatibility_sensors: |
              # Template sensor definitions for backward compatibility
          
          migration_procedures:
            data_migration: [step-by-step helper to Variable transfer]
            automation_updates: [required trigger and template changes]
        ```

        **Provide complete, deployable YAML content with no placeholders.**

        **END: CONFIDENCE ASSESSMENT: [n]%**

    # Phase 3: Implementation - Main Package
    - id: valetudo.implementation.main_package
      persona: strategos_gpt
      label: "Main Package Implementation — MQTT-based Vacuum Control"
      mode: implementation_mode
      protocols:
        - production_ready_first
        - mqtt_command_validation
        - comprehensive_error_handling
      bindings:
        - /mnt/data/valetudo-clean-rooms.yaml
        - /mnt/data/valetudo-notifications.yaml
      prompt: |
        **PROMPT 6/8: MAIN PACKAGE IMPLEMENTATION**

        **Implement complete optimized package with MQTT commands and error handling.**

        ## Inputs Required
        - All previous analysis, design, and variable implementation outputs
        - Blueprint references for implementation patterns

        ## Implementation Tasks

        ### 1. Core Package Structure
        **Create `packages/package_valetudo_control.yaml`:**
        - MQTT-based room cleaning scripts
        - Error handling automations
        - Status monitoring and notifications
        - Scheduled cleaning operations

        ### 2. MQTT Command Implementation
        **Replace all vacuum.send_command patterns:**
        - Proper mqtt.publish actions with validated payloads
        - Room-to-segment mapping integration
        - Command acknowledgment handling

        ### 3. Error Handling Integration
        **Implement comprehensive error detection:**
        - MQTT connectivity monitoring
        - Robot status validation
        - Cleaning verification procedures
        - Recovery and notification actions

        ### 4. Notification System
        **Complete notification framework:**
        - Cleaning completion reports
        - Error alerts with actionable content
        - Status dashboard updates

        ## Required Output Structure
        ```yaml
        main_package_implementation:
          file_content:
            packages_package_valetudo_control_yaml: |
              # Complete YAML content for optimized package
          
          key_improvements:
            mqtt_commands: [specific replacements made]
            error_handling: [implemented safeguards]
            notifications: [enhanced reporting features]
        ```

        **Provide complete, deployable YAML content with no placeholders.**

        **END: CONFIDENCE ASSESSMENT: [n]%**

    # Phase 4: Validation and Deployment
    - id: valetudo.validation.testing_procedures
      persona: strategos_gpt
      label: "Validation Suite — Testing and Deployment Procedures"
      mode: validation_mode
      protocols:
        - production_ready_first
        - comprehensive_error_handling
      bindings:
        - /mnt/data/README.md
      prompt: |
        **PROMPT 7/8: VALIDATION SUITE**

        **Create comprehensive testing and deployment procedures.**

        ## Inputs Required
        - All previous implementation outputs
        - Bundle documentation for context

        ## Validation Tasks

        ### 1. Configuration Validation
        **Create syntax and structure checks:**
        - YAML syntax validation commands
        - Home Assistant configuration checks
        - MQTT payload validation tests

        ### 2. Functional Testing Procedures
        **Design operational test scenarios:**
        - MQTT connectivity verification
        - Room cleaning command tests
        - Error handling simulation
        - Variable state management validation

        ### 3. Apply/Rollback Scripts
        **Create deployment automation:**
        - Apply script with validation gates
        - Rollback script with safety checks
        - Backup and restore procedures

        ### 4. Audit Template
        **Create monitoring template:**
        - System health dashboard
        - Performance metrics tracking
        - Ongoing validation checks

        ## Required Output Structure
        ```yaml
        validation_suite:
          configuration_checks:
            yaml_validation: [specific commands]
            ha_config_check: [validation procedures]
            mqtt_payload_tests: [test scenarios]
          
          functional_tests:
            connectivity_tests: [MQTT broker verification]
            cleaning_tests: [room-by-room validation]
            error_simulation: [failure scenario tests]
          
          deployment_scripts:
            apply_script: |
              # Complete bash script content
            rollback_script: |
              # Complete bash script content
          
          audit_template: |
            # Complete Jinja2 template for monitoring
        ```

        **Provide complete, executable scripts and templates.**

        **END: CONFIDENCE ASSESSMENT: [n]%**

    # Phase 4: Benefits Analysis and Documentation
    - id: valetudo.analysis.benefits_documentation
      persona: strategos_gpt
      label: "Benefits Analysis — Quantitative Improvements and Documentation"
      mode: analysis_mode
      protocols:
        - production_ready_first
      bindings:
        - /mnt/data/README.md
      prompt: |
        **PROMPT 8/8: BENEFITS ANALYSIS**

        **Provide comprehensive benefits analysis and final documentation.**

        ## Inputs Required
        - All previous analysis and implementation outputs
        - Original objectives from bundle documentation

        ## Analysis Tasks

        ### 1. Quantitative Benefits Assessment
        **Calculate measurable improvements:**
        - Entity reduction percentages
        - Automation trigger frequency reduction
        - Performance improvements
        - Reliability enhancements

        ### 2. Implementation Comparison
        **Before vs After analysis:**
        - Command reliability (vacuum.send_command vs MQTT)
        - State management efficiency
        - Error handling coverage
        - Maintenance complexity

        ### 3. Success Criteria Validation
        **Verify all objectives met:**
        - 50% entity reduction achieved
        - Complete MQTT implementation
        - Comprehensive error handling
        - Production-ready deployment

        ### 4. Final Documentation
        **Complete implementation guide:**
        - Installation procedures
        - Configuration overview
        - Troubleshooting guide
        - Maintenance procedures

        ## Required Output Structure
        ```yaml
        benefits_analysis:
          quantitative_improvements:
            entity_reduction: {from: N, to: N, percentage: N}
            automation_optimization: {trigger_reduction: N, efficiency_gain: N}
            reliability_metrics: [specific improvements]
          
          implementation_comparison:
            command_reliability: [MQTT vs send_command success rates]
            state_management: [Variable vs helper efficiency]
            error_coverage: [comprehensive vs basic handling]
          
          success_criteria_validation:
            entity_reduction_achieved: true/false
            mqtt_implementation_complete: true/false
            error_handling_comprehensive: true/false
            production_ready: true/false
          
          final_documentation:
            installation_guide: |
              # Complete installation procedures
            configuration_overview: |
              # System architecture and configuration
            troubleshooting_guide: |
              # Common issues and solutions
        ```

        **Provide complete documentation suitable for production deployment.**

        **END: CONFIDENCE ASSESSMENT: [n]%**

  # Migration & Extensibility
  migration:
    strategy: |
      This v2 promptset breaks the original monolithic phases into discrete, sequential prompts.
      Each prompt builds on previous outputs while maintaining focused scope and clear deliverables.
      Bundle artifacts are mapped to /mnt/data/* paths for consistent reference.

  extensibility:
    - Add new prompts between existing ones for additional analysis depth
    - Extend artifact mappings for different bundle configurations
    - Adapt room definitions and segment mappings for different robot models
    - Scale notification and error handling for multi-robot environments

  documentation:
    - Sequential execution: Each prompt depends on outputs from previous prompts
    - Bundle mapping: All artifacts available at /mnt/data/* paths
    - Confidence scoring: Each prompt provides numerical confidence assessment
    - Complete deliverables: Final prompts provide production-ready implementations
