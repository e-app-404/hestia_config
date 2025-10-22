---
id: ADR-0004
title: Canonical Area Hierarchy & Spatial Relationship Contract
slug: canonical-area-hierarchy-spatial-relationship-contract
status: Accepted
related:
- ADR-0021
supersedes: []
date: 2025-09-11
decision: Establish a canonical contract through this ADR to agree on a shared understanding of area hierarchy, containment relationships, and inference propagation rules to ensure consistent spatial reasoning across Home Assistant deployments.
tags: ["architecture", "area", "hierarchy", "spatial", "relationship", "contract", "adr"]
author: "e-app-404"
last_updated: 2025-10-21
---

# ADR-0004: Canonical Area Hierarchy & Spatial Relationship Contract

## Table of Contents

1. [Context](#1-context)
2. [Decision](#2-decision)
3. [Enforcement](#3-enforcement)
  - [Contract Metadata](#contract-metadata)
  - [Containment Graph](#containment-graph)
  - [Nodes](#nodes)
  - [Propagation Rules](#propagation-rules)
  - [Output Contract](#output-contract)
4. [Recent Improvements (2025-10-04)](#3-recent-improvements-2025-10-04)
  - [Structural Fixes Applied](#structural-fixes-applied)
  - [Registry Synchronization](#registry-synchronization)
5. [Enforcement](#4-enforcement)
6. [Tokens](#5-tokens)

## 1. Context

Spatial reasoning and containment relationships are essential for Home Assistant registry rehydration, automation, and entity logic. The same principles apply to the area hierarchy, where understanding the relationships between different areas, rooms, and floors is crucial for effective automation and control. 

## 2. Decision

Establish a canonical contract through this ADR to agree on a shared understanding of area hierarchy, containment relationships, and inference propagation rules to ensure consistent spatial reasoning across Home Assistant deployments.

## 3. Enforcement

### Contract Metadata

Defines key information about the contract:

| Key                                | Value                                   |
|-------------------------------------|----------------------------------------|
| **Contract ID**                    | area_relationships_contract             |
| **Version**                        | 1.1                                     |
| **Author**                         | Evert                                   |
| **Status**                         | canonical_draft                         |
| **File Path**                      | www/area_hierarchy.yaml                 |
| **Live Registry Consistency**      | improved                                |
| **Coverage Percent**               | 100.0                                   |
| **Last Validated**                 | 2025-10-04                              |

> Note: Programmatically validated against live Home Assistant registry data. Major structural improvements applied October 2025 including duplicate removal, missing node additions, and registry alignment.

### Containment Graph

Defines parent-child relationships for areas, rooms, floors, and containers. For instance:
- `ground_floor` contains: hallway, kitchen, laundry_room, living_room, powder_room
- `bedroom` contains: bedroom_main, wardrobe, desk
- ... (see full graph in source)

### Nodes
Each node defines:
- `id`, `type`, `canonical_name`, `parents`, `container`, `devices`, `entities`, `services`, `tags`

```yaml
  - id: hallway
    type: area
    canonical_name: Hallway
    parents: [ground_floor, top_floor]
    tags: [transit, structural_connector]
  - ...
```

### Propagation Rules

Defines how signals propagate through the hierarchy:

- **motion:**
  - from_subarea_to_area: probable
  - from_area_to_subarea: improbable
  - transient_decay: true
  - decay_rate: 0.7
- **presence:**
  - from_subarea_to_area: possible
  - memory: sticky
- **occupancy:**
  - aggregate_method: weighted_sum
  - weights: subarea: 0.6, area: 1.0, container: 0.4
  - decay_profile: timeouts per level
- **graph:**
  - allow_cycles: false
  - max_depth: 5
  - transitive_inference: true

### Output Contract

Defines the schema for emitting the area hierarchy:

- `area_id`: string
- `parent_room`: string | null
- `floor_id`: string
- `type`: enum(area, subarea, floor, service)
- `inference_weight`: float
- `contributes_to`: list[string]
- `inferred_by`: string | null

## 3. Recent Improvements (2025-10-04)

### Structural Fixes Applied

- **Duplicate Resolution:** Removed duplicate `downstairs` entries in containment graph
- **Missing Nodes:** Added `sanctum`, `clapham`, `warnings`, and completed `tailscale_vpn` definitions
- **Registry Alignment:** Updated canonical names to match Home Assistant registry exactly
- **Data Consistency:** Fixed format inconsistencies (empty arrays → proper integers)
- **Containment Logic:** Simplified parent-child relationships and removed circular references

### Registry Synchronization
- Canonical names now match registry: `bedroom` → "Bedroom", `upstairs` → "upstairs", `hifi_configuration` → "hifi configuration"
- All 37+ areas from live registry properly represented with complete node definitions
- Floor/area relationships accurately modeled based on current `core.area_registry` and `core.floor_registry`

## 4. Enforcement

- All subarea relationships must be explicitly declared to avoid inference ambiguity.
- Changes to inference propagation require a new contract version.
- This contract does not govern device placement, but entity logic implication.
- Registry consistency validation required before major automation deployments.

## 5. Token Blocks

- **Primary:** `containment_graph`, `nodes`, `propagation_rules`, `output_contract`, `contract_metadata`
- **Schema:** `area_id`, `parent_room`, `floor_id`, `type`, `inference_weight`, `contributes_to`, `inferred_by`
- **Registry:** `sanctum`, `clapham`, `tailscale_vpn`, `warnings`, `ottoman`, `hifi_configuration`
- **Relationships:** `bedroom_subareas`, `network_infrastructure`, `service_organization`

## ADR-0004 Addendum v1.1: Area Hierarchy Contract Update

## Executive Summary

This addendum updates ADR-0004 to reflect the current state of the area hierarchy as implemented in `area_mapping.yaml v3.3` (last updated 2025-10-20). The document captures significant architectural enhancements including:

1. **Integration with room_db** for centralized SQL-based configuration
2. **Multi-domain capabilities** (motion lighting, vacuum control, activity tracking)
3. **Enhanced spatial hierarchy** with explicit parent-child relationships
4. **Registry entities** for shared services (TTS Gate, Plex indexes)
5. **Propagation rules refinement** with granular control

---

## 1. Contract Metadata Updates

### Version & Source Information

| Key                                | Previous Value (v1.1)        | Current Value (v3.3)                                    |
|------------------------------------|------------------------------|--------------------------------------------------------|
| **Contract Version**               | 1.1                          | 3.3                                                    |
| **Last Updated**                   | 2025-10-04                   | 2025-10-20                                             |
| **Source File**                    | www/area_hierarchy.yaml      | canonical/support/contracts/area_hierarchy.yaml        |
| **Primary Consumer**               | Home Assistant Registry      | room_db (Activity Tracker, Motion Lighting, Vacuum)    |
| **Coverage Percent**               | 100.0                        | 100.0 (maintained)                                     |
| **Registry Synchronization**       | improved                     | canonical (full alignment)                             |

### Valid Rooms Registry

The contract now explicitly defines a **valid_rooms** list for room_db integration:

```yaml
valid_rooms:
  - bedroom
  - ensuite
  - kitchen
  - living_room
  - downstairs
  - upstairs
  - entrance
  - powder_room
  - desk
  - wardrobe
  - laundry_room
  - tts_gate_registry
  - plex_tv_index
  - plex_movie_index
```

**Implications:**
- Only these room IDs are valid for SQL database operations
- Registry entities (`tts_gate_registry`, `plex_*_index`) included for shared service mapping
- Motion lighting, vacuum control, and activity tracking must reference these canonical IDs

---

## 2. Enhanced Node Schema

### New Capabilities Structure

Each spatial node now includes a **capabilities** block defining domain-specific configurations:

#### Motion Lighting Capability
```yaml
capabilities:
  motion_lighting:
    timeout: 120                    # seconds before lights turn off
    illuminance_threshold: 10       # lux threshold for activation
```

**Coverage:** 10 rooms with motion lighting
- bedroom, ensuite, kitchen, living_room, downstairs, upstairs, entrance, desk, wardrobe

#### Vacuum Control Capability
```yaml
capabilities:
  vacuum_control:
    segment_id: 17                  # Valetudo map segment ID
    default_mode: "deep"            # cleaning mode: deep|standard
    cleaning_frequency_days: 3      # days between cleanings
    activity_threshold_hours: 12    # hours of inactivity to trigger cleaning
```

**Coverage:** 5 rooms with vacuum control
- kitchen, living_room, downstairs, powder_room, laundry_room

#### Shared Registry Capability
```yaml
capabilities:
  shared:
    description: "TTS announcement deduplication and rate limiting"
```

**Coverage:** 3 registry entities
- tts_gate_registry, plex_tv_index, plex_movie_index

### Updated Node Properties

New mandatory fields for all spatial nodes:

| Property              | Type                  | Description                                              | Example                          |
|-----------------------|-----------------------|----------------------------------------------------------|----------------------------------|
| `floor_id`            | string                | Physical floor designation                               | `sanctum`, `downstairs`          |
| `container`           | [type, id, name]      | Legacy container format for backward compatibility       | `["area", "bedroom", "Bedroom"]` |
| `children`            | list[string]          | Direct child node IDs (explicit hierarchy)               | `[desk, wardrobe, ottoman]`      |
| `propagation`         | dict                  | Node-specific propagation rules override                 | See section 4                    |
| `capabilities`        | dict                  | Domain-specific capabilities (motion/vacuum/shared)      | See examples above               |
| `devices`             | integer               | Home Assistant device count                              | `66`                             |
| `entities`            | integer               | Home Assistant entity count                              | `7`                              |
| `notes`               | string (optional)     | Implementation notes                                     | "Uses door contact proxy"        |

---

## 3. Spatial Hierarchy Refinements

### Floor Designations

The contract now uses two primary floor identifiers:

| Floor ID       | Type          | Canonical Name            | Purpose                          |
|----------------|---------------|---------------------------|----------------------------------|
| `downstairs`   | Physical      | "Downstairs"              | Ground floor / public areas      |
| `sanctum`      | Logical       | "Sanctum"                 | Upper floor / private areas      |

**Note:** The name "sanctum" reflects the private/bedroom zone rather than a strict physical floor designation.

### Revised Containment Graph

#### Top-Level Structure
```
home
├── hallway (structural connector)
│   ├── downstairs (floor: downstairs)
│   │   ├── entrance*        [subarea]
│   │   ├── kitchen
│   │   │   └── laundry_room* [subarea]
│   │   ├── living_room
│   │   └── powder_room
│   └── upstairs (floor: sanctum)
│       └── sanctum (logical zone)
│           ├── bedroom
│           │   ├── desk*             [subarea]
│           │   ├── wardrobe*         [subarea]
│           │   ├── ottoman*          [subarea]
│           │   └── hifi_configuration* [subarea]
│           └── ensuite
```

**Key Changes from v1.1:**
- `entrance` explicitly marked as subarea of `downstairs`
- `laundry_room` properly nested under `kitchen` (parent-child)
- `sanctum` introduced as logical zone containing `bedroom` and `ensuite`
- `ottoman` and `hifi_configuration` added as bedroom subareas

### Parent-Child Relationships

| Parent Node   | Children                                              | Type Relationship          |
|---------------|-------------------------------------------------------|----------------------------|
| `hallway`     | `downstairs`, `upstairs`                              | Structural connector       |
| `downstairs`  | `entrance`, `kitchen`, `living_room`, `powder_room`   | Floor-to-area              |
| `upstairs`    | `bedroom`, `ensuite`                                  | Floor-to-area              |
| `bedroom`     | `desk`, `wardrobe`, `ottoman`, `hifi_configuration`   | Area-to-subarea            |
| `kitchen`     | `laundry_room`                                        | Area-to-subarea            |
| `sanctum`     | `bedroom`, `ensuite`                                  | Logical zone-to-area       |

---

## 4. Propagation Rules Enhancements

### Global Propagation Rules (Unchanged)

The base propagation rules from v1.1 remain valid:

```yaml
motion:
  from_subarea_to_area: probable
  from_area_to_subarea: improbable
  transient_decay: true
  decay_rate: 0.7

presence:
  from_subarea_to_area: possible
  from_area_to_subarea: rare
  memory: sticky

occupancy:
  aggregate_method: weighted_sum
  weights:
    subarea: 0.6
    area: 1.0
    container: 0.4
  decay_profile:
    subarea_timeout: 2m
    area_timeout: 5m
    container_timeout: 10m
```

### Node-Specific Propagation Overrides

New feature: Individual nodes can override global propagation rules:

#### Example: Hallway Nodes (downstairs, upstairs)
```yaml
propagation:
  motion_from_children: probable     # High likelihood motion in child areas propagates up
  occupancy_aggregate: weighted_sum  # Sum child occupancy with weights
```

**Use Case:** Hallways aggregate motion from connected rooms (kitchen, living_room) to determine overall circulation patterns.

#### Example: Subarea Nodes (desk, wardrobe)
```yaml
propagation:
  motion_to_parent: probable         # Motion in desk likely means bedroom occupied
  occupancy_to_parent: possible      # Occupancy in desk suggests bedroom activity
```

**Use Case:** Bedroom subareas contribute to parent bedroom occupancy calculations for activity tracking.

---

## 5. Multi-Domain Integration

### Domain Mapping

| Domain               | Config Source                              | Consuming Systems              | Rooms Covered |
|----------------------|--------------------------------------------|--------------------------------|---------------|
| Motion Lighting      | `sensor.room_configs_motion_lighting`      | AppDaemon automations (v1.5)   | 10            |
| Vacuum Control       | `sensor.room_configs_vacuum_control`       | Valetudo integration           | 5             |
| Activity Tracking    | `sensor.room_configs_activity_tracking`    | Occupancy sensors              | 8             |
| TTS Gate Registry    | `sensor.room_configs_tts_gate_registry`    | TTS deduplication              | 1 (shared)    |
| Plex Media Indexes   | `sensor.room_configs_plex_*_index`         | Media metadata cache           | 2 (shared)    |

### Allowed Domains Map

Registry entities have domain restrictions:

```yaml
allowed_domains_map:
  tts_gate_registry: ["shared"]
  plex_tv_index: ["shared"]
  plex_movie_index: ["shared"]
```

**Rationale:** Registry entities are system-wide services not tied to physical spaces, so they only accept "shared" domain configurations.

---

## 6. Activity Tracking Coverage

### Monitored Rooms (8)

| Room ID       | Sensor Entity                                  | Type       | Notes                        |
|---------------|------------------------------------------------|------------|------------------------------|
| bedroom       | `binary_sensor.bedroom_occupancy_beta`         | Occupancy  | Primary sleeping area        |
| kitchen       | `binary_sensor.kitchen_occupancy_beta`         | Occupancy  | Cooking/dining               |
| living_room   | `binary_sensor.living_room_occupancy_beta`     | Occupancy  | Entertainment                |
| ensuite       | `binary_sensor.ensuite_occupancy_beta`         | Occupancy  | Private bathroom             |
| downstairs    | `binary_sensor.hallway_downstairs_occupancy_beta` | Occupancy | Circulation                  |
| upstairs      | `binary_sensor.hallway_upstairs_occupancy_beta` | Occupancy | Circulation                  |
| entrance      | `binary_sensor.entrance_motion_beta`           | Motion     | Door contact proxy           |
| desk          | `binary_sensor.desk_occupancy_beta`            | Occupancy  | Workspace                    |

### Not Tracked (5)

| Room ID             | Reason                                    | Alternative Sensing         |
|---------------------|-------------------------------------------|-----------------------------|
| wardrobe            | No occupancy sensor                       | Motion only                 |
| ottoman             | No occupancy sensor                       | Vibration sensor            |
| powder_room         | No occupancy sensor                       | Vacuum control only         |
| laundry_room        | No occupancy sensor                       | Vacuum control only         |
| hifi_configuration  | Virtual configuration area                | N/A                         |

**Inference Strategy:** Untracked subareas contribute to parent area occupancy through spatial propagation rules (weighted aggregation).

---

## 7. Vacuum Control Summary

### Segment Mapping

| Room          | Segment ID | Mode      | Frequency (days) | Activity Threshold (hours) |
|---------------|------------|-----------|------------------|----------------------------|
| laundry_room  | 16         | standard  | 7                | 72                         |
| kitchen       | 17         | deep      | 3                | 12                         |
| downstairs    | 18         | standard  | 3                | 24                         |
| living_room   | 19         | standard  | 3                | 24                         |
| powder_room   | 20         | standard  | 7                | 48                         |

**Integration Point:** Vacuum cleaning schedules are triggered based on room inactivity (from activity tracking) exceeding the activity threshold.

**Design Rationale:**
- High-traffic areas (kitchen, downstairs, living_room): 3-day frequency
- Low-traffic areas (laundry_room, powder_room): 7-day frequency
- Kitchen uses "deep" mode due to food debris potential

---

## 8. Registry Entity Types

### New Node Type: Registry

Registry entities represent system-wide shared services rather than physical spaces:

```yaml
- id: tts_gate_registry
  type: registry                          # New type designation
  name: "TTS Gate Registry"
  canonical_name: "TTS Gate Registry"
  capabilities:
    shared:
      description: "TTS announcement deduplication and rate limiting"
```

**Characteristics:**
- No spatial properties (`parents`, `floor_id`, `children`)
- No device/entity counts
- Single capability domain: `shared`
- Used for system-wide configuration storage in room_db

**Current Registry Entities:**
1. `tts_gate_registry` - TTS announcement management
2. `plex_tv_index` - TV show metadata cache
3. `plex_movie_index` - Movie metadata cache

---

## 9. Backward Compatibility

### Deprecated Properties (Maintained for Migration)

The `container` property is preserved in its legacy format for backward compatibility:

```yaml
container: ["area", "bedroom", "Bedroom"]
           # [type,  id,      display_name]
```

**Migration Path:**
- Old systems can continue reading `container[1]` for room ID
- New systems should use `id` directly
- Future v4.0 will remove `container` entirely

### Legacy Entity Pattern Support

While canonical room IDs are authoritative, the contract acknowledges that sensor entity names may differ:

- **Canonical ID:** `downstairs`
- **Sensor Entity:** `binary_sensor.hallway_downstairs_occupancy_beta`
- **Display Name:** "Hallway (Downstairs)"

**Rationale:** Home Assistant entity IDs are immutable after creation, so renaming requires breaking changes. The area mapping provides the translation layer.

---

## 10. Validation & Enforcement

### Structural Validation Rules

1. **Parent Existence:** Every `parents` entry must reference an existing node `id`
2. **Floor Consistency:** `floor_id` must match parent's `floor_id` or be explicitly overridden
3. **Capability Integrity:** Each capability block must include all required fields for its domain
4. **Circular References:** The hierarchy tree must be acyclic (no cycles allowed)
5. **Type Constraints:**
   - `type: registry` nodes cannot have spatial properties
   - `type: subarea` nodes must have exactly one parent
   - `type: area` nodes should not have more than 6 children (design guideline)

### Data Quality Metrics

| Metric                        | Target | Current | Status |
|-------------------------------|--------|---------|--------|
| Registry synchronization      | 100%   | 100%    | ✅     |
| Node definitions complete     | 100%   | 100%    | ✅     |
| Capability coverage           | 80%    | 90%     | ✅     |
| Activity tracking coverage    | 70%    | 62%     | 🟨     |
| Vacuum control coverage       | 40%    | 36%     | ✅     |

**Note:** Activity tracking coverage is 62% (8/13 physical rooms), which is acceptable given that subareas contribute to parent occupancy via propagation rules.

---

## 11. Implementation Notes

### Integration with AppDaemon room_db

The area mapping serves as the **canonical source of truth** for room configurations stored in `room_database.db`:

**Data Flow:**
1. `area_mapping.yaml` defines room capabilities
2. `room_db_updater` app reads YAML and populates SQLite database
3. SQL sensors expose configurations: `sensor.room_configs_motion_lighting`
4. Automations read from sensors: `state_attr('sensor.room_configs_motion_lighting', 'payload')['bedroom']`

**REST Command Integration:**
```yaml
rest_command.room_db_update_config:
  url: "http://localhost:5000/api/room_db/update"
  payload:
    room_id: "{{ room_id }}"
    domain: "{{ domain }}"
    config: "{{ config }}"
```

### Motion Lighting Automation Pattern

Current SQL-based automations follow this naming convention:
```
automation.motion_lights_{room}_sql_v1_5
```

Example: `automation.motion_lights_bedroom_sql_v1_5`

**Entity References:**
- Motion sensor: `binary_sensor.{room}_motion_beta`
- Light group: `light.adaptive_{room}_light_group` OR `light.group_{room}_lights`
- Adaptive lighting: `switch.adaptive_lighting_{room}`
- Configuration: `state_attr('sensor.room_configs_motion_lighting', 'payload')['{room}']`

### Adaptive Lighting Integration

Each room with motion lighting has corresponding adaptive lighting switches:

| Switch Purpose           | Entity Pattern                                 |
|--------------------------|------------------------------------------------|
| Main switch              | `switch.adaptive_lighting_{room}`              |
| Brightness adaptation    | `switch.adaptive_lighting_adapt_brightness_{room}` |
| Color adaptation         | `switch.adaptive_lighting_adapt_color_{room}`   |
| Sleep mode               | `switch.adaptive_lighting_sleep_mode_{room}`    |

**Circadian Rhythm:** Adaptive lighting automatically adjusts color temperature and brightness based on time of day to match natural circadian rhythms.

---

## 12. Future Considerations

### Planned Enhancements (v4.0)

1. **Canonical Entity Naming:**
   - Migrate to `roomdb_` prefix for all SQL-derived entities
   - Example: `sensor.roomdb_motion_lighting_configs`
   - Preserves backward compatibility during transition

2. **Enhanced Propagation Inference:**
   - Machine learning-based occupancy prediction
   - Temporal patterns in room transitions
   - Bayesian inference for presence likelihood

3. **Multi-Floor Expansion:**
   - Support for houses with 3+ floors
   - Elevator/stairway zones as structural connectors
   - Vertical propagation rules (floor-to-floor)

4. **Dynamic Capability Discovery:**
   - Auto-detect new domains from room_db schemas
   - Extensible capability framework
   - Third-party integration support

### Deprecation Timeline

| Component                | Version | Status      | Removal Target |
|--------------------------|---------|-------------|----------------|
| `container` property     | v3.3    | Maintained  | v5.0           |
| Non-`_beta` motion sensors | v3.3  | Legacy      | v4.0           |
| `var.*` entities         | v3.0    | Removed     | N/A            |
| YAML-based room configs  | v2.0    | Removed     | N/A            |

---

## 13. Addendum Approval

### Stakeholder Sign-Off

- [ ] **System Architect** (Evert): Structural review
- [ ] **AppDaemon Maintainer**: room_db integration validation
- [ ] **Motion Lighting Maintainer**: Automation compatibility check
- [ ] **Vacuum Control Maintainer**: Segment mapping verification
- [ ] **Home Assistant Administrator**: Registry synchronization audit

### Testing Requirements

Before merging this addendum:

1. ✅ All 14 valid rooms present in Home Assistant registry
2. ✅ SQL sensors expose correct JSON payloads for all domains
3. ✅ Motion lighting automations reference correct entity patterns
4. ✅ Vacuum segment IDs match Valetudo map
5. ✅ Propagation rules tested with sample occupancy events
6. ✅ Registry entities accessible via room_db API

---

## 14. Token Blocks (Updated)

### Primary Tokens
- `area_mapping_v3.3`, `room_db_integration`, `motion_lighting_sql_v15`, `vacuum_control_segments`
- `activity_tracking_coverage`, `propagation_rules_v3`, `spatial_hierarchy_v3`, `registry_entity_type`

### Capability Tokens
- `motion_lighting_capability`, `vacuum_control_capability`, `shared_registry_capability`
- `timeout`, `illuminance_threshold`, `segment_id`, `cleaning_frequency_days`, `activity_threshold_hours`

### Spatial Tokens
- `sanctum_zone`, `downstairs_floor`, `hallway_connector`, `bedroom_subareas`, `kitchen_subareas`
- `parent_child_explicit`, `floor_id`, `container_legacy`, `propagation_override`

### Integration Tokens
- `sensor.room_configs_motion_lighting`, `sensor.room_configs_vacuum_control`, `sensor.room_configs_activity_tracking`
- `rest_command.room_db_update_config`, `automation.motion_lights_*_sql_v15`
- `binary_sensor.*_motion_beta`, `binary_sensor.*_occupancy_beta`, `light.adaptive_*_light_group`

### Registry Tokens
- `tts_gate_registry`, `plex_tv_index`, `plex_movie_index`, `allowed_domains_map`, `valid_rooms`

---

## 15. References

- **Parent ADR:** ADR-0004 v1.1 (Canonical Area Hierarchy & Spatial Relationship Contract)
- **Source Document:** `/config/canonical/support/contracts/area_hierarchy.yaml` (area_mapping.yaml v3.3)
- **Related ADRs:**
  - ADR-0021: Room Database Architecture
  - ADR-0024: Path Resolution Standards
  - ADR-0027: Configuration Change Management
  - ADR-0028: SQL Migration for Room Database
  - ADR-0031: Hestia Architectural Doctrine
- **Integration Guides:**
  - Media Registry Integration Guide
  - Motion Lighting SQL Migration Guide
  - Activity Tracker Configuration Guide

---

## Changelog

### v1.1 (2025-10-21)
- Initial addendum creation
- Documented area_mapping.yaml v3.3 integration with room_db
- Added multi-domain capabilities (motion lighting, vacuum control, activity tracking)
- Defined registry entity type and allowed_domains_map
- Captured propagation rule enhancements with node-specific overrides
- Documented spatial hierarchy refinements (sanctum zone, bedroom subareas)
- Added activity tracking coverage analysis
- Included vacuum control segment mapping
- Established validation rules and data quality metrics
- Outlined future enhancements for v4.0

---

**Document Status:** Proposed for review  
**Next Review Date:** 2025-11-01  
**Effective Date:** Upon approval and merge into ADR-0004 v2.0

## Token Blocks

```yaml
TOKEN_BLOCK:
  accepted:
    - AREA_CONTRACT_DEFINED
  requires:
    - ADR_SCHEMA_V1
```
