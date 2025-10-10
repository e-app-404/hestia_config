---
id: prompt_20251007_650863
slug: valetudo-vacuum-control-optimization-promptset
title: Valetudo Vacuum Control Optimization Promptset
date: '2025-10-07'
tier: "α"
domain: generation
persona: pythagoras
status: approved
tags: [valetudo, vacuum, package, yaml, configuration, packages, room_db, appdaemon, hacs, var, sql]
version: '1.0'
source_path: valetudo_optimization_comprehensive.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:26.775522'
redaction_log: []
---

**Execute this optimization completely. Provide all files in full with no placeholders. Include comprehensive apply procedures and validation suite. Demonstrate clear benefits over current implementation.**

      phases:
        - name: analysis_design
          persona: strategos_gpt
          instructions: |
            Analyze current vacuum package inefficiencies and design optimized architecture.
            Focus on Variable component benefits, MQTT command improvements, and entity reduction opportunities.
            Provide quantitative analysis of current vs optimized approach.
          outputs:
            - name: optimization_analysis.md
              required: true
              content: |
                # Valetudo Optimization Analysis
                ## Current State Assessment
                - Entity inventory: 12 input helpers
                - Command reliability issues with vacuum.send_command
                - Limited error handling and notification capabilities
                
                ## Optimization Opportunities
                - HACS Variable consolidation potential
                - MQTT command modernization requirements
                - Error handling enhancement areas
                
                ## Benefits Projection
                - Entity reduction: X% decrease
                - Reliability improvement: MQTT vs send_command
                - Performance gains: reduced automation triggers

        - name: core_implementation
          persona: strategos_gpt
          instructions: |
            Implement complete optimized package with all components in full.
            No placeholders or TODO items - provide production-ready configuration.
            Include comprehensive error handling and notification systems.
          outputs:
            - name: domain/variables/vacuum_variables.yaml
              required: true
              content: |
                # Complete Variable component definitions
            - name: packages/package_valetudo_control.yaml
              required: true
              content: |
                # Complete optimized package with MQTT commands
            - name: devtools/templates/valetudo_audit.jinja2
              required: true
              content: |
                # Comprehensive audit template for monitoring

        - name: validation_deployment
          persona: strategos_gpt
          instructions: |
            Provide complete apply/rollback procedures with comprehensive validation.
            Include all testing scenarios and safety checks.
            Document benefits and performance improvements.
          outputs:
            - name: tools/valetudo_optimization_apply.sh
              required: true
              content: |
                # Complete apply script with validation gates
            - name: tools/valetudo_optimization_rollback.sh
              required: true
              content: |
                # Complete rollback script with safety checks
            - name: validation_suite.md
              required: true
              content: |
                # Comprehensive validation procedures and test scenarios

  # Migration & Extensibility
  migration:
    strategy: |
      This promptset targets ChatGPT-5 Thinking model for comprehensive Valetudo optimization.
      Includes complete context analysis, technical requirements, and production validation.
      Designed for single-execution optimization with complete deliverables.

  extensibility:
    - Adapt segment mapping for different robot models by updating valetudo.conf
    - Extend room definitions by adding new Variable attributes and automation triggers
    - Integrate additional Valetudo capabilities (zones, go-to locations) using same MQTT patterns
    - Scale notification system for multiple robots using topic prefixes

  documentation:
    - Reference: Valetudo MQTT API documentation at valetudo.cloud
    - HACS Variable component: github.com/snarky-snark/home-assistant-variables
    - Home Assistant vacuum integration: home-assistant.io/integrations/vacuum/
    - MQTT autodiscovery: home-assistant.io/integrations/mqtt/#discovery
