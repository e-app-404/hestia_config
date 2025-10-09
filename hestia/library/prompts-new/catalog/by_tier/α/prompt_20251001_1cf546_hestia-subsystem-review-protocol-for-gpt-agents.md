---
id: prompt_20251001_1cf546
slug: hestia-subsystem-review-protocol-for-gpt-agents
title: "\u2705 Hestia Subsystem Review Protocol (For GPT Agents)"
date: '2025-10-01'
tier: "\u03B1"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch6_mac-import_hestia_subsystem_review_protocol.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:23.561522'
redaction_log: []
---

# ✅ Hestia Subsystem Review Protocol (For GPT Agents)

This document defines the formal review process for GPT agents tasked with evaluating an individual **subsystem** within the Hestia architecture. A review covers **internal correctness**, **external integration**, and **conformance to Hestia standards**.

---

## 🎯 Review Objective

To ensure that the selected subsystem:
- Functions correctly in isolation
- Integrates cleanly into Hestia’s layered architecture
- Follows best practices for naming, abstraction, and diagnostic coverage

---

## 🧱 1. Review Scope

When a subsystem is selected (e.g., `hermes`, `aether`, `theia`), the GPT should:

### a. **Isolate and Load All Related Files**
Include all files within:
```
/config/hestia/packages/<subsystem>/
```
e.g., `climate.yaml`, `sensors.yaml`, `automations.yaml`, `scripts.yaml`, `diagnostics.yaml`, `readme.yaml`

Also check if the subsystem references:
- Core files (e.g., `hestia_config.yaml`)
- Shared templates or helpers
- Metadata registries (`room_registry`, `device_registry`)

---

## 🔍 2. Audit Checklist

For each file in the subsystem:

### A. Sensors & Abstractions
- [ ] Are sensor names consistent and informative?
- [ ] Are Jinja2 templates resilient to unavailable/missing states?
- [ ] Do abstractions respect override flags and fallback logic?

### B. Automations & Scripts
- [ ] Are automations scoped properly to mode, state, or triggers?
- [ ] Are `action:` blocks used correctly (post-2024.8)?
- [ ] Do scripts reuse templates where appropriate?

### C. Diagnostic & Readiness
- [ ] Does the subsystem include diagnostic coverage?
- [ ] Are all required sensors/devices verified via validation logic?
- [ ] Are fallback or unavailable scenarios handled gracefully?

### D. Metadata Awareness
- [ ] Does the subsystem pull room/device context from the registry?
- [ ] Are behaviors modulated by metadata flags (e.g., `presence_enabled`)?

### E. Naming & Structure
- [ ] Are entity IDs structured predictably (`<type>_<room>_<purpose>`)?
- [ ] Are files modular and separated by concern?
- [ ] Is the `readme.yaml` or metadata sensor included?

---

## 🔄 3. Relationship Mapping

For data inputs and outputs:
- Map sensors this subsystem **consumes**
- Map sensors this subsystem **produces**
- Trace any **cross-subsystem dependencies**
- Note if it modifies **core helper values** (input_booleans, etc.)

---

## 🧠 4. Contextual Awareness

- [ ] Does the subsystem respect presence, proximity, or routines?
- [ ] If integrated with another subsystem, is the interface clean?
- [ ] Are global flags (`home_mode`, `eco_mode`, etc.) observed?

---

## 📝 5. Report Output

The GPT should provide:
- ✅ Summary of compliance (per category)
- 🔧 List of potential issues or deviations
- 💡 Suggestions for refactor, cleanup, or better integration
- 📌 Specific entity or file references

---

This protocol should be applied consistently for any Hestia subsystem under review.
