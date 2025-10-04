# ═══════════════════════════════════════════════════════════════════════
# ▶ MOTION LIGHTING BLUEPRINT USAGE GUIDE ◀
# Asymmetric Presence Policy for Single Person + Untracked Housemate
# ═══════════════════════════════════════════════════════════════════════

## CRITICAL CONFIGURATION PATTERNS ##

### 1. DEFAULT MOTION PACKAGE INPUTS ###
```yaml
# NEVER block motion activation due to absence
presence_entity: ""                           # Leave blank by default
require_presence_for_activation: false        # CRITICAL: must be false
motion_entity: sensor.bedroom_motion          # Motion sensor (required)
light_entity: light.bedroom_main             # Light to control (required)

# Base timeout (always allow activation)
timeout_seconds: 120                         # Base timeout for all occupants
```

### 2. PRESENCE-ENHANCED BEHAVIORS (OPTIONAL) ###

#### A) Dynamic Timeout Based on Known Person Presence ####
```yaml
timeout_seconds: >-
  {% set base = states('var.motion_timeout_' ~ area) | int(120) %}
  {% set presence_sensor = 'binary_sensor.' ~ area ~ '_presence_beta' %}
  {% if is_state(presence_sensor, 'on') %}
    {{ base + 180 }}    # +3min when known person present
  {% else %}
    {{ base }}          # Normal timeout (untracked housemate gets standard time)
  {% endif %}
```

#### B) Brightness Enhancement for Known Person ####
```yaml
brightness_pct: >-
  {% set presence_sensor = 'binary_sensor.' ~ area ~ '_presence_beta' %}
  {% if is_state(presence_sensor, 'on') %}
    {{ 100 }}           # Full brightness for tracked person
  {% else %}
    {{ 60 }}            # Dimmer for untracked housemate (but still activate!)
  {% endif %}
```

#### C) Scene Selection Based on Presence ####
```yaml
scene_on: >-
  {% set presence_sensor = 'binary_sensor.' ~ area ~ '_presence_beta' %}
  {% if is_state(presence_sensor, 'on') %}
    scene.{{ area }}_bright     # Preferred scene for known person
  {% else %}
    scene.{{ area }}_comfortable # Gentle scene for untracked housemate
  {% endif %}
```

### 3. AREA-SPECIFIC RECOMMENDATIONS ###

#### Bedroom (Known Person's Space) ####
```yaml
# Safe to use presence enhancement - known person's private area
presence_entity: "binary_sensor.bedroom_presence_beta"
require_presence_for_activation: false      # Still false for safety
timeout_seconds: >-
  {% if is_state('binary_sensor.bedroom_presence_beta', 'on') %}
    {{ 300 }}   # 5min when person present
  {% else %}
    {{ 60 }}    # 1min baseline (rare untracked use)
  {% endif %}
```

#### Kitchen (Untracked Housemate Primary User) ####
```yaml
# Never use presence - untracked housemate cooks here
presence_entity: ""                         # Always blank
require_presence_for_activation: false      # Always false
timeout_seconds: 180                        # Fixed timeout for cooking activities
brightness_pct: 80                          # Standard brightness for all users
```

#### Ensuite (Untracked Housemate Primary User) ####
```yaml
# Never use presence - untracked housemate uses ensuite
presence_entity: ""                         # Always blank  
require_presence_for_activation: false      # Always false
timeout_seconds: 600                        # Long timeout for bathroom activities
brightness_pct: 40                          # Gentle lighting for all users
```

#### Living Room (Shared Space) ####
```yaml
# Optional light enhancement only - never blocking
presence_entity: ""                         # Recommend blank for shared space
require_presence_for_activation: false      # Always false
brightness_pct: >-
  {% if is_state('binary_sensor.living_room_presence_beta', 'on') %}
    {{ 90 }}    # Bright for known person entertainment
  {% else %}
    {{ 70 }}    # Standard for untracked housemate
  {% endif %}
```

#### Desk (Known Person's Workspace) ####
```yaml
# Enhanced presence logic with workstation indicators
presence_entity: "binary_sensor.desk_presence_beta"
require_presence_for_activation: false      # Still false for safety
timeout_seconds: >-
  {% if is_state('binary_sensor.desk_presence_beta', 'on') %}
    {{ 1800 }}  # 30min for work sessions
  {% else %}
    {{ 120 }}   # 2min baseline
  {% endif %}
brightness_pct: >-
  {% if is_state('binary_sensor.desk_presence_beta', 'on') %}
    {{ 100 }}   # Full task lighting
  {% else %}
    {{ 50 }}    # Ambient lighting
  {% endif %}
```

### 4. DEBUGGING & VALIDATION ###

#### Test Motion Activation (Critical Test) ####
```yaml
# Simulate motion when known person is away
# Motion MUST still activate lights for untracked housemate
test_scenario: "person.evert = not_home, motion triggered"
expected_result: "lights activate normally"
failure_mode: "lights don't activate = untracked housemate in dark"
```

#### Presence Sensor Debug Attributes ####
```yaml
# Check these attributes on presence sensors:
attributes:
  strategy: "asymmetric: presence enhances, absence never blocks"
  untracked_housemate_warning: "Motion activation must remain independent"
  persons: ["person.evert"]  # Should list tracked persons only
```

### 5. ANTI-PATTERNS (NEVER DO THIS) ###

#### ❌ WRONG: Requiring Presence ####
```yaml
# NEVER DO THIS - blocks untracked housemate
require_presence_for_activation: true       # ❌ BLOCKS UNTRACKED PERSON
condition:
  - condition: state
    entity_id: person.evert
    state: 'home'                           # ❌ BLOCKS WHEN AWAY
```

#### ❌ WRONG: Multiple Person Logic ####
```yaml
# NEVER DO THIS - assumes multiple people
condition:
  - condition: template
    value_template: >-
      {{ expand('person') | selectattr('state','equalto','home') | list | count >= 2 }}
      # ❌ REQUIRES 2+ PEOPLE - only 1 person tracked
```

#### ❌ WRONG: "House Empty" Logic ####
```yaml
# NEVER DO THIS - false assumption about occupancy
condition:
  - condition: template
    value_template: >-
      {{ expand('person') | selectattr('state','equalto','home') | list | count > 0 }}
      # ❌ ASSUMES NO PERSON = NO HUMANS
```

### 6. RECOMMENDED BLUEPRINT TEMPLATE ###

```yaml
# motion_light_asymmetric_presence.yaml
blueprint:
  name: Motion Light (Asymmetric Presence)
  description: Motion lighting with optional presence enhancement (never blocking)
  domain: automation
  input:
    motion_entity:
      name: Motion Sensor
      selector:
        entity:
          domain: binary_sensor
          device_class: motion
    light_entity:
      name: Light
      selector:
        entity:
          domain: light
    presence_entity:
      name: Presence Sensor (Optional Enhancement)
      description: Leave blank to never require presence
      default: ""
      selector:
        entity:
          domain: binary_sensor
          device_class: occupancy
    require_presence_for_activation:
      name: Require Presence (DANGEROUS - see docs)  
      description: "WARNING: Set to true only if you accept false negatives for untracked occupants"
      default: false
      selector:
        boolean:
    timeout_base:
      name: Base Timeout (seconds)
      default: 120
      selector:
        number:
          min: 30
          max: 3600
    timeout_presence_bonus:
      name: Presence Timeout Bonus (seconds)
      description: Extra time when known person present
      default: 180
      selector:
        number:
          min: 0
          max: 1800

trigger:
  - platform: state
    entity_id: !input motion_entity
    to: 'on'

condition:
  # CRITICAL: Only check presence if explicitly required AND entity provided
  - condition: template
    value_template: >-
      {% set require = require_presence_for_activation %}
      {% set entity = presence_entity %}
      {% if not require or entity == "" %}
        true
      {% else %}
        {{ is_state(entity, 'on') }}
      {% endif %}

action:
  - service: light.turn_on
    target:
      entity_id: !input light_entity
    data:
      brightness_pct: >-
        {% set entity = presence_entity %}
        {% if entity != "" and is_state(entity, 'on') %}
          {{ 90 }}    # Bright for known person
        {% else %}
          {{ 70 }}    # Standard for untracked person
        {% endif %}
  
  - delay:
      seconds: >-
        {% set base = timeout_base %}
        {% set bonus = timeout_presence_bonus %}  
        {% set entity = presence_entity %}
        {% if entity != "" and is_state(entity, 'on') %}
          {{ base + bonus }}
        {% else %}
          {{ base }}
        {% endif %}
  
  - service: light.turn_off
    target:
      entity_id: !input light_entity
```

## VALIDATION CHECKLIST ##
✅ Motion activates when person.evert = not_home
✅ require_presence_for_activation defaults to false everywhere  
✅ Presence sensors include untracked_housemate_warning
✅ Kitchen/ensuite sensors always return false (untracked primary users)
✅ Timeout/brightness enhancements work without blocking
✅ No logic assumes "no person = no humans"
✅ No logic requires multiple people for activation