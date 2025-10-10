---
id: prompt_20251001_d37187
slug: architecturerecommendationsmd
title: "\U0001F9F1 ARCHITECTURE_RECOMMENDATIONS.md"
date: '2025-10-01'
tier: "α"
domain: extraction
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch6_mac-import_ARCHITECTURE_RECOMMENDATIONS.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:22.574250'
redaction_log: []
---


# 🧱 ARCHITECTURE_RECOMMENDATIONS.md

## 🧭 Overview

This document presents a refactor and optimization plan for your Home Assistant architecture under `/config/hestia/`, focusing on clarity, subsystem cohesion, modularity, and diagnostic separation.

---

## ✅ Subsystem Audit Summary

### 🛰️ `hermes`
- Owns `proximity_integration.yaml` under `hestia/sensors/`
- Includes a metadata sensor with source tracing
- ✅ Conforms to sensor encapsulation guidelines
- 🔄 Suggest moving sensor logic to `packages/hermes/hermes_presence_templates.yaml` and import via `template:` block

### 🧠 `iris` (under `selene`)
- Dashboard (`iris_dashboard_view.yaml`) and compact card (`iris_dashboard_card.yaml`) are modular and coherent
- `iris_mode_buttons.yaml` includes inline service logic:
  - 🔁 Suggest extracting service calls into `scripts/iris/set_mode.yaml`
- ✅ Metadata and diagnostic sensors are well-represented

### 🔧 Tooling Layer (`clio`, `phanes`, `hephaestus`)
- Entities for these tools are scattered in `selene`:
  - ❌ Misplaced files: `hephaestus_dashboard_card.yaml` and `hestia_tools_clio_phanes.yml`
  - 🛠️ Recommended Move → `tools/diagnostics/` or `tools/tool_dashboards/`

---

## 📂 Directory Layout Suggestions

```
/hestia/
├── packages/
│   ├── hermes/
│   │   ├── hermes_config.yaml
│   │   └── templates/hermes_presence_templates.yaml
├── selene/
│   ├── dashboards/
│   │   ├── iris_dashboard_view.yaml
│   │   └── iris_dashboard_card.yaml
│   └── controls/
│       └── iris_mode_buttons.yaml
├── tools/
│   ├── diagnostics/
│   │   ├── hephaestus_dashboard_card.yaml
│   │   └── hestia_tools_clio_phanes.yml
```

---

## 📌 Refactor Opportunities

- **Blueprint or script abstraction** for repeated service calls in `iris_mode_buttons.yaml`
- Consolidate `tool_*` entities into a single `tools_status.yaml`
- Extract all metadata sensors into a centralized template block in `/core/` or `/metrics/`

---

## 🧪 Metadata Principles

- Metadata sensors (e.g., `metadata_hermes_proximity_integration`) should always be isolated from business logic
- All metadata should declare:
  - `file`
  - `subsystem`
  - `last_updated`
  - `version` (if applicable)

---

## 🔄 Migration Plan (See `MIGRATION_MAP.yaml`)
- Move non-selene tools dashboards to `/tools/`
- Realign proximity templates into the Hermes package
- Move `architecture_status_sensor.yaml` to `/core/diagnostics.yaml`

---

## 📎 Notes
- This refactor respects current entity names (no renaming)
- A `FULL_BACKUP` should be created before changes are applied

