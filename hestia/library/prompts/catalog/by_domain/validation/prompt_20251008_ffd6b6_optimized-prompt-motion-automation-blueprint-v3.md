---
id: prompt_20251008_ffd6b6
slug: optimized-prompt-motion-automation-blueprint-v3
title: "Optimized Prompt — Motion Automation Blueprint (v3)"
date: '2025-10-08'
tier: "beta"
domain: validation
persona: icaria
status: candidate
tags:
- automation
version: '1.0'
source_path: ha-config/motion_automation_blueprint.promptset
author: Unknown
related: []
last_updated: '2025-10-09T01:44:27.367948'
redaction_log: []
---

# Optimized Prompt — Motion Automation Blueprint (v3)

Follow this prompt exactly. Produce helpers and packages for all eligible areas, strictly from the supplied files, with no speculation. If any required mapping is missing, emit the file with a blank/optional input and a `# TODO` comment, then stop.

## Objective

Produce deploy-ready Home Assistant automations for **motion-driven lighting** using the provided blueprint and configs, optimized for **simplicity, robustness, and zero guesswork**.

## Inputs (load in this order)

1. `system_instruction.yaml` → hydrate protocols & enforcement.
2. `hestia_config_bundle_*.tar.gz` → unpack; read:

   * `hestia/library/templates/blueprints/sensor-light.yaml` (verified existing blueprint)
   * `hestia/config/devices/lighting.conf` (eta-tier group light entities: `light.group_*`)
   * `hestia/config/devices/motion.conf` (alpha-tier motion/occupancy sources)
   * Variable component integration via `domain/variables/` and `packages/package_tts_gate.yaml`
   * any referenced helper or include files

## Workspace Doctrine (must comply)

* Paths (canonical):
  * Blueprint → `hestia/library/templates/blueprints/sensor-light.yaml` (verified existing)
  * Package YAML incl. helpers → `packages/motion_lights/`
  * Variables → `domain/variables/motion_variables.yaml` (new file using HACS Variable component)
  * Helper includes → `hestia/helpers/motion_lights/` (following ADR-0016 structure)
* YAML standards: **2-space indentation**, **A→Z key sorting**, comments minimal and factual.
* Entity naming: preserve suffixes (e.g., `*_alpha`), prefer **eta-tier group lights** (verified: `light.group_all_bedroom_lights`, `light.group_kitchen_lights`, etc.) as targets.
* Variable integration: Use HACS Variable component for state management, timeouts, and bypass logic.
* No speculative entities. If something is missing, emit a clear **TODO** and keep the input optional/blank.

## Blueprint Capabilities to Use (sensor-light.yaml)

* Dynamic lighting & transitions
* Night mode via **sun elevation**; optional ambient **LUX** gating  
* Bypass controls (per-area) integrated with **HACS Variable component**
* State management & restart safeguards (inhibit on startup, restore state)
* Optional device tracking (person / device_tracker)
* Timeout/auto-off behavior managed via **variables**
* Template-based conditional logic
* Weekend/weekday scheduling options

## Deliverables

1. **Variables** using HACS Variable component under `domain/variables/motion_variables.yaml` for:
   - Per-area bypass states
   - Dynamic timeout management  
   - Motion detection counters
   - Last motion timestamps
2. **Per-area package files** under `packages/motion_lights/`, each using sensor-light.yaml blueprint with concrete inputs from the configs
3. **Helper integration** using existing Variable component instead of traditional `input_boolean`/`input_number`
4. **Minimal include stanzas** (if missing) for `var`, and `automation` in `configuration.yaml`
5. A **brief validation checklist** and **test plan** per area

## Paint-by-Numbers Process (do this exactly)

1. **Load** `system_instruction.yaml`. Enforce its protocols throughout.
2. **Unpack & index** the tarball. Parse `lighting.conf` and `motion.conf`.
3. **Area selection**: create packages **only** for areas that have at least one motion/occupancy source **and** at least one eta-tier **group** light.
4. **Targets**: for each selected area, set `target_lights` to the **group** entity from verified list:
   - `light.group_all_bedroom_lights`
   - `light.group_kitchen_lights`
   - `light.group_living_room_lights_all`
   - `light.group_ensuite_lights`
   - etc. (verified entities from .storage/core.entity_registry)

   * Never mix group + individual fixtures unless explicitly required by the file.
5. **Sensors**: wire alpha-tier motion/occupancy sensors from verified list:
   - `binary_sensor.bedroom_security_cam_alpha_motion`
   - `binary_sensor.kitchen_motion_alpha_motion`
   - `binary_sensor.living_room_multipurpose_alpha_motion`
   - etc. (verified entities from motion.conf and entity registry)
6. **Variable Integration**: create variables using HACS Variable component:
   - `var.motion_bypass_<area>` (required)
   - `var.motion_timeout_<area>` (dynamic timeout management)
   - `var.motion_last_triggered_<area>` (state tracking)
7. **Night/LUX defaults** (safe, simple):

   * `night_mode_enabled: true`
   * `night_mode_sun_elevation: -6`
   * `ambient_lux_entity: ""` (leave blank unless present in bundle)
   * `ambient_lux_threshold: 10` (only used if entity is provided)
8. **Resilience**:

   * `mode: restart`, `max_exceeded: silent`
   * `restore_state_after_restart: true`
   * `inhibit_on_startup_seconds: 10`
9. **Presence**:

   * Default off: `presence_entity: ""`, `require_presence_for_activation: false`
   * Only enable if the bundle provides explicit `person.*` or `device_tracker.*` mappings.
10. **Normalization**: sort keys A→Z, indent 2 spaces, remove dead comments.
11. **Emit** helpers + packages and **stop**. No speculative expansions.

## Package Template (copy per area; fill placeholders)

```yaml
alias: Motion Lights — <Area>
description: Motion-driven lighting for <Area> using eta-tier group; night mode, Variable bypass, sun elevation, restart-safe.
id: motion_lights_<area>
initial_state: true
max_exceeded: silent
mode: restart
use_blueprint:
  path: hestia/library/templates/blueprints/sensor-light.yaml
  input:
    ambient_lux_entity: ""                        # set only if present in illuminance.conf
    ambient_lux_threshold: 10
    bypass_entity: "{{ states('var.motion_bypass_<area>') == 'true' }}"  # Variable integration
    inhibit_on_startup_seconds: 10
    motion_sensors:
      # fill from verified motion.conf (alpha-tier) for this area:
      # bedroom: binary_sensor.bedroom_security_cam_alpha_motion
      # kitchen: binary_sensor.kitchen_motion_alpha_motion
      # living_room: binary_sensor.living_room_multipurpose_alpha_motion
      - binary_sensor.<verified_sensor_from_entity_registry>
    night_mode_brightness_pct: 12
    night_mode_color_temp_mired: 420
    night_mode_enabled: true
    night_mode_sun_elevation: -6
    only_if_lights_off: false
    presence_entity: ""                           # set only if present
    require_presence_for_activation: false
    require_sun_condition: false
    restore_state_after_restart: true
    sun_max_elevation: 20
    sun_min_elevation: -12
    target_lights:
      # fill from verified lighting.conf (eta-tier groups):
      # bedroom: light.group_all_bedroom_lights
      # kitchen: light.group_kitchen_lights
      # living_room: light.group_living_room_lights_all
      - light.group_<verified_group_from_entity_registry>
    timeout_seconds: "{{ states('var.motion_timeout_<area>') | int(120) }}"  # Variable timeout
    transition_seconds: 0.3
```

## Variable Template (HACS Variable Component)

`domain/variables/motion_variables.yaml` - Integrated with existing Variable structure

```yaml
# Motion control variables using HACS Variable component
# Following pattern from packages/package_tts_gate.yaml and domain/variables/plex_variables.yaml

motion_bypass_bedroom:
  friendly_name: "Motion Bypass — Bedroom"
  unique_id: "var_motion_bypass_bedroom"
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: "bedroom" 
    last_toggled: ""

motion_timeout_bedroom:
  friendly_name: "Motion Timeout — Bedroom (sec)"
  unique_id: "var_motion_timeout_bedroom"
  initial_value: 120
  restore: true
  unit_of_measurement: "seconds"
  icon: mdi:timer-outline
  attributes:
    min: 5
    max: 1800
    area: "bedroom"

motion_last_triggered_bedroom:
  friendly_name: "Last Motion — Bedroom"
  unique_id: "var_motion_last_triggered_bedroom"
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    sensor_id: ""
    area: "bedroom"
    
# Repeat pattern for each area: kitchen, living_room, ensuite, etc.
```

## Includes (add once if missing)

```yaml
# Variable component integration (following existing pattern)
var: !include_dir_merge_named domain/variables/
automation: !include_dir_merge_list packages/motion_lights/

# Note: HACS Variable component replaces need for input_boolean/input_number
# Existing structure in configuration.yaml already includes domain/variables/
```

## Defaults (use unless overridden by bundle data)

* `timeout_seconds`: 120 (wardrobe: 30–45; bathroom/ensuite: 45–90; hallway: 60–120)
* `transition_seconds`: 0.3
* `night_mode_brightness_pct`: 7–15 (choose 12 if unsure)
* `night_mode_color_temp_mired`: 400–450 (choose 420 if unsure)

## Safety & Simplicity Rules

* **Never fabricate** entities. Leave inputs blank and add a `# TODO` if missing.
* **Prefer group targets** (`light.group_*`). Do not fan out to individual fixtures unless required by the file.
* **Keep optional features off by default** (LUX, presence) unless the entities exist.
* **Minimize churn**: one package per area; no overlapping automations for the same group.

## Validation Checklist (binary pass/fail)

* YAML parses; `ha core check` passes.
* Files in canonical paths; includes resolve.
* Variable component integration:
  * Variables defined in `domain/variables/motion_variables.yaml`
  * Variables follow existing pattern from `packages/package_tts_gate.yaml`
  * Variable service calls (`var.set`) properly formatted
  * Template syntax for Variable state access correct
* Each generated package:
  * references only **verified entities** from .storage/core.entity_registry
  * uses **verified group lights** (`light.group_all_bedroom_lights`, etc.)
  * wires **verified motion sensors** (`binary_sensor.*_alpha_motion`)
  * integrates Variable component for bypass/timeout logic
  * adheres to 2-space indent + A→Z key order
* Startup is stable (restart safeguards present)
* Variable restore functionality enabled

## Test Plan (per area, 3 minutes)

1. **Variable Bypass Test**: 
   - Use `var.set` service to set `var.motion_bypass_<area>` to `true` (blocks automation)
   - Set to `false` (allows automation)
   - Verify template `{{ states('var.motion_bypass_<area>') == 'true' }}` works correctly
2. **Motion Detection**: Trigger verified motion sensor; confirm group light turns on
3. **Variable Timeout**: 
   - Use `var.set` to adjust `var.motion_timeout_<area>` value
   - Verify template `{{ states('var.motion_timeout_<area>') | int(120) }}` applies new timeout
4. **Night Mode**: After sunset (or simulate), confirm night brightness/temp applied
5. **Persistence**: Restart HA; confirm Variable restore functionality and no flapping
6. **Variable State Tracking**: Verify `var.motion_last_triggered_<area>` updates correctly

## Variable Component Service Integration Examples

### Update bypass state from automation:
```yaml
- service: var.set
  data:
    entity_id: var.motion_bypass_bedroom
    value: true
    attributes:
      last_toggled: "{{ now().isoformat() }}"
```

### Dynamic timeout adjustment based on time of day:
```yaml
- service: var.set
  data_template:
    entity_id: var.motion_timeout_{{ area }}
    value: >-
      {% if now().hour >= 22 or now().hour <= 6 %}
        300  # 5 minutes at night
      {% else %}
        120  # 2 minutes during day
      {% endif %}
```

### Track last motion detection:
```yaml
- service: var.set
  data:
    entity_id: var.motion_last_triggered_{{ area }}
    value: "{{ now().isoformat() }}"
    attributes:
      sensor_id: "{{ trigger.entity_id }}"
      area: "{{ area }}"
```

---
