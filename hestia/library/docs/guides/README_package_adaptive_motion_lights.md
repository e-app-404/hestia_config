# Assumptions

* The **var integration** (HACS) is installed and enabled; variables declared under `domain/variables/*.yaml` are supported and restored on startup.
* The **Adaptive Lighting** integration (HACS) is installed; controller entities will be created with ids derived from `name:` (e.g., `switch.adaptive_lighting_bedroom`).
* The following *eta-tier* light groups exist and are correct for targeting:

  * `light.group_all_bedroom_lights`
  * `light.group_desk_lights`
  * `light.group_ensuite_lights`
  * `light.group_kitchen_lights`
  * `light.group_hallway_lights_downstairs`
  * `light.group_hallway_lights_upstairs`
  * `light.group_ottoman_lights` (optional; automation included herein)
* The following *beta-tier* motion/occupancy/illuminance sensors exist:

  * `binary_sensor.bedroom_motion_beta`
  * `binary_sensor.desk_motion_beta` (if not present, `binary_sensor.desk_occupancy_beta` is acceptable)
  * `binary_sensor.ensuite_motion_beta`, `binary_sensor.ensuite_occupancy_beta`
  * `binary_sensor.kitchen_motion_beta`, `binary_sensor.kitchen_occupancy_beta`
  * `binary_sensor.hallway_downstairs_motion_beta`, `binary_sensor.hallway_upstairs_motion_beta`
  * `sensor.bedroom_illuminance_beta`
* Hallway propagation will use a **recent-motion proxy** created below (`binary_sensor.hallway_downstairs_motion_recent_beta` with `delay_off: 20s`).
* An **α-sourced** vibration entity exists for the Ottoman composite: `binary_sensor.bedroom_bed_vibration_alpha`. This exception is allowed by ADR-0021 when explicitly documented; it is annotated in-file.

---

# Blueprint Inputs Whitelist

(Used for schema lock. Only these keys are permitted in `use_blueprint.input:`)

## `library/blueprints/sensor-light.yaml` (core motion→light)

* `ambient_lux_entity` (entity: sensor) — optional
* `ambient_lux_threshold` (number) — optional; effective only if `ambient_lux_entity` provided
* `bypass_entity` (entity: binary_sensor or boolean-like entity) — optional
* `inhibit_on_startup_seconds` (number) — optional
* `max_exceeded` (enum/string) — optional; recommend `silent`
* `mode` (enum/string) — optional; recommend `restart`
* `motion_sensors` (list of entity: binary_sensor) — **required** (≥1)
* `night_mode_brightness_pct` (number) — optional
* `night_mode_color_temp_mired` (number) — optional
* `night_mode_enabled` (boolean) — optional
* `night_mode_sun_elevation` (number) — optional
* `only_if_lights_off` (boolean) — optional
* `presence_entity` (entity) — optional; **presence must never gate**
* `require_presence_for_activation` (boolean) — **must be false**
* `require_sun_condition` (boolean) — optional
* `restore_state_after_restart` (boolean) — optional
* `sun_max_elevation` (number) — optional
* `sun_min_elevation` (number) — optional
* `target_lights` (list of entity: light) — **required** (≥1; eta-tier groups)
* `timeout_seconds` (number or template) — **required**
* `transition_seconds` (number) — optional

## `library/blueprints/sensor-light-add-on.yaml` (context add-on, e.g., cooking)

* `target_lights` (list of entity: light) — **required**
* `timeout_seconds` (number) — **required**
* `trigger_entities` (list of entity) — **required**
* `trigger_on_state` (string or list of strings) — **required**
* `trigger_off_state` (string or list of strings) — **required**

## `library/blueprints/ha-blueprint-linked-entities.yaml` (link/proxy)

* `delay_milliseconds` (number) — optional
* `linked_entities` (list of entity) — **required**

---

# Patch Set

## `domain/variables/room_profiles.yaml`

```yaml
room_profile_bedroom:
  friendly_name: "Room Profile — Bedroom"
  unique_id: var_room_profile_bedroom
  initial_value: normal
  restore: true
  icon: mdi:home-analytics
  attributes:
    al_enabled: true
    only_once: true
    sleep: false
    default_brightness_pct: 100
    default_ct_mired: 420
    night_brightness_pct: 12
    night_ct_mired: 420
    presence_boost_timeout: 120
    manual_override_until: ""
    last_event: ""

room_profile_desk:
  friendly_name: "Room Profile — Desk"
  unique_id: var_room_profile_desk
  initial_value: work
  restore: true
  icon: mdi:desk
  attributes:
    al_enabled: true
    only_once: true
    sleep: false
    default_brightness_pct: 100
    default_ct_mired: 420
    night_brightness_pct: 12
    night_ct_mired: 420
    presence_boost_timeout: 120
    manual_override_until: ""
    last_event: ""

room_profile_ensuite:
  friendly_name: "Room Profile — Ensuite"
  unique_id: var_room_profile_ensuite
  initial_value: normal
  restore: true
  icon: mdi:shower
  attributes:
    al_enabled: true
    only_once: true
    sleep: false
    default_brightness_pct: 100
    default_ct_mired: 420
    night_brightness_pct: 12
    night_ct_mired: 420
    presence_boost_timeout: 60
    manual_override_until: ""
    last_event: ""

room_profile_kitchen:
  friendly_name: "Room Profile — Kitchen"
  unique_id: var_room_profile_kitchen
  initial_value: normal
  restore: true
  icon: mdi:stove
  attributes:
    al_enabled: true
    only_once: true
    sleep: false
    default_brightness_pct: 100
    default_ct_mired: 420
    night_brightness_pct: 12
    night_ct_mired: 420
    presence_boost_timeout: 120
    manual_override_until: ""
    last_event: ""

room_profile_hallway_downstairs:
  friendly_name: "Room Profile — Hallway Downstairs"
  unique_id: var_room_profile_hallway_downstairs
  initial_value: transit
  restore: true
  icon: mdi:stairs-down
  attributes:
    al_enabled: true
    only_once: true
    sleep: false
    default_brightness_pct: 100
    default_ct_mired: 420
    night_brightness_pct: 12
    night_ct_mired: 420
    presence_boost_timeout: 60
    manual_override_until: ""
    last_event: ""

room_profile_hallway_upstairs:
  friendly_name: "Room Profile — Hallway Upstairs"
  unique_id: var_room_profile_hallway_upstairs
  initial_value: transit
  restore: true
  icon: mdi:stairs-up
  attributes:
    al_enabled: true
    only_once: true
    sleep: false
    default_brightness_pct: 100
    default_ct_mired: 420
    night_brightness_pct: 12
    night_ct_mired: 420
    presence_boost_timeout: 60
    manual_override_until: ""
    last_event: ""
```

## `domain/variables/motion_variables.yaml`

```yaml
motion_bypass_bedroom:
  friendly_name: "Motion Bypass — Bedroom"
  unique_id: var_motion_bypass_bedroom
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: bedroom
    last_toggled: ""

motion_last_triggered_bedroom:
  friendly_name: "Last Motion — Bedroom"
  unique_id: var_motion_last_triggered_bedroom
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    area: bedroom
    sensor_id: ""

motion_timeout_bedroom:
  friendly_name: "Motion Timeout — Bedroom (sec)"
  unique_id: var_motion_timeout_bedroom
  initial_value: 120
  restore: true
  unit_of_measurement: seconds
  icon: mdi:timer-outline
  attributes:
    area: bedroom
    min: 5
    max: 1800

motion_bypass_desk:
  friendly_name: "Motion Bypass — Desk"
  unique_id: var_motion_bypass_desk
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: desk
    last_toggled: ""

motion_last_triggered_desk:
  friendly_name: "Last Motion — Desk"
  unique_id: var_motion_last_triggered_desk
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    area: desk
    sensor_id: ""

motion_timeout_desk:
  friendly_name: "Motion Timeout — Desk (sec)"
  unique_id: var_motion_timeout_desk
  initial_value: 300
  restore: true
  unit_of_measurement: seconds
  icon: mdi:timer-outline
  attributes:
    area: desk
    min: 30
    max: 3600

motion_bypass_ensuite:
  friendly_name: "Motion Bypass — Ensuite"
  unique_id: var_motion_bypass_ensuite
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: ensuite
    last_toggled: ""

motion_last_triggered_ensuite:
  friendly_name: "Last Motion — Ensuite"
  unique_id: var_motion_last_triggered_ensuite
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    area: ensuite
    sensor_id: ""

motion_timeout_ensuite:
  friendly_name: "Motion Timeout — Ensuite (sec)"
  unique_id: var_motion_timeout_ensuite
  initial_value: 240
  restore: true
  unit_of_measurement: seconds
  icon: mdi:timer-outline
  attributes:
    area: ensuite
    min: 5
    max: 1800

motion_bypass_kitchen:
  friendly_name: "Motion Bypass — Kitchen"
  unique_id: var_motion_bypass_kitchen
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: kitchen
    last_toggled: ""

motion_last_triggered_kitchen:
  friendly_name: "Last Motion — Kitchen"
  unique_id: var_motion_last_triggered_kitchen
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    area: kitchen
    sensor_id: ""

motion_timeout_kitchen:
  friendly_name: "Motion Timeout — Kitchen (sec)"
  unique_id: var_motion_timeout_kitchen
  initial_value: 300
  restore: true
  unit_of_measurement: seconds
  icon: mdi:timer-outline
  attributes:
    area: kitchen
    min: 5
    max: 1800

motion_bypass_hallway_downstairs:
  friendly_name: "Motion Bypass — Hallway Downstairs"
  unique_id: var_motion_bypass_hallway_downstairs
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: hallway_downstairs
    last_toggled: ""

motion_last_triggered_hallway_downstairs:
  friendly_name: "Last Motion — Hallway Downstairs"
  unique_id: var_motion_last_triggered_hallway_downstairs
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    area: hallway_downstairs
    sensor_id: ""

motion_timeout_hallway_downstairs:
  friendly_name: "Motion Timeout — Hallway Downstairs (sec)"
  unique_id: var_motion_timeout_hallway_downstairs
  initial_value: 90
  restore: true
  unit_of_measurement: seconds
  icon: mdi:timer-outline
  attributes:
    area: hallway_downstairs
    min: 15
    max: 900

motion_bypass_hallway_upstairs:
  friendly_name: "Motion Bypass — Hallway Upstairs"
  unique_id: var_motion_bypass_hallway_upstairs
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: hallway_upstairs
    last_toggled: ""

motion_last_triggered_hallway_upstairs:
  friendly_name: "Last Motion — Hallway Upstairs"
  unique_id: var_motion_last_triggered_hallway_upstairs
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    area: hallway_upstairs
    sensor_id: ""

motion_timeout_hallway_upstairs:
  friendly_name: "Motion Timeout — Hallway Upstairs (sec)"
  unique_id: var_motion_timeout_hallway_upstairs
  initial_value: 90
  restore: true
  unit_of_measurement: seconds
  icon: mdi:timer-outline
  attributes:
    area: hallway_upstairs
    min: 15
    max: 900

motion_bypass_ottoman:
  friendly_name: "Motion Bypass — Ottoman"
  unique_id: var_motion_bypass_ottoman
  initial_value: false
  restore: true
  icon: mdi:motion-sensor-off
  attributes:
    area: ottoman
    last_toggled: ""

motion_last_triggered_ottoman:
  friendly_name: "Last Motion — Ottoman"
  unique_id: var_motion_last_triggered_ottoman
  initial_value: ""
  restore: true
  icon: mdi:motion-sensor
  attributes:
    area: ottoman
    sensor_id: ""

motion_timeout_ottoman:
  friendly_name: "Motion Timeout — Ottoman (sec)"
  unique_id: var_motion_timeout_ottoman
  initial_value: 180
  restore: true
  unit_of_measurement: seconds
  icon: mdi:timer-outline
  attributes:
    area: ottoman
    min: 5
    max: 1800
```

## `packages/helpers/_bypass_sensors.yaml`

```yaml
template:
  - binary_sensor:
      - name: "Motion Bypass Bedroom"
        unique_id: motion_bypass_bedroom
        device_class: safety
        state: "{{ states('var.motion_bypass_bedroom') in ['true','on','1'] }}"
      - name: "Motion Bypass Desk"
        unique_id: motion_bypass_desk
        device_class: safety
        state: "{{ states('var.motion_bypass_desk') in ['true','on','1'] }}"
      - name: "Motion Bypass Ensuite"
        unique_id: motion_bypass_ensuite
        device_class: safety
        state: "{{ states('var.motion_bypass_ensuite') in ['true','on','1'] }}"
      - name: "Motion Bypass Kitchen"
        unique_id: motion_bypass_kitchen
        device_class: safety
        state: "{{ states('var.motion_bypass_kitchen') in ['true','on','1'] }}"
      - name: "Motion Bypass Hallway Downstairs"
        unique_id: motion_bypass_hallway_downstairs
        device_class: safety
        state: "{{ states('var.motion_bypass_hallway_downstairs') in ['true','on','1'] }}"
      - name: "Motion Bypass Hallway Upstairs"
        unique_id: motion_bypass_hallway_upstairs
        device_class: safety
        state: "{{ states('var.motion_bypass_hallway_upstairs') in ['true','on','1'] }}"
      - name: "Motion Bypass Ottoman"
        unique_id: motion_bypass_ottoman
        device_class: safety
        state: "{{ states('var.motion_bypass_ottoman') in ['true','on','1'] }}"
```

## `packages/helpers/hallway_motion_recent.yaml`

```yaml
template:
  - binary_sensor:
      - name: "Hallway Downstairs Motion Recent (beta)"
        unique_id: hallway_downstairs_motion_recent_beta
        device_class: motion
        state: "{{ is_state('binary_sensor.hallway_downstairs_motion_beta','on') }}"
        delay_off: "00:00:20"
        attributes:
          area: hallway_downstairs
          decay_rate: 0.7
          tier: beta
```

## `packages/helpers/ottoman_motion_beta.yaml`

```yaml
# ADR-0021 Exception: α-sourced composite promoted to β for Ottoman.
# Rationale: minimize helper sprawl; reuse reliable α vibration source with explicit provenance.
# Source entity: binary_sensor.bedroom_bed_vibration_alpha
template:
  - binary_sensor:
      - name: "Ottoman Motion (beta)"
        unique_id: motion_beta_ottoman
        device_class: motion
        state: "{{ is_state('binary_sensor.bedroom_bed_vibration_alpha','on') }}"
        availability: "{{ states('binary_sensor.bedroom_bed_vibration_alpha') not in ['unknown','unavailable','none',''] }}"
        delay_off: "00:00:45"
        attributes:
          area: ottoman
          source: binary_sensor.bedroom_bed_vibration_alpha
          tier: beta
```

## `packages/adaptive_lighting/rooms.yaml`

```yaml
adaptive_lighting:
  - name: bedroom
    lights:
      - light.group_all_bedroom_lights
    only_once: true
    take_over_control: true
    initial_transition: 0.3
    transition: 2

  - name: desk
    lights:
      - light.group_desk_lights
    only_once: true
    take_over_control: true
    initial_transition: 0.3
    transition: 2

  - name: ensuite
    lights:
      - light.group_ensuite_lights
    only_once: true
    take_over_control: true
    initial_transition: 0.3
    transition: 2

  - name: kitchen
    lights:
      - light.group_kitchen_lights
    only_once: true
    take_over_control: true
    initial_transition: 0.3
    transition: 2

  - name: hallway_downstairs
    lights:
      - light.group_hallway_lights_downstairs
    only_once: true
    take_over_control: true
    initial_transition: 0.3
    transition: 2

  - name: hallway_upstairs
    lights:
      - light.group_hallway_lights_upstairs
    only_once: true
    take_over_control: true
    initial_transition: 0.3
    transition: 2

  # Optional additional controllers may be added separately for ottoman/hifi when groups are formalized.
```

## `packages/room_profiles/bridge_all_rooms.yaml`

```yaml
automation:
  - alias: Room Profiles → Adaptive Lighting Sync (All Rooms)
    id: room_profiles_to_al_all_rooms
    initial_state: "on"
    mode: restart
    trigger:
      - platform: state
        entity_id:
          - var.room_profile_bedroom
          - var.room_profile_desk
          - var.room_profile_ensuite
          - var.room_profile_kitchen
          - var.room_profile_hallway_downstairs
          - var.room_profile_hallway_upstairs
      - platform: homeassistant
        event: start
    variables:
      room_map: >-
        {{ {
          'bedroom': {
            'al_main': 'switch.adaptive_lighting_bedroom',
            'al_sleep': 'switch.adaptive_lighting_sleep_mode_bedroom',
            'group':   'light.group_all_bedroom_lights'
          },
          'desk': {
            'al_main': 'switch.adaptive_lighting_desk',
            'al_sleep': 'switch.adaptive_lighting_sleep_mode_desk',
            'group':   'light.group_desk_lights'
          },
          'ensuite': {
            'al_main': 'switch.adaptive_lighting_ensuite',
            'al_sleep': 'switch.adaptive_lighting_sleep_mode_ensuite',
            'group':   'light.group_ensuite_lights'
          },
          'kitchen': {
            'al_main': 'switch.adaptive_lighting_kitchen',
            'al_sleep': 'switch.adaptive_lighting_sleep_mode_kitchen',
            'group':   'light.group_kitchen_lights'
          },
          'hallway_downstairs': {
            'al_main': 'switch.adaptive_lighting_hallway_downstairs',
            'al_sleep': 'switch.adaptive_lighting_sleep_mode_hallway_downstairs',
            'group':   'light.group_hallway_lights_downstairs'
          },
          'hallway_upstairs': {
            'al_main': 'switch.adaptive_lighting_hallway_upstairs',
            'al_sleep': 'switch.adaptive_lighting_sleep_mode_hallway_upstairs',
            'group':   'light.group_hallway_lights_upstairs'
          }
        } }}
      changed_room: >-
        {% if trigger is defined and trigger.platform == 'state' and 'var.room_profile_' in trigger.entity_id %}
          {{ trigger.entity_id.split('var.room_profile_')[1] }}
        {% else %} all {% endif %}
      rooms: >-
        {% if changed_room == 'all' %}
          {{ room_map.keys() | list }}
        {% else %}
          {{ [changed_room] }}
        {% endif %}
    action:
      - if:
          - condition: template
            value_template: "{{ trigger.platform == 'homeassistant' }}"
        then:
          - variables:
              rooms: "{{ room_map.keys() | list }}"
      - repeat:
          for_each: "{{ rooms }}"
          sequence:
            - variables:
                current_room: "{{ repeat.item }}"
                main_switch: "{{ room_map[current_room]['al_main'] }}"
                sleep_switch: "{{ room_map[current_room]['al_sleep'] }}"
                group_light: "{{ room_map[current_room]['group'] }}"
                al_enabled: "{{ state_attr('var.room_profile_' ~ current_room, 'al_enabled') | default(true) }}"
                sleep_flag: "{{ state_attr('var.room_profile_' ~ current_room, 'sleep') | default(false) }}"
            - choose:
                - conditions: "{{ al_enabled | bool }}"
                  sequence:
                    - service: switch.turn_on
                      target: { entity_id: "{{ main_switch }}" }
                - conditions: "{{ not (al_enabled | bool) }}"
                  sequence:
                    - service: switch.turn_off
                      target: { entity_id: "{{ main_switch }}" }
            - choose:
                - conditions: "{{ sleep_flag | bool }}"
                  sequence:
                    - service: switch.turn_on
                      target: { entity_id: "{{ sleep_switch }}" }
                - conditions: "{{ not (sleep_flag | bool) }}"
                  sequence:
                    - service: switch.turn_off
                      target: { entity_id: "{{ sleep_switch }}" }
            - choose:
                - conditions: "{{ al_enabled | bool }}"
                  sequence:
                    - service: adaptive_lighting.set_manual_control
                      data:
                        entity_id: "{{ main_switch }}"
                        lights: [ "{{ group_light }}" ]
                        manual_control: false
```

## `packages/motion_lights/motion_lights_bedroom.yaml`

```yaml
automation:
  - alias: Motion Lights — Bedroom
    id: motion_lights_bedroom
    description: Motion-driven; AL handles brightness/CT; presence never gates.
    initial_state: "on"
    max_exceeded: silent
    mode: restart
    use_blueprint:
      path: library/blueprints/sensor-light.yaml
      input:
        ambient_lux_entity: sensor.bedroom_illuminance_beta
        ambient_lux_threshold: 10
        bypass_entity: binary_sensor.motion_bypass_bedroom
        inhibit_on_startup_seconds: 10
        motion_sensors:
          - binary_sensor.bedroom_motion_beta
        night_mode_brightness_pct: 12
        night_mode_color_temp_mired: 420
        night_mode_enabled: true
        night_mode_sun_elevation: -6
        only_if_lights_off: false
        presence_entity: ""
        require_presence_for_activation: false
        require_sun_condition: false
        restore_state_after_restart: true
        sun_max_elevation: 20
        sun_min_elevation: -12
        target_lights:
          - light.group_all_bedroom_lights
        timeout_seconds: "{{ states('var.motion_timeout_bedroom') | int(120) }}"
        transition_seconds: 0.3
```

## `packages/motion_lights/motion_lights_desk.yaml`

```yaml
automation:
  - alias: Motion Lights — Desk
    id: motion_lights_desk
    description: Task lighting; AL handles brightness/CT; presence never gates.
    initial_state: "on"
    max_exceeded: silent
    mode: restart
    use_blueprint:
      path: library/blueprints/sensor-light.yaml
      input:
        bypass_entity: binary_sensor.motion_bypass_desk
        inhibit_on_startup_seconds: 10
        motion_sensors:
          - binary_sensor.desk_motion_proxy
        night_mode_brightness_pct: 12
        night_mode_color_temp_mired: 420
        night_mode_enabled: true
        night_mode_sun_elevation: -6
        only_if_lights_off: false
        presence_entity: ""
        require_presence_for_activation: false
        require_sun_condition: false
        restore_state_after_restart: true
        sun_max_elevation: 20
        sun_min_elevation: -12
        target_lights:
          - light.group_desk_lights
        timeout_seconds: "{{ states('var.motion_timeout_desk') | int(300) }}"
        transition_seconds: 0.3
```

## `packages/motion_lights/motion_lights_ensuite.yaml`

```yaml
automation:
  - alias: Motion Lights — Ensuite
    id: motion_lights_ensuite
    description: Privacy-aware; AL handles brightness/CT; presence never gates.
    initial_state: "on"
    max_exceeded: silent
    mode: restart
    use_blueprint:
      path: library/blueprints/sensor-light.yaml
      input:
        bypass_entity: binary_sensor.motion_bypass_ensuite
        inhibit_on_startup_seconds: 10
        motion_sensors:
          - binary_sensor.ensuite_motion_beta
          - binary_sensor.ensuite_occupancy_beta
        night_mode_brightness_pct: 12
        night_mode_color_temp_mired: 420
        night_mode_enabled: true
        night_mode_sun_elevation: -6
        only_if_lights_off: false
        presence_entity: ""
        require_presence_for_activation: false
        require_sun_condition: false
        restore_state_after_restart: true
        sun_max_elevation: 20
        sun_min_elevation: -12
        target_lights:
          - light.group_ensuite_lights
        timeout_seconds: "{{ states('var.motion_timeout_ensuite') | int(240) }}"
        transition_seconds: 0.3
```

## `packages/motion_lights/motion_lights_kitchen.yaml`

```yaml
automation:
  - alias: Motion Lights — Kitchen
    id: motion_lights_kitchen
    description: Main area; AL handles brightness/CT; presence never gates.
    initial_state: "on"
    max_exceeded: silent
    mode: restart
    use_blueprint:
      path: library/blueprints/sensor-light.yaml
      input:
        bypass_entity: binary_sensor.motion_bypass_kitchen
        inhibit_on_startup_seconds: 10
        motion_sensors:
          - binary_sensor.kitchen_motion_beta
          - binary_sensor.kitchen_occupancy_beta
        night_mode_brightness_pct: 12
        night_mode_color_temp_mired: 420
        night_mode_enabled: true
        night_mode_sun_elevation: -6
        only_if_lights_off: false
        presence_entity: ""
        require_presence_for_activation: false
        require_sun_condition: false
        restore_state_after_restart: true
        sun_max_elevation: 20
        sun_min_elevation: -12
        target_lights:
          - light.group_kitchen_lights
        timeout_seconds: "{{ states('var.motion_timeout_kitchen') | int(300) }}"
        transition_seconds: 0.3
```

## `packages/motion_lights/motion_lights_hallway_downstairs.yaml`

```yaml
automation:
  - alias: Motion Lights — Hallway Downstairs
    id: motion_lights_hallway_downstairs
    description: Transit lighting; short timeout; AL handles brightness/CT.
    initial_state: "on"
    max_exceeded: silent
    mode: restart
    use_blueprint:
      path: library/blueprints/sensor-light.yaml
      input:
        bypass_entity: binary_sensor.motion_bypass_hallway_downstairs
        inhibit_on_startup_seconds: 10
        motion_sensors:
          - binary_sensor.hallway_downstairs_motion_beta
        night_mode_brightness_pct: 12
        night_mode_color_temp_mired: 420
        night_mode_enabled: true
        night_mode_sun_elevation: -6
        only_if_lights_off: false
        presence_entity: ""
        require_presence_for_activation: false
        require_sun_condition: false
        restore_state_after_restart: true
        sun_max_elevation: 20
        sun_min_elevation: -12
        target_lights:
          - light.group_hallway_lights_downstairs
        timeout_seconds: "{{ states('var.motion_timeout_hallway_downstairs') | int(90) }}"
        transition_seconds: 0.3
```

## `packages/motion_lights/motion_lights_hallway_upstairs.yaml`

```yaml
automation:
  - alias: Motion Lights — Hallway Upstairs
    id: motion_lights_hallway_upstairs
    description: Transit lighting with recent-motion propagation; AL handles brightness/CT.
    initial_state: "on"
    max_exceeded: silent
    mode: restart
    use_blueprint:
      path: library/blueprints/sensor-light.yaml
      input:
        bypass_entity: binary_sensor.motion_bypass_hallway_upstairs
        inhibit_on_startup_seconds: 10
        motion_sensors:
          - binary_sensor.hallway_upstairs_motion_beta
          - binary_sensor.hallway_downstairs_motion_recent_beta
        night_mode_brightness_pct: 12
        night_mode_color_temp_mired: 420
        night_mode_enabled: true
        night_mode_sun_elevation: -6
        only_if_lights_off: false
        presence_entity: ""
        require_presence_for_activation: false
        require_sun_condition: false
        restore_state_after_restart: true
        sun_max_elevation: 20
        sun_min_elevation: -12
        target_lights:
          - light.group_hallway_lights_upstairs
        timeout_seconds: "{{ states('var.motion_timeout_hallway_upstairs') | int(90) }}"
        transition_seconds: 0.3
```

## `packages/motion_lights/motion_lights_ottoman.yaml`

```yaml
automation:
  - alias: Motion Lights — Ottoman
    id: motion_lights_ottoman
    description: Subarea lighting via α-sourced composite (documented); AL optional.
    initial_state: "on"
    max_exceeded: silent
    mode: restart
    use_blueprint:
      path: library/blueprints/sensor-light.yaml
      input:
        bypass_entity: binary_sensor.motion_bypass_ottoman
        inhibit_on_startup_seconds: 10
        motion_sensors:
          - binary_sensor.ottoman_motion_beta
        night_mode_brightness_pct: 12
        night_mode_color_temp_mired: 420
        night_mode_enabled: true
        night_mode_sun_elevation: -6
        only_if_lights_off: false
        presence_entity: ""
        require_presence_for_activation: false
        require_sun_condition: false
        restore_state_after_restart: true
        sun_max_elevation: 20
        sun_min_elevation: -12
        target_lights:
          - light.group_ottoman_lights
        timeout_seconds: "{{ states('var.motion_timeout_ottoman') | int(180) }}"
        transition_seconds: 0.3
```

## `packages/linked/kitchen_to_laundry.yaml`

```yaml
automation:
  - alias: Linked Entities — Kitchen → Laundry (one-way)
    id: link_kitchen_to_laundry
    initial_state: "on"
    mode: restart
    trigger:
      - platform: state
        entity_id: light.group_kitchen_lights
    action:
      - choose:
          - conditions: "{{ trigger.to_state.state == 'on' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.group_laundry_room_lights
          - conditions: "{{ trigger.to_state.state == 'off' }}"
            sequence:
              - service: light.turn_off
                target:
                  entity_id: light.group_laundry_room_lights
```

## `devtools/templates/al_room_audit.jinja2`

```jinja
{% set rooms = ['bedroom','desk','ensuite','kitchen','hallway_downstairs','hallway_upstairs','ottoman'] %}
{% set al_main = {
  'bedroom':'switch.adaptive_lighting_bedroom',
  'desk':'switch.adaptive_lighting_desk',
  'ensuite':'switch.adaptive_lighting_ensuite',
  'kitchen':'switch.adaptive_lighting_kitchen',
  'hallway_downstairs':'switch.adaptive_lighting_hallway_downstairs',
  'hallway_upstairs':'switch.adaptive_lighting_hallway_upstairs',
  'ottoman':'switch.adaptive_lighting_ottoman' } %}
{% set group = {
  'bedroom':'light.group_all_bedroom_lights',
  'desk':'light.group_desk_lights',
  'ensuite':'light.group_ensuite_lights',
  'kitchen':'light.group_kitchen_lights',
  'hallway_downstairs':'light.group_hallway_lights_downstairs',
  'hallway_upstairs':'light.group_hallway_lights_upstairs',
  'ottoman':'light.group_ottoman_lights' } %}
{% set timeout = {
  'bedroom':'var.motion_timeout_bedroom',
  'desk':'var.motion_timeout_desk',
  'ensuite':'var.motion_timeout_ensuite',
  'kitchen':'var.motion_timeout_kitchen',
  'hallway_downstairs':'var.motion_timeout_hallway_downstairs',
  'hallway_upstairs':'var.motion_timeout_hallway_upstairs',
  'ottoman':'var.motion_timeout_ottoman' } %}

# Adaptive Lighting & Motion Audit
{% for r in rooms %}
### {{ r }}
- **AL switch**: {{ al_main[r] }} → {{ states(al_main[r]) | default('unknown') }}
- **Motion timeout**: {{ timeout[r] }} → {{ states(timeout[r]) | default('n/a') }} sec
- **Group light**: {{ group[r] }} → {{ states(group[r]) | default('unknown') }}
  {% set scms = state_attr(group[r], 'supported_color_modes') or [] %}
  {% set supports_ct = 'color_temp' in scms %}
  - supports_color_temp: {{ supports_ct }} (modes: {{ scms }})
- **Guard**:
  {% set al_enabled = true if r in ['bedroom','desk','ensuite','kitchen','hallway_downstairs','hallway_upstairs'] else false %}
  {% if al_enabled %}⚠️ AL enabled — motion package must not set brightness/CT.
  {% else %}✅ AL disabled — motion fallback brightness/CT may apply.{% endif %}
---
{% endfor %}
```

## `README_ADAPTIVE_MOTION_LIGHTING.md`

````md
# Adaptive Motion Lighting (Self-Contained Package)

## What this ships
- **Variables (var integration):** per-room motion bypass, timeout (seconds), last-triggered; per-room **room profile** (AL policy).
- **Helper sensors:** binary_sensor.* alias for bypass; hallway recent-motion proxy (20 s, `decay_rate: 0.7` attr); optional α→β Ottoman composite with provenance annotation.
- **Adaptive Lighting controllers:** one per room; `take_over_control: true`, `only_once: true`.
- **Bridge:** room-profile → Adaptive Lighting switches (main + sleep) with startup resync.
- **Motion automations:** one per room using **sensor-light.yaml** blueprint; presence never gates; AL handles brightness/CT.
- **Linked entities:** one-way Kitchen → Laundry mirroring.
- **Dev Tools template:** quick audit of AL + motion surfaces.

## Enable packages and variables
Add to `/config/configuration.yaml` (if not already present):
```yaml
homeassistant:
  packages: !include_dir_named packages
var:
  !include_dir_merge_named domain/variables/
````

## Validate configuration

1. **Check syntax:** Supervisor → Developer Tools → YAML → *Check Configuration* or `ha core check`.
2. **Restart HA.**
3. **Audit:** Developer Tools → Templates → paste `devtools/templates/al_room_audit.jinja2`.

## Usage notes

* **Presence never gates** activation; AL decides *how*, motion decides *when*.
* **Propagation:** upstairs hallway listens to `binary_sensor.hallway_downstairs_motion_recent_beta` (20 s window).
* **ADR-0021 exception:** Ottoman composite promotes α vibration to β with explicit `attributes.source` and `attributes.tier: beta`.

## Knobs

* Per-room **timeouts:** adjust `var.motion_timeout_<room>` values (seconds).
* Bypass per room: toggle `var.motion_bypass_<room>` (true/false).
* AL policy per room: edit attributes in `room_profile_<room>` (e.g., `al_enabled`, `sleep`).

## Disable or rollback

* Set `initial_state: "off"` in a given automation file, or remove the corresponding file from `packages/…`, then restart HA.

````

---

# Apply Plan
1. **Create directories** (idempotent):
   ```bash
   mkdir -p /config/domain/variables
   mkdir -p /config/packages/helpers
   mkdir -p /config/packages/adaptive_lighting
   mkdir -p /config/packages/room_profiles
   mkdir -p /config/packages/motion_lights
   mkdir -p /config/packages/linked
   mkdir -p /config/devtools/templates
````

2. **Write files** exactly as provided above into the matching paths.
3. **Ensure includes** exist in `/config/configuration.yaml`:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   var:
     !include_dir_merge_named domain/variables/
   ```
4. **Restart Home Assistant** from Settings → System → Restart (or `ha core restart`).
5. **Post-restart checks**:

   * Developer Tools → States: verify `binary_sensor.hallway_downstairs_motion_recent_beta` exists.
   * Verify Adaptive Lighting switches (e.g., `switch.adaptive_lighting_bedroom`) exist.

---

# Validation Suite

* **Config check (CLI):**

  ```bash
  ha core check
  ```

  Expected: `Configuration valid!`

* **Room-profile bridge:**

  * Set `var.room_profile_bedroom` attribute `al_enabled` to `false` via UI → States → Set State.
  * Expected: `switch.adaptive_lighting_bedroom` turns **off** within ~1s.
  * Set `al_enabled` to `true`; switch turns **on**.

* **Motion → light (Bedroom):**

  * Trigger `binary_sensor.bedroom_motion_beta` to `on`.
  * Expected: `light.group_all_bedroom_lights` turns **on** immediately; AL controls brightness/CT.
  * After `var.motion_timeout_bedroom` seconds elapse with no motion, light turns **off**.

* **Bypass (Kitchen):**

  * Set `var.motion_bypass_kitchen` to `true`.
  * Trigger `binary_sensor.kitchen_motion_beta` → **no** action (bypass active).
  * Set var back to `false` → motion resumes normal operation.

* **Hallway propagation window:**

  * Trigger `binary_sensor.hallway_downstairs_motion_beta` and **do not** trigger upstairs.
  * Expected: `binary_sensor.hallway_downstairs_motion_recent_beta` = `on` for ~20 s; if upstairs motion fires within that window, upstairs lights should come on faster (due to extra trigger already on).

* **Ottoman composite behavior:**

  * Toggle `binary_sensor.bedroom_bed_vibration_alpha` to `on`.
  * Expected: `binary_sensor.ottoman_motion_beta` = `on` (45 s `delay_off`), and ottoman lights (if group exists) follow its motion automation.

* **Dev Tools audit:**

  * Developer Tools → Templates → paste `devtools/templates/al_room_audit.jinja2`.
  * Expected: a section per room with AL status, timeout value, and color-temp support summary.

---

# Rollback and Risks & Mitigations

**Rollback**

* To disable globally: remove `/config/packages/*` directories created here or comment the `packages:` include, then restart HA.
* To disable per-room: set `initial_state: "off"` in the relevant `packages/motion_lights/*.yaml` file and restart.

**Risks & Mitigations**

* **Entity id divergence:** If group or sensor IDs differ, automations won’t trigger. Mitigation: adjust IDs in the package files and re-run `ha core check`.
* **Blueprint update drift:** Future changes to blueprint inputs may break schema lock. Mitigation: compare new blueprint `input:` keys with the *Whitelist* above and update automations accordingly.
* **α-source provenance (Ottoman):** Composite relies on an α vibration entity. Mitigation: provenance is documented in the helper’s attributes; replace with a native β motion if/when available.
* **AL controller ids:** Controller entity ids depend on `name:`; if customized via UI, update `bridge_all_rooms.yaml` mappings.

---

# Acceptance Criteria (binary)

* All YAML files load under **true HA packages** (`homeassistant: packages`) without configuration errors (`ha core check` passes).
* All motion automations use **only** whitelisted blueprint keys; **no invented inputs**.
* Presence never gates activation (`require_presence_for_activation: false` or equivalent default).
* Only **β** sensors and eta-tier **group lights** are referenced; Ottoman’s α→β composite is explicitly annotated and limited in scope.
* Hallway propagation uses a **20 s recent-motion** helper and is effective upstream → downstream.
* AL controllers are created and `bridge_all_rooms` flips their main & sleep switches per room-profile vars.
* Dev Tools audit template renders per-room status and guards.
* YAML uses two-space indentation, A→Z keys within each mapping, and quotes `initial_state: "on"` where present.

**END OF DELIVERABLE**
