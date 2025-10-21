---
id: ADR-0004
title: Canonical Area Hierarchy & Spatial Relationship Contract
slug: canonical-area-hierarchy-spatial-relationship-contract
status: Accepted
related:
- ADR-0021
supersedes: []
last_updated: '2025-10-15'
date: 2025-09-11
decision: '### Contract Metadata - **Contract ID:** area_relationships_contract -
  **Version:** 1.1 - **Author:** Evert - **Status:** canonical_draft - **File Path:**
  canonical/support/contracts/area_hierarchy.yaml - **Live Registry Consistency:**
  improved - **Coverage Percent:** 100.0 - **Last Validated:** 2025-10-04 - **Notes:**
  Programmatically validated against live Home Assistant registry data.'
tags:
- architecture
- area
- hierarchy
- spatial
- relationship
- contract
- adr
author: "e-app-404"
---

# ADR-0004: Canonical Area Hierarchy & Spatial Relationship Contract

## Table of Contents

1. Context
2. Decision
3. Enforcement
4. Tokens
5. Last updated

## 1. Context

Spatial reasoning and containment relationships are essential for Home Assistant registry rehydration, automation, and entity logic. The same principles apply to the area hierarchy, where understanding the relationships between different areas, rooms, and floors is crucial for effective automation and control. 

## 2. Decision

Establish a canonical contract through this ADR to agree on a shared understanding of area hierarchy, containment relationships, and inference propagation rules to ensure consistent spatial reasoning across Home Assistant deployments.

## 3. Enforcement

### Contract Metadata

Defines key information about the contract:

| Key                   | Value                                           |
|-----------------------  |-------------------------------------------------|
| **Contract ID**       | area_relationships_contract                     |
| **Version**           | 1.1                                             |
| **Author**            | Evert                                          |
| **Status**                    | canonical_draft                                 |
| **File Path**                 | canonical/support/contracts/area_hierarchy.yaml |
| **Live Registry Consistency** | improved |
| **Coverage Percent**  | 100.0 |
| **Last Validated**    | 2025-10-04 |

- **Notes:** Programmatically validated against live Home Assistant registry data. Major structural improvements applied October 2025 including duplicate removal, missing node additions, and registry alignment.

### Containment Graph
Defines parent-child relationships for areas, rooms, floors, and containers. Example:
- `ground_floor` contains: hallway, kitchen, laundry_room, living_room, powder_room
- `bedroom` contains: bedroom_main, wardrobe, desk
- ... (see full graph in source)

### Nodes
Each node defines:
- `id`, `type`, `canonical_name`, `parents`, `container`, `devices`, `entities`, `services`, `tags`
- Example:
  - id: hallway
    type: area
    canonical_name: Hallway
    parents: [ground_floor, top_floor]
    tags: [transit, structural_connector]
  - ...

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

## 5. Tokens
- **Primary:** `containment_graph`, `nodes`, `propagation_rules`, `output_contract`, `contract_metadata`
- **Schema:** `area_id`, `parent_room`, `floor_id`, `type`, `inference_weight`, `contributes_to`, `inferred_by`
- **Registry:** `sanctum`, `clapham`, `tailscale_vpn`, `warnings`, `ottoman`, `hifi_configuration`
- **Relationships:** `bedroom_subareas`, `network_infrastructure`, `service_organization`

---
_Last updated: 2025-10-04_
