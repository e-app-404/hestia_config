---
id: prompt_20251001_f247b4
slug: task-transform-the-hestia-alpha-light-registry-to
title: 'Task: Transform the HESTIA Alpha Light Registry to New Schema Format'
date: '2025-10-01'
tier: "α"
domain: extraction
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: 'batch 1/batch1-# Task: Transform the HESTIA Alpha Light.md'
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.501464'
redaction_log: []
---

# Task: Transform the HESTIA Alpha Light Registry to New Schema Format

## 🎯 Objective

Restructure the existing `alpha_light_registry.json` into a new schema format aligned with HESTIA meta-standards. The transformation must retain all existing information while organizing it into a deterministic, extensible structure. Do not invent, hallucinate, or omit data.

---

## 📂 Source Artifacts

- `alpha_light_registry.json`: Device-level smart light definitions (OMEGA models)
- `alpha_light_meta.json`: Governing meta-registry schema

---

## 🧱 Target Schema Structure

The output JSON must follow this exact top-level structure:

```json
{
  "_meta": {...},
  "protocol_definitions": {...},
  "light_devices": {...},
  "room_light_mappings": {...},
  "validation_rules": [...]
}
```

---

## 📌 Conversion Instructions

### 1. `_meta` Section

Populate using source values:

- `"schema_version"`, `"last_updated"`, `"schema_notes"` from original file
- Add `validation_status` block:

```json
"validation_status": {
  "status": "pending",
  "validated_by": null,
  "timestamp": null
}
```

---

### 2. `protocol_definitions` Section

Extract all unique protocols from `integration_stack`. For each, create a definition with:

```json
"<protocol>": {
  "name": "<Formal Name>",
  "description": "<One-sentence summary>",
  "priority": <lower is higher>
}
```

Use the following canonical values:

| Protocol       | Name         | Description                                     | Priority |
|----------------|--------------|-------------------------------------------------|----------|
| matter         | Matter       | Thread-based smart home protocol               | 1        |
| wifi           | Wi-Fi        | Legacy wireless IP protocol                    | 2        |
| tuya           | Tuya Wi-Fi   | OEM Wi-Fi protocol used by Enshine             | 3        |
| smartthings    | SmartThings  | Samsung's smart home integration               | 4        |
| tplink         | TP-Link Wi-Fi| TP-Link’s direct device integration protocol   | 5        |

---

### 3. `light_devices` Section

Place each original device (e.g., `bedroom_desk_omega`) under `light_devices`.

- Keys must retain the original identifier ending in `_omega`
- If `"alpha"` is present without `"canonical_id"`: rename `"alpha"` → `"canonical_id"`
- Ensure consistent use of Greek letters (e.g., `α`, `ω`)
- Retain **all** properties and nested objects
- Standardize inconsistent field names (e.g., entity naming, protocol formats)

---

### 4. `room_light_mappings` Section

Group lights into zones based on:

- `"room_id"` (top-level grouping)
- `"location.area"` (nested zone grouping)

Example:

```json
"room_light_mappings": {
  "bedroom": {
    "zones": {
      "desk": ["bedroom_desk_omega", "bedroom_desk_corner_omega"],
      "nightstand": ["bedroom_nightstand_left_omega"]
    }
  },
  ...
}
```

If `location.area` is null, treat as `"general"`.

---

### 5. `validation_rules` Section

Add the following predefined rules:

```json
"validation_rules": [
  {
    "rule": "canonical_id_format",
    "target": "light_devices.*.canonical_id",
    "regex": "^[a-z0-9_]+_ω$"
  },
  {
    "rule": "protocol_availability",
    "target": "light_devices.*.integration_stack",
    "condition": "at least one protocol with 'status':'paired'"
  },
  {
    "rule": "room_id_reference",
    "target": "light_devices.*.room_id",
    "must_exist": true
  }
]
```

---

## 🛠 Defaults & Fallbacks

- Missing `canonical_id`: skip renaming, preserve existing key
- Missing `room_id`: omit from `room_light_mappings`, still include in `light_devices`
- Devices with no paired protocols: include with `"status": "unavailable"`

---

## ✅ Deliverable Validation Criteria

- Structure matches target JSON format
- All devices preserved under `"light_devices"`
- No new fields invented or omitted
- All protocols categorized and prioritized
- Light mapping zones derived without ambiguity

---
