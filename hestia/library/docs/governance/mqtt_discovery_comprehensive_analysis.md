---
title: "MQTT Discovery Information Analysis"
date: 2025-09-30
author: "GitHub Copilot"
status: "Analysis Complete"
tags: ["mqtt", "discovery", "analysis", "governance", "documentation"]
scope: "comprehensive workspace analysis"
---

# MQTT Discovery — Comprehensive Workspace Analysis

## Executive Summary

Your workspace contains extensive MQTT discovery information across multiple categories:
- **Implementation guides** and practical playbooks
- **Active discovery configurations** for devices like BB-8 and HDMI matrix
- **Integration documentation** from Home Assistant
- **Real-time discovery errors** in current logs
- **BB-8 add-on discovery architecture** documentation

## 1. Core Documentation & Guides

### Primary Playbook
**Location:** `/Users/evertappels/hass/hestia/library/docs/playbooks/ha_mqtt_discovery.md`

**Key Content:**
- Comprehensive practical guide for MQTT discovery implementation
- Covers both **device-based discovery** (modern, single payload) and **per-component discovery** (legacy, multiple payloads)
- Prerequisites: MQTT integration, discovery enabled, Mosquitto broker
- Examples for creating devices with multiple button entities
- Integration with Broadlink IR for action wiring

### Official Integration Documentation
**Location:** `/Users/evertappels/hass/hestia/workspace/operations/guides/ha_implementation/integration_mqtt.md`

**Key Topics:**
- MQTT broker setup and configuration
- Discovery options and birth/will messages
- Discovery topic formats: `<discovery_prefix>/<component>/<object_id>/config`
- Device-based vs component-based discovery
- Migration procedures between discovery methods
- Discovery payload validation and debugging

## 2. Active Configurations

### Bedroom HDMI Matrix Discovery
**Location:** `/Users/evertappels/hass/packages/package_universal_media.yaml`

**Implementation:**
- **Automation ID:** `bedroom_matrix_discovery_once_20250910_a`
- **Trigger:** Home Assistant start event
- **Discovery Topic:** `homeassistant/device/bedroom_hdmi_matrix/config`
- **Device Type:** Virtual IR HDMI Matrix with 10 button entities
- **Features:** Uses topic abbreviation (`~`) and component mapping (`cmps`)

**Current Issue:** 
```
Invalid MQTT device discovery payload for bedroom_hdmi_matrix, extra keys not allowed @ data['~']
```
**Problem:** Home Assistant doesn't accept the `~` (topic abbreviation) key in device-based discovery

### Discovery JSON Template
**Location:** `/Users/evertappels/hass/hestia/library/docs/playbooks/bedroom_hdmi_matrix.discovery.json`

**Structure:**
- Proper device identification with `identifiers`
- Origin information
- 10 button components (A1-A4, B1-B4, Power, ARC)
- Proper device class assignments and icons

### MQTT Native Sensor Integration
**Location:** `/Users/evertappels/hass/domain/templates/mqtt_native.yaml`

**Implementation:**
- Real-time motion sensor using MQTT trigger
- Topic: `zigbee2mqtt/ensuite_motion_alpha`
- Tier: α (alpha - raw sensor data)
- Auto-off functionality with 2-second timeout

## 3. BB-8 Add-on Discovery Architecture

### Documentation Locations
- `/Users/evertappels/Projects/HA-BB8/docs/ADR/ADR-0032-mqtt-ble-integration-architecture.md`
- `/Users/evertappels/Projects/HA-BB8/docs/ADR/ADR-0020-motion-safety-and-mqtt-contract.md`

### Discovery Features
- **Topic Schema:** Configurable base prefix with override support
- **Entity Types:** Buttons (sleep, drive), Numbers (heading, speed)
- **MQTT Configuration:**
  ```yaml
  mqtt_host: 192.168.0.129
  mqtt_port: 1883
  mqtt_user: mqtt_bb8
  mqtt_password: mqtt_bb8
  ```

### Current Discovery Errors
**From logs (2025-09-30 11:32:45):**
```
Error 'Device must have at least one identifying value in 'identifiers' and/or 'connections'
```
**Affected Entities:**
- `bb8_sleep` button
- `bb8_drive` button  
- `bb8_heading` number
- `bb8_speed` number

**Problem:** Empty device block `'device': {}` missing required identifiers

## 4. Discovery Patterns & Best Practices

### Topic Structure
- **Device Discovery:** `homeassistant/device/<object_id>/config`
- **Component Discovery:** `homeassistant/<component>/<object_id>/config`
- **Default Prefix:** `homeassistant` (configurable)

### Required Fields
**Device-based discovery:**
- `device` block with `identifiers` or `connections`
- `origin` block (recommended)
- `cmps` (components) map with platform (`p`) specification

**Component-based discovery:**
- `unique_id` (required)
- Platform-specific fields (e.g., `command_topic`, `state_topic`)
- Optional `device` context

### Message Properties
- **QoS:** 1 (recommended for discovery)
- **Retain:** `true` (required for discovery persistence)
- **Payload:** JSON with proper schema validation

## 5. Common Issues & Resolutions

### Issue 1: Topic Abbreviation Not Supported
**Error:** `extra keys not allowed @ data['~']`
**Solution:** Remove topic abbreviation from device discovery; use full topics

### Issue 2: Missing Device Identifiers  
**Error:** `Device must have at least one identifying value in 'identifiers'`
**Solution:** Add device block with identifiers:
```json
"device": {
  "identifiers": ["device_unique_id"],
  "name": "Device Name"
}
```

### Issue 3: Discovery Payload Validation
**Common causes:**
- Invalid JSON structure
- Missing required fields
- Incorrect platform (`p`) specification
- Malformed topic names

## 6. Integration Architecture

### MQTT Broker Configuration
- **Host:** 192.168.0.129 (internal network)
- **Port:** 1883 (non-TLS)
- **Authentication:** User-specific credentials (mqtt_bb8, etc.)
- **Add-on:** Official Mosquitto broker recommended

### Discovery Flow
1. **Birth Message:** Home Assistant publishes `homeassistant/status` → `online`
2. **Device Response:** Devices subscribe to birth message and publish discovery
3. **Entity Creation:** Home Assistant processes discovery payloads
4. **State Updates:** Devices publish to state topics
5. **Commands:** Home Assistant publishes to command topics

### Migration Strategy
- **Legacy → Device Discovery:** Use `migrate_discovery: true` payload
- **Cleanup:** Publish empty payloads to remove old configurations
- **Validation:** Monitor logs for successful migration

## 7. Tools & Utilities

### Testing Commands
```bash
# Subscribe to discovery messages
mosquitto_sub -h 192.168.0.129 -p 1883 -u mqtt_bb8 -P mqtt_bb8 -t "homeassistant/+/+/config" -v

# Publish discovery payload
mosquitto_pub -h 192.168.0.129 -p 1883 -u mqtt_bb8 -P mqtt_bb8 -t "homeassistant/device/test/config" -m '{"device":{"identifiers":["test"],"name":"Test Device"}}'

# Clean up discovery
mosquitto_pub -h 192.168.0.129 -p 1883 -u mqtt_bb8 -P mqtt_bb8 -t "homeassistant/device/test/config" -m '' -r
```

### Home Assistant Tools
- **MQTT Integration UI:** Settings → Devices & Services → MQTT → Configure
- **Publish/Subscribe:** MQTT → Configure → Publish a packet / Listen to a topic
- **Discovery Options:** Configure MQTT Options → Discovery settings

## 8. Recommendations

### Immediate Actions
1. **Fix BB-8 Discovery:** Add proper device identifiers to resolve current errors
2. **Fix Matrix Discovery:** Remove unsupported `~` key from device payload
3. **Validate Payloads:** Use JSON schema validation before publishing

### Strategic Improvements
1. **Standardize Discovery:** Migrate all devices to device-based discovery for consistency
2. **Implement Birth Listener:** Add birth message subscription for reliable discovery
3. **Add Discovery Validation:** Create CI validation for discovery payload schemas
4. **Document Device Registry:** Maintain canonical device definitions per ADR patterns

### Monitoring & Maintenance
1. **Log Monitoring:** Regular review of MQTT discovery errors
2. **Topic Management:** Clean up orphaned discovery topics
3. **Schema Evolution:** Plan for Home Assistant discovery schema changes

---

## File Inventory

### Active Configuration Files
- `packages/package_universal_media.yaml` - Bedroom matrix discovery automation
- `domain/templates/mqtt_native.yaml` - MQTT-triggered template sensors
- `packages/integrations/mqtt.yaml` - MQTT integration configuration (legacy format)

### Documentation Files  
- `hestia/library/docs/playbooks/ha_mqtt_discovery.md` - Primary implementation guide
- `hestia/workspace/operations/guides/ha_implementation/integration_mqtt.md` - Official HA documentation
- `hestia/library/docs/playbooks/bedroom_hdmi_matrix.discovery.json` - Discovery payload template

### Related Projects
- HA-BB8 addon discovery architecture (separate repository)
- PS5-MQTT credentials configuration
- Zigbee2MQTT integration patterns

---

**Analysis completed:** 2025-09-30  
**Last log review:** home-assistant.log (current session)  
**Discovery errors identified:** 4 active BB-8 entity errors, 1 matrix payload warning