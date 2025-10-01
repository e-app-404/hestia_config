# Helper Registries & Entity Comparison Analysis
**Analysis Date:** 2025-10-01  
**Status:** 🔍 HELPER REGISTRY DEGRADATION ANALYSIS  
**Comparison:** Backup f050d566 vs Live System  

## Executive Summary
Analysis of helper registries (input_*, counter), person, and zones reveals **significant data loss and functionality reduction** in the current live system compared to the backup. The live system appears to be operating with **minimal helper entities** and **reduced automation infrastructure**.

---

## 📊 **INPUT_SELECT Registry Comparison**

### **🎯 CRITICAL FINDING: Massive Input Select Loss**

| Registry | Backup Count | Live Count | Loss | Status |
|----------|-------------|------------|------|--------|
| **input_select items** | **13 items** | **2 items** | **-11 items (85% LOSS)** | 🚨 CRITICAL |

### **Lost Input Select Entities (11 entities)**

#### **🎬 Media Control Entities (6 lost)**
1. **plex_show** - "Plex – Show" (mdi:television-box) ❌ LOST
2. **plex_movie** - "Plex – Movie" (mdi:movie) ❌ LOST  
3. **plex_library** - "plex_library" (mdi:plex) ❌ LOST
4. **ps4_recent_game_2** - "ps4_recent_game" (mdi:format-list-bulleted) ❌ LOST
5. **tv_source_list** - "bedroom_universal_source" (mdi:remote-tv) ❌ LOST
6. **camera_privacy_mode** - "camera_privacy_mode" (mdi:cctv) ❌ LOST

#### **🎵 Audio/HiFi Control Entities (4 lost)**  
7. **bedroom_matrix_video_source** - "bedroom_matrix_video_source" (mdi:video-input-hdmi) ❌ LOST
8. **bedroom_matrix_audio_source** - "bedroom_matrix_audio_source" (mdi:video-input-hdmi) ❌ LOST
9. **bedroom_matrix_mode** - "bedroom_matrix_mode" (mdi:video-input-hdmi) ❌ LOST
10. **radio_station** - "radio_station" (mdi:radio) ❌ LOST
11. **radio_player** - "radio_player" (mdi:radio) ❌ LOST

### **Surviving Input Select Entities (2 remaining)**
✅ **sonos_alarm_recurrence** - Alarm recurrence settings (✅ PRESERVED)  
✅ **sonos_alarm_zone** - SONOS zone selection (✅ PRESERVED)

### **🎯 Sonos Alarm Analysis**  
**CRITICAL**: The Sonos alarm entities **ARE PRESENT** in the live system:
- ✅ `sonos_alarm_recurrence` exists in live system
- ✅ `sonos_alarm_zone` exists in live system  
- ❌ **MISSING**: `input_select.alarm_time_bedroom` (the entity mentioned in original issue)

**Root Cause**: The missing `input_select.alarm_time_bedroom` entity is **NOT PRESENT in backup either**. This suggests:
1. **Entity was created after backup date**  
2. **Entity was custom/manually created and lost during system degradation**
3. **Entity belongs to a different helper type** (input_datetime, input_number, or input_text)

---

## 📊 **INPUT_DATETIME Registry Comparison**

### **Dramatic DateTime Helper Loss**

| Registry | Backup Count | Live Count | Loss | Status |
|----------|-------------|------------|------|--------|
| **input_datetime items** | **8 items** | **1 item** | **-7 items (88% LOSS)** | 🚨 CRITICAL |

### **Lost DateTime Entities (7 entities)**
1. **last_presence_mode_change** - Presence tracking timestamp ❌ LOST
2. **last_error_time** - Error logging timestamp ❌ LOST  
3. **last_error_timestamp** - Alternative error timestamp ❌ LOST
4. **charon_last_run_timestamp** - System process timestamp ❌ LOST
5. **last_run_publish_all_registries** - Registry publishing timestamp ❌ LOST
6. **bedroom_matrix_last_updated** - HiFi matrix update timestamp ❌ LOST
7. **fridge_last_alert** - Appliance alert timestamp ❌ LOST

### **Surviving DateTime Entity (1 remaining)**
✅ **last_ha_restart** - HA restart timestamp (✅ PRESERVED)

---

## 📊 **COUNTER Registry Comparison**

### **Counter Entity Modifications**

| Registry | Backup Count | Live Count | Change | Status |
|----------|-------------|------------|--------|--------|
| **counter items** | **5 items** | **6 items** | **+1 item** | 🟡 MODIFIED |

### **Counter Changes Analysis**

#### **Modified Counters**
| Counter ID | Backup Max | Live Max | Icon Change | Status |
|------------|------------|----------|-------------|---------|
| **homeassistant_errors** | 999 | 100 | No change | 🔄 Range reduced |
| **homeassistant_warnings** | 999 | 100 | No change | 🔄 Range reduced |
| **log_error_count** | 100 | 255 | No change | 🔄 Range increased |
| **log_error_counter** | null (unlimited) | 255 | No change | 🔄 Range limited |
| **failed_service_calls** | 1000 | 255 | mdi:room-service → mdi:counter | 🔄 Modified |

#### **New Counter**  
✅ **homeassistant_warnings_2** - Duplicate warning counter (**NEW** in live)

### **Counter Analysis**
- **Range modifications**: Most counters have reduced maximum values (999→100)
- **Icon changes**: `failed_service_calls` lost specific icon (mdi:room-service → mdi:counter)
- **Duplicate entity**: `homeassistant_warnings_2` suggests configuration issues

---

## 📊 **PERSON Registry Comparison**

### **Person Configuration Changes**

| Aspect | Backup | Live | Status |
|--------|--------|------|--------|
| **Person count** | 1 person | 1 person | ✅ Same |
| **Person name** | "Evert" | "Evert" | ✅ Same |
| **User ID** | 6acd54c...d6e603c | 36e0f8...148bf567 | 🔄 **DIFFERENT USER ID** |
| **Picture** | null | /api/image/serve/... | ➕ **Profile picture added** |

### **Device Tracker Changes**
| Backup Device Trackers | Live Device Trackers | Status |
|------------------------|---------------------|---------|
| device_tracker.ephone_uk | device_tracker.ephone | 🔄 Name changed |
| device_tracker.iphone11_2 | device_tracker.ephone_uk | 🔄 Still present |
| device_tracker.epad | device_tracker.backpack | 🔄 Name changed |
| device_tracker.macbook | device_tracker.wallet | ➕ New tracker |
| (none) | device_tracker.keys | ➕ New tracker |
| (none) | device_tracker.macbook | ✅ Still present |

**Analysis**: Person entity shows **active development** with more device trackers and profile picture added.

---

## 📊 **ZONE Registry Comparison**

### **🚨 COMPLETE ZONE REGISTRY LOSS**

| Registry | Backup Count | Live Count | Loss | Status |
|----------|-------------|------------|------|--------|
| **Zone entities** | **5 zones** | **0 zones** | **-5 zones (100% LOSS)** | 🚨 COMPLETE LOSS |

### **Lost Zone Entities (5 zones)**
1. **sis** - "Sis" (51.13°N, 4.38°E, radius: 583m) ❌ LOST
2. **london** - "London" (51.45°N, -0.14°W, radius: 29.5km) ❌ LOST
3. **antwerp** - "Antwerp" (51.20°N, 4.33°E, radius: 37.1km) ❌ LOST  
4. **belgium** - "Belgium" (50.86°N, 4.09°E, radius: 91.4km) ❌ LOST
5. **clapham_north** - "Clapham North" (51.47°N, -0.13°W, radius: 72m) ❌ LOST

### **Zone Loss Impact**
- **Complete location tracking loss**: No geographic zones for automation  
- **Presence detection degraded**: No location-based presence automation
- **Travel automation broken**: No zone-based travel detection
- **Geographic context lost**: No location awareness for international/regional automation

---

## 📊 **MISSING HELPER REGISTRIES**

### **Completely Missing Helper Types**

| Helper Type | Backup Status | Live Status | Impact |
|-------------|---------------|-------------|---------|
| **input_boolean** | ✅ **30+ entities** | ❌ **MISSING FILE** | 🚨 COMPLETE LOSS |
| **input_number** | ✅ **38+ entities** | ❌ **MISSING FILE** | 🚨 COMPLETE LOSS |  
| **input_text** | ✅ **10 entities** | ❌ **MISSING FILE** | 🚨 COMPLETE LOSS |

### **input_boolean Loss Impact (30+ entities lost)**
**Critical automation toggles lost:**
- Presence detection controls (multi_sensor_fusion, presence_detection_enabled)
- Climate controls (climate_automation_enabled, eco_mode_enabled)  
- System controls (debug_mode_enabled, system_alert_active)
- Scene and lighting controls (scene_control, adaptive_brightness)
- Security and monitoring (security_monitoring, battery_monitoring)

### **input_number Loss Impact (38+ entities lost)**  
**Critical numeric controls lost:**
- Presence detection thresholds and weights
- Temperature control settings (bedroom_target_temperature, etc.)
- System monitoring thresholds (system_health_threshold)  
- Automation timing controls (motion_timeout, home_away_threshold)
- Lighting controls (morning_color_temp, brightness settings)

### **input_text Loss Impact (10 entities lost)**
**Critical text storage lost:**
- System state tracking (current_active_room, last_error_message)
- Registry hash tracking (omega_room_registry_hash, etc.) 
- Configuration storage (glances_credentials, plex mappings)
- System diagnostics (bedroom_matrix_last_command)

---

## 🎯 **SONOS ALARM INVESTIGATION RESULTS**

### **Key Finding: Missing Entity Not in Backup**
The original issue `input_select.alarm_time_bedroom` **is NOT present in the backup**, which suggests:

1. **Post-backup creation**: Entity was created after the f050d566 backup date
2. **Different helper type**: Entity might be `input_datetime.alarm_time_bedroom` instead
3. **Custom entity**: May have been manually created and lost during degradation

### **Sonos Alarm Infrastructure Status**
✅ **Core alarm entities present**: `sonos_alarm_recurrence`, `sonos_alarm_zone`  
❌ **Time selection missing**: No time-setting entity found
❌ **Alarm area missing**: `alarm` area not in live registry (restored in enhanced strategy)

### **Recommended Investigation**
1. **Check entity registry**: Search for any `*alarm_time*` entities in core.entity_registry
2. **Check automation configs**: Look for references to alarm_time entities in automations
3. **Verify entity type**: Confirm if it should be input_datetime, input_select, or input_number

---

## 🚨 **CRITICAL IMPACT ASSESSMENT**

### **Automation Infrastructure Loss**
| Infrastructure Type | Loss Percentage | Impact Level |
|-------------------|-----------------|--------------|
| **Zone tracking** | 100% loss | 🚨 COMPLETE |
| **Boolean toggles** | 100% loss | 🚨 COMPLETE |  
| **Number controls** | 100% loss | 🚨 COMPLETE |
| **Text storage** | 100% loss | 🚨 COMPLETE |
| **DateTime helpers** | 88% loss | 🚨 CRITICAL |
| **Select controls** | 85% loss | 🚨 CRITICAL |

### **System Functionality Impact**
- **Presence detection**: Completely broken (all controls missing)
- **Climate automation**: Completely broken (all controls missing)
- **Scene control**: Completely broken (all controls missing)  
- **Media automation**: 85% broken (most controls missing)
- **Location awareness**: Completely broken (all zones missing)
- **System monitoring**: Completely broken (all thresholds missing)

---

## 📋 **ENHANCED RECONSTRUCTION RECOMMENDATIONS**

### **Phase 1: Critical Helper Restoration**
1. **Restore missing helper files**: input_boolean, input_number, input_text from backup
2. **Restore zone registry**: All 5 geographic zones for location awareness
3. **Restore datetime helpers**: Critical system timestamps and automation timing

### **Phase 2: Sonos Alarm Resolution**  
1. **Create missing alarm_time entity**: Add `input_datetime.alarm_time_bedroom` 
2. **Assign to alarm area**: Use enhanced reconstruction's `alarm` area
3. **Test Sonos integration**: Verify alarm entities work with restored infrastructure

### **Phase 3: Automation Infrastructure**
1. **Restore presence detection**: All boolean toggles and number thresholds
2. **Restore climate controls**: Temperature targets and automation toggles
3. **Restore media automation**: Plex, matrix, and entertainment controls

## 🎯 **CONCLUSION**

The helper registry analysis reveals **catastrophic infrastructure loss** beyond the area/floor registry degradation. The live system is operating with:

- **100% loss of automation toggles** (input_boolean)
- **100% loss of numeric controls** (input_number)  
- **100% loss of text storage** (input_text)
- **100% loss of location awareness** (zones)
- **85%+ loss of selection controls** (input_select)

This explains why the system appears to be in "emergency recovery mode" - **the entire automation infrastructure has been lost**, not just the organizational structure.

**The enhanced reconstruction strategy must be expanded** to include complete helper registry restoration from the backup.

---
**Helper Analysis Status:** ✅ COMPLETE  
**Severity:** 🚨 CATASTROPHIC (85-100% helper infrastructure loss)  
**Recommendation:** 🔴 **FULL BACKUP RESTORATION REQUIRED**