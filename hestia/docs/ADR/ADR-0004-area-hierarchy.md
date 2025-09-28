---
id: ADR-0004
title: "Canonical Area Hierarchy & Spatial Relationship Contract"
date: 2025-09-11
related: []
supersedes: []
status: Accepted
tags: ["architecture", "area", "hierarchy", "spatial", "relationship", "contract", "adr"]
last_updated: 2025-07-22
author: "Evert Appels"
---

# ADR-0004: Canonical Area Hierarchy & Spatial Relationship Contract

## Table of Contents
1. Context
2. Decision
3. Enforcement
4. Tokens
5. Last updated

## 1. Context
Spatial reasoning and containment relationships are essential for Home Assistant registry rehydration, automation, and entity logic. This ADR formalizes the canonical area, room, and floor hierarchy, including containment, propagation, and output contract rules.

## 2. Decision
### Contract Metadata
- **Contract ID:** area_relationships_contract
- **Version:** 1.0
- **Author:** Evert
- **Status:** canonical_draft
- **File Path:** canonical/support/contracts/area_hierarchy.yaml
- **Live Registry Consistency:** partial
- **Coverage Percent:** 100.0
- **Notes:** Programmatically validated against live Home Assistant registry data. Coverage and consistency updated on each validation run.

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

## 3. Enforcement
- All subarea relationships must be explicitly declared to avoid inference ambiguity.
- Changes to inference propagation require a new contract version.
- This contract does not govern device placement, but entity logic implication.

## 4. Tokens
- `containment_graph`, `nodes`, `propagation_rules`, `output_contract`, `contract_metadata`
- `area_id`, `parent_room`, `floor_id`, `type`, `inference_weight`, `contributes_to`, `inferred_by`

---
_Last updated: 2025-09-11_
