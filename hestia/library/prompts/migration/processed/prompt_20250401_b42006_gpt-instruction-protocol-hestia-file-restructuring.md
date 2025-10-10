---
id: prompt_20250401_b42006
slug: gpt-instruction-protocol-hestia-file-restructuring
title: "\U0001F6E1\uFE0F GPT Instruction Protocol: HESTIA File Restructuring & Redistribution"
date: '2025-04-01'
tier: "α"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch6_mac-import_gpt_restructure_protocol.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:24.823108'
redaction_log: []
---

Absolutely. Below is a detailed **Standard Operating Procedure (SOP)** tailored for GPT-based assistants involved in **redistributing Home Assistant YAML packages**, ensuring **internal consistency**, **link integrity**, and **bulletproof risk mitigation**.

---

# 🛡️ GPT Instruction Protocol: HESTIA File Restructuring & Redistribution

---

## 🎯 Objective

To safely restructure and redistribute Home Assistant subsystem and template files across the `/config/hestia/` directory, while:

- Maintaining complete data and logic fidelity
- Ensuring reference and dependency consistency
- Preventing service interruptions
- Enabling modular reuse and long-term maintainability

---

## 🧩 1. Scope of Operation

These instructions apply to the reorganization or relocation of any content from:

- `/config/hestia/packages/<subsystem>/`
- `/config/hestia/core/`, `/tools/`, `/templates/`
- Global helpers, automations, and scripts
- Files referenced by `sensor`, `script`, `template`, or `automation`

---

## 🔐 2. Risk Mitigation & Backup Protocol

### ✅ A. **Immutable Backup (Pre-Edit Snapshot)**
Before modifying any file or moving content:
- Create a **timestamped backup** of the **entire source directory**, e.g.:

```bash
cp -r /config/hestia /config/_backup/hestia_2025-04-01/
```

- This ensures 100% reversibility and audit traceability.

### ✅ B. **Hash-Based File Verification**
- Optionally generate SHA256 hashes before and after to verify content integrity:

```bash
sha256sum /config/hestia/**/*.yaml > before_hashes.txt
sha256sum /config/hestia/**/*.yaml > after_hashes.txt
diff before_hashes.txt after_hashes.txt
```

---

## 🧠 3. Internal Consistency Checks

### 🔗 A. Reference Tracing

Check for **cross-file dependencies**, including:

- `state_attr('sensor.*_config', 'field')`
- `states('sensor.file_*')`, `states('sensor.device_monitor_*')`
- All `include` paths
- All uses of `input_`, `binary_sensor.`, `device_tracker.`, etc.

Update **references and naming paths** where content is relocated.

### 🧾 B. Template Integrity

For each modified or extracted Jinja2 template block:
- Ensure all entities referenced still exist
- Validate syntax using:

```yaml
Developer Tools → Templates → Paste logic
```

---

## 🗂️ 4. Recommended Directory Structure

**Templates** (dynamic logic):
```
/config/hestia/core/templates/device_monitor_templates.yaml
/config/hestia/packages/hermes/templates/presence_templates.yaml
```

**Metadata Configs**:
```
/config/hestia/core/device_monitor.yaml
/config/hestia/packages/hermes/hermes_config.yaml
```

**Shared Library**:
```
/config/hestia/templates/template_library.yaml
```

**Scripts/Automations**:
```
/config/hestia/scripts/<subsystem>/...
/config/hestia/automations/<subsystem>/...
```

---

## 🧰 5. Redistribution Procedure (Step-by-Step)

### 🪜 Step 1: Identify What Moves
- Jinja2-heavy logic → `templates/*.yaml`
- Metadata summary → stays in `*_config.yaml`
- Shared utilities → move to `template_library.yaml`

### 🪜 Step 2: Extract + Refactor
- Isolate logic blocks and test in the template editor
- Wrap in `template:` format under a named sensor or attribute

### 🪜 Step 3: Update Metadata Sensor
- Replace inlined logic with:
```jinja2
{{ states('sensor.device_monitor_risk_score') }}
{{ state_attr('sensor.device_monitor_unavailable_count', 'value') }}
```

### 🪜 Step 4: Revalidate Entire Subsystem
Run a **dry restart**:
```bash
ha core check
```

Check:
- Automations still load
- Lovelace dashboards show data
- No `unknown`/`unavailable` on key sensors

---

## 🧪 6. Final Safety Checks

| Test | Expected Result |
|------|------------------|
| File backup exists | `/config/_backup/hestia_*` |
| HA config validates (`ha core check`) | ✅ |
| Templates load in Dev Tools | ✅ |
| No references to missing sensors/scripts | ✅ |
| Logs contain no `TemplateError`, `KeyError` | ✅ |

---

## 🧾 7. Post-Migration Documentation

- Document the move in each affected file's `changelog:` attribute.
- Create a `MIGRATION.md` in the root of the config folder if the move is large-scale.
- Update README index links if using Git or file explorer dashboard.
