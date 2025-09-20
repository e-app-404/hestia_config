---
title: ADR-0005: Entity Registry, Sensor Matrix, Logic Path Index, and Signal Emitters Contract
date: 2025-09-11
status: Pending Validation
---

# ADR-0005: Entity Registry, Sensor Matrix, Logic Path Index, and Signal Emitters Contract

## Table of Contents
1. Context
2. Rationale & Scope
3. Canonical Logic & Examples
4. Enforcement & Validation
5. Tokens
6. Last updated

## 1. Context
This ADR formalizes the canonical contracts governing entity registry patching, sensor classification, logic path indexing, and signal emitter definitions. These artifacts underpin core relationships, propagation, and classification logic for all Home Assistant domains, automations, and templates. They ensure consistency, traceability, and robust signal flow throughout the system.

## 2. Rationale & Scope
### Why Canonicalize?
- **Entity Registry Patching:** Ensures all entities are consistently defined, tiered, and validated. Enables automated review and patching of registry artifacts.
- **Sensor Matrix:** Provides a unified classification and confidence scoring for all sensors, supporting cross-domain logic and signal aggregation.
- **Logic Path Index:** Maps canonical signal flow, automation triggers, and entity relationships, supporting traceability and auditability.
- **Signal Emitters:** Defines all signal sources, their scores, and usage, supporting propagation, inference, and macro logic.

### Scope
- All referenced YAML contracts and their relationships
- All automations, templates, and scripts that depend on these contracts
- Cross-artifact validation and review

## 3. Canonical Logic & Examples
### Entity Registry Patch Contract
Defines the canonical set of entities, their domains, tiers, and review status. Example:
```yaml
- entity_id: binary_sensor.bedroom_heating_needed
	domain: binary_sensor
	origin: logic_path_index.yaml
	tier: beta
	review_required: true
	notes: Auto-detected during logic path consistency validation on 2025-06-08
- entity_id: input_boolean.climate_automation_enabled
	domain: input_boolean
	origin: logic_path_index.yaml
	tier: beta
	review_required: true
	notes: Auto-detected during logic path consistency validation on 2025-06-08
```

### Sensor Class Matrix
Classifies all sensors and binary_sensors, providing signal class, domain, integration, area, tags, and confidence scores. Example:
```yaml
- entity_id: binary_sensor.floor_activity_detected_
	signal_class: generic
	domain: binary_sensor
	integration: unknown
	area: unspecified
	used_in_logic: []
	crosslinked_emitters: []
	tags: []
	confidence_score:
		structural: 0.94
		operational: 0.91
		semantic: 0.93
	session_reference: hestia_phase_scan_20250608_full_rebuild
```

### Logic Path Index
Maps canonical signal flow, automation triggers, and referenced entities. Example:
```yaml
- id: automation_ensuite_lighting_motion
	alias: Ensuite Lighting - Motion
	mode: single
	source_file: automations/subsystems/hermes_automations_combined.yaml
	referenced_entities:
		- binary_sensor.ensuite_occupancy_beta
		- script.dispatch_light_state
	conditions:
		- condition: time
			after: 05:30:00
			before: '22:00:00'
	session_reference: hestia_phase_scan_20250608_automation_trace
```

### Signal Emitters
Defines all signal sources, their domain, class, emitter score, confidence, and usage. Example:
```yaml
- entity_id: binary_sensor.macbook_active
	domain: binary_sensor
	signal_class: generic
	emitter_score: 0.85
	confidence_score:
		structural: 0.95
		operational: 0.9
		semantic: 0.92
	status: active
	used_in:
		- templates/templates/gamma_inferred_occupancy_evaluator.yaml
	unique_id: bd594b84bd37
```

## 4. Enforcement & Validation
- All referenced contracts must be validated against live registry, automations, and templates.
- Entities must be reviewed for tier, domain, and origin consistency.
- Sensor matrix must be updated with new sensors and confidence scores after each phase scan.
- Logic path index must trace all automation triggers and referenced entities.
- Signal emitters must be scored and referenced in all relevant logic and templates.
- Changes to any contract require a new ADR version and full review.

## 5. Tokens
- `entity_registry_patch_contract`, `sensor_class_matrix`, `logic_path_index`, `signal_emitters`
- `entity_id`, `domain`, `tier`, `signal_class`, `confidence_score`, `emitter_score`, `referenced_entities`, `session_reference`, `used_in`, `origin`, `review_required`, `notes`

## 6. Last updated
_Last updated: 2025-09-11_
