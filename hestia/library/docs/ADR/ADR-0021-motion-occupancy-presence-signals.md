---
id: ADR-0021
title: "Motion, Occupancy, and Presence Signal Architecture (beta abstractions)"
authors: 
  - "Strategos Governance"
  - "Evert Appels"
status: Accepted
date: 2025-10-03
last_updated: 2025-10-03
tags: ["home-automation","adr","motion","occupancy","presence","lighting","architecture","beta-tier","abstractions","blueprints"]
notes:
---

# ADR-0021 — Motion, Occupancy, and Presence Signal Architecture (beta abstractions)

## 1. Context

Hestia’s lighting automations historically referenced **raw (alpha-tier)** device entities (e.g., PIRs, cameras). This created brittleness: false-offs during stillness, sensitivity drift, and device outages. We now maintain **abstract, room-level composites** at the **beta tier** (e.g., `binary_sensor.<room>_motion_beta`, `binary_sensor.<room>_occupancy_beta`, `sensor.<room>_illuminance_beta`) and **eta-tier** group light targets (e.g., `light.group_*`). We must define how **motion**, **occupancy**, and **presence** signals are **interpreted, constructed, and consumed** by blueprints—without adding unnecessary layering.

### Current constraints

* Household has **one `person.*` entity** (the user) and **one untracked housemate**.
* Presence **must not** be used to block activations; it may **enhance** behavior (timeouts, scenes).
* We standardize on **HACS Variable** component for dynamic timeouts, bypass, and telemetry.

## 2. Decision (Summary)

1. **Single abstraction layer**: Automations **must consume beta-tier room composites** for motion/occupancy and eta-tier group lights. **No additional layer** is introduced above beta.
2. **Signal roles**:

   * **Motion** → *fast trigger* (enter/leave detection).
   * **Occupancy** → *stickiness* (stillness tolerance; extends hold).
   * **Presence** → *context only* (never a hard gate in our household).
3. **Blueprint standard**: Use `hestia/library/templates/blueprints/sensor-light.yaml` as the **primary** automation executor. `sensor-light-add-on.yaml` and `ha-blueprint-linked-entities.yaml` may refine behavior **without** duplicating motion logic.
4. **Variables**: Configure per-area `var.motion_bypass_<area>`, `var.motion_timeout_<area>`, and `var.motion_last_triggered_<area>`.
5. **Guardrail**: Where an abstract signal does **not exist** for an area, leave the input **blank** and annotate with `# TODO`; do **not** fall back to alpha devices inside packages.

## 3. Definitions (Robust)

### 3.1 Motion (room-level)

* **Meaning:** Evidence of recent movement in the room.
* **Entity shape:** `binary_sensor.<room>_motion_beta` (boolean)
* **Expected characteristics:**

  * **Fast ON** upon movement; **fast OFF** when motion quiesces (subject to short debounce).
  * Aggregated from multiple alphas (PIR, camera motion, mmWave entrance spikes) with basic debouncing and OR fusion.
* **Intended use:** Primary trigger for turning lights **on**.

### 3.2 Occupancy (room-level)

* **Meaning:** Likelihood that the room is **currently occupied**, even without visible motion.
* **Entity shape:** `binary_sensor.<room>_occupancy_beta` (boolean)
* **Expected characteristics:**

  * **Sticky** relative to motion; extends ON state via hysteresis.
  * Aggregates motion history, dwell time, seated-stillness signals (e.g., mmWave), contact events.
* **Intended use:** Optional input to **extend hold** (prevent premature off).

### 3.3 Presence (household/person-level)

* **Meaning:** Whether a specific person is reachable/at home or likely in a given area.
* **Entity shapes:** `person.*`, `device_tracker.*`, or derived `binary_sensor.<area>_presence_beta`.
* **Expected characteristics:**

  * **Very sticky**; not always tied to room activity.
  * Susceptible to staleness; **never used** to assert "no humans" in this household due to an **untracked housemate**.
* **Intended use:** **Contextual modifier** (longer timeout, brighter scenes). **Not** a hard prerequisite for activation.

## 4. Construction Rules (Beta Abstractions)

> These rules describe how beta composites should be built upstream of automations. If an element is missing in the current repo, defer with `# TODO` and keep the automation input blank.

### 4.1 Motion Beta Construction

* **Inputs (examples):** PIR motion, camera motion, doorway mmWave burst.
* **Fusion:** Logical **OR** with per-sensor debounce; optional entrance/exit heuristics.
* **Output:** `binary_sensor.<room>_motion_beta` true when any motion source fires.

### 4.2 Occupancy Beta Construction

* **Inputs (examples):** Motion beta, mmWave continuous presence, seat/desk micro-movements, recent door open.
* **Fusion:** Weighted logic with **hysteresis**:

  * ON: motion beta OR mmWave presence
  * OFF: no motion AND no mmWave **for T_still ≥ Xs** (room-specific)
* **Output:** `binary_sensor.<room>_occupancy_beta` captures stillness.

### 4.3 Illuminance Beta Construction

* **Inputs:** One or more illuminance sensors (desk, near window) with smoothing and min/max guards.
* **Output:** `sensor.<room>_illuminance_beta` as a smoothed lux proxy.

### 4.4 Presence Beta (optional, per-area)

* **Inputs:** `person.*`, `device_tracker.*` (phone > router) and policy flags.
* **Asymmetry:** With an **untracked housemate**, presence **cannot** imply emptiness. Presence **may** enhance behavior only.
* **Output:** `binary_sensor.<area>_presence_beta` (optional). If absent, leave blueprint presence inputs blank.

## 5. Consumption Rules (Blueprint Integration)

### 5.1 Primary blueprint inputs

Use **exactly these** inputs per area package:

```yaml
use_blueprint:
  path: hestia/library/templates/blueprints/sensor-light.yaml
  input:
    ambient_lux_entity: "sensor.<room>_illuminance_beta"   # leave "" with # TODO if not available
    ambient_lux_threshold: 10
    bypass_entity: "{{ states('var.motion_bypass_<area>') == 'true' }}"
    inhibit_on_startup_seconds: 10
    motion_sensors:
      - binary_sensor.<room>_motion_beta
    night_mode_brightness_pct: 12
    night_mode_color_temp_mired: 420
    night_mode_enabled: true
    night_mode_sun_elevation: -6
    only_if_lights_off: false
    presence_entity: ""                             # optional; see §5.3
    require_presence_for_activation: false
    require_sun_condition: false
    restore_state_after_restart: true
    sun_max_elevation: 20
    sun_min_elevation: -12
    target_lights:
      - light.group_<verified_group>
    timeout_seconds: "{{ states('var.motion_timeout_<area>') | int(120) }}"
    transition_seconds: 0.3
```

### 5.2 Occupancy as an extender (optional)

If the blueprint supports multiple `motion_sensors`, you may list both **motion** and **occupancy** betas to keep the light on during stillness:

```yaml
motion_sensors:
  - binary_sensor.<room>_motion_beta
  - binary_sensor.<room>_occupancy_beta
```

### 5.3 Presence as a modifier (optional)

Presence **must not** gate activation in this household. It may **enhance** timeouts or scenes:

```yaml
presence_entity: "binary_sensor.<area>_presence_beta"     # only if this sensor exists
require_presence_for_activation: false
# Example enhancement
timeout_seconds: >-
  {% set base = states('var.motion_timeout_<area>') | int(120) %}
  {% if is_state('binary_sensor.<area>_presence_beta','on') %}
    {{ base + 120 }}
  {% else %}
    {{ base }}
  {% endif %}
```

## 6. Guardrails

1. **No alpha fallbacks inside packages.** If a beta or illuminance composite is missing, set input to `""` and add `# TODO` comment.
2. **Do not hard-require presence.** `require_presence_for_activation` remains `false` unless a future ADR changes the household policy.
3. **Prefer eta-tier group lights** (`light.group_*`) as targets; do **not** mix group and individual fixtures.
4. **Variables are authoritative** for bypass/timeout/telemetry. Do not introduce `input_boolean`/`input_number` duplicates.
5. **Two-space YAML indentation; A→Z keys** in emitted files.
6. **Restart safety** is mandatory: `mode: restart`, `max_exceeded: silent`, `restore_state_after_restart: true`, `inhibit_on_startup_seconds: 10`.

## 7. Rationale

* **Resilience:** Room-level composites absorb individual sensor failures and reduce flapping.
* **Simplicity:** A single abstraction layer (beta) keeps mental load and maintenance low.
* **Household reality:** Presence cannot prove emptiness (untracked housemate). Asymmetric policy avoids dark rooms caused by misattribution.
* **Upgradability:** Inputs-only approach preserves blueprint reuse and clean diffs.

## 8. Consequences

* **Positive:** Faster iteration; fewer brittle overrides; coherent per-room behavior.
* **Negative:** Where beta composites are missing, lights may be less context-aware until the `# TODO` is addressed.
* **Neutral:** Presence remains optional and may be added later without refactoring.

## 9. Implementation Plan

1. **Audit** each area for available beta entities (`motion`, `occupancy`, `illuminance`).
2. **Emit** per-area packages using the standard inputs (see §5.1), leaving blanks with `# TODO` where composites are missing.
3. **Define variables** in `domain/variables/motion_variables.yaml` for each area (bypass/timeout/last-trigger).
4. **(Optional)** Create `hestia/helpers/motion_lights/presence_sensors.yaml` if presence betas are desired.
5. **Add includes** in `configuration.yaml` if not present:

```yaml
automation: !include_dir_merge_list packages/motion_lights/
var: !include_dir_merge_named domain/variables/
```

6. **Validate** with `ha core check` and run the test plan (§10).

## 10. Validation & Test Plan (binary)

* **Files/Structure:** Canonical paths; YAML parses; includes resolve.
* **Entities:** Packages reference only verified beta composites and eta-tier groups.
* **Variables:** `var.*` entities exist; templates resolve; `var.set` works.
* **Runtime:** On motion, lights turn on; timeouts honor variable values; restart is stable (10s inhibit).
* **Night Mode:** At sun elevation < −6, brightness 12% @ 420 mired.
* **Presence (if used):** Enhances only; does not prevent activation.

## 11. Alternatives Considered

* **Presence-gated activation** (rejected): contradicts household constraint (untracked housemate) and increases false negatives.
* **Introduce an additional policy layer sensor** (rejected): beta layer suffices; policy is better encoded via variables.

## 12. Future Work

* Add missing `*_illuminance_beta` composites for kitchen, ensuite, hallways.
* Evaluate mmWave seats/desk sensors feeding `*_occupancy_beta` for stillness improvements.
* Consider a guest mode variable that relaxes night-mode thresholds.

## 13. References

* Hestia blueprints: `hestia/library/templates/blueprints/`
* Variables pattern: `domain/variables/*.yaml`
* Packages path: `packages/motion_lights/`
