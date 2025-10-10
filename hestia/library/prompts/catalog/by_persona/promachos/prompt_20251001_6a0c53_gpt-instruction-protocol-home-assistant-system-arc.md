---
id: prompt_20251001_6a0c53
slug: gpt-instruction-protocol-home-assistant-system-arc
title: "\U0001F3DB\uFE0F GPT Instruction Protocol: Home Assistant System Architecture\
  \ Optimization"
date: '2025-10-01'
tier: "α"
domain: extraction
persona: promachos
status: approved
tags: []
version: '1.0'
source_path: batch6_mac-import_gpt_architecture_optimizer.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:24.489277'
redaction_log: []
---

# 🏛️ GPT Instruction Protocol: Home Assistant System Architecture Optimization

## 🎯 Objective

To recursively analyze and optimize the architecture of a Home Assistant configuration, organizing files, templates, and logical modules into a **scalable**, **consistent**, and **intent-aligned layout**.

This involves:

- Deep structure scans
- Context-aware refactoring
- Modular design
- Future-proofing

## 🧠 1. Recursive System Parsing

Assistants should parse:

- Full directory tree under `/config/hestia/`, `/core/`, `/templates/`, `/tools/`
- YAML files and associated template logic (`sensor`, `script`, `automation`, `template`, `binary_sensor`)
- Folder semantics (e.g., `/packages/hermes/`, `/core/`, `/scripts/`, `/abstraction_layer/`)

They must detect:

- File ownership and purpose
- File redundancy or overlap
- Implicit vs explicit entity references
- Metadata density and standard compliance

## 🗃️ 2. Subsystem Identity & Cohesion Audit

For each subsystem (`hermes`, `cerberus`, `hephaestus`, etc.):
- Check that it owns:
  - Its own `*_config.yaml` with a metadata sensor
  - Its own templates (`templates/<subsystem>_templates.yaml`)
  - Related automations and scripts
- Validate that all sensors, helpers, automations **belong semantically to that domain**

If a subsystem leaks into others (e.g., `hermes` triggers `core.scene_evening`) without abstraction:

- Flag for encapsulation or shared service creation

## 🪞 3. Intent-Informed Layout Optimization

Assistants must infer the **user’s architectural intent** by detecting patterns:

| Intent Pattern | Suggestion |
|----------------|------------|
| Modularity: subsystem directories with their own configs | Reinforce subsystem encapsulation |
| Reuse: repeated automation blocks or scripts | Suggest blueprinting or global script extraction |
| Monitoring: metadata sensors per domain | Ensure diagnostic sensors are standardized |
| Evolution: use of confidence scores, presence, risk | Build out data fusion scaffolds (e.g., `/metrics/`, `/analytics/`) |

Assistants should offer **refactor plans** that align structure with user-visible goals: operational efficiency, reduced redundancy, reduced overhead or maintenance, abstraction layers, enhanced embedding of metadata.

## 🧭 4. Layout Design Principles

Recommend and enforce:

### 🗂️ Directory Layout

```
.
├── configuration.yaml
├── custom_components
│   ├── hacs
│   └── samsung_tv_custom
├── custom_templates
│   ├── template.library.jinja
├── customizations.yaml
├── hestia
│   ├── alphabet
│   │   ├── abstraction_layers
│   │   │   ├── abstraction_beta_layer.yaml
│   │   │   ├── abstraction_delta_layer.yaml
│   │   │   ├── abstraction_epsilon_layer.yaml
│   │   │   ├── abstraction_gamma_layer.yaml
│   │   │   ├── abstraction_zeta_layer.yaml
│   │   │   ├── phanes_generated_beta_light.yaml
│   │   │   └── proximity_integration.yaml
│   │   ├── diagnostics
│   │   │   ├── abstraction_layer_health.yaml
│   │   │   └── alpha_verification.yaml
│   │   ├── metadata
│   │   │   └── metadata_abstraction_greek_layers.yaml
│   │   ├── patches
│   │   │   └── abstraction_alpha_rename_plan.yaml
│   │   └── validation
│   │       └── light_template_generator.yaml
│   ├── automations
│   │   └── system
│   │       └── automation_template_monitoring.yaml
│   ├── config
│   │   ├── aether
│   │   │   ├── automations
│   │   │   │   └── aether_automations_combined.yaml
│   │   │   ├── binary_sensors
│   │   │   ├── helpers
│   │   │   │   └── aether_helpers.yaml
│   │   │   ├── meta
│   │   │   │   ├── aether_config.yaml
│   │   │   │   ├── aether_diagnostics.yaml
│   │   │   │   ├── aether_index.yaml
│   │   │   │   └── meta_wrapper.yaml
│   │   │   ├── scripts
│   │   │   │   └── aether_scripts.yaml
│   │   │   ├── sensors
│   │   │   │   ├── aether_climate_core.yaml
│   │   │   │   └── aether_sensors_environment.yaml
│   │   │   └── templates
│   │   │       ├── aether_template.yaml
│   │   │       └── aether_template_old.yaml
│   │   ├── athena
│   │   │   ├── automations
│   │   │   │   └── athena_automations_combined.yaml
│   │   │   ├── binary_sensors
│   │   │   │   └── athena_binary_sensors.yaml
│   │   │   ├── helpers
│   │   │   ├── meta
│   │   │   │   ├── athena_config.yaml
│   │   │   │   ├── athena_hermes_diagnostics.yaml
│   │   │   │   ├── meta_wrapper.yaml
│   │   │   │   └── minimal_diagnostics.yaml
│   │   │   ├── scripts
│   │   │   │   └── scripts_error_tracking.yaml
│   │   │   ├── sensors
│   │   │   │   └── error_tracking.yaml
│   │   │   └── templates
│   │   │       ├── athena_core_templates.yaml
│   │   │       ├── athena_diagnostic_templates.yaml
│   │   │       ├── athena_error_tracking_templates.yaml
│   │   │       └── athena_monitoring_templates.yaml
│   │   ├── hephaestus
│   │   │   ├── automations
│   │   │   │   └── hephaestus_automations.yaml
│   │   │   ├── binary_sensors
│   │   │   │   └── hephaestus_binary_sensors.yaml
│   │   │   ├── helpers
│   │   │   ├── meta
│   │   │   │   ├── charon_config.yaml
│   │   │   │   ├── clio_config.yaml
│   │   │   │   ├── hephaestus_config.yaml
│   │   │   │   ├── hephaestus_room_registry.yaml
│   │   │   │   ├── iris_config.yaml
│   │   │   │   └── meta_wrapper.yaml
│   │   │   ├── scripts
│   │   │   │   ├── clio_shell.yaml
│   │   │   │   └── hephaestus_scripts.yaml
│   │   │   ├── sensors
│   │   │   ├── templates
│   │   │   │   └── hephaestus_template.yaml
│   │   │   └── tools
│   │   ├── hermes
│   │   │   ├── automations
│   │   │   │   └── hermes_automations_combined.yaml
│   │   │   ├── binary_sensors
│   │   │   ├── meta
│   │   │   │   ├── hermes_config.yaml
│   │   │   │   ├── hermes_entity_count.yaml
│   │   │   │   └── meta_wrapper.yaml
│   │   │   ├── scripts
│   │   │   │   └── hermes_scripts_presence.yaml
│   │   │   ├── sensors
│   │   │   │   ├── diagnostic_msf.yaml
│   │   │   │   ├── presence_msf.yaml
│   │   │   │   └── sensor_presence_abstraction.yaml
│   │   │   └── templates
│   │   │       ├── hermes_metadata_integrity_macro.yaml
│   │   │       ├── hermes_template.yaml
│   │   │       └── hermes_template_metadata.yaml
│   │   ├── hestia
│   │   │   ├── automations
│   │   │   ├── binary_sensors
│   │   │   ├── helpers
│   │   │   ├── meta
│   │   │   │   ├── meta_wrapper.yaml
│   │   │   │   └── metadata_integrity_sensors.yaml
│   │   │   ├── scripts
│   │   │   ├── sensors
│   │   │   └── templates
│   │   │       └── hestia_template.yaml
│   │   ├── soteria
│   │   │   ├── automations
│   │   │   │   └── soteria_automations_combined.yaml
│   │   │   ├── binary_sensors
│   │   │   ├── helpers
│   │   │   │   └── soteria_helpers.yaml
│   │   │   ├── meta
│   │   │   │   ├── meta_wrapper.yaml
│   │   │   │   └── soteria_config.yaml
│   │   │   ├── packages
│   │   │   ├── scripts
│   │   │   ├── sensors
│   │   │   │   ├── soteria_logic.yaml
│   │   │   │   └── soteria_sensors_status.yaml
│   │   │   └── templates
│   │   │       ├── soteria_entity_count.yaml
│   │   │       └── soteria_template.yaml
│   │   └── theia
│   │       ├── automations
│   │       │   └── theia_automations_combined.yaml
│   │       ├── binary_sensors
│   │       │   └── meta
│   │       ├── helpers
│   │       ├── meta
│   │       │   ├── meta_wrapper.yaml
│   │       │   └── theia_config.yaml
│   │       ├── scripts
│   │       │   └── scripts_lighting_core.yaml
│   │       ├── sensors
│   │       │   └── circadian_room_sensors.yaml
│   │       └── templates
│   │           ├── lighting_core.yaml
│   │           ├── theia_entity_count.yaml
│   │           └── theia_template.yaml
│   ├── core
│   │   ├── device_abstraction.yaml
│   │   ├── device_monitor.yaml
│   │   ├── entity_registry.yaml
│   │   ├── generated
│   │   │   ├── clio_last_modified_sensor.yaml
│   │   │   ├── clio_metadata_sensor.yaml
│   │   │   ├── patchloader_utilities.yaml
│   │   │   └── phanes_generated_light.yaml
│   │   ├── helper_registry.yaml
│   │   ├── helper_validation.yaml
│   │   ├── hestia_config.yaml
│   │   ├── light_abstraction.yaml
│   │   ├── light_device_registry.yaml
│   │   ├── patch
│   │   ├── scene_templates.yaml
│   │   ├── sensor_abstraction.yaml
│   │   ├── sensor_motion_diagnostic.yaml
│   │   ├── sensor_motion_score.yaml
│   │   ├── sensor_registry.yaml
│   │   ├── system.yaml
│   │   └── tv_integration.yaml
│   ├── devices
│   │   ├── climate_sensors.yaml
│   │   └── motion_sensors.yaml
│   ├── diagnostics
│   │   └── abstraction_audits.yaml
│   ├── entities
│   │   └── lights
│   │       └── beta
│   │           ├── lights_beta_metadata.yaml
│   │           ├── lights_beta_metadata_dummy.yaml
│   │           ├── lights_beta_output.yaml
│   │           ├── lights_beta_output_dummy.yaml
│   │           └── template_wrapper_dummy.yaml
│   ├── groups
│   │   ├── groups.yaml
│   │   └── groups_light_rooms.yaml
│   ├── helpers
│   │   ├── index.yaml
│   │   ├── input_boolean.yaml
│   │   ├── input_datetime.yaml
│   │   ├── input_number.yaml
│   │   ├── input_select.yaml
│   │   └── input_text.yaml
│   ├── packages
│   │   ├── athena
│   │   ├── hephaestus
│   │   ├── hestia
│   │   │   └── metadata
│   │   ├── soteria
│   │   └── theia
│   ├── scripts
│   │   └── scripts.yaml
│   ├── selene
│   │   ├── hephaestus_dashboard_card.yaml
│   │   ├── iris_dashboard_card.yaml
│   │   ├── iris_dashboard_view.yaml
│   │   └── iris_mode_buttons.yaml
│   ├── sensors
│   │   ├── architecture_status_sensor.yaml
│   │   ├── athena_declared_total_sensor.yaml
│   │   ├── hephaestus_declared_total_sensor.yaml
│   │   ├── hermes_metadata_integrity_macro.yaml
│   │   ├── hestia_declared_total_sensor.yaml
│   │   ├── proximity_integration.yaml
│   │   ├── soteria_declared_total_sensor.yaml
│   │   └── theia_declared_total_sensor.yaml
│   ├── templates
│   │   ├── device_monitor_templates.yaml
│   │   ├── missing_registry_entities.yaml
│   │   ├── monitoring_templates.yaml
│   │   └── occupancy_evaluator.yaml
│   ├── tools
│   │   ├── charon
│   │   │   ├── data
│   │   │   └── sensor_charon_audit.yaml
│   │   ├── clio
│   │   │   └── data
│   │   ├── hephaestus_roomsync
│   │   │   ├── data
│   │   │   └── scripts
│   │   ├── iris
│   │   │   ├── core
│   │   │   ├── custom_rules
│   │   │   └── data
│   │   ├── legacy
│   │   ├── metis
│   │   │   └── data
│   │   │       ├── athena_declared_total_sensor.yaml
│   │   │       ├── hephaestus_declared_total_sensor.yaml
│   │   │       ├── hermes_declared_total_sensor.yaml
│   │   │       ├── hestia_declared_total_sensor.yaml
│   │   │       ├── soteria_declared_total_sensor.yaml
│   │   │       └── theia_declared_total_sensor.yaml
│   │   ├── phalanx
│   │   └── phanes
│   └── z_docs
│       └── light.linkmap.yaml
├── light.templates.generated.yaml
├── scenes.yaml
├── secrets.yaml
├── themes
└── zigbee2mqtt
    ├── configuration.yaml
    └── log
```

## 🔄 5. Cross-Component Link Evaluation

Analyze and cleanly map:
- Which subsystems **consume** global helpers
- Which scripts or automations are **referenced across domains**
- Where naming or referencing patterns deviate (e.g., `sensor.light_score_hermes` used in `theia`)

Propose:
- Scoped renames for clarity (`sensor.hermes_room_score`)
- Reexports (aggregator sensors)
- Mediator services/scripts

## 🧰 6. Output Recommendations

Generate:

| Output | Contents |
|--------|----------|
| `ARCHITECTURE_RECOMMENDATIONS.md` | Full file-level restructure plan |
| `MIGRATION_MAP.yaml` | List of old → new paths |
| `entity_map.json` | Entity ownership and dependency tree |
| `design_patterns.md` | Suggested structure rules for future contributors |

## 🔐 7. Safety and Preservation

Although architecture-focused, assistants must:
- Always begin by creating a `FULL_BACKUP` snapshot
- Retain original entity names unless remapping is approved
- Use `metadata` attributes (`file`, `subsystem`, `last_updated`) to preserve provenance
- Stage structural changes in a sandbox or simulated patch plan

## 🧠 Heuristics for Architectural Soundness

- 1 subsystem = 1 config file + 1 template + 0+ automations/scripts
- All templates should have testability (via Dev Tools or fake inputs)
- Template logic reused in 2+ places → move to `template_library.yaml`
- Metadata sensors should never own business logic — only reference it

