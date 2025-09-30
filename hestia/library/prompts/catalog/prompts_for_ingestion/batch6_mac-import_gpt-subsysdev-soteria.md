## 🧠 GPT Instruction Prompt: *SOTERIA Subsystem Package Generator*

> You are an expert in Home Assistant configuration and YAML architecture. Your task is to generate a new subsystem package called **SOTERIA**, part of a larger modular smart home operating system (Hestia).  
>  
> SOTERIA is responsible for **monitoring the presence, battery status, and health of small electronics and personal items**—including phones, tablets, Bluetooth trackers, remotes, and wearable devices.  
>  
> **Your output must follow the AETHER subsystem structure**, with modular separation and embedded metadata sensors. Each component must be cleanly scoped and use best practices (2024.8+), Jinja2 templating, and fully support Home Assistant GUI integration.

---

### 🎯 Scope and Goals

- **Subsystem Name**: `SOTERIA`
- **Subsystem Function**: Monitor presence, battery health, and diagnostics for small devices and personal items.
- **Target Entities**: Devices like phones, AirTags, Tile trackers, Smart remotes, Headphones, Smart pens, etc.
- **Key Use Cases**:
  - Alert when battery drops below threshold
  - Notify if critical personal items leave the home zone
  - Track "last seen" and "connected status" across rooms
  - Integrate with room presence (HERMES) and notifications (ATHENA)

---

### 🗂️ File Structure (to generate)

1. `soteria_config.yaml`: Central configuration with thresholds, tracked item list, and display settings.
2. `soteria_helpers.yaml`: `input_number`, `input_boolean`, `input_select` helpers for control and thresholds.
3. `soteria_sensors_status.yaml`: Template sensors for battery, presence, and signal strength abstraction.
4. `soteria_logic.yaml`: Evaluation logic (e.g., is_critical_missing, is_battery_low, needs_attention).
5. `soteria_automations.yaml`: Notifications, reminders, and device lifecycle logic.
6. `soteria_scripts.yaml`: Optional routines (e.g., refresh device, escalate alert).
7. `soteria_diagnostics.yaml`: Diagnostics including missing count, average battery level, and subsystem health.
8. `soteria_index.yaml`: Master include file, with metadata sensor and file includes.

---

### 🧱 Required Design Features

- Every file must start with a metadata template sensor describing:
  - `module`, `type`, `description`, `file`, `subsystem`, `version`, `last_updated`
- Use `dict2items`, `selectattr`, and quality-aware logic where needed
- All `repeat` loops must use lists, with `| default([])` protections
- Automations and scripts must follow the new 2024.8+ `action:` convention

---

### 📘 Documentation Requirement

Generate a `README_SOTERIA.md` structured like the AETHER readme:
- Overview, Architecture, Information Flow
- Key Metrics (battery %, last seen, presence)
- Integration points with HERMES, ATHENA
- Troubleshooting guide for offline/missing devices