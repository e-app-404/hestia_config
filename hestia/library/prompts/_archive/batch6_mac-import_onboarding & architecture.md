# 🏗️ Hestia System: Onboarding & Architecture Guide

Welcome to the Hestia system! This guide introduces the modular design, subsystem organization, and logic strategies that underpin Hestia. Whether you're here to build new packages or maintain legacy behavior, this is your technical compass.

---

## 🔍 1. Conceptual Overview

### What is Hestia?

Hestia is a modular, package-driven architecture built on top of Home Assistant and ESPHome, aimed at building **deeply integrated, context-aware smart environments**. It’s more than a configuration—it's an ecosystem designed for **maintainability, abstraction, and cross-deployment portability**.

Hestia tackles complexity in automation-rich environments by clearly separating concerns between data, logic, behavior, and presentation. With Hestia, a sensor isn’t just a value—it’s a _layered signal_ that moves through progressively abstracted pipelines before becoming actionable automation logic.

---

### Why Hestia Exists

Originally born from the limitations of sprawling, monolithic Home Assistant configurations, Hestia answers this question: **How do we make automations scale across time, environments, and users?**

The answer was a principled system:
- Where presence could be reasoned about with a scoring model.
- Where overrides and temporary states had priority-aware logic.
- Where new locations could be brought online just by injecting metadata and enabling packages.
- Where automation logic didn’t live in chaos—but in structure.

It's not just about function—it's about **future-proof design**.

---

### Files & Modularity

Hestia’s backbone is its use of Home Assistant’s `!include` and `!include_dir_merge_named` directives, paired with strict file naming standards.

```yaml
/config/
├── hestia/
│   ├── core/          # Essential definitions (defaults, constants)
│   ├── packages/      # Primary logic split by subsystem or location
│   ├── overrides/     # Deployment-specific alterations
│   ├── shared/        # Reusable macros and templates
│   └── metadata/      # Location/room config, zone schemas
```

All systems operate via packages, or subsystems, and can be selectively enabled by location, type, or override.

---

### Key Design Principles

- **Modularity & Reuse**  
  Every sensor or automation is defined once and reused through includes and templates.

- **Decoupled Logic**  
  Presence detection doesn’t know about automations. Automations rely on confidence scores.

- **Template Abstraction**  
  No magic numbers; everything that can be templated is. If logic varies by room or mode, it lives in metadata.

- **Subsystem Encapsulation**  
  Presence, media, lighting, energy—each has its own internal pipeline and doesn’t leak logic between domains.

---

### The Many Layers of Hestia

Hestia is structured into **five core layers**, each serving a distinct purpose in how data is sensed, reasoned about, acted upon, and diagnosed. These layers work together to provide separation of concerns, reduce tight coupling, and enable scalability across domains and deployments.

---

#### 1. Abstraction Layer

This layer translates raw device data into a structured, reusable internal vocabulary.

- **What it does**:
  Unifies raw sensors and device signals into high-level abstractions. This is where data normalization and internal representations are built.
  
- **Examples**:
  - `sensor.sensor_motion_score` (from `/hestia/core/sensor_motion_score.yaml`)
  - `binary_sensor.presence_raw` and `sensor.motion_detected_recently`

- **HA Elements**: Template sensors, binary sensors, sometimes via MQTT.
- **Design Goal**: Allow the same logic layer to function identically across locations with different hardware inputs.

---

#### 2. Logic Layer

This layer interprets abstracted signals into logical conclusions, usually using Jinja2 templates or scoring systems.

- **What it does**: 
  Computes "understanding"—presence confidence, lighting state suitability, routine activity evaluation, etc.
  
- **Examples**:
  - `sensor.presence_abstraction_layer` (aggregates multiple raw inputs into a presence confidence)
  - `sensor.motion_state_logic`
  - `sensor.occupancy_score`

- **HA Elements**: Template sensors, Jinja2 expressions, input helpers for thresholds.
- **Design Goal**: Encapsulate heuristics and scoring logic separately from raw input or automation code.

---

#### 3. Automation Layer

This is where behaviors are defined—when lights turn on, notifications are sent, or routines trigger.

- **What it does**: 
  Converts logic-derived states into actions, often driven by modes, time, or conditions.

- **Examples**:
  - `/hestia/packages/hermes/automations_motion_lighting.yaml`
  - `/hestia/automations/athena/template_monitor_automation.yaml`

- **HA Elements**: `automation:`, `script:`, and `action:` blocks (note: as of Home Assistant 2024.8, `service:` is now under `action:`).
- **Design Goal**: Isolate execution rules from reasoning logic. Enables reusing logic with different behavioral triggers.

---

#### 4. Interface Layer

The only layer exposed to end users (via dashboards or voice). Includes inputs, status indicators, and manual toggles.

- **What it does**: 
  Surfaces helper inputs (like input_booleans), displays sensor states, allows override controls.

- **Examples**:
  - `/hestia/helpers/input_boolean.yaml`
  - `/hestia/helpers/input_select.yaml`
  - Lovelace cards that bind to state attributes and expose override options.

- **HA Elements**: Helpers, Lovelace UI components, user triggers.
- **Design Goal**: Keep internal logic and automations safely hidden; allow safe user interaction points.

---

#### 5. Diagnostic Layer

An often overlooked but critical layer for maintainability.

- **What it does**: 
  Performs audits, exposes missing entities, and tracks consistency and operational health.

- **Examples**:
  - `/hestia/config/diagnostics/light_hestia_abstraction_audit.yaml`
  - `sensor.missing_registry_entities`
  - `sensor.unavailable_entities_counter`

- **HA Elements**: Template sensors, diagnostic scripts, input logs, developer dashboard hooks.
- **Design Goal**: Detect degradation before it impacts logic or user experience. Enables safe evolution of config.

---

### How These Layers Interplay

Let’s walk through a practical flow:

1. A Zigbee motion sensor triggers.
2. The **abstraction layer** (e.g., `sensor.motion_event_recent`) normalizes this into a standardized state.
3. The **logic layer** (e.g., `sensor.presence_abstraction_layer`) assigns a confidence score, perhaps boosted if recent motion aligns with a known routine.
4. The **automation layer** checks if presence confidence exceeds a configured threshold _and_ the room is dark.
5. A light turns on—this is exposed via the **interface layer** (e.g., `input_boolean.auto_lighting_enabled` toggle).
6. The **diagnostic layer** confirms the triggering sensor was registered and online, or it reports an anomaly.

This layered flow ensures modular growth and maintainability.

---

## 🧱 2.5 Deep Mechanics of the Core

Let’s dig deeper into how Hestia’s architecture actually ticks day-to-day: **how files are wired together**, how **dynamic behavior emerges from static YAML**, and **how the system stays override-friendly without losing determinism**.

Hestia operates more like an engine than a traditional Home Assistant config. The mechanics involve templating, data flattening, and runtime adaptation. This section peels back the curtain.

---

### 🧩 File Composition & Inclusion Strategy

Hestia leverages Home Assistant's `!include`, `!include_dir_merge_named`, and `!include_dir_merge_list` to maximum effect. Here's how they're used:

- **`!include`**: For single-file inserts (e.g., `hestia/core/system.yaml`)
- **`!include_dir_merge_named`**: To merge YAML dictionaries—ideal for grouped helpers, sensors, or package blocks.
- **`!include_dir_merge_list`**: For additive list structures like `automation:` blocks

#### 🔗 Examples:

```yaml
# configuration.yaml
sensor: !include_dir_merge_named hestia/core/
automation: !include_dir_merge_list hestia/automations/
```

This creates a flat view where multiple sources appear merged in HA’s runtime config—but still stay modular in code.

---

### 🧰 Core Mechanisms in Action

#### 1. **Registry-Centric Design**

Hestia leans on registry constructs: `room_registry`, `sensor_registry`, `device_registry`, etc., allowing new rooms/devices to be onboarded declaratively.

Example: `room_registry` entries define the room ID, type, and which systems apply.

```yaml
room_registry:
  bedroom_1:
    friendly_name: "Master Bedroom"
    systems:
      - hermes
      - theia
```

This drives inclusion logic and default settings across multiple packages. You don't "add a room" by copying files—you register it.

---

#### 2. **Data-Driven Template Logic**

Template sensors use Jinja2 to dynamically reference input values, conditions, and registry metadata.

```yaml
{{ state_attr('sensor.presence_abstraction_layer', 'confidence') | float > states('input_number.presence_threshold') | float }}
```

These templates often use `expand()` or `area_id` logic to operate across all matching devices by room or function, like:

```yaml
{% set sensors = expand('group.motion_sensors_bedroom_1') %}
```

---

#### 3. **Override-First Behavior**

Hestia allows override YAML at multiple levels:

- **Helper overrides** in `hestia/helpers/input_boolean.yaml`
- **Automation overrides** in `hestia/overrides/`
- **System behavior overrides** via metadata flags or `input_boolean.system_override_*`

These toggles are respected across the logic and automation layers. For instance:

```yaml
{% if is_state('input_boolean.auto_lighting_override', 'on') %}
  false
{% else %}
  logic_computed_value
{% endif %}
```

---

#### 4. **Implicit Relationships via Naming Standards**

Thanks to strict naming and registry systems (`sensor.presence_<room>`, `binary_sensor.motion_<device>`), dynamic references become predictable. This is vital for generic templates that scale across rooms and systems.

```yaml
sensor:
  - name: "presence_score_{{ room }}"
    unique_id: "presence_score_{{ room }}"
    state: >
      {{ states('sensor.motion_score_' ~ room) | float * 0.7 +
         states('sensor.audio_score_' ~ room) | float * 0.3 }}
```

---

### 💡 Dynamic, Yet Predictable

Despite YAML being static, Hestia achieves dynamic behavior by combining:

- **Registries** (define what exists)
- **Scoring Templates** (define how to evaluate)
- **System Flags & Overrides** (define when to bypass)
- **Namespacing** (definition of relationships between elements)

This ensures new hardware or rooms "just work" without hand-wiring them into automations.

---

### Methodology Deep-Dive: Weighted Signal Fusion in Hestia

Hestia’s approach to **weighted signal fusion** is not a one-off —it’s a recurring design pattern that underpins many of its “intelligent” subsystems (presence, lighting context, activity routines, etc.). At its core, it's an abstracted methodology that can and should be reused, adapted and evolved organically as the system grows.

#### 📌 What Is It?

Weighted fusion is Hestia’s “thinking” pattern—use it when reality isn’t binary, and your automations deserve to reason like a human would. More practically speaking, weighted signal fusion is the practice of **combining multiple data inputs** to generate **a single interpretive data outcome**, a result to which the various input components contribute with varying influence, in a process with many different use applications, such as presence confidence, scene suitability, lighting context, etc.

Rather than binary logic (`if motion then occupied`), this method assigns **proportional influence to signals**, allowing Hestia to reason probabilistically and degrade gracefully.

#### 🔄 General Fusion Process

1. **Signal Isolation**  
   Each input is converted into a normalized score (usually `0–100` or `0.0–1.0`), representing how strongly that input suggests a certain state.
   - E.g., recent motion → 90
   - Active audio detection → 60

2. **Weight Assignment**  
   Each signal is assigned a weight (`w`) representing its reliability or importance in context.
   - Motion (0.7), Audio (0.3)

3. **Fusion Logic**  
   A weighted sum or conditional aggregation is performed:

   ```yaml
   final_score = (motion_score * 0.7) + (audio_score * 0.3)
   ```

4. **Override Check (Optional)**  
   Manual or exceptional states override the score if active:

    ```yaml
   {% if override %}
     return 100
   {% endif %}
   ```

5. **Threshold Evaluation**  
   Final scores are then evaluated against thresholds (which may be helper-driven):

   ```yaml
   {% if final_score > states('input_number.presence_threshold') | float %}
     return 'occupied'
   {% endif %}
   ```

#### 🧬 Put into practice

- **Context Awareness**: Motion might be strong at night, but audio could be stronger during sedentary activities.
- **Fault Tolerance**: Missing or failing devices don’t collapse the logic entirely.
- **Flexibility**: You can add/remove signals without rewriting the core logic.
- **Transparency**: Score output can be visualized and debugged.

#### 🧰 Reusable Template Pattern

This structure appears in presence scoring, lighting readiness evaluations, and could be reused in routines, cleaning logic, or HVAC awareness:

```yaml
{% set motion = states('sensor.motion_score_' ~ room) | float(0) %}
{% set audio = states('sensor.audio_score_' ~ room) | float(0) %}
{% set override = is_state('input_boolean.presence_override_' ~ room, 'on') %}
{% if override %}
  100
{% else %}
  (motion * 0.7) + (audio * 0.3)
{% endif %}
```

#### 🛑 Common Pitfalls

- **Not normalized inputs**: Always convert raw sensors into bounded scores before fusion.
- **Static weights**: In some cases, weights should vary by mode (e.g., day vs. night).
- **Lack of diagnostics**: Missing signal sources can skew logic silently. Always back fusion with diagnostics (`sensor.missing_registry_entities`, etc.).

#### ✅ When to Use This

| Use Case | Fusion Target |
|----------|---------------|
| Presence Confidence | `sensor.presence_abstraction_layer` |
| Lighting Context | `sensor.room_lighting_suitability_score` |
| Room Activity | `sensor.room_routine_activity_score` |
| Cleaning Readiness | `sensor.room_cleaning_candidate_score` |

---

## 📚 Core System: Metadata & `room_registry`

Metadata is what makes Hestia **data-driven** instead of hardcoded -an understanding of its **metadata systems** and the all-important **`room_registry`** is crucial for getting the most out of HESTIA's architectural design, and what makes it *declarative*, scalable, and cleanly overrideable.

### **Purpose**

The metadata system externalizes context: it tells Hestia _what rooms exist_, _what type they are_, _what systems should apply_, and _how logic should behave per space_—all without touching logic code.

### **Artifacts**

- `/hestia/.../hephaestus_room_registry.yaml`

This file is a YAML dictionary, mapping each room to metadata like its name, systems, modes, and flags.

---

### **Structure Example**

```yaml
room_registry:
  bedroom_1:
    friendly_name: "Master Bedroom"
    systems:
      - hermes
      - theia
    lighting_enabled: true
    presence_enabled: true
    circadian_profile: relax
    override_exempt: false

  hallway_1:
    friendly_name: "Upstairs Hallway"
    systems:
      - hermes
    lighting_enabled: true
    presence_enabled: false
    circadian_profile: alert
    override_exempt: true
```

---

### **How It Works**

1. **Room Registration**  
   Each room is given a unique ID (`bedroom_1`, `hallway_1`, etc.), plus descriptive tags.

2. **System Routing**  
   The `systems` list determines which subsystem packages are activated for this room.

3. **Behavior Flags**  
   Fields like `lighting_enabled` and `override_exempt` guide logic execution:
   - `override_exempt: true` bypasses manual toggles in some automations
   - `circadian_profile` determines light presets

4. **Registry-Driven Templating**  
   Most Jinja2 templates load room metadata dynamically, like:

```jinja2
{% set meta = state_attr('sensor.room_registry', room) %}
{% if meta.lighting_enabled and (lux | float < 20) %}
  true
{% endif %}
```

5. **Automation Gating**  
   Automations check registry flags before executing to prevent unintended triggers.

---

### **Design Philosophy**

- **Declarative**: Rooms are _declared_, not manually coded into packages.
- **Scalable**: New rooms are onboarded in one place.
- **Configurable**: Behavior can be tweaked per room without rewriting logic.
- **Override-Safe**: Metadata gates logic from applying to incompatible rooms.

---

### **Helper Generation**

Registry data can also be used to dynamically generate:
- `input_boolean.auto_lighting_override_<room>`
- `input_boolean.presence_override_<room>`
- `group.motion_sensors_<room>`

If a room has `presence_enabled: true`, the system expects those helpers to exist and includes them in diagnostics.

---

### **Related Files**

| File | Role |
|------|------|
| `room_registry.yaml` | Core registry |
| `sensor_room_registry.yaml` | Exposes registry as a sensor for templates |
| `missing_registry_entities.yaml` | Validates registry vs entity state |
| `occupancy_evaluator.yaml` | Uses metadata to weight presence logic |

---

### **Pro Tip**

When adding a room:
1. Add an entry in `room_registry.yaml`
2. Ensure helpers and sensors are named correctly
3. Add to `device_registry.yaml` if needed
4. Validate via diagnostics view

---


---

## 🧩 Subsystem: Room Lighting (`theia`)

Let's dive into the subsystems starting with **Theia**, Hestia’s subsystem for lighting intelligence. It mirrors presence in structure but brings in **scene readiness**, **ambient context**, and **override-aware logic** for light automation.

### **Purpose**

Theia governs lighting behaviors across rooms—blending motion, presence, ambient light, and time of day into lighting context decisions. It's designed to feel intuitive: lights come on when they're _supposed_ to, not just because something moved.

---

### **Key Entities**

| Entity | Type | Purpose |
|--------|------|---------|
| `sensor.room_lighting_suitability_score` | Template Sensor | Contextual readiness score |
| `input_boolean.auto_lighting_override_<room>` | Helper | Manual control toggle |
| `binary_sensor.motion_event_recent` | Binary Sensor | Core motion input |
| `sensor.circadian_phase_<room>` | Sensor | Time-of-day lighting phase (from `theia`) |
| `sensor.lux_level_<room>` | Sensor | Current ambient light level |

---

### **Architecture**

Theia is implemented as a structured subsystem under:

- `/hestia/packages/theia/`
  - `lighting_core.yaml`: scoring and logic
  - `circadian_room_sensors.yaml`: circadian phase tagging
  - `automations_motion_lighting.yaml`: motion-based activation
  - `device_monitoring.yaml`: sensor health
- `/hestia/core/` contains shared abstractions (`light_abstraction.yaml`)
- `/templates/` contains fallbacks and overrides for lighting behavior

---

### **Design Story**

Early versions of lighting automations used `motion_detected → light.turn_on`. This worked—until it didn’t. Users hated:

- Lights turning on in well-lit rooms
- Brightness being wrong for time of day
- Reactions to non-human movement (e.g. dogs)

Theia’s design fixes this by fusing:

- **Presence confidence**
- **Ambient brightness**
- **Circadian “light zones”** (wake, relax, sleep)
- **Overrides and user modes**

This produced a context-aware score, making light decisions _feel_ human.

### **Logic Pipeline**

1. **Sensor Data**  
   Motion, lux sensors, circadian phase, and room presence are gathered.

2. **Suitability Score Calculation**  
   `sensor.room_lighting_suitability_score_<room>` weights motion presence, ambient light, and time-of-day.

3. **Override Check**  
   If `input_boolean.auto_lighting_override_<room>` is on, automation is blocked.

4. **Automation Triggers**  
   Automations evaluate:
   - Suitability score ≥ threshold
   - Lights are currently off
   - Room isn’t in "no disturb" mode

5. **Lighting Profiles Applied**  
   Scene, brightness, and color temperature are chosen via circadian phase.

### **Best Practices**

- Use `room_registry` to ensure rooms have `lighting_enabled: true`
- Set `input_boolean.auto_lighting_override_<room>` as needed
- Tag brightness presets per circadian phase
- Ensure `lux_level` sensors are accurate—misreading can block lighting

### **Example: Suitability Fusion Template**

```yaml
{% set motion = states('sensor.motion_score_' ~ room) | float %}
{% set presence = states('sensor.presence_abstraction_layer_' ~ room) | float %}
{% set lux = states('sensor.lux_level_' ~ room) | float %}
{% set override = is_state('input_boolean.auto_lighting_override_' ~ room, 'on') %}

{% if override %}
  0
{% else %}
  ((motion * 0.5) + (presence * 0.3)) * (1 if lux < 20 else 0)
{% endif %}
```

---

Theia is a great example of how Hestia uses the same core logic principles—**layered scoring, override awareness, dynamic thresholds**—and applies them to a completely different use case.
