# HESTIA Architecture & Sensor Abstraction Mapping - Compact Summary

## 1. System Overview

HESTIA is a Home Assistant-based architecture that follows a Greek-letter tiered abstraction model:

- **α (alpha)**: Raw sensor inputs directly from devices
- **β (beta)**: Hardware-independent abstractions/aliases of raw inputs
- **γ (gamma)**: Logic/scoring layer that processes abstracted inputs
- **δ (delta)**: Decay/aggregation layer that handles temporal aspects
- **ε (epsilon)**: Validation layer that ensures data reliability
- **ζ (zeta)**: Final output/presence layer used by automations

The system is organized into subsystems:
- **HERMES**: Presence detection
- **THEIA**: Lighting control
- **AETHER**: Climate/environmental control
- **ATHENA**: System diagnostics
- **SOTERIA**: Device tracking
- **HEPHAESTUS**: Room registry & configuration

## 2. Key Patterns & Issues

### Naming Patterns:
- Standard pattern should be `<room>_<role>_<tier>` (e.g., `bedroom_motion_score_γ`)
- Display names follow `[Semantic Role] - [Room] (Tier)` (e.g., "Motion Activity Score - Bedroom (γ)")
- Attributes must include `canonical_id` and `tier`

### Common Issues:
1. **Naming Inconsistencies**: Both `bedroom_motion_score_γ` and `motion_score_bedroom_γ` patterns exist
2. **Missing Tier Markers**: Many sensors lack explicit tier designation
3. **Incorrect Tier Assignment**: Some sensors marked with wrong tier (e.g., ζ functions labeled as γ)
4. **Duplicated Functionality**: Multiple sensors perform same function with different names

## 3. Room & Sensor Type Matrix

Primary rooms:
- Bedroom (incl. Wardrobe)
- Living Room
- Kitchen
- Ensuite
- Hallway (Upstairs, Downstairs, Entrance)

Sensor types:
- Motion
- Occupancy
- Temperature
- Humidity
- Illuminance
- Contact
- Presence (MSF)
- Climate Status

## 4. Tier Mapping Examples

### Motion Sensors (Bedroom):
```
α: binary_sensor.bedroom_motion_sensor_α (missing/implicit)
β: binary_sensor.bedroom_motion_β
γ: sensor.bedroom_motion_score_γ, sensor.motion_score_bedroom_γ (conflict)
δ: sensor.bedroom_motion_score_δ
ε: sensor.bedroom_motion_score_ε
ζ: binary_sensor.bedroom_presence_ζ
```

### Temperature Sensors (Kitchen):
```
α: sensor.kitchen_climate_temperature (missing tier suffix)
β: sensor.combined_temperature_kitchen (incorrect pattern)
γ: sensor.kitchen_temperature_trend_γ (missing)
ε: binary_sensor.kitchen_climate_status (missing tier suffix)
ζ: binary_sensor.kitchen_heating_needed (incorrectly marked as γ)
```

## 5. Implementation Strategy

1. **Attribute Standardization**: Add correct `canonical_id` and `tier` attributes
2. **Create Missing Tiers**: Add sensors where gaps exist in the tier chain
3. **Fix Tier Assignments**: Correct sensors with wrong tier designation
4. **Standardize Naming**: Align entity_ids with standard pattern
5. **Semantic Naming**: Update friendly_names to follow semantic model

## 6. Special Subsystems

### ATHENA (Diagnostics):
- Mostly ε-tier sensors for monitoring and validation
- Uses problem detection patterns for system monitoring

### SOTERIA (Device Tracking):
- Focuses on device battery, presence, and status monitoring
- Registry-based approach with status tracking

### HEPHAESTUS (Room Registry):
- Manages room configurations and device mappings
- Provides central registry for other subsystems

## 7. YAML Mapping Format

Proposed format for mapping sensors to canonical tiers:
```yaml
sensor_type:
  room:
    α: "entity_id_alpha"
    β: "entity_id_beta"
    γ: "entity_id_gamma"
    δ: "entity_id_delta"
    ε: "entity_id_epsilon"
    ζ: "entity_id_zeta"
```