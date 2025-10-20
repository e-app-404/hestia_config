---
id: prompt_20251001_5acafb
slug: you-are-the-hestia-sensor-mapper
title: "\U0001F527 You Are The Hestia Sensor Mapper"
date: '2025-10-01'
tier: "α"
domain: extraction
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch6_mac-import_sensor-mapper.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:22.293030'
redaction_log: []
---

# 🔧 You Are The Hestia Sensor Mapper
### ✅ 1. **Correct Sensor Declaration Source**
**Replace:**
```markdown
Parse all YAML configuration files in the /config/hestia/ directory
Focus on template sensors in these locations: /alphabet/, /core/, /packages/
```
**With:**
```markdown
Parse all YAML files included under the `template:` section in `configuration.yaml`, particularly those declared using:
```yaml
template:
  - !include_dir_merge_list hestia/sensors/
  - !include_dir_merge_list hestia/alphabet/abstraction_layers/
  - !include_dir_merge_list hestia/core/
  - !include_dir_merge_list /config/hestia/config/<subsystem>/templates
```
These files typically contain a **flat list of sensor dictionaries**, not nested under `sensor:` or `template:` keys.
```

---

## 🎭 Canonical Metadata & Tier Extraction (Your Point 1)

### ✅ 2. **Avoid Parsing Tier from `name` Field**
**Replace:**
```markdown
Identify the tier based on Greek suffix (α, β, γ, δ, ε, ζ, η, μ, Ω)
```
**With:**
```markdown
Do not infer tier from the sensor `name` field due to Unicode limitations. Instead:
- Extract tier and abstraction layer metadata from the `canonical_id` field found in the `attributes` dictionary.
- The `canonical_id` format must follow: `room.function.layer_tier` (e.g., `bedroom.motion.occupancy_γ`)
- Parse tier (α–ζ, η, μ, Ω) and abstraction layer from the `canonical_id` suffix. (Full tier list in prompt_library_workflow.yaml)
```

---

## 📁 Template Sensor Parsing Logic

### ✅ 3. **Clarify Flat List Sensor Format**
**Add Under “YAML Configuration File Crawling”:**
```markdown
Note: Files included via `!include_dir_merge_list` under `template:` return **flat lists** of sensor templates.
Each file may contain one or more dictionaries with keys like `name`, `unique_id`, `value_template`, and `attributes`.
```

---

## 🧠 Dependency Logic Upgrade

### ✅ 4. **Adapt Dependency Parsing**
**Clarify:**
```markdown
Dependencies should be extracted by parsing references in `value_template` or `state`.
Use canonical_id-style references to validate cross-tier relationships.
```

