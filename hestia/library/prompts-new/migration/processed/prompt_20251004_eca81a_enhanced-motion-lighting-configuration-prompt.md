---
id: prompt_20251004_eca81a
slug: enhanced-motion-lighting-configuration-prompt
title: Enhanced Motion-Lighting Configuration Prompt
date: '2025-10-04'
tier: "\u03B1"
domain: governance
persona: promachos
status: deprecated
tags: []
version: '1.0'
source_path: ha-config/enhanced-lighting-prompt.md
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.295069'
redaction_log: []
---

# Enhanced Motion-Lighting Configuration Prompt

> **⚠️ DEPRECATED:** This prompt has been migrated to structured promptset format.  
> **New Location:** `enhanced-motion-lighting-config.promptset`  
> **Migration Date:** 2025-10-04  
> 
> The new promptset provides:
> - Multi-phase workflow (validation → generation → analysis)
> - Structured artifact bindings and protocols
> - Enhanced governance and compliance checking
> - Improved extensibility and documentation
>
> Use the promptset version for all new implementations.

---

## Context & Prerequisites (Legacy Content)
I'm working with a comprehensive Home Assistant setup that includes motion-lighting blueprints, device configurations, and area hierarchy documentation. I need to implement area-specific lighting automation that respects spatial relationships and occupancy patterns.

**Attached Resources:**
- Complete blueprint collection (`hestia/library/blueprints/`)
- Device configuration files (`presence.conf`, `motion.conf`, `lighting.conf`, `illuminance.conf`)
- Area hierarchy contract (`area_hierarchy.yaml` v1.1 with registry alignment)
- Room registry with sensor mappings (`room_registry.yaml`)
- Motion timeout configuration matrix (`motion_timeout.conf`)
- ADR documentation (ADR-0021 motion/occupancy/presence signals)

## Primary Objective
Create a working, validated, and intuitive lighting configuration for three key area groups with hierarchical behavior:

### Target Areas:
1. **Sanctum Complex** (upstairs private space)
   - `sanctum` (container)
   - `bedroom` (main area) → `desk`, `wardrobe`, `ottoman`, `hifi_configuration` (subareas)
   - `ensuite` (connected area)

2. **Kitchen Complex** (downstairs utility)
   - `kitchen` (main area)
   - `laundry_room` (connected utility space)

3. **Hallway System** (circulation spaces)
   - `hallway_downstairs` (main circulation)
   - `entrance` (motion proxy only - no direct lighting)
   - `upstairs` (upper circulation)

## Specific Requirements

### Area-Specific Behaviors (Please Validate Assumptions)
- **Desk subarea:** Extended timeout for work sessions, presence-enhanced brightness, independence from bedroom main lighting
- **Wardrobe subarea:** Brief interaction lighting, automatic off after clothing selection
- **Kitchen:** Cooking-mode context awareness, counter vs ambient lighting zones
- **Ensuite:** Privacy-aware timing, shower occupancy detection integration
- **Hallways:** Motion-triggered transit lighting with area-to-area propagation logic

### Hierarchical Constraints
- **Floor → Area → Subarea** inheritance with override capability
- **Presence enhancement** for tracked person (person.evert) without blocking untracked housemate
- **Propagation rules** following area_hierarchy.yaml contract (decay_rate: 0.7)
- **Timeout profiles** per motion_timeout.conf matrix

### Technical Specifications
- Use existing blueprint patterns from `hestia/library/blueprints/`
- Integrate with `binary_sensor.*_motion_*` and `binary_sensor.*_occupancy_*` entities
- Respect illuminance thresholds from `sensor.*_illuminance_*`
- Follow ADR-0021 signal standardization (alpha→beta→eta progression)

## Deliverables Requested

### 1. Entity Inventory Validation
Please confirm all required entities exist and are correctly mapped:
- Motion sensors per area (from motion.conf)
- Light entities and groups (from lighting.conf)  
- Illuminance sensors (from illuminance.conf)
- Presence sensors (from presence.conf integration)

### 2. Blueprint Configuration Files
Generate working YAML configurations using appropriate blueprints:
- Area-specific parameter tuning
- Hierarchical behavior implementation
- Context-aware timeout application

### 3. Critical Analysis
**Areas of Opportunity:**
- Identify automation gaps or optimization potential
- Suggest improvements to existing blueprint patterns
- Highlight entity relationship improvements

**Uncertainty/Machine-Friendliness Issues:**
- Flag ambiguous sensor mappings or missing entities
- Identify complex logic that needs template sensors
- Point out blueprint limitations requiring custom automation

### 4. Validation Checklist
- [ ] All target areas have complete sensor coverage
- [ ] Hierarchical relationships properly implemented
- [ ] Presence enhancement works without blocking untracked housemate
- [ ] Timeout profiles match expected usage patterns
- [ ] Blueprint parameters align with ADR-0021 standards

## Constraints & Context

### Household Policy
- **Single tracked person** (person.evert) + **untracked housemate**
- **Asymmetric presence policy:** Presence enhances, absence never blocks
- **Motion must activate independently** for untracked occupant scenarios

### Technical Architecture
- **ADR compliance:** Follow ADR-0021 motion/occupancy/presence signal standards
- **Tier progression:** Use alpha (raw) → beta (processed) → eta (aggregated) sensor hierarchy
- **Area hierarchy:** Respect containment relationships and propagation rules from area_hierarchy.yaml

## Questions for Validation
1. Do the assumed area-specific behaviors match your actual usage patterns?
2. Are there additional context sensors (time of day, activity modes) to consider?
3. Should any areas have manual override capabilities or scheduling exceptions?
4. Are there specific brightness or color temperature preferences per area?
5. Do the timeout profiles in motion_timeout.conf align with your experience?

Please proceed with the entity validation first, then move to blueprint configuration generation with critical analysis throughout.
