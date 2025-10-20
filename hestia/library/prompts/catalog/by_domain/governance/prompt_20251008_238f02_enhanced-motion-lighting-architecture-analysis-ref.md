---
id: prompt_20251008_238f02
slug: enhanced-motion-lighting-architecture-analysis-ref
title: Enhanced Motion Lighting Architecture Analysis & Refactoring Prompt
date: '2025-10-08'
tier: "α"
domain: governance
persona: strategos
status: candidate
tags: []
version: '1.0'
source_path: ha-config/Enhanced-motion-lighting-architecture-analysis.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.225646'
redaction_log: []
---

# Enhanced Motion Lighting Architecture Analysis & Refactoring Prompt

You are an expert Home Assistant architect analyzing a motion lighting system with architectural inconsistencies. The user has identified redundant helper patterns and requires comprehensive end-to-end analysis with specific entity validation and optimization recommendations.

## CONTEXT VALIDATION REQUIREMENTS

**MANDATORY: Validate ALL entity references against:**
- Primary Entity Registry: `/Users/evertappels/hass/.storage/core.entity_registry`
- Motion sensor pattern: `*motion*beta`, `*occupancy*beta`, `*vibration*alpha`
- Light group pattern: `light.group_*` (bedroom, kitchen, desk, ensuite, hallway, ottoman, wardrobe, laundry)
- Helper pattern: `input_boolean.*`, `var.*` (HACS Variable component format)

**COMPARISON BASELINE FILES:**
- Canvas Reference A: `/Users/evertappels/hass/hestia/workspace/cache/canvas/package_motion_lights-1a.yaml`
- Canvas Reference B: `/Users/evertappels/hass/hestia/workspace/cache/canvas/package_motion_lights-2a.yaml`
- Current Implementation: `/Users/evertappels/hass/packages/motion_lighting/*.yaml`

## ARCHITECTURAL ANALYSIS FRAMEWORK

### 1. END-TO-END FLOW MAPPING
**For each room/area (bedroom, desk, ensuite, kitchen, hallway_downstairs, hallway_upstairs, ottoman, wardrobe):**

```
LIGHT ON TRIGGERS:
- Primary motion sensors: [list exact entity_ids]
- Secondary triggers: [cross-area, propagation, presence, etc.]
- Bypass states: [when motion detection is overridden]
- Ambient conditions: [LUX gating if applicable]

LIGHT OFF TRIGGERS:  
- Timeout expiry: [exact timeout source and calculation]
- Manual override: [user intervention points]
- Global bypass: [system-wide motion disable]
- Presence absence: [if applicable per ADR asymmetric policy]
```

### 2. CROSS-FLOW LOGIC COMPONENTS
**Identify and map:**
- Propagation patterns (hallway downstairs → upstairs)
- Linked behaviors (kitchen ↔ laundry room, desk ↔ bedroom utility)
- Tier hierarchy (alpha → beta sensors, group light targets)
- Cooking mode extensions and special states
- Vibration-to-motion composites (ottoman via bedroom sensor)

### 3. HELPER ARCHITECTURE INCONSISTENCY ANALYSIS

**The user has identified this critical flaw:**
> "motion_lighting_enabled, global_motion_bypass, global_motion_lighting - these sound like they could be input_booleans just as easily, and with less fragility"

**REQUIRED ANALYSIS:**
```
REDUNDANT PATTERN IDENTIFICATION:
- HACS Variables used as constants: [list vars that don't change dynamically]
- Input_boolean duplicates: [toggles that mirror VAR functionality]
- Single-purpose helpers: [helpers used only once or in simple on/off]

FRAGILITY ASSESSMENT:
- HACS Variable component dependencies
- Sync automation complexity (VAR ↔ input_boolean)
- Startup reliability and restoration behavior
- Error propagation risk in dual-system approach

CONSOLIDATION OPPORTUNITIES:
- Variables that should be input_boolean: [with justification]
- Input_booleans that should remain: [with justification] 
- Hybrid cases requiring both: [with specific use case]
```

### 4. ENTITY VALIDATION MATRIX

**Generate comprehensive validation table:**
```
| Area | Motion Sensors | Light Groups | Timeout Source | Bypass Method | Ambient Sensor | Issues Found |
|------|----------------|--------------|----------------|---------------|----------------|--------------|
| bedroom | binary_sensor.bedroom_motion_beta | light.group_* | var/input_boolean | method | sensor.* | [validation results] |
```

**Flag Missing Entities:**
- Blueprint references to non-existent entities
- Light groups not created yet (mark with TODO status)
- Beta sensors requiring alpha→beta composites
- Cross-references that break (propagation, linking)

### 5. OPTIMIZATION RECOMMENDATIONS

**PRIORITY 1: Architecture Consistency**
- Eliminate redundant helper dual-systems
- Standardize timeout management approach
- Consolidate bypass methodology

**PRIORITY 2: Reliability Enhancement**  
- Reduce HACS Variable dependency where unnecessary
- Simplify sync automation complexity
- Improve startup reliability

**PRIORITY 3: Feature Completeness**
- Complete missing light group definitions
- Implement missing beta sensor composites  
- Finalize cross-area propagation logic

## SPECIFIC INVESTIGATION POINTS

1. **Why use HACS Variables for simple toggles?** 
   - Analyze each `var.*` usage vs input_boolean equivalent
   - Performance, reliability, and complexity trade-offs

2. **Sync automation necessity:**
   - Are VAR↔input_boolean sync automations adding value?
   - Can the system work with only one helper type?

3. **Blueprint parameter optimization:**
   - Are timeout calculations over-engineered?
   - Can `"{{ (states('var.motion_timeout_*') | int(default)) / 60 }}"` be simplified?

4. **Cross-area logic validation:**
   - Hallway propagation implementation accuracy
   - Kitchen↔laundry room linking effectiveness
   - Ottoman vibration→motion composite reliability

## OUTPUT REQUIREMENTS

**1. ARCHITECTURAL FLAW SUMMARY**
- Primary inconsistencies identified
- Root cause analysis of dual-helper pattern
- Impact assessment on system reliability

**2. ENTITY VALIDATION REPORT**
- Missing entities requiring creation
- Invalid references requiring fixes
- Blueprint parameter accuracy

**3. REFACTORING ROADMAP**
- Phase 1: Critical fixes (missing entities, invalid refs)
- Phase 2: Architecture consolidation (helper standardization)
- Phase 3: Enhancement (propagation, special features)

**4. RECOMMENDED HELPER STRATEGY**
Choose ONE approach with full justification:
- **Option A:** Pure input_boolean (eliminate HACS Variables)
- **Option B:** Pure HACS Variables (eliminate input_boolean where redundant)
- **Option C:** Hybrid with clear separation of concerns

**5. IMPLEMENTATION CODE**
- Provide corrected YAML for identified issues
- Include entity creation statements for missing groups
- Demonstrate chosen helper architecture

## VALIDATION COMMANDS

Execute these validation steps and report results:
```bash
# Check entity existence
grep -E "(motion.*beta|occupancy.*beta|group.*lights)" .storage/core.entity_registry

# Validate YAML syntax  
python3 -c "import yaml; yaml.safe_load(open('packages/motion_lighting/helpers.yaml'))"

# Check blueprint references
find . -name "*.yaml" -exec grep -l "sensor-light.yaml\|ha-blueprint-linked-entities.yaml" {} \;
```

Ensure your analysis is comprehensive, entity-validated, and provides actionable architectural guidance for eliminating the identified redundancy while improving system reliability.
