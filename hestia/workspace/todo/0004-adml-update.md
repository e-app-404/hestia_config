Here’s a tighter, execution-ready prompt you can drop into Copilot (or reuse with me), followed by the full YAML components that implement the **single-variable-per-room** design.

---

## Optimized prompt (copy-paste)

```
You are GitHub Copilot in VS Code. Refactor my Adaptive Motion Lighting (AML) package to use ONE consolidated var per room/subarea (e.g., var.bedroom_aml_config) that carries BOTH Adaptive Lighting and Motion settings. Do not ask questions. Apply exactly as specified and output a list of files changed.

## Rules
- Canonical root: /config. True HA packages: homeassistant.packages !include_dir_named packages
- Blueprints: /config/blueprints/automation/Blackshome/sensor-light.yaml
- AL light groups: 
  - Bedroom: light.adaptive_bedroom_light_group
  - Desk:    light.adaptive_desk_light_group
  - Kitchen: light.adaptive_kitchen_light_group
- Subareas (motion only): 
  - Ottoman:  light.group_ottoman_light
  - Wardrobe: light.group_wardrobe_light
- Hallways + Ensuite groups unchanged.
- Presence never gates activation. Use beta motion sensors and existing proxies.
- Use consolidated vars in automations **where runtime templating is supported** (timeouts, manual windows, AL enable/sleep). For blueprint inputs that require static entity_ids (motion_sensors, target_lights), keep explicit entities.
- Provide: 
  1) vars_consolidated.yaml — per-room var.*_aml_config with all attributes (AL + Motion).
  2) bypass_alias_sensors.yaml — binary_sensor.motion_bypass_* that mirror var.*.attributes.bypass.
  3) bridge_aml_config_to_al.yaml — one automation that reads a triggered var’s attributes (al_enabled, al_main, al_sleep, group, manual_override_until) and syncs AL.
  4) telemetry_last_triggered.yaml — stamp last_triggered on:
     - MOTION (primary beta/proxy sensors), and
     - LIGHT GROUP ON (canonical groups). Update the corresponding var.*_aml_config attribute.
- Keep YAML two-space indented; keys A→Z within each mapping; quote initial_state: "on".

## Important
- Use the following consolidated attributes for each var.*_aml_config:
  - al_enabled, al_main, al_sleep, group, manual_override_until, only_once, sleep
  - bypass, last_triggered, timeout_seconds
  - ambient_lux_entity, ambient_lux_threshold
  - inhibit_on_startup_seconds, motion_sensors (list), night_mode_* (enabled, brightness_pct, color_temp_mired, sun_elevation), only_if_lights_off, presence_entity, require_presence_for_activation, require_sun_condition, restore_state_after_restart, sun_max_elevation, sun_min_elevation
- Subareas (ottoman, wardrobe): al_enabled=false, al_main/al_sleep="".
- Do NOT remove existing motion_lights_* automations; but change their jinja’d fields (e.g., timeout_seconds) to read from the consolidated vars. Blueprint static entity lists remain explicit.
```

---

## YAML components (drop into `/config/packages/adaptive_motion_lighting/`)

### 1) `vars_consolidated.yaml`

```yaml
---
# AML — Consolidated per-room configuration variables (AL + Motion)

var:
  bedroom_aml_config:
    friendly_name: "Bedroom — AML Config"
    unique_id: var_bedroom_aml_config
    initial_value: normal
    restore: true
    attributes:
      al_enabled: true
      al_main: switch.adaptive_lighting_bedroom
      al_sleep: switch.adaptive_lighting_sleep_mode_bedroom
      ambient_lux_entity: sensor.bedroom_illuminance_beta
      ambient_lux_threshold: 10
      bypass: false
      group: light.adaptive_bedroom_light_group
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors: [binary_sensor.bedroom_motion_beta]
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 120

  desk_aml_config:
    friendly_name: "Desk — AML Config"
    unique_id: var_desk_aml_config
    initial_value: work
    restore: true
    attributes:
      al_enabled: true
      al_main: switch.adaptive_lighting_desk
      al_sleep: switch.adaptive_lighting_sleep_mode_desk
      ambient_lux_entity: ""
      ambient_lux_threshold: 10
      bypass: false
      group: light.adaptive_desk_light_group
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors: [binary_sensor.desk_motion_proxy]
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 300

  ensuite_aml_config:
    friendly_name: "Ensuite — AML Config"
    unique_id: var_ensuite_aml_config
    initial_value: normal
    restore: true
    attributes:
      al_enabled: true
      al_main: switch.adaptive_lighting_ensuite
      al_sleep: switch.adaptive_lighting_sleep_mode_ensuite
      ambient_lux_entity: ""
      ambient_lux_threshold: 10
      bypass: false
      group: light.group_ensuite_lights
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors: [binary_sensor.ensuite_motion_beta]
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 240

  kitchen_aml_config:
    friendly_name: "Kitchen — AML Config"
    unique_id: var_kitchen_aml_config
    initial_value: normal
    restore: true
    attributes:
      al_enabled: true
      al_main: switch.adaptive_lighting_kitchen
      al_sleep: switch.adaptive_lighting_sleep_mode_kitchen
      ambient_lux_entity: ""
      ambient_lux_threshold: 10
      bypass: false
      group: light.adaptive_kitchen_light_group
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors: [binary_sensor.kitchen_motion_beta]
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 300

  hallway_downstairs_aml_config:
    friendly_name: "Hallway Downstairs — AML Config"
    unique_id: var_hallway_downstairs_aml_config
    initial_value: transit
    restore: true
    attributes:
      al_enabled: true
      al_main: switch.adaptive_lighting_hallway_downstairs
      al_sleep: switch.adaptive_lighting_sleep_mode_hallway_downstairs
      ambient_lux_entity: ""
      ambient_lux_threshold: 10
      bypass: false
      group: light.group_hallway_lights_downstairs
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors: [binary_sensor.hallway_downstairs_motion_beta]
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 90

  hallway_upstairs_aml_config:
    friendly_name: "Hallway Upstairs — AML Config"
    unique_id: var_hallway_upstairs_aml_config
    initial_value: transit
    restore: true
    attributes:
      al_enabled: true
      al_main: switch.adaptive_lighting_hallway_upstairs
      al_sleep: switch.adaptive_lighting_sleep_mode_hallway_upstairs
      ambient_lux_entity: ""
      ambient_lux_threshold: 10
      bypass: false
      group: light.group_hallway_lights_upstairs
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors:
        - binary_sensor.hallway_upstairs_motion_beta
        - binary_sensor.hallway_downstairs_motion_recent_beta
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 90

  ottoman_aml_config:
    friendly_name: "Ottoman — AML Config"
    unique_id: var_ottoman_aml_config
    initial_value: brief
    restore: true
    attributes:
      al_enabled: false
      al_main: ""
      al_sleep: ""
      ambient_lux_entity: ""
      ambient_lux_threshold: 10
      bypass: false
      group: light.group_ottoman_light
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors: [binary_sensor.bedroom_ottoman_motion_proxy]
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 180

  wardrobe_aml_config:
    friendly_name: "Wardrobe — AML Config"
    unique_id: var_wardrobe_aml_config
    initial_value: brief
    restore: true
    attributes:
      al_enabled: false
      al_main: ""
      al_sleep: ""
      ambient_lux_entity: ""
      ambient_lux_threshold: 10
      bypass: false
      group: light.group_wardrobe_light
      inhibit_on_startup_seconds: 10
      last_triggered: ""
      motion_sensors: [binary_sensor.wardrobe_motion_beta]
      night_mode_brightness_pct: 12
      night_mode_color_temp_mired: 420
      night_mode_enabled: true
      night_mode_sun_elevation: -6
      only_if_lights_off: false
      only_once: true
      presence_entity: ""
      require_presence_for_activation: false
      require_sun_condition: false
      restore_state_after_restart: true
      sleep: false
      sun_max_elevation: 20
      sun_min_elevation: -12
      timeout_seconds: 180
```

---

### 2) `bypass_alias_sensors.yaml`

```yaml
---
# AML — Alias binary_sensors read the consolidated var's 'bypass' attribute.

template:
  - binary_sensor:
      - name: "Motion Bypass Bedroom"
        unique_id: motion_bypass_bedroom
        device_class: safety
        state: "{{ state_attr('var.bedroom_aml_config','bypass') | bool(false) }}"

      - name: "Motion Bypass Desk"
        unique_id: motion_bypass_desk
        device_class: safety
        state: "{{ state_attr('var.desk_aml_config','bypass') | bool(false) }}"

      - name: "Motion Bypass Ensuite"
        unique_id: motion_bypass_ensuite
        device_class: safety
        state: "{{ state_attr('var.ensuite_aml_config','bypass') | bool(false) }}"

      - name: "Motion Bypass Kitchen"
        unique_id: motion_bypass_kitchen
        device_class: safety
        state: "{{ state_attr('var.kitchen_aml_config','bypass') | bool(false) }}"

      - name: "Motion Bypass Hallway Downstairs"
        unique_id: motion_bypass_hallway_downstairs
        device_class: safety
        state: "{{ state_attr('var.hallway_downstairs_aml_config','bypass') | bool(false) }}"

      - name: "Motion Bypass Hallway Upstairs"
        unique_id: motion_bypass_hallway_upstairs
        device_class: safety
        state: "{{ state_attr('var.hallway_upstairs_aml_config','bypass') | bool(false) }}"

      - name: "Motion Bypass Ottoman"
        unique_id: motion_bypass_ottoman
        device_class: safety
        state: "{{ state_attr('var.ottoman_aml_config','bypass') | bool(false) }}"

      - name: "Motion Bypass Wardrobe"
        unique_id: motion_bypass_wardrobe
        device_class: safety
        state: "{{ state_attr('var.wardrobe_aml_config','bypass') | bool(false) }}"
```

---

### 3) `bridge_aml_config_to_al.yaml`

```yaml
---
# AML — Bridge consolidated vars → Adaptive Lighting switches & manual control.
# Triggers on any var.*_aml_config update or HA start; reads attributes from the
# triggered var to avoid duplicating room maps.

automation:
  - alias: AML Bridge — Room Config to Adaptive Lighting
    id: aml_bridge_room_config_to_al
    mode: restart
    trigger:
      - platform: state
        entity_id:
          - var.bedroom_aml_config
          - var.desk_aml_config
          - var.ensuite_aml_config
          - var.kitchen_aml_config
          - var.hallway_downstairs_aml_config
          - var.hallway_upstairs_aml_config
          - var.ottoman_aml_config
          - var.wardrobe_aml_config
      - platform: homeassistant
        event: start
    variables:
      var_entity: >-
        {% if trigger is defined and trigger.entity_id %}
          {{ trigger.entity_id }}
        {% else %}
          var.bedroom_aml_config
        {% endif %}
      al_enabled: "{{ state_attr(var_entity, 'al_enabled') | default(false) }}"
      al_main:    "{{ state_attr(var_entity, 'al_main')    | default('') }}"
      al_sleep:   "{{ state_attr(var_entity, 'al_sleep')   | default('') }}"
      group:      "{{ state_attr(var_entity, 'group')      | default('') }}"
      until_ts:   "{{ state_attr(var_entity, 'manual_override_until') | default('') }}"
    action:
      - choose:
          - conditions: "{{ al_main != '' }}"
            sequence:
              - choose:
                  - conditions: "{{ al_enabled | bool }}"
                    sequence:
                      - service: switch.turn_on
                        target: { entity_id: "{{ al_main }}" }
                  - conditions: "{{ not (al_enabled | bool) }}"
                    sequence:
                      - service: switch.turn_off
                        target: { entity_id: "{{ al_main }}" }
      - choose:
          - conditions: "{{ al_sleep != '' }}"
            sequence:
              - choose:
                  - conditions: "{{ (state_attr(var_entity, 'sleep') | default(false)) | bool }}"
                    sequence:
                      - service: switch.turn_on
                        target: { entity_id: "{{ al_sleep }}" }
                  - conditions: "{{ not (state_attr(var_entity, 'sleep') | default(false)) | bool }}"
                    sequence:
                      - service: switch.turn_off
                        target: { entity_id: "{{ al_sleep }}" }
      - choose:
          - conditions: "{{ al_main != '' and group != '' }}"
            sequence:
              - choose:
                  - conditions: "{{ until_ts != '' and now() < as_datetime(until_ts) }}"
                    sequence:
                      - service: adaptive_lighting.set_manual_control
                        data:
                          entity_id: "{{ al_main }}"
                          lights: ["{{ group }}"]
                          manual_control: true
                  - conditions: "{{ until_ts == '' or now() >= as_datetime(until_ts) }}"
                    sequence:
                      - service: adaptive_lighting.set_manual_control
                        data:
                          entity_id: "{{ al_main }}"
                          lights: ["{{ group }}"]
                          manual_control: false
```

---

### 4) `telemetry_last_triggered.yaml`

```yaml
---
# AML — Telemetry stamping for last_triggered (both motion-based and light-based)

# A) Motion-based stamps (captures intent even if light didn't turn on)
automation:
  - alias: AML Telemetry — Motion (Bedroom)
    id: aml_telemetry_motion_bedroom
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.bedroom_motion_beta
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.bedroom_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

  - alias: AML Telemetry — Motion (Desk)
    id: aml_telemetry_motion_desk
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.desk_motion_proxy
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.desk_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

  - alias: AML Telemetry — Motion (Ensuite)
    id: aml_telemetry_motion_ensuite
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.ensuite_motion_beta
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.ensuite_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

  - alias: AML Telemetry — Motion (Kitchen)
    id: aml_telemetry_motion_kitchen
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.kitchen_motion_beta
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.kitchen_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

  - alias: AML Telemetry — Motion (Hallway Downstairs)
    id: aml_telemetry_motion_hallway_downstairs
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.hallway_downstairs_motion_beta
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.hallway_downstairs_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

  - alias: AML Telemetry — Motion (Hallway Upstairs)
    id: aml_telemetry_motion_hallway_upstairs
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.hallway_upstairs_motion_beta
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.hallway_upstairs_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

  - alias: AML Telemetry — Motion (Ottoman)
    id: aml_telemetry_motion_ottoman
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.bedroom_ottoman_motion_proxy
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.ottoman_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

  - alias: AML Telemetry — Motion (Wardrobe)
    id: aml_telemetry_motion_wardrobe
    mode: single
    trigger:
      - platform: state
        entity_id: binary_sensor.wardrobe_motion_beta
        from: "off"
        to: "on"
    action:
      - service: var.set
        data:
          entity_id: var.wardrobe_aml_config
          attributes:
            last_triggered: "{{ now().isoformat() }}"

# B) Light-group ON stamps (confirms actual activation)
  - alias: AML Telemetry — Light ON (Groups)
    id: aml_telemetry_light_on_groups
    initial_state: "on"
    mode: parallel
    trigger:
      - platform: state
        entity_id:
          - light.adaptive_bedroom_light_group
          - light.adaptive_desk_light_group
          - light.group_ensuite_lights
          - light.adaptive_kitchen_light_group
          - light.group_hallway_lights_downstairs
          - light.group_hallway_lights_upstairs
          - light.group_ottoman_light
          - light.group_wardrobe_light
        to: "on"
    variables:
      map: >-
        {{ {
          'light.adaptive_bedroom_light_group': 'var.bedroom_aml_config',
          'light.adaptive_desk_light_group':    'var.desk_aml_config',
          'light.group_ensuite_lights':            'var.ensuite_aml_config',
          'light.adaptive_kitchen_light_group': 'var.kitchen_aml_config',
          'light.group_hallway_lights_downstairs': 'var.hallway_downstairs_aml_config',
          'light.group_hallway_lights_upstairs':   'var.hallway_upstairs_aml_config',
          'light.group_ottoman_light':             'var.ottoman_aml_config',
          'light.group_wardrobe_light':            'var.wardrobe_aml_config'
        } }}
      target_var: "{{ map.get(trigger.entity_id, '') }}"
    condition: "{{ target_var != '' }}"
    action:
      - service: var.set
        data:
          entity_id: "{{ target_var }}"
          attributes:
            last_triggered: "{{ now().isoformat() }}"
```

---

### How this consolidates duplication

* **One var per room** carries *all* AML knobs.
* **Bridge** reads attributes from the **triggered var** (no hardcoded room maps).
* **Bypass alias** reads the `bypass` attribute (no separate motion_profile var).
* **Telemetry** writes back to the same var (`last_triggered`).
* Motion automations still need static entity lists for blueprint inputs (HA limitation), but timeouts and other numeric flags can be pulled from the consolidated var (and you already do that).

If you want, I can also emit updated `motion_lights_*.yaml` showing how to read `timeout_seconds` and other non-entity options from these consolidated vars while keeping static entity lists for `motion_sensors` and `target_lights`.
