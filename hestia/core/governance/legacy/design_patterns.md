
# HESTIA DESIGN PATTERNS

This document captures consistent structural and architectural decisions that should guide
future development and prevent entropy in subsystem design.

## Entity Naming
Pattern: `<domain>_<room>_<role>`
Example: `binary_sensor.living_room_motion`, `sensor.kitchen_temperature_score`

## Template Separation
Template logic must be isolated to:
- template_library.yaml (shared, generic)
- /templates/<subsystem>_templates.yaml (scoped)

## Subsystem Layout
Each subsystem should include:
- <subsystem>_config.yaml
- /templates/
- 0+ scripts and automations

$$$## 🔁 Sensor Abstractions

### 🧠 Use Canonical Aliases (`*_β`) Before Logic

All logic sensors should point to `*_β` aliases rather than raw device IDs. This decouples logic from hardware and aligns with the Hestia abstraction stack.

> 💡 *Always use canonical aliases when referring to motion, temperature, humidity, light, or occupancy inputs in logic layers.*

✅ Do:
```yaml
sensor.kitchen_motion_score:
  source: binary_sensor.kitchen_motion_β
```

❌ Don’t:
```yaml
source: binary_sensor.kitchen_pir_1
```

## 🧱 Tier Isolation

### 🚫 Never Skip Abstraction Tiers

Each logic sensor must only depend on its immediate lower abstraction tier. Skipping tiers violates architecture and introduces hard-to-debug failures.

✅ Do:
```yaml
sensor.bedroom_motion_score:
  source: binary_sensor.bedroom_motion_β
```

❌ Don’t:
```yaml
source: binary_sensor.bedroom_pir_α
```

---

## 🧪 Validation Layers

### ⚙️ Use Binary Outputs for Sanity Checks

Sanity wrappers like `*_sanity_checked` must return `on` or `off`. This avoids ambiguity and ensures compatibility with automations, sensors, and dashboards.

✅ Do:
```yaml
binary_sensor.kitchen_light_sanity_checked:
  state: >
    {{ states('sensor.kitchen_light_γ') not in ['unknown', 'unavailable'] }}
```

---

### 🔒 Wrap β Sensors in Validated Checks Before Use

Never trust alias layers blindly. Always introduce a validated layer to ensure upstream readiness.

✅ Do:
```yaml
binary_sensor.bedroom_motion_validated:
  state: >
    {{ is_state('binary_sensor.bedroom_motion_β', 'on') }}
```

---

### 🛡️ Keep Aliases (β) Logic-Free

Alias sensors must directly reflect raw states. Avoid embedding calculations or logic at this tier. β exists only to abstract the physical source.

✅ Do:
```yaml
binary_sensor.bedroom_occupancy_β:
  state: >
    {{ states('binary_sensor.bedroom_occupancy') }}
```

---

## 🔧 Template Best Practices

### 🛑 Always Use `float(0)` for Numeric State Reads

To handle sensors that may report `unknown` or `unavailable`, cast all numeric values using `| float(0)` as a safeguard.

✅ Do:
```yaml
{% set temp = states('sensor.kitchen_temperature_β') | float(0) %}
```

## ⏱️ Decay Scores

### ⛔ Prevent Decay Overflows

Decay sensors (`*_δ`) should never accumulate above their trigger threshold. Reset to 10, decay down — no stacking.

✅ Do:
```yaml
{% set decay.score = 10 if raw > 0 else max(decay.score - 0.5, 0) %}
```

---

### 🕓 Use Consistent Decay Timing Across Rooms

All `*_δ` sensors must decay using the same decrement logic to ensure system-wide predictability.

✅ Do:
```yaml
decay.score = decay.score - 0.5
```

---

## 🧠 Template Design

### 📦 Use `namespace()` for Stateful Logic

To retain and mutate variables across multiple lines, wrap state using Jinja2’s `namespace()` feature.

✅ Do:
```yaml
{% set decay = namespace(score=states('sensor.room_motion_δ') | float(0)) %}
```

---

## 🧩 Logic Composition

### ⚠️ Avoid Cross-Domain Logic in One Sensor

A single sensor should operate within one semantic domain. Split composite logic into separate layers.

❌ Don’t:
```yaml
{% if motion == 'on' and temp > 22 and lux < 30 %}
```

---

## 🔁 Template Reuse

### ♻️ Use Shared Scoring Formulas

Don’t copy-paste scoring logic across rooms. Build reusable macros or standardized blocks.

✅ Do:
```yaml
{% set temp_score = compute_temperature_score('sensor.kitchen_temperature_β') %}
```

## 🏛️ Motion Score Integrity

### 📏 Canonical Aliasing Is Required for Motion Abstractions

Every `motion_score` must point to a well-defined binary sensor alias. These aliases (`*_motion_β`) must be explicitly created from raw sensors.

✅ Do:
```yaml
binary_sensor.kitchen_motion:
  value_template: "{{ is_state('binary_sensor.kitchen_motion_sensor', 'on') }}"
```

❌ Don’t:
```yaml
sensor.kitchen_motion_score:
  source: binary_sensor.kitchen_motion_sensor
```

---

## 🧠 Presence Stack Layering

### 🧭 Define Final Presence Signals as Tier ζ

Presence outputs used in automation must not directly use raw sensors or scores. Instead, derive them from abstracted and validated `motion_score` + `occupancy_score` inputs.

✅ Do:
```yaml
binary_sensor.kitchen_presence_ζ:
  state: >
    {{ score('motion_γ') + score('occupancy_γ') > threshold }}
```

---

## 🧮 Greek Tier Naming Convention

Use tier suffixes to denote level of abstraction:

- `_α` → Raw device
- `_β` → Alias/template
- `_γ` → Scored logic
- `_δ` → Decay, aggregation, smoothing
- `_ε` → Validation
- `_ζ` → Final interpreted outputs

## 🏛️ Motion Score Integrity

### 📏 Canonical Aliasing Is Required for Motion Abstractions

Every `motion_score` must point to a well-defined binary sensor alias. These aliases (`*_motion_β`) must be explicitly created from raw sensors.

✅ Do:
```yaml
binary_sensor.kitchen_motion:
  value_template: "{{ is_state('binary_sensor.kitchen_motion_sensor', 'on') }}"
```

❌ Don’t:
```yaml
sensor.kitchen_motion_score:
  source: binary_sensor.kitchen_motion_sensor
```

---

## 🧠 Presence Stack Layering

### 🧭 Define Final Presence Signals as Tier ζ

Presence outputs used in automation must not directly use raw sensors or scores. Instead, derive them from abstracted and validated `motion_score` + `occupancy_score` inputs.

✅ Do:
```yaml
binary_sensor.kitchen_presence_ζ:
  state: >
    {{ score('motion_γ') + score('occupancy_γ') > threshold }}
```

---

## 🧮 Greek Tier Naming Convention

Use tier suffixes to denote level of abstraction:

- `_α` → Raw device
- `_β` → Alias/template
- `_γ` → Scored logic
- `_δ` → Decay, aggregation, smoothing
- `_ε` → Validation
- `_ζ` → Final interpreted outputs$$$

---

### Fallback-First Value Recovery

**Principle**: Always prefer live entity state when valid; fallback to last-known values when unavailable.

**Why**: Ensures resilience when devices disconnect, restart, or become momentarily unavailable. Maintains logical continuity and user experience.

✅ **Do**:
```yaml
value_template: >
  {% if states('light.foxy') in ['on', 'off'] %}
    {{ states('light.foxy') }}
  {% else %}
    {{ states('input_text.last_known_foxy_state') }}
  {% endif %}
```

❌ **Don't**:
```yaml
value_template: "{{ states('light.foxy') }}"  # No resilience, breaks if device unavailable
```

**Context**: Used in `phanes_generated_beta_light.yaml` to support light abstraction under connectivity loss.

---

### Metadata Injection in Abstractions

**Principle**: Validated (β-layer) entities should carry all critical metadata normally associated with physical (α-layer) devices.

**Why**: Aligns metadata with the semantic and functional reference layer. Eliminates dependency on device registries or physical state.

✅ **Do**:

```yaml
light.foxy_beta:
  attributes:
    canonical_alpha: light.foxy
    model: "Candle"
    manufacturer: "Philips"
    firmware: "1.33.0"
    integration: ["Matter", "Wiz"]
```

❌ **Don't**:

```yaml
# Separate metadata into a registry file
core/light_device_registry.yaml:
  - light.foxy:
      model: "Candle"
```

**Context**: Reflects move toward "tier-and-a-half" abstraction pattern.
