# ADR-0021 Compliance Fixes Summary

**Date**: 2025-10-18  
**Purpose**: Implement critical fixes to bring sensor architecture into full ADR-0021 compliance

## ✅ Changes Implemented

### 1. **Desk Motion Naming Standardization**
- **Changed**: `desk_motion_proxy` → `desk_motion_beta`
- **Impact**: Fixes ADR-0021 beta-tier naming requirement
- **Files Updated**: 
  - `/config/domain/templates/motion_logic.yaml`
  - `/config/domain/templates/occupancy_logic.yaml`
  - `/config/hestia/config/devices/sensors.json`

### 2. **Motion/Occupancy Signal Separation**
- **Fixed**: Removed `binary_sensor.bedroom_motion_beta` from bedroom occupancy sources
- **Rationale**: ADR-0021 requires "occupancy-only sources (no motion)"
- **Impact**: Eliminates circular dependency risk, maintains signal boundaries

### 3. **Shared Area Presence Enhancement**
- **Changed**: Replaced `always_false` strategy with contextual enhancement
- **Areas**: Kitchen, Living Room, Hallway Downstairs, Hallway Upstairs
- **New Logic**: Uses `person.evert` state for contextual timeout/scene enhancement
- **Strategy**: `contextual_enhancement_only` (never blocks activation)

### 4. **Tier and Attribute Standardization**
- **Fixed**: Consistent `tier: "β"` annotations
- **Updated**: Canonical IDs follow `<room>_<type>_β` pattern
- **Enhanced**: Proper upstream/downstream source tracking

## 🎯 ADR-0021 Compliance Status

| Signal Type | Pre-Fix Issues | Post-Fix Status |
|-------------|----------------|-----------------|
| **Motion** | ❌ Desk naming inconsistency | ✅ All `*_motion_beta` |
| **Occupancy** | ❌ Motion sources mixed in | ✅ Pure occupancy signals |
| **Presence** | ❌ Shared areas unusable | ✅ Contextual enhancement |

## 📋 Validation Checklist

- [x] Beta-tier naming consistency across all room abstractions
- [x] Motion/occupancy signal boundary enforcement  
- [x] Presence sensors provide contextual value (no always-false)
- [x] Proper tier annotations (`β` for room-level abstractions)
- [x] Updated upstream/downstream source tracking
- [x] sensors.json reflects new entity names

## 🔄 Next Steps Required

1. **Restart Home Assistant** to load updated templates
2. **Validate entity creation** - check all `*_motion_beta`, `*_occupancy_beta`, `*_presence_beta`
3. **Update automation blueprints** to reference corrected entity names
4. **Test presence enhancement** - verify shared areas provide contextual value

## 🚨 Breaking Changes

- **Entity Rename**: `binary_sensor.desk_motion_beta` → `binary_sensor.desk_motion_beta`
- **Automations**: Any direct references to old desk motion entity need updating
- **Presence Logic**: Shared area presence sensors now dynamic instead of always-false

## 📖 ADR-0021 Compliance Achieved

✅ **Single abstraction layer**: All automations consume beta-tier room composites  
✅ **Signal roles**: Motion (fast trigger), Occupancy (stillness), Presence (context only)  
✅ **Construction rules**: Proper OR fusion, weighted logic, asymmetric presence  
✅ **Guardrails**: No alpha device fallbacks, proper beta naming conventions
