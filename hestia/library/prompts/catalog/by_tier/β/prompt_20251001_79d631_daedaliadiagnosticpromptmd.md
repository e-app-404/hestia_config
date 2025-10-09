---
id: prompt_20251001_79d631
slug: daedaliadiagnosticpromptmd
title: Daedalia_diagnostic_prompt.md
date: '2025-10-01'
tier: "\u03B2"
domain: validation
persona: icaria
status: deprecated
tags:
- diagnostic
version: '1.0'
source_path: batch 1/batch1-daedalia_diagnostic_prompt.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.468677'
redaction_log: []
---

# Daedalia_diagnostic_prompt.md

## 🛰️ Daedalia Mission: Entity Reactivation & Structural Diagnostics

### 🎯 Objective
Investigate and resolve widespread `Unavailable`, `Unknown`, or `Idle` states across lighting, climate, and monitoring domains in HESTIA — operating silently until you reach concrete, validated resolutions.

---

### 🔒 Operational Constraints

- You **must not interact with the user** unless:
  1. You have completed full consultation of:
     - `configuration.yaml`
     - `mqtt.yaml`, `*_sensor.yaml`, all active integrations
     - `home-assistant.log`, `validator_log.json` (if present)
     - Template and custom component source files
  2. You can propose a **copy-paste-ready or file-drag-ready** implementation (YAML patch, command, or file path) with minimal user adjustment.

---

### 🧩 Task Modules

#### 1. Integration Audit

- Identify all custom integrations (`manifest.json` in `/custom_components`)
- Cross-check for Home Assistant Core compatibility, missing color mode, or deprecated API use
- Disable sandboxed integration only if it breaks availability propagation

#### 2. Template Reactivation

- Analyze and selectively reactivate commented `template:` blocks in `configuration.yaml`
- Identify failures in merged template imports from paths like:
  - `hestia/sensors/*/`
  - `hestia/core/template/`
- Confirm presence of `diagnostic_macros.yaml` and render test entity

#### 3. MQTT Schema Repair

- Fully validate `mqtt.yaml`:
  - Remove all `attributes:` keys violating schema
  - Normalize `availability:` entries
- Test each correction by simulating availability topic publish
- Prepare a fixed, formatted `mqtt.yaml` segment for direct merge

#### 4. Silent Probing & Entity Verification

- Use developer tools to test dead sensors via:
  - Manual state injection
  - MQTT `publish` probe
- Cross-reference with `entity_map.json` if present
- Log failed probes but **do not raise** until a fix is ready

---

### 🧠 Cognitive Output

- If a fix is achieved, output must contain:
  - Full YAML patch or command script (e.g., shell, Python)
  - Drag-ready path within HESTIA
  - Confirmation that state returns to `available`, `idle`, or `on`

---

### 📁 Final Artifact Deliverables

When ready, prepare:
- `FIX_mqtt_repair_20250501.yaml`
- `TEMPLATE_REACTIVATION_20250501.yaml`
- `diagnostic_log_20250501.md` (summarized fix map)
- Optional: `phanes_run_validation_report.json`

---

### 🧬 End State
No contact, no noise, no theory — only working, injected architecture.

---


