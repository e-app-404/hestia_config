---
title: "MQTT Discovery Error Patch Plan - Bedroom HDMI Matrix"
date: 2025-09-30
author: "GitHub Copilot"
status: "Ready for Implementation"
severity: "Warning - Non-blocking"
tags: ["mqtt", "discovery", "patch", "bedroom", "matrix"]
error_code: "extra keys not allowed @ data['~']"
source_file: "packages/package_universal_media.yaml"
automation_id: "bedroom_matrix_discovery_once_20250910_a"
---

# 🔧 Bedroom HDMI Matrix MQTT Discovery Patch Plan

## 📊 Error Analysis

### **Root Cause**
Home Assistant's MQTT discovery schema validation **does not support topic abbreviation (`~`) in device-based discovery payloads**. The current implementation uses the `~` key to define a base topic path that gets expanded in component definitions.

### **Error Details**
```
2025-09-30 11:32:46.986 WARNING [homeassistant.components.mqtt.discovery] 
Invalid MQTT device discovery payload for bedroom_hdmi_matrix, 
extra keys not allowed @ data['~']: '{"cmps": {...}, "~": "ha/bedroom_hdmi_matrix"}'
```

### **Impact Assessment**
- **Severity:** ⚠️ Warning (Non-blocking)
- **Current Status:** Discovery payload is **rejected** but automation continues running
- **Functionality:** Matrix controls are **not available** in Home Assistant UI
- **Frequency:** Occurs on **every Home Assistant restart**

## 🛠️ Patch Implementation Plan

### **Step 1: Remove Topic Abbreviation**
**Target:** Lines 833-840 in `/packages/package_universal_media.yaml`

**Current (problematic):**
```yaml
"~":"ha/bedroom_hdmi_matrix",
"cmps": {
  "power":{"command_topic":"~/cmd","availability_topic":"~/status",...}
}
```

**Fixed (compliant):**
```yaml
"cmps": {
  "power":{"command_topic":"ha/bedroom_hdmi_matrix/cmd","availability_topic":"ha/bedroom_hdmi_matrix/status",...}
}
```

### **Step 2: Update All Component Topics**
Replace all `~/` references with full topic paths `ha/bedroom_hdmi_matrix/`:

**Components to update:**
- `power`, `arc`, `a_1`, `a_2`, `a_3`, `a_4`, `b_1`, `b_2`, `b_3`, `b_4`
- Each has: `command_topic: "~/cmd"` → `"ha/bedroom_hdmi_matrix/cmd"`
- Each has: `availability_topic: "~/status"` → `"ha/bedroom_hdmi_matrix/status"`

### **Step 3: Validation Strategy**
1. **Pre-deployment:** Validate JSON schema with Home Assistant discovery docs
2. **Test payload:** Use MQTT publish tool to verify payload acceptance
3. **Post-deployment:** Monitor logs for discovery success confirmation

## 📝 Exact Code Changes

### **File:** `/Users/evertappels/hass/packages/package_universal_media.yaml`

**Replace entire payload section (lines ~832-845):**

```yaml
payload: >-
  {{ {
    "device": {"identifiers":["bedroom_hdmi_matrix"],"name":"Bedroom HDMI Matrix","manufacturer":"Virtual","model":"IR HDMI Matrix","suggested_area":"bedroom"},
    "o": {"name":"matrix-virtual","sw":"1.1.0","url":"homeassistant://settings"},
    "cmps": {
      "power":{"p":"button","unique_id":"bedroom_hdmi_matrix_power","object_id":"bedroom_matrix_power","name":"Power","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"power","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "arc":{"p":"button","unique_id":"bedroom_hdmi_matrix_arc","object_id":"bedroom_matrix_arc","name":"ARC","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"arc","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "a_1":{"p":"button","unique_id":"bedroom_hdmi_matrix_a_1","object_id":"bedroom_matrix_a1","name":"A • 1 (Apple TV)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"a_1","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "a_2":{"p":"button","unique_id":"bedroom_hdmi_matrix_a_2","object_id":"bedroom_matrix_a2","name":"A • 2 (Switch)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"a_2","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "a_3":{"p":"button","unique_id":"bedroom_hdmi_matrix_a_3","object_id":"bedroom_matrix_a3","name":"A • 3 (PS4)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"a_3","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "a_4":{"p":"button","unique_id":"bedroom_hdmi_matrix_a_4","object_id":"bedroom_matrix_a4","name":"A • 4 (Wii)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"a_4","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "b_1":{"p":"button","unique_id":"bedroom_hdmi_matrix_b_1","object_id":"bedroom_matrix_b1","name":"B • 1 (Apple TV)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"b_1","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "b_2":{"p":"button","unique_id":"bedroom_hdmi_matrix_b_2","object_id":"bedroom_matrix_b2","name":"B • 2 (Switch)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"b_2","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "b_3":{"p":"button","unique_id":"bedroom_hdmi_matrix_b_3","object_id":"bedroom_matrix_b3","name":"B • 3 (PS4)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"b_3","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false},
      "b_4":{"p":"button","unique_id":"bedroom_hdmi_matrix_b_4","object_id":"bedroom_matrix_b4","name":"B • 4 (Wii)","command_topic":"ha/bedroom_hdmi_matrix/cmd","payload_press":"b_4","availability_topic":"ha/bedroom_hdmi_matrix/status","qos":1,"retain":false}
    }
  } | tojson }}
```

## 🧪 Testing Protocol

### **Immediate Verification**
1. **Restart Home Assistant** to trigger discovery automation
2. **Check logs** for absence of `bedroom_hdmi_matrix` warnings
3. **Verify devices** appear in Settings → Devices & Services → MQTT
4. **Test functionality** by pressing matrix buttons in UI

### **MQTT Broker Verification**
```bash
# Subscribe to discovery messages
mosquitto_sub -h 192.168.0.129 -p 1883 -u mqtt_user -P mqtt_pass \
-t "homeassistant/device/bedroom_hdmi_matrix/config" -v

# Subscribe to command topic
mosquitto_sub -h 192.168.0.129 -p 1883 -u mqtt_user -P mqtt_pass \
-t "ha/bedroom_hdmi_matrix/cmd" -v
```

### **Success Criteria**
- ✅ No MQTT discovery warnings in logs
- ✅ Device "Bedroom HDMI Matrix" appears with 10 button entities
- ✅ Button presses publish to `ha/bedroom_hdmi_matrix/cmd`
- ✅ Automation ID `bedroom_matrix_discovery_once_20250910_a` completes successfully

## 📋 Implementation Checklist

- [ ] **Backup current configuration** (automated via git)
- [ ] **Apply code changes** to remove `~` abbreviation
- [ ] **Restart Home Assistant** to trigger discovery
- [ ] **Verify log output** shows no discovery errors
- [ ] **Test entity functionality** in UI
- [ ] **Monitor MQTT topics** for proper message flow
- [ ] **Document resolution** in ADR or changelog

## 🔄 Rollback Plan

If issues occur:
1. **Git revert** the payload changes
2. **Restart Home Assistant** to restore previous state
3. **Clear retained discovery message** if needed:
   ```bash
   mosquitto_pub -h 192.168.0.129 -p 1883 -u mqtt_user -P mqtt_pass \
   -t "homeassistant/device/bedroom_hdmi_matrix/config" -r -m ""
   ```

## 📖 References

- **Home Assistant MQTT Discovery Docs:** [Device Discovery Format](https://www.home-assistant.io/integrations/mqtt/#discovery-messages)
- **Topic Abbreviation Support:** Not supported in device-based discovery (component discovery only)
- **Workspace Playbook:** `/hestia/library/docs/playbooks/ha_mqtt_discovery.md`

---

**Implementation Priority:** 🟡 Medium (Warning resolution, improves functionality)  
**Estimated Time:** 5 minutes (config change + restart)  
**Risk Level:** 🟢 Low (rollback available, non-breaking change)