## [alias_first_001] Use Canonical Aliases Before Logic

**Tier**: β  
**Domain**: abstraction  
**Status**: approved  
**Created**: 2025-04-09  
**Last Updated**: 2025-04-17  
**Contributors**: gpt_architect, sensor_mapper  

### Principle

All logic sensors must reference β-tier abstractions, not raw α-tier sensors.

#### Rationale

This decouples logic from hardware, enabling substitution and stability.

#### Good Example

```yaml
sensor.motion_score_γ:
  source: binary_sensor.kitchen_motion_β
```

#### Bad Example

```yaml
source: binary_sensor.kitchen_pir_α
```

---

## [alias_logic_free_001] Keep Aliases Logic-Free

**Tier**: β  
**Domain**: abstraction  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Alias sensors must directly reflect raw states without embedded calculations or logic.

#### Rationale

β tier exists only to abstract the physical source, not to transform data.

#### Good Example

```yaml
binary_sensor.bedroom_occupancy_β:
  state: >
    {{ states('binary_sensor.bedroom_occupancy_α') }}
```

#### Bad Example

```yaml
binary_sensor.bedroom_occupancy_β:
  state: >
    {% if states('binary_sensor.bedroom_occupancy_α') == 'on' 
       and states('sensor.bedroom_temperature') > 19 %}
      on
    {% else %}
      off
    {% endif %}
```

---

## [alias_reference_enforcement_001] Alias-Only Reference Doctrine

**Tier**: γ  
**Domain**: abstraction  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-02  
**Contributors**: system  

### Principle

No logic, UI, or control may reference α-layer entities directly. All references must go through validated aliases (β-layer or above).

#### Rationale

Prevents fragility and coupling to hardware implementation. Supports substitutability, fallback logic, and metadata centralization.

#### Good Example

```yaml
sensor.foxy_motion_score:
  source: binary_sensor.foxy_motion_beta
```

#### Bad Example

```yaml
source: binary_sensor.foxy_motion_α  # Breaks abstraction
```

---

## [attributes_logic_separation_001] Keep State Logic Out of Attributes

**Tier**: all  
**Domain**: templating  
**Status**: approved  
**Created**: 2025-04-03  
**Last Updated**: 2025-04-03  
**Contributors**: system  

### Principle

Do not embed state logic inside attributes blocks unless the attribute is purely diagnostic.

#### Rationale

Separating state computation from attribute assignment improves clarity, testability, and maintainability.

#### Good Example

```yaml
# Compute state independently from attributes
binary_sensor.example:
  state: >
    {% set is_valid = states('sensor.source') not in ['unavailable', 'unknown'] %}
    {{ is_valid }}
  attributes:
    last_checked: "{{ now() }}"
    source: "sensor.source"
```

#### Bad Example

```yaml
# Embedding complex logic in attributes
binary_sensor.example:
  state: "{{ is_valid }}"
  attributes:
    is_valid: >
      {% set value = states('sensor.source') %}
      {% if value not in ['unavailable', 'unknown'] %}
        true
      {% else %}
        false
      {% endif %}
```

---

## [beta_identity_shift_001] Validated Abstractions Own Metadata

**Tier**: β+  
**Domain**: abstraction  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-02  
**Contributors**: system  

### Principle

The β-layer (validated abstraction) should be the canonical source of truth for light identity and metadata, superseding the α-layer and registries.

#### Rationale

Reduces drift, simplifies upstream logic, and aligns system behavior with operational reality. Validated entities are what users and automations actually reference.

#### Good Example

```yaml
light.foxy_beta:
  attributes:
    canonical_alpha: light.foxy
    model: "Candle"
    manufacturer: "Philips"
    firmware: "1.33.0"
```

#### Bad Example

```yaml
# Treating the registry or physical device as the metadata authority
core/light_device_registry.yaml holds primary metadata
```

---

## [canonical_alias_001] Use Canonical Aliases Before Logic

**Tier**: β  
**Domain**: abstraction  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

All logic sensors should point to β-tier aliases rather than raw device IDs.

#### Rationale

Decouples logic from hardware implementations and enables sensor substitution without breaking automations.

#### Good Example

```yaml
sensor.kitchen_motion_score:
  source: binary_sensor.kitchen_motion_β
```

#### Bad Example

```yaml
source: binary_sensor.kitchen_pir_1  # Breaks abstraction
```

---

## [canonical_aliasing_001] Canonical Aliasing

**Tier**: β  
**Domain**: abstraction  
**Status**: approved  
**Created**: —  
**Last Updated**: —  
**Contributors**: —  

### Principle

All logic sensors must point to β-tier aliases rather than raw device IDs.

#### Rationale

Decouples logic from hardware implementations and enables substitution of sensors without modifying logic rules.

#### Good Example

```yaml
binary_sensor.living_room_present:
  state: "{{ is_state('sensor.room_beacon_distance_β', '< 100') }}"
```

#### Bad Example

```yaml
binary_sensor.living_room_present:
  state: "{{ is_state('sensor.room_beacon_distance_α', '< 100') }}"
```

---

## [core_layering_001] Layered Abstraction Model

**Tier**: all  
**Domain**: architecture  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Structure all components in defined abstraction layers, using Greek-named subsystems for organizational clarity.

#### Rationale

Separating concerns into distinct layers allows for better maintainability, reusability, and testing.

#### Good Example

```yaml
# Layer α: Raw sensor data
binary_sensor.kitchen_motion_sensor: <physical device>

# Layer β: Abstracted sensor (hardware-independent)
binary_sensor.kitchen_motion_validated:
  value_template: "{{ is_state('binary_sensor.kitchen_motion_sensor', 'on') }}"

# Layer γ: Logic layer (business logic)
sensor.kitchen_motion_score:
  value_template: "{{ 100 if is_state('binary_sensor.kitchen_motion_validated', 'on') else 0 }}"
```

#### Bad Example

```yaml
# Don't skip layers or mix concerns
sensor.kitchen_presence_score:
  value_template: "{{ 100 if is_state('binary_sensor.kitchen_motion_sensor', 'on') else 0 }}"
```

---

## [decay_overflow_001] Prevent Decay Overflows

**Tier**: δ  
**Domain**: decay  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Decay sensors (*_δ) should never accumulate above their trigger threshold.

#### Rationale

Ensures predictable behavior when sensors reactivate after being triggered multiple times.

#### Good Example

```yaml
{% set decay = namespace(score=states('sensor.room_motion_δ') | float(0)) %}
{% if is_state('binary_sensor.room_motion_β', 'on') %}
  {% set decay.score = 10 %}  # Reset to max value
{% else %}
  {% set decay.score = max(decay.score - 0.5, 0) %}  # Decay with floor
{% endif %}
{{ decay.score }}
```

#### Bad Example

```yaml
{% set decay = namespace(score=states('sensor.room_motion_δ') | float(0)) %}
{% if is_state('binary_sensor.room_motion_β', 'on') %}
  {% set decay.score = decay.score + 5 %}  # Accumulating!
{% else %}
  {% set decay.score = decay.score - 0.5 %}
{% endif %}
{{ decay.score }}
```

---

## [decay_timing_001] Use Consistent Decay Timing

**Tier**: δ  
**Domain**: decay  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

All *_δ sensors must decay using the same decrement logic to ensure system-wide predictability.

#### Rationale

Creates consistent expectations about how long a signal persists after triggering.

#### Good Example

```yaml
# Standardize on a consistent decay rate:
decay.score = decay.score - 0.5
```

#### Bad Example

```yaml
# Varying decay rates by room type:
decay.score = decay.score - (1.0 if room_type == 'hallway' else 0.3)
```

---

## [file_reorganization_protocol_001] File Reorganization Protocol

**Tier**: system  
**Domain**: organization  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-02  
**Contributors**: system  

### Principle

All rehomed config files must be evaluated for module load compatibility and path correctness.

#### Rationale

Ensures file relocations don't break template includes, module loads, or runtime behavior.

#### Good Example

```yaml
# After moving file from core/example.yaml to alphabet/validation/example.yaml:
# 1. Update configuration.yaml inclusion
template:
  - !include_dir_merge_list hestia/alphabet/validation
# 2. Update any references in entity_map.json
"sensor.example": {
  "owned_by": "alphabet/validation/example.yaml"
}
# 3. Verify all template references
```

#### Bad Example

```yaml
# Moving files without updating inclusion paths
# or checking for dependent references
```

---

## [greek_suffix_001] Greek Tier Naming Convention

**Tier**: all  
**Domain**: naming  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Use Greek letter suffixes to denote level of abstraction in entity naming.

#### Rationale

Clearly identifies each component's role in the abstraction hierarchy and enables automated verification.

#### Good Example

```yaml
# Follow this abstraction hierarchy
binary_sensor.kitchen_motion_α        # Raw device input
binary_sensor.kitchen_motion_β        # Alias/abstraction  
sensor.kitchen_motion_score_γ         # Logic/calculation
sensor.kitchen_motion_decay_δ         # Decay/aggregation
binary_sensor.kitchen_motion_validated_ε  # Validation
binary_sensor.kitchen_presence_ζ      # Final output
```

#### Bad Example

```yaml
# Skip tiers or use inconsistent naming
binary_sensor.kitchen_motion_sensor   # Missing tier suffix
sensor.kitchen_presence               # Ambiguous abstraction level
```

---

## [include_scope_principle_001] Single-Domain Scope for All Includes

**Tier**: all  
**Domain**: configuration  
**Status**: approved  
**Created**: 2025-04-04  
**Last Updated**: 2025-04-04  
**Contributors**: user  

### Principle

All includes must be single-domain scoped. Use !include_dir_merge_named when modularizing sensors, scripts, and helpers. Separate template: logic from sensor: declarations explicitly.

#### Rationale

Ensures clarity in Home Assistant's configuration structure and prevents mixed or ambiguous YAML domains that lead to parsing errors or misbehavior.

#### Good Example

```yaml
sensor: !include_dir_merge_named hestia/config/hermes/sensors
template: !include_dir_merge_named hestia/config/hermes/templates
```

#### Bad Example

```yaml
homeassistant:
  packages: !include_dir_named hestia/packages/hermes  # May include both sensors and templates
```

---

## [layered_abstraction_001] Layered Abstraction Model

**Tier**: all  
**Domain**: architecture  
**Status**: approved  
**Created**: —  
**Last Updated**: —  
**Contributors**: —  

### Principle

Structure all components in defined abstraction layers, with tier dependencies only flowing downward.

#### Rationale

Separating concerns into distinct layers allows for better maintainability, reusability, and testing. Ensures each tier focuses on a single responsibility and avoids logic duplication.

#### Good Example

```yaml
# α (alpha): raw sensors
sensor.room_temperature_α

# β (beta): abstraction
sensor.room_temperature_β:
  state: "{{ states('sensor.room_temperature_α') }}"

# γ (gamma): scoring
sensor.room_temperature_suitability_γ:
  state: "{{ states('sensor.room_temperature_β') | float > 22 }}"
```

#### Bad Example

```yaml
# Don't reference α-layer directly in logic
sensor.room_temperature_suitability_γ:
  state: "{{ states('sensor.room_temperature_α') | float > 22 }}"
```

---

## [metadata_injection_001] Metadata Injection in Abstractions

**Tier**: β  
**Domain**: abstraction  
**Status**: approved  
**Created**: —  
**Last Updated**: —  
**Contributors**: —  

### Principle

Validated (β-layer) entities should carry all critical metadata normally associated with physical (α-layer) devices.

#### Rationale

Aligns metadata with the semantic and functional reference layer and eliminates dependency on device registries or physical state.

#### Good Example

```yaml
sensor.kitchen_motion_β:
  attributes:
    mac: "A4:7C:XX:YY:ZZ"
    manufacturer: "Tuya"
    registered_room: "kitchen"
```

#### Bad Example

```yaml
# Metadata only stored on the α-entity
sensor.kitchen_motion_α:
  attributes:
    mac: "A4:7C:XX:YY:ZZ"
```

---

## [metadata_registry_json_001] JSON-Based Abstraction Registry

**Tier**: β+  
**Domain**: abstraction  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-02  
**Contributors**: system  

### Principle

All β-layer abstraction metadata must be declared in `beta_light_entities.json`, not YAML fragments or device registries.

#### Rationale

Centralizes metadata, supports multi-alpha-device resolution, and ensures tooling compatibility.

#### Good Example

```yaml
{
  "bamboo_lamp_beta": {
    "canonical_alpha": [
      "light.bamboo_lamp",
      "light.bamboo_lamp_mtr"
    ],
    "firmware": "1.33.0",
    "model": "Bamboo",
    "integration": ["Matter", "Wiz"]
  }
}
```

#### Bad Example

```yaml
light_device_registry.yaml
```

---

## [metis_entity_location_001] Store Declared Entity Totals in Tool Directory

**Tier**: ε  
**Domain**: tooling  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-04  
**Contributors**: gizmo, iris  

### Principle

Generated declared entity total sensors should be stored in hestia/tools/metis/data/, not with the subsystem packages.

#### Rationale

Separates system introspection artifacts from human-authored configuration, reducing config surface area and clarifying ownership.

#### Good Example

```yaml
# File: hestia/tools/metis/data/hermes_declared_total_sensor.yaml
sensor:
  - name: "Hermes Declared Total"
    unique_id: "hermes_declared_total"
    ...
```

#### Bad Example

```yaml
# Stored with the package (leads to confusion)
hestia/packages/hermes/hermes_declared_total_sensor.yaml
```

---

## [module_metadata_001] Maintain Consistent Module Metadata

**Tier**: system  
**Domain**: documentation  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-02  
**Contributors**: system  

### Principle

Every YAML module must start with a metadata sensor block including file path, version, status, and changelog.

#### Rationale

Enhances clarity, simplifies debugging, and supports effective version control.

#### Good Example

```yaml
- sensor:
    - name: Metadata - XYZ Module
      unique_id: metadata_xyz
      canonical_id: xyz_module
      state: ok
      attributes:
        module: XYZ Module
        type: abstraction
        file: /config/hestia/packages/xyz.yaml
        version: 1.2.3
        status: active
        last_updated: "2025-04-01"
        version_history:
          - version: "1.2.3"
            date: "2025-04-01"
            changes: "Refactored for new tier system"
          - version: "1.1.0"
            date: "2025-03-15"
            changes: "Initial implementation"
```

#### Bad Example

```yaml
# No metadata block
- sensor:
    - name: Regular Sensor Without Metadata
      state: "{{ states('input_boolean.something') }}"
```

---

## [motion_alias_001] Canonical Aliasing For Motion Abstractions

**Tier**: β  
**Domain**: motion  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Every motion score sensor must point to a well-defined binary sensor alias.

#### Rationale

Creates standard interface points for motion data, regardless of underlying hardware.

#### Good Example

```yaml
binary_sensor.kitchen_motion_β:
  value_template: "{{ is_state('binary_sensor.kitchen_motion_sensor_α', 'on') }}"

sensor.kitchen_motion_score_γ:
  value_template: "{{ 100 if is_state('binary_sensor.kitchen_motion_β', 'on') else 0 }}"
```

#### Bad Example

```yaml
sensor.kitchen_motion_score_γ:
  value_template: "{{ 100 if is_state('binary_sensor.kitchen_motion_sensor_α', 'on') else 0 }}"
```

---

## [motion_alias_template_patch_001] Ensure All Motion Aliases Are Explicitly Defined

**Tier**: β  
**Domain**: motion  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-02  
**Contributors**: system  

### Principle

Define binary_sensor.<room>_motion_β aliases using template sensors that reference physical PIRs.

#### Rationale

Prevents motion_score() from breaking due to undefined sources, and makes system substitutions declarative.

#### Good Example

```yaml
binary_sensor.kitchen_motion_β:
  value_template: "{{ is_state('binary_sensor.kitchen_motion_sensor_α', 'on') }}"
```

#### Bad Example

```yaml
# Missing explicit alias definition
sensor.kitchen_motion_score_γ:
  value_template: "{{ is_state('binary_sensor.kitchen_motion_sensor_α', 'on') }}"
```

---

## [namespace_state_001] Use namespace() for Stateful Logic

**Tier**: all  
**Domain**: templating  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

To retain and mutate variables across multiple lines, wrap state using Jinja2's namespace() feature.

#### Rationale

Enables complex state tracking within templates while maintaining variable scope.

#### Good Example

```yaml
value_template: >
  {% set decay = namespace(score=states('sensor.room_motion_δ') | float(0)) %}
  {% if is_state('binary_sensor.room_motion_β', 'on') %}
    {% set decay.score = 10 %}
  {% else %}
    {% set decay.score = decay.score - 0.5 %}
  {% endif %}
  {{ decay.score }}
```

#### Bad Example

```yaml
value_template: >
  {% set score = states('sensor.room_motion_δ') | float(0) %}
  {% if is_state('binary_sensor.room_motion_β', 'on') %}
    {% set score = 10 %}
  {% else %}
    {% set score = score - 0.5 %}  # Mutation won't work correctly
  {% endif %}
  {{ score }}
```

---

## [package_structure_002] Don't Load Fragmented Files as Packages

**Tier**: all  
**Domain**: configuration  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-04  
**Contributors**: gizmo, iris  

### Principle

Only place files with top-level domain keys under `homeassistant.packages`; use domain-based includes for fragmented files.

#### Rationale

Fragment files like individual scripts or timers can break when treated as packages, leading to startup errors and hard-to-trace bugs.

#### Good Example

```yaml
script: !include_dir_merge_named hestia/config/hermes/scripts
```

#### Bad Example

```yaml
homeassistant:
  packages: !include_dir_named hestia/packages/hermes  # Includes fragments like timers and scripts directly
```

---

## [presence_final_001] Define Final Presence as Tier ζ

**Tier**: ζ  
**Domain**: presence  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Presence outputs used in automation must be derived from abstracted and validated inputs.

#### Rationale

Creates a clean final integration point that other subsystems can safely consume.

#### Good Example

```yaml
binary_sensor.kitchen_presence_ζ:
  state: >
    {{ states('sensor.kitchen_motion_score_γ') | float(0) + 
       states('sensor.kitchen_occupancy_score_γ') | float(0) > 
       states('input_number.presence_threshold') | float(50) }}
```

#### Bad Example

```yaml
# Don't use raw sensors directly in final outputs
binary_sensor.kitchen_presence:
  state: >
    {{ is_state('binary_sensor.kitchen_motion_sensor_α', 'on') }}
```

---

## [presence_pipeline_abstraction_002] Presence State Should Be Derived From Fused Layers

**Tier**: ζ  
**Domain**: presence  
**Status**: approved  
**Created**: 2025-04-02  
**Last Updated**: 2025-04-02  
**Contributors**: system  

### Principle

Construct binary_sensor.<room>_presence_ζ using MSF outputs from *_γ,*_δ, and *_validated scores.

#### Rationale

Centralizes presence logic in a composable, override-friendly, debuggable final abstraction layer.

#### Good Example

```yaml
binary_sensor.kitchen_presence_ζ:
  value_template: >
    {{ states('sensor.kitchen_motion_score_γ') | float(0) + 
       states('sensor.kitchen_occupancy_score_γ') | float(0) > 
       states('input_number.presence_threshold') | float(50) }}
```

#### Bad Example

```yaml
binary_sensor.kitchen_presence:
  value_template: "{{ is_state('binary_sensor.kitchen_motion_sensor_α', 'on') }}"
```

---

## [sensor_config_source_traceability_001] Every Sensor Must Declare Its Configuration Source

**Tier**: μ  
**Domain**: traceability  
**Status**: approved  
**Created**: 2025-04-17  
**Last Updated**: 2025-04-17  
**Contributors**: sensor_mapper  

### Principle

Each YAML-defined sensor must be traceable to its source file path and name. This mapping must be recorded and exposed in all downstream data exports.

#### Rationale

When reviewing validation, auditing, or resolving identity issues, the absence of a `config_yaml` and `config_directory` breaks traceability and undermines trust.

#### Good Example

```yaml
config_yaml: aether_diagnostics.yaml
config_directory: /config/hestia/config/athena/templates
```

#### Bad Example

```yaml
config_yaml: [missing]
```

---

## [sensor_identity_flattening_001] Sensor Identifier Must Be Normalized from YAML Name

**Tier**: μ  
**Domain**: identity  
**Status**: approved  
**Created**: 2025-04-17  
**Last Updated**: 2025-04-17  
**Contributors**: sensor_mapper  

### Principle

Each `sensor_id` used in Airtable must be a deterministic, domain-prefixed transformation of the YAML `name` field.

#### Rationale

This ensures one-to-one traceability, eliminates reliance on inferred mappings, and preserves entity resolution integrity.

#### Good Example

```yaml
name: "Metadata - ATHENA: Presence Diagnostics (HERMES)"
→ sensor_id: sensor.metadata_athena_presence_diagnostics_hermes
```

#### Bad Example

```yaml
sensor_id inferred from unique_id, canonical_id, or unrelated keys
```

---

## [sensor_merge_structure_001] Sensor Merge Requires Structured Entity Definitions

**Tier**: all  
**Domain**: sensor  
**Status**: approved  
**Created**: 2025-04-04  
**Last Updated**: 2025-04-04  
**Contributors**: user  

### Principle

Any directory merged under the sensor: domain must contain only valid sensor dictionaries. Template sensors should be structured with platform: template and included only via sensor: or template: as appropriate.

#### Rationale

Improperly structured files (e.g., empty lists, direct template definitions without platform) will cause Home Assistant to reject configuration or silently skip entities.

#### Good Example

```yaml
# Correct structure in merged file
- platform: template
  sensors:
    my_template_sensor:
      friendly_name: "Room Motion Score"
      value_template: "{{ states('binary_sensor.motion') }}"
```

#### Bad Example

```yaml
# Incorrect structure – empty list
[]

# Incorrect – template block without platform
my_template_sensor:
  value_template: "{{ states('binary_sensor.motion') }}"
```

---

## [template_library_convention_001] Template Library Convention

**Tier**: ε  
**Domain**: templating  
**Status**: approved  
**Created**: 2025-04-03  
**Last Updated**: 2025-04-03  
**Contributors**: system  

### Principle

All reusable macros must reside under the jinja_macros section of template.library.yaml and must be logic-free, deterministic, and side-effect-free.

#### Rationale

Centralizing logic-free macro definitions ensures consistency, testability, and easier maintenance of validation utilities.

#### Good Example

```yaml
# In template.library.yaml
jinja_macros:
  - name: is_available
    description: "Checks if a sensor is available"
    arguments: entity_id
    template: >
      {{ states(entity_id) not in ['unavailable', 'unknown', 'none'] }}

# Usage in other files
value_template: "{{ is_available('sensor.example') }}"
```

#### Bad Example

```yaml
# Scattered macro definitions
- macro:
    - name: is_available
      template: >
        {{ states(entity_id) not in ['unavailable', 'unknown', 'none'] }}
    
# Or macros with side effects
- macro:
    - name: track_update
      template: >
        {% set result = states(entity_id) %}
        {% do state_attr.update({'last_checked': now()}) %}
        {{ result }}
```

---

## [tier_integrity_001] Never Skip Abstraction Tiers

**Tier**: all  
**Domain**: abstraction  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Each logic sensor must only depend on its immediate lower abstraction tier.

#### Rationale

Skipping tiers violates the architecture and introduces dependencies that are difficult to debug or modify.

#### Good Example

```yaml
sensor.bedroom_motion_score_γ:
  source: binary_sensor.bedroom_motion_β
```

#### Bad Example

```yaml
source: binary_sensor.bedroom_pir_α  # Skips β tier
```

---

## [tier_lineage_integrity_001] Preserve Tier Lineage Integrity

**Tier**: γ–δ  
**Domain**: tiering  
**Status**: approved  
**Created**: 2025-04-10  
**Last Updated**: 2025-04-17  
**Contributors**: gpt_architect, sensor_mapper  

### Principle

All sensor entities must be part of a complete and connected Greek-tier lineage without skipped tiers.

#### Rationale

This ensures that abstraction layers can build consistently and that value propagation from source to logic remains predictable.

#### Good Example

```yaml
sensor.motion_score_δ:
  derived_from: sensor.motion_score_γ
```

#### Bad Example

```yaml
sensor.motion_score_δ:
  derived_from: sensor.motion_score_β
```

---

## [validation_wrapping_001] Wrap Sensors in Validated Checks

**Tier**: ε  
**Domain**: diagnostics  
**Status**: approved  
**Created**: 2025-04-01  
**Last Updated**: 2025-04-01  
**Contributors**: system  

### Principle

Always introduce a validated layer to ensure upstream readiness.

#### Rationale

Provides a safe inspection point for validating sensor availability.

#### Good Example

```yaml
binary_sensor.bedroom_motion_validated:
  state: >
    {{ is_state('binary_sensor.bedroom_motion_β', 'on') }}
```

#### Bad Example

```yaml
# Don't use β sensors directly in automations
automation:
  trigger:
    platform: state
    entity_id: binary_sensor.bedroom_motion_β
    to: 'on'
```

---

## [metadata_sensor_tiering_001] Tiering Metadata Sensors According to Referent Module

**Tier**: μ  
**Domain**: documentation  
**Status**: approved  
**Created**: 2025-04-22  
**Last Updated**: 2025-04-22  
**Contributors**: system  

### Principle

Tiering Metadata Sensors According to Referent Module

---

## [metadata_sensor_tiering_001] Metadata Sensor Tiering (Expanded)

**Tier**: μ  
**Domain**: documentation  
**Status**: approved  
**Created**: 2025-04-19  
**Last Updated**: 2025-04-19  
**Contributors**: system  

### Principle

Metadata sensors should adopt the tier of the system or module they describe, unless they describe other metadata sensors—at which point they assume tier μ (mu).

#### Rationale

This avoids conflating metadata sensor tiering with metadata about metadata. When a sensor documents a module, its tier reflects the referent module's role. When it documents other metadata (e.g., validation chains, registry patterns), it is tier μ.

#### Good Example

```yaml
# Describing a γ-tier logic module
- name: Metadata – core/light_abstraction
  tier: γ
  file: /config/hestia/config/hestia/templates/light_abstraction.yaml
  module: Light Abstraction

# Describing the metadata schema itself
- name: Metadata – validation sensor registry
  tier: μ
  module: Metadata Registry Integrity
```

#### Bad Example

```yaml
- name: Metadata – core/light_abstraction
  tier: μ  # Incorrect: the sensor describes a γ-layer logic module
```

---

## [dataflow_rule_001] Flexible Tier Dependencies

**Status**: approved  
**Domain**: dataflow  
**Tier**: system  
**Derived From**: HESTIA Optimized Data Flow Guidelines.md  
**Created**: 2025-04-24  
**Last Updated**: 2025-04-24  
**Contributors**: gpt_architect  
**Tags**: bypass, tier_dependencies, documentation  

### Principle

Tier bypass is acceptable when explicitly documented and contextually justified.

#### Rationale

Ensures clarity when tier model is selectively overridden for simplicity or efficiency.

---

## [dataflow_rule_002] Tier-Appropriate Processing

**Status**: approved  
**Domain**: dataflow  
**Tier**: system  
**Derived From**: HESTIA Optimized Data Flow Guidelines.md  
**Created**: 2025-04-24  
**Last Updated**: 2025-04-24  
**Contributors**: gpt_architect  
**Tags**: tier_roles, logic_separation, tier_design  

### Principle

Each tier must implement logic appropriate to its semantic function, avoiding cross-tier logic contamination.

#### Rationale

Preserves the abstraction boundaries of the tier system and simplifies diagnosis and reasoning.

---

## [dataflow_rule_003] Fallback Chains

**Status**: approved  
**Domain**: resilience  
**Tier**: system  
**Derived From**: HESTIA Optimized Data Flow Guidelines.md  
**Created**: 2025-04-24  
**Last Updated**: 2025-04-24  
**Contributors**: gpt_architect  
**Tags**: fallback, tier_resilience, dependency_handling  

### Principle

Higher tiers must provide fallback mechanisms to handle unavailable dependencies gracefully.

#### Rationale

Improves resilience by allowing higher-tier logic to degrade gracefully without failures.

---

## [sensor_extraction_guide_001] Sensor Extraction Strategy

**Status**: proposed  
**Domain**: sensors  
**Tier**: system  
**Derived From**: Sensor Extraction - Additional Guidance.md  
**Tags**: sensor, extraction, tier, validation  

### Principle

Apply tier-based parsing and validation logic when extracting sensors from YAML, ensuring metadata completeness and architectural compliance.

#### Rationale

Prevents entity misclassification, supports automated documentation, and ensures semantic traceability.

---

## [package_script_include_001] Package Script Integration Pattern

**Status**: proposed  
**Domain**: configuration  
**Tier**: all  
**Derived From**: HESTIA Architecture Principles: Conver.yml  
**Tags**: configuration, includes, scripts, packages  

### Principle  
Use unquoted !include directives for scripts structured as dictionaries within meta_wrapper packages.

### Rationale  
Ensures HomeAssistant merges script files correctly without treating them as strings.

---

## [script_merge_structure_001] Script Merge Compatible Structure

**Status**: proposed  
**Domain**: configuration  
**Tier**: all  
**Derived From**: HESTIA Architecture Principles: Conver.yml  
**Tags**: configuration, scripts, packages, merging  

### Principle  
Ensure both main config and packages use dictionary-style formatting for script sections.

### Rationale  
Avoids merging conflicts by maintaining structural consistency expected by HomeAssistant.

---

## [patterns_jinjamacro1] Script Merge Compatible Structure

```yaml
date: 2025-05-24
tier: γ
domain: templating
status: approved
change: Introduced design pattern for external Jinja macro imports in Home Assistant templates
cause: Integration need for modular templating logic
effect: Enables maintainable Jinja2 macro architecture within sensor and automation definitions
applied_by: meta_architect
```

---

## [tool_doctrine_001] Snapshot Phase Assumptions

Each phase of the Mnemosyne Snapshot Engine operates under strict directory and structural preconditions. These assumptions are critical to maintain deterministic output and audit consistency:

### Phase: `symlink_merge`

- Expects all upstream directories (especially `/config/hestia/sensors/`, `/tools/`, and `/templates/`) to be free of:
  - broken symbolic links
  - recursive symlink cycles
  - non-resolvable relative paths (`../` that exceed root context)
- Target path `/config/hestia/symlink/_merged_templates` must:
  - exist and be writable
  - not be a symlink itself
  - be clear of residual partial merges

### Phase: `tree_generate`

- Assumes successful completion of `symlink_merge`, producing a stable, readable root directory.
- Fails hard if target directory is:
  - missing
  - unreadable due to permissions
  - structurally malformed (e.g., empty with no symbolic content)

### Cross-Phase Contract

- If `symlink_merge` fails in strict mode, `tree_generate` will not execute unless patched for fallback.
- Any hard failure in a preparatory phase must be recoverable through relaxed mode or stub generation.

These assumptions must be enforced in doctrine-aware validators and honored across toolchain simulations.

---