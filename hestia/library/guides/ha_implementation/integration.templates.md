---
title: "Template Integration Guide"
authors: "Home Assistant Team"
source: "https://www.home-assistant.io/integrations/template/"
slug: "template-integration"
tags: ["home-assistant", "ops", "integration"]
original_date: "2025-10-06"
last_updated: "2025-10-07"
url: "https://www.home-assistant.io/integrations/template/"
---


# Template Integration

The template integration allows creating entities which derive their values from other data. This is done by specifying templates for properties of an entity, like the name or the state.


> **Note**: Configuration using the user interface provides a more limited subset of options, making this integration more accessible while covering most use cases. If you need more specific features for your use case, the manual YAML-configuration section of this integration might provide them.

## Supported Device Types

There is currently support for the following device types within Home Assistant:

- Alarm control panel
- Binary sensor
- Button
- Cover
- Event
- Fan
- Image
- Light
- Lock
- Number
- Select
- Sensor
- Switch
- Update
- Vacuum
- Weather

## Table of Contents

- [Configuration](#configuration)
- [YAML Configuration](#yaml-configuration)
- [State-based Template Entities](#state-based-template-entities)
- [Trigger-based Template Entities](#trigger-based-template-entities)
- [Configuration Reference](#configuration-reference)
- [Common Device Configuration Options](#common-device-configuration-options)
- [Examples](#examples)
- [Considerations](#considerations)
- [Using Blueprints](#using-blueprints)
- [Legacy Configuration Formats](#legacy-configuration-formats)

## Configuration

To be able to add Helpers via the user interface, you should have `default_config:` in your `configuration.yaml`. It should already be there by default unless you removed it.

## YAML Configuration

Entities are defined in your YAML configuration files under the `template:` key. You can define multiple configuration blocks as a list. Each block defines sensor/binary sensor/number/select entities and can contain optional update triggers.

### State-based Template Entities

Template entities will by default update as soon as any of the referenced data in the template updates.

For example, you can have a template that takes the averages of two sensors. Home Assistant will update your template sensor as soon as either source sensor updates.

```yaml
template:
  - sensor:
      - name: "Average temperature"
        unit_of_measurement: "°C"
        state: >
          {% set bedroom = states('sensor.bedroom_temperature') | float %}
          {% set kitchen = states('sensor.kitchen_temperature') | float %}

          {{ ((bedroom + kitchen) / 2) | round(1, default=0) }}
```

### Trigger-based Template Entities

If you want more control over when an entity updates, you can define triggers. Triggers follow the same format and work exactly the same as triggers in automations. This feature is a great way to create entities based on webhook data (example), or update entities based on a schedule.

Whenever a trigger fires, all related entities will re-render and it will have access to the trigger data in the templates.

Trigger-based entities do not automatically update when states referenced in the templates change. This functionality can be added back by defining a state trigger for each entity that you want to trigger updates.

The state, including attributes, of trigger-based sensors and binary sensors is restored when Home Assistant is restarted. The state of other trigger-based template entities is not restored.

> **Note**: Buttons do not support using trigger or action options.


#### Example configuration entry

```yaml
template:
  - triggers:
      - trigger: time_pattern
        # This will update every night
        hours: 0
        minutes: 0
    sensor:
      # Keep track how many days have past since a date
      - name: "Not smoking"
        state: '{{ ( ( as_timestamp(now()) - as_timestamp(strptime("06.07.2018", "%d.%m.%Y")) ) / 86400 ) | round(default=0) }}'
        unit_of_measurement: "Days"
```

## Configuration Reference


### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `actions` | list (Optional) | Define actions to be executed when the trigger fires (for trigger-based entities only). Optional. Variables set by the action script are available when evaluating entity templates. This can be used to interact with anything using actions, in particular actions with response data. See action documentation. |
| `conditions` | list (Optional) | Define conditions that have to be met after a trigger fires and before any actions are executed or sensor updates are performed (for trigger-based entities only). Optional. See condition documentation. |
| `triggers` | list (Optional) | Define one or multiple automation triggers to update the entities. Optional. If omitted will update based on referenced entities. See trigger documentation. |
| `unique_id` | string (Optional) | The unique ID for this config block. This will be prefixed to all unique IDs of all entities in this block. |
| `variables` | map (Optional) | Key-value pairs of variable definitions which can be referenced and used in the templates below (for trigger-based entities only). Mostly used by blueprints. With State-based template entities, variables are only resolved when the configuration is loaded or reloaded. Trigger based template entities resolve variables between triggers and actions. |

`variable_name: value` string Required
: The variable name and corresponding value.

## Common Device Configuration Options

Each entity platform has its own set of configuration options, but there are some common options that can be used across all entity platforms.


#### Example configuration.yaml entry

```yaml
template:
  - binary_sensor:
      # Common configuration options
    - default_entity_id: binary_sensor.my_alert
      unique_id: my_unique_sensor_id
      variables:
        my_entity: sensor.watts
      availability: "{{ my_entity | has_value }}"
      icon: "{{ 'mdi:flash-alert' if states(my_entity) | float > 100 else 'mdi:flash' }}"
      name: "{{ states(my_entity) }} Alert"
      # Entity specific configuration options
      state: "{{ states(my_entity) | float > 100}}"
      device_class: problem
```


### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `availability` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `default_entity_id` | string (Optional) | Use default_entity_id instead of name for automatic generation of the entity id. E.g. sensor.my_awesome_sensor. When used without a unique_id, the entity id will update during restart or reload if the entity id is available. If the entity id already exists, the entity id will be created with a number at the end. When used with a unique_id, the default_entity_id is only used when the entity is added for the first time. When set, this overrides a user-customized Entity ID in case the entity was deleted and added again. |
| `icon` | template (Optional) | Defines a template for the icon of the entity. |
| `picture` | template (Optional) | Defines a template for the entity picture of the sensor. |
| `name` | template (Optional) | Defines a template to get the name of the entity. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this entity. Will be combined with the unique ID of the configuration block if available. This allows changing the name, icon and entity_id from the web interface. Changing the entity_id from the web interface will overwrite the value in default_entity_id. |
| `variables` | map (Optional) | Key-value pairs of variable definitions which can be referenced and used in the templates below (for trigger-based entities only). Mostly used by blueprints. With State-based template entities, variables are only resolved when the configuration is loaded or reloaded. Trigger based template entities resolve variables between triggers and actions. |

`variable_name: value` string Required
: The variable name and corresponding value.

## Alarm Control Panel

The template alarm control panel platform allows you to create a alarm control panels with templates to define the state and scripts to define each actions.

Alarm control panel entities can be created from the frontend in the Helpers section or via YAML.


#### Example state-based configuration.yaml entry

```yaml
template:
  - alarm_control_panel:
      - name: "Alarm Control Panel 1"
        state: "{{ states('input_select.panel_1_state') }}"
        arm_away:
          action: script.arm_panel_away
        arm_home:
          action: script.arm_panel_home
        disarm:
          action: script.disarm_panel
```


#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: input_select.panel_1_state
    alarm_control_panel:
      - name: "Alarm Control Panel 1"
        state: "{{ states('input_select.panel_1_state') }}"
        arm_away:
          action: script.arm_panel_away
        arm_home:
          action: script.arm_panel_home
        disarm:
          action: script.disarm_panel
```


### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `alarm_control_panel` | map Required | List of alarm control panels |
| `arm_away` | action (Optional) | Defines an action to run when the alarm is armed to away mode. |
| `arm_custom_bypass` | action (Optional) | Defines an action to run when the alarm is armed to custom bypass mode. |
| `arm_home` | action (Optional) | Defines an action to run when the alarm is armed to home mode. |
| `arm_night` | action (Optional) | Defines an action to run when the alarm is armed to night mode. |
| `arm_vacation` | action (Optional) | Defines an action to run when the alarm is armed to vacation mode. |
| `code_arm_required` | boolean (Optional, default: true) | If true, the code is required to arm the alarm. |
| `code_format` | string (Optional, default: number) | One of number, text or no_code. Format for the code used to arm/disarm the alarm. |
| `disarm` | action (Optional) | Defines an action to run when the alarm is disarmed. |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the alarm control panel works in optimistic mode. When enabled, the alarm control panel’s state will update immediately when a new option is chosen through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the alarm control panel will only update when the state template returns a new value. |
| `state` | template (Optional) | Defines a template to set the state of the alarm panel. Only the states armed_away, armed_home, armed_night, armed_vacation, arming, disarmed, pending, triggered and unavailable are used. |
| `trigger` | action (Optional) | Defines an action to run when the alarm is triggered. |

## Binary Sensor

The template binary sensor platform allows you to create binary sensors with templates to define the state and attributes.

Binary sensor entities can be created from the frontend in the Helpers section or via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - binary_sensor:
      - name: Sun Up
        state: >
          {{ is_state("sun.sun", "above_horizon") }}
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
    - trigger: state
      entity_id: sun.sun
    binary_sensor:
      - name: Sun Up
        state: >
          {{ is_state("sun.sun", "above_horizon") }}
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `binary_sensor` | list Required | List of binary sensors |
| `attributes` | map (Optional) | Defines templates for attributes of the entity. |
| `attribute: template` | template Required | The attribute and corresponding template. |
| `auto_off` | time (Optional) | Requires a trigger. After how much time the entity should turn off after it rendered ‘on’. |
| `delay_off` | time (Optional) | The amount of time the template state must be not met before this sensor will switch to off. This can also be a template. |
| `delay_on` | time (Optional) | The amount of time (e.g. 0:00:05) the template state must be met before this sensor will switch to on. This can also be a template. |
| `device_class` | device_class (Optional, default: None) | Sets the class of the device, changing the device state and icon that is displayed on the UI (see below). It does not set the unit_of_measurement. |
| `state` | template Required | The sensor is on if the template evaluates as True, yes, on, enable or a positive number. The sensor is unknown if the template evaluates as None. Any other value will render it as off. The actual appearance in the frontend (Open/Closed, Detected/Clear etc) depends on the sensor’s device_class value |

## Examples

### State based binary sensor - Washing Machine Running

This example creates a washing machine “load running” sensor by monitoring an energy meter connected to the washer. During the washer’s operation, the energy meter will fluctuate wildly, hitting zero frequently even before the load is finished. By utilizing `delay_off`, we can have this sensor only turn off if there has been no washer activity for 5 minutes.


#### Example configuration.yaml entry

```yaml
# Determine when the washing machine has a load running.
template:
  - binary_sensor:
      - name: "Washing Machine"
        delay_off:
          minutes: 5
        state: >
          {{ states('sensor.washing_machine_power')|float > 0 }}
```

### State based binary sensor - Is Anyone Home

This example is determining if anyone is home based on the combination of device tracking and motion sensors. It’s extremely useful if you have kids/baby sitter/grand parents who might still be in your house that aren’t represented by a trackable device in Home Assistant. This is providing a composite of Wi-Fi based device tracking and Z-Wave multisensor presence sensors.

#### Example configuration.yaml entry

```yaml
template:
  - binary_sensor:
      - name: People home
        state: >
          {{ is_state('device_tracker.sean', 'home')
             or is_state('device_tracker.susan', 'home')
             or is_state('binary_sensor.office_124', 'on')
             or is_state('binary_sensor.hallway_134', 'on')
             or is_state('binary_sensor.living_room_139', 'on')
             or is_state('binary_sensor.porch_ms6_1_129', 'on')
             or is_state('binary_sensor.family_room_144', 'on') }}
```

### State based binary sensor - device tracker sensor with latitude and longitude attributes

This example shows how to combine a non-GPS (e.g., NMAP) and GPS device tracker while still including latitude and longitude attributes

#### Example configuration.yaml entry

```yaml
template:
  - binary_sensor:
      - name: My Device
        state: >
          {{ is_state('device_tracker.my_device_nmap', 'home') or is_state('device_tracker.my_device_gps', 'home') }}
        device_class: "presence"
        attributes:
          latitude: >
            {% if is_state('device_tracker.my_device_nmap', 'home') %}
              {{ state_attr('zone.home', 'latitude') }}
            {% else %}
              {{ state_attr('device_tracker.my_device_gps', 'latitude') }}
            {% endif %}
          longitude: >
            {% if is_state('device_tracker.my_device_nmap', 'home') %}
              {{ state_attr('zone.home', 'longitude') }}
            {% else %}
              {{ state_attr('device_tracker.my_device_gps', 'longitude') }}
            {% endif %}
```

### State based binary sensor - Change the icon when a state changes

This example demonstrates how to use template to change the icon as its state changes. This icon is referencing its own state.

#### Example configuration.yaml entry

```yaml
template:
  - binary_sensor:
      - name: Sun Up
        state: >
          {{ is_state("sun.sun", "above_horizon") }}
        icon: >
          {% if is_state("binary_sensor.sun_up", "on") %}
            mdi:weather-sunset-up
          {% else %}
            mdi:weather-sunset-down
          {% endif %}
```

### Trigger based binary sensor - Change state and icon when a custom event is received

A more advanced use case could be to set the icon based on the sensor’s own state like above, but when triggered by an event. This example demonstrates a binary sensor that turns on momentarily, such as when a doorbell button is pressed.

The binary sensor turns on and sets the matching icon when the appropriate event is received. After 5 seconds, the binary sensor turns off automatically. To ensure the icon gets updated, there must be a trigger for when the state changes to off.

#### Example configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: event
        event_type: YOUR_EVENT
      - trigger: state
        entity_id: binary_sensor.doorbell_rang
        to: "off"
    binary_sensor:
      name: doorbell_rang
      icon: "{{ (trigger.platform == 'event') | iif('mdi:bell-ring-outline', 'mdi:bell-outline') }}"
      state: "{{ trigger.platform == 'event' }}"
      auto_off:
        seconds: 5
```

## Button

The template button platform allows you to create button entities with scripts to define each action.

Button entities can be created from the frontend in the Helpers section or via YAML.

#### Example configuration.yaml entry

```yaml
template:
  - button:
      - name: Fast Forward
        press:
          action: remote.send_command
          target:
            entity_id: remote.living_room
          data:
            command: fast_forward
```

## Cover

The template cover platform allows you to create covers with templates to define the state and scripts to define each action.


#### Example state-based configuration.yaml entry

```yaml
template:
  - cover:
      - name: Garage Door
        state: "{{ states('sensor.garage_door')|float > 0 }}"
        device_class: garage
        open_cover:
          action: script.open_garage_door
        close_cover:
          action: script.close_garage_door
        stop_cover:
          action: script.stop_garage_door
```


#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: sensor.garage_door
    cover:
      - name: Garage Door
        state: "{{ trigger.to_state.state|float(0) > 0 }}"
        device_class: garage
        open_cover:
          action: script.open_garage_door
        close_cover:
          action: script.close_garage_door
        stop_cover:
          action: script.stop_garage_door
```


### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `cover` | map | Characteristics of a cover |
| `close_cover` | action (Inclusive) | Defines an action to close the cover. |
| `device_class` | string (Optional) | Sets the class of the device, changing the device state and icon that is displayed on the frontend. |
| `open_cover` | action (Inclusive) | Defines an action to open the cover. If open_cover is specified, close_cover must also be specified. At least one of open_cover and set_cover_position must be specified. |
| `optimistic` | boolean (Optional, default: false) | Force cover position to use optimistic mode. |
| `position` | template (Optional) | Defines a template to get the position of the cover. Legal values are numbers between 0 (closed) and 100 (open). If the template produces a None value the current position will be set to unknown. |
| `set_cover_position` | action (Optional) | Defines an action to set to a cover position (between 0 and 100). The variable position will contain the entity’s set position. |
| `set_cover_tilt_position` | action (Optional) | Defines an action to set the tilt of a cover (between 0 and 100). The variable tilt will contain the entity’s set tilt position. |
| `state` | template (Optional) | Defines a template to get the state of the cover. Valid output values from the template are open, opening, closing and closed which are directly mapped to the corresponding states. In addition, true is valid as a synonym to open and false as a synonym to closed. If both a state and a position template are specified, only opening and closing are set from the state template. If the template produces a None value the state will be set to unknown. |
| `stop_cover` | action (Optional) | Defines an action to stop the cover. |
| `tilt` | template (Optional) | Defines a template to get the tilt state of the cover. Legal values are numbers between 0 (closed) and 100 (open). If the template produces a None value, the current tilt state will be set to unknown. |
| `tilt_optimistic` | boolean (Optional, default: false) | Force cover tilt position to use optimistic mode. |

### Cover Optimistic Mode

In optimistic mode, the cover position state is maintained internally. This mode is automatically enabled if neither state or position are specified. Note that this is unlikely to be very reliable without some feedback mechanism, since there is otherwise no way to know if the cover is moving properly. The cover can be forced into optimistic mode by using the optimistic attribute. There is an equivalent mode for tilt_position that is enabled when tilt is not specified or when the tilt_optimistic attribute is used.

### Combining state and position templates

If both a state and a position are specified only opening and closing states are set directly from the state, the open and closed states will instead be derived from the cover position.

| value_template output | result |
| --------------------- | ------ |
| open | state defined by position_template |
| closed | state defined by position_template |
| true | state defined by position_template |
| false | state defined by position_template |
| opening | state set to opening |
| closing | state set to closing |
| No change of state or position | |

#### State based cover - Garage Door

This example converts a garage door with a controllable switch and position sensor into a cover. The condition check is optional, but suggested if you use the same switch to open and close the garage.

```yaml
template:
  - cover:
      - name: Garage Door
        device_class: garage
        position: "{{ states('sensor.garage_door') }}"
        open_cover:
          - condition: state
            entity_id: sensor.garage_door
            state: "off"
          - action: switch.turn_on
            target:
              entity_id: switch.garage_door
        close_cover:
          - condition: state
            entity_id: sensor.garage_door
            state: "on"
          - action: switch.turn_off
            target:
              entity_id: switch.garage_door
        stop_cover:
          action: switch.turn_on
          target:
            entity_id: switch.garage_door
        icon: >-
          {% if states('sensor.garage_door')|float > 0 %}
            mdi:garage-open
          {% else %}
            mdi:garage
          {% endif %}
```

#### State based cover - Optimistic Garage Door with Momentary Switch

This example converts a garage door with a momentary switch.

```yaml
template:
  - cover:
      - name: Garage Door
        device_class: garage
        open_cover:
          - action: switch.turn_on
            target:
              entity_id: switch.garage_door
        close_cover:
          - action: switch.turn_on
            target:
              entity_id: switch.garage_door
        stop_cover:
          - action: switch.turn_on
            target:
              entity_id: switch.garage_door
```

## Event

The template event platform allows you to create events with templates to define the state.

#### Example state-based configuration.yaml entry

```yaml
template:
  - event:
      - name: Scene Controller
        device_class: button
        event_type: "{{ states('input_select.scene_controller_button_press') }}"
        event_types: "{{ ['single', 'double', 'hold'] }}"
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: event
        event_type: zwave_js_notification
        event_data:
          node_id: 14
    event:
      - name: Lock Operation
        event_type: "{{ trigger.event.data.event_label }}"
        event_types: "{{ ['Keypad lock operation', 'Keypad unlock operation'] }}"
```

## Fan

The template fan platform allows you to create fans with templates to define the state and scripts to define each action.

Fan entities can only be created from YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - fan:
      - name: "Bedroom fan"
        state: "{{ states('input_boolean.state') }}"
        percentage: "{{ states('input_number.percentage') }}"
        preset_mode: "{{ states('input_select.preset_mode') }}"
        oscillating: "{{ states('input_select.osc') }}"
        direction: "{{ states('input_select.direction') }}"
        turn_on:
          action: script.fan_on
        turn_off:
          action: script.fan_off
        set_percentage:
          action: script.fans_set_speed
          data:
            percentage: "{{ percentage }}"
        set_preset_mode:
          action: script.fans_set_preset_mode
          data:
            preset_mode: "{{ preset_mode }}"
        set_oscillating:
          action: script.fan_oscillating
          data:
            oscillating: "{{ oscillating }}"
        set_direction:
          action: script.fan_direction
          data:
            direction: "{{ direction }}"
        speed_count: 6
        preset_modes:
          - 'auto'
          - 'smart'
          - 'whoosh'
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id:
          - input_boolean.state
          - input_number.percentage
          - input_select.preset_mode
          - input_select.osc
          - input_select.direction
    fan:
      - name: "Bedroom fan"
        state: "{{ states('input_boolean.state') }}"
        percentage: "{{ states('input_number.percentage') }}"
        preset_mode: "{{ states('input_select.preset_mode') }}"
        oscillating: "{{ states('input_select.osc') }}"
        direction: "{{ states('input_select.direction') }}"
        turn_on:
          action: script.fan_on
        turn_off:
          action: script.fan_off
        set_percentage:
          action: script.fans_set_speed
          data:
            percentage: "{{ percentage }}"
        set_preset_mode:
          action: script.fans_set_preset_mode
          data:
            preset_mode: "{{ preset_mode }}"
        set_oscillating:
          action: script.fan_oscillating
          data:
            oscillating: "{{ oscillating }}"
        set_direction:
          action: script.fan_direction
          data:
            direction: "{{ direction }}"
        speed_count: 6
        preset_modes:
          - 'auto'
          - 'smart'
          - 'whoosh'
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `fan` | map Required | List of fans |
| `direction` | template (Optional) | Defines a template to get the direction of the fan. Valid values: forward, reverse. |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the fan works in optimistic mode. When enabled, the fan’s state will update immediately when a new option is chosen through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the fan will only update when the state template returns a new value. |
| `oscillating` | template (Optional) | Defines a template to get the oscillation state of the fan. Valid values: true, false. |
| `percentage` | template (Optional) | Defines a template to get the speed percentage of the fan. |
| `preset_mode` | template (Optional) | Defines a template to get the preset mode of the fan. |
| `preset_modes` | string | list (Optional, default: []) | List of preset modes the fan is capable of. This is an arbitrary list of strings and must not contain any speeds. |
| `set_percentage` | action (Optional) | Defines an action to run when the fan is given a speed percentage command. |
| `set_preset_mode` | action (Optional) | Defines an action to run when the fan is given a preset command. |
| `set_oscillating` | action (Optional) | Defines an action to run when the fan is given an oscillation state command. |
| `set_direction` | action (Optional) | Defines an action to run when the fan is given a direction command. |
| `speed_count` | integer (Optional, default: 100) | The number of speeds the fan supports. Used to calculate the percentage step for the fan.increase_speed and fan.decrease_speed actions. |
| `state` | template Required | Defines a template to get the state of the fan. Valid values: on, off. |
| `turn_on` | action Required | Defines an action to run when the fan is turned on. |
| `turn_off` | action Required | Defines an action to run when the fan is turned off. |

### Converting from speeds to percentage

When converting a fan with 3 speeds from the old fan entity model, the following percentages can be used:

0 - off 33 - low 66 - medium 100 - high


### State based fan - Helper fan

This example uses an input_boolean and an input_number to mimic a fan, and the example shows multiple actions for set_percentage.

```yaml
template:
  - fan:
      - name: "Helper Fan"
        state: "{{ states('input_boolean.state') }}"
        turn_on:
          - action: input_boolean.turn_on
            target:
              entity_id: input_boolean.state
        turn_off:
          - action: input_boolean.turn_off
            target:
              entity_id: input_boolean.state
        speed_count: 6
        percentage: >
          {{ states('input_number.percentage') if is_state('input_boolean.state', 'on') else 0 }}
        set_percentage:
          - action: input_boolean.turn_{{ 'on' if percentage > 0 else 'off' }}
            target:
              entity_id: input_boolean.state
          - action: input_number.set_value
            target:
              entity_id: input_number.percentage
            data:
              value: "{{ percentage }}"
```


### State based fan - Fan with preset modes

This example uses an existing fan with only a percentage. It extends the percentage value into useable preset modes without a helper entity.

```yaml
template:
  - fan:
      - name: "Preset Mode Fan Example"
        state: "{{ states('fan.percentage_fan') }}"
        turn_on:
          - action: fan.turn_on
            target:
              entity_id: fan.percentage_fan
        turn_off:
          - action: fan.turn_off
            target:
              entity_id: fan.percentage_fan
        percentage: >
          {{ state_attr('fan.percentage_fan', 'percentage') }}
        speed_count: 3
        set_percentage:
          - action: fan.set_percentage
            target:
              entity_id: fan.percentage_fan
            data:
              percentage: "{{ percentage }}"
        preset_modes:
          - "off"
          - "low"
          - "medium"
          - "high"
        preset_mode: >
          {% if is_state('fan.percentage_fan', 'on') %}
            {% if state_attr('fan.percentage_fan', 'percentage') == 100  %}
              high
            {% elif state_attr('fan.percentage_fan', 'percentage') == 66 %}
              medium
            {% else %}
              low
            {% endif %}
          {% else %}
            off
          {% endif %}
        set_preset_mode:
          - action: fan.set_percentage
            target:
              entity_id: fan.percentage_fan
            data:
              percentage: >-
                {% if preset_mode == 'high' %}
                  100
                {% elif preset_mode == 'medium' %}
                  66
                {% elif preset_mode == 'low' %}
                  33
                {% else %}
                  0
                {% endif %}
```

## Image

The template image platform allows you to create image entities with templates to define the image URL.

Image entities can be created from the frontend in the Helpers section or via YAML.


#### Example state-based configuration.yaml entry

```yaml
template:
  - image:
      - name: "My Image"
        url: "http://example.com/image.jpg"
```


#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id:
          - input_boolean.state
    image:
      - name: "My Image"
        url: >
          {% if is_state('input_boolean.state', 'on') %}
            http://example.com/image_on.jpg
          {% else %}
            http://example.com/image_off.jpg
          {% endif %}
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `image` | map Required | List of images |
| `url` | template Required | The URL on which the image is served. |
| `verify_ssl` | boolean (Optional, default: true) | Enable or disable SSL certificate verification. Set to false to use an http-only URL, or you have a self-signed SSL certificate and haven’t installed the CA certificate to enable verification. |

## Light

The template light platform allows you to create lights with templates to define the state and scripts to define each action.

Light entities can only be created from YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - light:
      - name: "Theater Lights"
        level: "{{ state_attr('sensor.theater_brightness', 'lux')|int }}"
        state: "{{ state_attr('sensor.theater_brightness', 'lux')|int > 0 }}"
        temperature: "{{states('input_number.temperature_input') | int}}"
        hs_template: "({{states('input_number.h_input') | int}}, {{states('input_number.s_input') | int}})"
        effect_list: "{{ state_attr('light.led_strip', 'effect_list') }}"
        turn_on:
          action: script.theater_lights_on
        turn_off:
          action: script.theater_lights_off
        set_level:
          action: script.theater_lights_level
          data:
            brightness: "{{ brightness }}"
        set_temperature:
          action: input_number.set_value
          data:
            value: "{{ color_temp }}"
            entity_id: input_number.temperature_input
        set_hs:
          - action: input_number.set_value
            data:
              value: "{{ h }}"
              entity_id: input_number.h_input
          - action: input_number.set_value
            data:
              value: "{{ s }}"
              entity_id: input_number.s_input
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              transition: "{{ transition | float }}"
              hs_color:
                - "{{ hs[0] }}"
                - "{{ hs[1] }}"
        set_effect:
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              effect: "{{ effect }}"
        supports_transition: "{{ true }}"
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id:
        - sensor.theater_brightness
        - input_number.temperature_input
        - input_number.h_input
        - input_number.s_input
        - light.led_strip
    light:
      - name: "Theater Lights"
        level: "{{ state_attr('sensor.theater_brightness', 'lux')|int }}"
        state: "{{ state_attr('sensor.theater_brightness', 'lux')|int > 0 }}"
        temperature: "{{states('input_number.temperature_input') | int}}"
        hs_template: "({{states('input_number.h_input') | int}}, {{states('input_number.s_input') | int}})"
        effect_list: "{{ state_attr('light.led_strip', 'effect_list') }}"
        turn_on:
          action: script.theater_lights_on
        turn_off:
          action: script.theater_lights_off
        set_level:
          action: script.theater_lights_level
          data:
            brightness: "{{ brightness }}"
        set_temperature:
          action: input_number.set_value
          data:
            value: "{{ color_temp }}"
            entity_id: input_number.temperature_input
        set_hs:
          - action: input_number.set_value
            data:
              value: "{{ h }}"
              entity_id: input_number.h_input
          - action: input_number.set_value
            data:
              value: "{{ s }}"
              entity_id: input_number.s_input
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              transition: "{{ transition | float }}"
              hs_color:
                - "{{ hs[0] }}"
                - "{{ hs[1] }}"
        set_effect:
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              effect: "{{ effect }}"
        supports_transition: "{{ true }}"
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `light` | map Required | List of your lights. |
| `effect` | template (Inclusive, default: optimistic) | Defines a template to get the effect of the light. |
| `effect_list` | template (Inclusive, default: optimistic) | Defines a template to get the list of supported effects. Must render a list. |
| `hs` | template (Optional, default: optimistic) | Defines a template to get the HS color of the light. Must render a tuple (hue, saturation). |
| `level` | template (Optional, default: optimistic) | Defines a template to get the brightness of the light. |
| `min_mireds` | template (Optional, default: optimistic) | Defines a template to get the minimum mired value of the light. |
| `max_mireds` | template (Optional, default: optimistic) | Defines a template to get the maximum mired value of the light. |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the light works in optimistic mode. When enabled, the light’s state will update immediately when a new option is chosen through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the light will only update when the state template returns a new value. |
| `rgb` | template (Optional, default: optimistic) | Defines a template to get the RGB color of the light. Must render a tuple or a list (red, green, blue). |
| `rgbw` | template (Optional, default: optimistic) | Defines a template to get the RGBW color of the light. Must render a tuple or a list (red, green, blue, white). |
| `rgbww` | template (Optional, default: optimistic) | Defines a template to get the RGBWW color of the light. Must render a tuple or a list (red, green, blue, cold white, warm white). |
| `set_effect` | action (Inclusive) | Defines an action to run when the light is given an effect command. Receives the variable effect. May also receive the variables brightness, and/or transition. |
| `set_level` | action (Optional) | Defines an action to run when the light is given a brightness command. The script will only be called if the turn_on call only ha brightness, and optionally transition. Receives variables brightness and, optionally, transition. |
| `set_temperature` | action (Optional) | Defines an action to run when the light is given a color temperature command. Receives variable color_temp. May also receive variables brightness and/or transition. |
| `set_hs` | action (Optional) | Defines an action to run when the light is given a hs color command. Available variables: hs as a tuple, h and s. |
| `set_rgb` | action (Optional) | Defines an action to run when the light is given an RGB color command. Available variables: rgb as a tuple, r, g and b. |
| `set_rgbw` | action (Optional) | Defines an action to run when the light is given an RGBW color command. Available variables: rgbw as a tuple, rgb as a tuple, r, g, b and w. |
| `set_rgbww` | action (Optional) | Defines an action to run when the light is given an RGBWW color command. Available variables: rgbww as a tuple, rgb as a tuple, r, g, b, cw and ww. |
| `state` | template (Optional, default: optimistic) | Defines a template to set the state of the light. If not defined, the switch will optimistically assume all commands are successful. |
| `supports_transition` | template (Optional, default: false) | Defines a template to get if the light supports transition. Should return a boolean value (True/False). If this value is True, the transition parameter in a turn on or turn off call will be passed as a named parameter transition in either of the scripts. |
| `temperature` | template (Optional, default: optimistic) | Defines a template to get the color temperature of the light. |
| `turn_on` | action Required | Defines an action to run when the light is turned on. May receive the variables brightness and/or transition. |
| `turn_off` | action Required | Defines an action to run when the light is turned off. May receive the variable transition. |

### Light Considerations

Transition doesn’t have its own script, it will instead be passed as a named parameter transition to the turn_on, turn_off, brightness, color_temp, effect, hs_color, rgb_color, rgbw_color or rgbww_color scripts. Brightness will be passed as a named parameter brightness to either of turn_on, color_temp, effect, hs_color, rgb_color, rgbw_color or rgbww_color scripts if the corresponding parameter is also in the call. In this case, the brightness script (set_level) will not be called. If only brightness is passed to light.turn_on action, then set_level script is called.

#### State based light - Theater Volume Control

This example shows a light that is actually a home theater’s volume. This integration gives you the flexibility to provide whatever you’d like to send as the payload to the consumer including any scale conversions you may need to make; the media player integration needs a floating point percentage value from 0.0 to 1.0.

##### Example configuration.yaml entry

```yaml
template:
  - light:
      - name: Receiver Volume
        state: >-
          {% if is_state('media_player.receiver', 'on') %}
            {% if state_attr('media_player.receiver', 'is_volume_muted') %}
              off
            {% else %}
              on
            {% endif %}
          {% else %}
            off
          {% endif %}
        turn_on:
          action: media_player.volume_mute
          target:
            entity_id: media_player.receiver
          data:
            is_volume_muted: false
        turn_off:
          action: media_player.volume_mute
          target:
            entity_id: media_player.receiver
          data:
            is_volume_muted: true
        set_level:
          action: media_player.volume_set
          target:
            entity_id: media_player.receiver
          data:
            volume_level: "{{ (brightness / 255 * 100)|int / 100 }}"
        level: >-
          {% if is_state('media_player.receiver', 'on') %}
            {{ (state_attr('media_player.receiver', 'volume_level')|float * 255)|int }}
          {% else %}
            0
          {% endif %}
```

#### State based light - Make a global light entity for a multi-segment WLED light

This example shows how to group together 2 RGBW segments from the same WLED controller into a single usable light.

```yaml
template:
  - light:
        unique_id: 28208f257b54c44e50deb2d618d44710
        name: Multi-segment Wled control
        state: "{{ states('light.wled_master') }}"
        level: "{{ state_attr('light.wled_master', 'brightness')|d(0,true)|int }}"
        rgbw: (
          {{ (state_attr('light.wled_segment_0', 'rgbw_color')[0]|d(0) + state_attr('light.wled_segment_1', 'rgbw_color')[0]|d(0))/2 }},
          {{ (state_attr('light.wled_segment_0', 'rgbw_color')[1]|d(0) + state_attr('light.wled_segment_1', 'rgbw_color')[1]|d(0))/2 }},
          {{ (state_attr('light.wled_segment_0', 'rgbw_color')[2]|d(0) + state_attr('light.wled_segment_1', 'rgbw_color')[2]|d(0))/2 }},
          {{ (state_attr('light.wled_segment_0', 'rgbw_color')[3]|d(0) + state_attr('light.wled_segment_1', 'rgbw_color')[3]|d(0))/2 }}
          )
        effect_list: "{{ state_attr('light.wled_segment_0', 'effect_list') }}"
        effect: "{{ state_attr('light.wled_segment_0', 'effect') if state_attr('light.wled_segment_0', 'effect') == state_attr('light.wled_segment_1', 'effect') else none }}"
        availability: "{{ not is_state('light.wled_master', 'unknown') }}"

        turn_on:
          action: light.turn_on
          entity_id: light.wled_segment_0, light.wled_segment_1, light.wled_master
        turn_off:
          action: light.turn_off
          entity_id: light.wled_master
        set_level:
          action: light.turn_on
          entity_id: light.wled_master
          data:
            brightness: "{{ brightness }}"
        set_rgbw:
          action: light.turn_on
          entity_id: light.wled_segment_0, light.wled_segment_1
          data:
            rgbw_color:
              - "{{ r }}"
              - "{{ g }}"
              - "{{ b }}"
              - "{{ w }}"
            effect: "Solid"
        set_effect:
          action: light.turn_on
          entity_id: light.wled_segment_0, light.wled_segment_1
          data:
            effect: "{{ effect }}"
```

## Lock

The template lock platform allows you to create locks with templates to define the state and scripts to define each action.

Lock entities can only be created from YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - lock:
      - name: Garage door
        state: "{{ is_state('sensor.door', 'on') }}"
        lock:
          action: switch.turn_on
          target:
            entity_id: switch.door
        unlock:
          action: switch.turn_off
          target:
            entity_id: switch.door
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: sensor.door
    lock:
      - name: Garage door
        state: "{{ trigger.to_state.state == 'on' }}"
        lock:
          action: switch.turn_on
          target:
            entity_id: switch.door
        unlock:
          action: switch.turn_off
          target:
            entity_id: switch.door
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `lock` | map Required | List of locks |
| `code_format` | template (Optional, default: None) | Defines a template to get the code_format attribute of the entity. This template must evaluate to a valid Python regular expression or None. If it evaluates to a not-None value, the user is prompted to enter a code when interacting with the lock. The code will be matched against the regular expression, and only if it matches, the lock/unlock actions will be executed. The actual validity of the entered code must be verified within these actions. If there’s a syntax error in the template, the entity will be unavailable. If the template fails to render for other reasons or if the regular expression is invalid, no code will be accepted and the lock/unlock actions will never be invoked. |
| `lock` | action Required | Defines an action to run when the lock is locked. |
| `unlock` | action Required | Defines an action to run when the lock is unlocked. |
| `open` | action (Optional) | Defines an action to run when the lock is opened. |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the lock works in optimistic mode. When enabled, the lock’s state will update immediately when a new option is chosen through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the lock will only update when the state template returns a new value. |

## Number

The template number platform allows you to create number entities with templates to define the state and scripts to define each action.

Number entities can be created from the frontend in the Helpers section or via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - number:
      - name: Desk Height
        unit_of_measurement: "in"
        state: "{{ states('sensor.desk_height') }}"
        set_value:
          - action: script.set_desk_height
            data:
              value: "{{ value }}"
        step: 0.5
        min: 1
        max: 24
        icon: mdi:ruler
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: sensor.desk_height
  - number:
      - name: Desk Height
        unit_of_measurement: "in"
        state: "{{ states('sensor.desk_height') }}"
        set_value:
          - action: script.set_desk_height
            data:
              value: "{{ value }}"
        step: 0.5
        min: 1
        max: 24
        icon: mdi:ruler
```

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `number` | map Required | List of numbers |
| `max` | template (Optional, default: 100.0) | Template for the number’s maximum value. |
| `min` | template (Optional, default: 0.0) | Template for the number’s minimum value. |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the number works in optimistic mode. When enabled, the number’s state will update immediately when changed through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the number will only update when the state template returns a new value. |
| `set_value` | action Required | Defines actions to run when the number value changes. The variable value will contain the number entered. |
| `state` | template (Optional, default: optimistic) | Template for the number’s current value. When omitted, the state will be set to the value provided by the set_value action. |
| `unit_of_measurement` | string (Optional, default: None) | Defines the units of measurement of the number, if any. |

### State based number - Changing the unit of measurement of another number

This example demonstrates the usage of a template number with a unit of measurement set to change a unit-less value of another number entity.

```yaml
template:
  - number:
      - name: "Cutting Height"
        unit_of_measurement: "cm"
        unique_id: automower_cutting_height
        state: "{{ states('number.automower_cutting_height_raw')|int(0) * 0.5 + 1.5 }}"
        set_value:
          - service: number.set_value
            target:
              entity_id: number.automower_cutting_height_raw
            data:
              value: "{{ (value - 1.5) * 2 }}"
        step: 0.5
        min: 2
        max: 6
        icon: mdi:ruler
```

## Select

The template select platform allows you to create select entities with templates to define the state and scripts to define each action.

Select entities can be created from the frontend in the Helpers section or via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - select:
      - name: Camera Day-Night Mode
        state: "{{ state_attr('camera.porch', 'day_night_mode') }}"
        options: "{{ ['off', 'on', 'auto'] }}"
        select_option:
          - action: script.porch_camera_day_night_mode
            data:
              day_night_mode: "{{ option }}"
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: camera.porch
        attribute: day_night_mode
    select:
      - name: Camera Day-Night Mode
        state: "{{ state_attr('camera.porch', 'day_night_mode') }}"
        options: "{{ ['off', 'on', 'auto'] }}"
        select_option:
          - action: script.porch_camera_day_night_mode
            data:
              day_night_mode: "{{ option }}"
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `select` | map Required | List of selects |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the select works in optimistic mode. When enabled, the select’s state will update immediately when a new option is chosen through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the select will only update when the state template returns a new value. |
| `options` | template Required | Template for the select’s available options. |
| `select_option` | action Required | Defines actions to run to select an option from the options list. The variable option will contain the option selected. |
| `state` | template (Optional, default: optimistic) | Template for the select’s current value. When omitted, the state will be set to the option provided by the select_option action. |

### State based select - Control Day/Night mode of a camera

This show how a state based template select can be used to perform an action.

```yaml
template:
  select:
    - name: "Porch Camera Day-Night Mode"
      unique_id: porch_camera_day_night_mode
      state: "{{ state_attr('camera.porch_camera_sd', 'day_night_mode') }}"
      options: "{{ ['off', 'on', 'auto'] }}"
      select_option:
        - action: tapo_control.set_day_night_mode
          data:
            day_night_mode: "{{ option }}"
          target:
            entity_id: camera.porch_camera_sd
```

## Sensor

The template sensor platform allows you to create sensors with templates to define the state and attributes.

Sensor entities can be created from the frontend in the Helpers section or via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - sensor:
      - name: "Kettle"
        state: >
          {% if is_state('switch.kettle', 'off') %}
            off
          {% elif state_attr('switch.kettle', 'W')|float < 1000 %}
            standby
          {% elif is_state('switch.kettle', 'on') %}
            on
          {% else %}
            failed
          {% endif %}
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: sensor.outside_temperature
        not_to:
        - unknown
        - unavailable
    sensor:
      - name: Outside Temperature
        device_class: temperature
        unit_of_measurement: °C
        state: "{{ (states('sensor.outside_temperature') | float - 32) * 5/9 }}"
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `sensor` | list Required | List of sensors |
| `attributes` | map (Optional) | Defines templates for attributes of the entity. |
| `attribute: template` | template Required | The attribute and corresponding template. |
| `last_reset` | template (Optional, default: None) | Defines a template that describes when the state of the sensor was last reset. Must render to a valid datetime. Only available when state_class is set to total |
| `state` | template Required | Defines a template to get the state of the sensor. If the sensor is numeric, i.e. it has a state_class or a unit_of_measurement, the state template must render to a number or to none. The state template must not render to a string, including unknown or unavailable. An availability template may be defined to suppress rendering of the state template. |
| `state_class` | string (Optional, default: None) | The state_class of the sensor. This will also display the value based on the user profile Number Format setting and influence the graphical presentation in the history visualization as a continuous value. If you desire to include the sensor in Long-term statistics, include this key and assign it the appropriate value |
| `unit_of_measurement` | string (Optional, default: None) | Defines the units of measurement of the sensor, if any. This will also display the value based on the user profile Number Format setting and influence the graphical presentation in the history visualization as a continuous value. |

## Examples

### State based sensor - Exposing sun angle

This example shows the sun angle in the frontend.

#### Example configuration.yaml entry

```yaml
template:
  - sensor:
      - name: Sun Angle
        unit_of_measurement: "°"
        state: "{{ '%+.1f'|format(state_attr('sun.sun', 'elevation')) }}"
```

### State based sensor - Modifying another sensor’s output

If you don’t like the wording of a sensor output, then the Template Sensor can help too. Let’s rename the output of the Sun integration as a simple example:

#### Example configuration.yaml entry

```yaml
template:
  - sensor:
      - name: "Sun State"
        state: >
          {% if is_state('sun.sun', 'above_horizon') %}
            up
          {% else %}
            down
          {% endif %}
```

### State based sensor - Changing the unit of measurement of another sensor

With a Template Sensor, it’s easy to convert given values into others if the unit of measurement doesn’t fit your needs. Because the sensors do math on the source sensor’s state and need to render to a numeric value, an availability template is used to suppress rendering of the state template if the source sensor does not have a valid numeric state.

#### Example configuration.yaml entry

```yaml
template:
  - sensor:
      - name: "Transmission Down Speed"
        unit_of_measurement: "kB/s"
        state: "{{ states('sensor.transmission_down_speed')|float * 1024 }}"
        availability: "{{ is_number(states('sensor.transmission_down_speed')) }}"

      - name: "Transmission Up Speed"
        unit_of_measurement: "kB/s"
        state: "{{ states('sensor.transmission_up_speed')|float * 1024 }}"
        availability: "{{ is_number(states('sensor.transmission_up_speed')) }}"
```

### Trigger based sensor - Using conditions to control updates

This example shows how to store the last valid value of a temperature sensor. It will update as long as the source sensor has a valid (numeric) state. Otherwise, the template sensor’s state will remain unchanged.

#### Example configuration.yaml entry

```yaml
template:
  - triggers:
      trigger: state
      entity_id: sensor.outside_temperature
    conditions:
      - condition: template
        value_template: "{{ is_number(states('sensor.outside_temperature')) }}"
    sensor:
      - name: Outside Temperature last known value
        state: "{{ states('sensor.outside_temperature') }}"
```

## Switch

The template switch platform allows you to create switches with templates to define the state and scripts to define each action.

Switch entities can be created from the frontend in the Helpers section or via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - switch:
      - name: Skylight
        state: "{{ is_state('binary_sensor.skylight', 'on') }}"
        turn_on:
          action: switch.turn_on
          target:
            entity_id: switch.skylight_open
        turn_off:
          action: switch.turn_off
          target:
            entity_id: switch.skylight_close
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: binary_sensor.skylight
    switch:
      - name: Skylight
        state: "{{ is_state('binary_sensor.skylight', 'on') }}"
        turn_on:
          action: switch.turn_on
          target:
            entity_id: switch.skylight_open
        turn_off:
          action: switch.turn_off
          target:
            entity_id: switch.skylight_close
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `switch` | map Required | List of switches |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the switch works in optimistic mode. When enabled, the switch’s state will update immediately when a new option is chosen through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the switch will only update when the state template returns a new value. |
| `state` | template (Optional, default: optimistic) | Defines a template to set the state of the switch. If not defined, the switch will optimistically assume all commands are successful. |
| `turn_off` | action Required | Defines an action or list of actions to run when the switch is turned off. |
| `turn_on` | action Required | Defines an action or list of actions to run when the switch is turned on. |

### State based switch - Invert a Switch

This example shows a switch that is the inverse of another switch.

```yaml
template:
  - switch:
      - state: "{{ not is_state('switch.target', 'on') }}"
        availability: "{{ has_value('switch.target') }}"
        turn_on:
          action: switch.turn_off
          target:
            entity_id: switch.target
        turn_off:
          action: switch.turn_on
          target:
            entity_id: switch.target
```

### State based switch - Toggle Switch

This example shows a switch that takes its state from a sensor and toggles a switch.

```yaml
template:
  - switch:
      - name: "Blind"
        state: "{{ is_state_attr('switch.blind_toggle', 'sensor_state', 'on') }}"
        turn_on:
          action: switch.toggle
          target:
            entity_id: switch.blind_toggle
        turn_off:
          action: switch.toggle
          target:
            entity_id: switch.blind_toggle
```

### State based switch - Sensor and Two Switches

This example shows a switch that takes its state from a sensor, and uses two momentary switches to control a device.

```yaml
template:
  - switch:
      - name: "Skylight"
        value_template: "{{ is_state('sensor.skylight', 'on') }}"
        turn_on:
          action: switch.turn_on
          target:
            entity_id: switch.skylight_open
        turn_off:
          action: switch.turn_on
          target:
            entity_id: switch.skylight_close
```

### State based switch - Optimistic Switch

This example switch with an assumed state based on the actions performed. This switch will immediately change state after a turn_on/turn_off command.

```yaml
template:
  - switch:
      - name: "Blind"
        turn_on:
          action: switch.toggle
          target:
            entity_id: switch.blind_toggle
        turn_off:
          action: switch.toggle
          target:
            entity_id: switch.blind_toggle
```

## Update

The template update platform allows you to create update entities with templates to define the state and a script to define the install action.

Update entities can be created from the frontend in the Helpers section or via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - update:
      - name: Frigate
        installed_version: "{{ states('sensor.installed_version') }}"
        latest_version: "{{ states('sensor.latest_version') }}"
        install:
          action: script.update_frigate
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: time
        at: "00:00:00"
    update:
      - name: Frigate
        installed_version: "{{ states('sensor.installed_version') }}"
        latest_version: "{{ states('sensor.latest_version') }}"
        install:
          action: script.update_frigate
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `update` | map Required | List of update entities |
| `backup` | boolean (Optional, default: false) | Enable or disable the automatic backup before update option in the update repair. When disabled, the backup variable will always provide False during the install action and it will not accept the backup option. |
| `device_class` | device_class (Optional, default: None) | Sets the class of the device, changing the device state and icon that is displayed on the UI. |
| `in_progress` | template (Optional) | Defines a template to get the in-progress state. |
| `install` | action (Optional) | Defines actions to run when the update is installed. Receives variables specific_version and backup when enabled. |
| `installed_version` | template Required | Defines a template to get the installed version. When the value of installed_version matches the value of latest_version, the update entity state will be on. |
| `latest_version` | template Required | Defines a template to get the latest version. When the value of installed_version matches the value of latest_version, the update entity state will be on. |
| `release_summary` | template (Optional) | Defines a template to get the release summary. |
| `release_url` | template (Optional) | Defines a template to get the release URL. |
| `specific_version` | boolean (Optional, default: false) | Enable or disable using the version variable with the install action. When disabled, the specific_version variable will always provide None in the install actions. |
| `title` | template (Optional) | Defines a template to get the update title. |
| `update_percent` | template (Optional) | Defines a template to get the update completion percentage. |

## Vacuum

The template vacuum platform allows you to create vacuum entities with templates to define the state and scripts to define each action.

Vacuum entities can only be created via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - vacuum:
      - name: Living Room Vacuum
        start:
          action: script.vacuum_start
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id: sensor.living_room_vacuum_state
    vacuum:
      - name: Living Room Vacuum
        state: "{{ states('sensor.living_room_vacuum_state') }}"
        start:
          action: script.vacuum_start
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `vacuum` | map Required | List of vacuum entities |
| `attributes` | map (Optional) | Defines templates for attributes of the entity. |
| `attribute: template` | template Required | The attribute and corresponding template. |
| `battery_level` | template (Optional) | Defines a template to get the battery level of the vacuum. Legal values are numbers between 0 and 100. |
| `clean_spot` | action (Optional) | Defines an action to run when the vacuum is given a clean spot command. |
| `fan_speed` | template (Optional) | Defines a template to get the fan speed of the vacuum. |
| `fan_speeds` | string | list (Optional) | List of fan speeds supported by the vacuum. |
| `locate` | action (Optional) | Defines an action to run when the vacuum is given a locate command. |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if the vacuum works in optimistic mode. When enabled, the vacuum’s state will update immediately when a new option is chosen through the UI or service calls, without waiting for the template defined in state to update. When disabled (default), the vacuum will only update when the state template returns a new value. |
| `pause` | action (Optional) | Defines an action to run when the vacuum is paused. |
| `return_to_base` | action (Optional) | Defines an action to run when the vacuum is given a return to base command. |
| `set_fan_speed` | action (Optional) | Defines an action to run when the vacuum is given a command to set the fan speed. |
| `start` | action Required | Defines an action to run when the vacuum is started. |
| `state` | template (Optional, default: optimistic) | Defines a template to get the state of the vacuum. Valid value: docked/cleaning/idle/paused/returning/error |
| `stop` | action (Optional) | Defines an action to run when the vacuum is stopped. |

## Examples

### State based vacuum - Control vacuum with Harmony Hub

This example shows how you can use a Template Vacuum to control an IR vacuum cleaner using the Harmony Hub Remote integration.

```yaml
vacuum:
  - platform: template
    vacuums:
      living_room_vacuum:
        start:
          - action: remote.send_command
            target:
              entity_id: remote.harmony_hub
            data:
              command: Clean
              device: 52840686
        return_to_base:
          - action: remote.send_command
            target:
              entity_id: remote.harmony_hub
            data:
              command: Home
              device: 52840686
        clean_spot:
          - action: remote.send_command
            target:
              entity_id: remote.harmony_hub
            data:
              command: SpotCleaning
              device: 52840686
```

### State based vacuum - Custom attributes

This example shows how to add custom attributes.

```yaml
vacuum:
  - platform: template
    vacuums:
      living_room_vacuum:
        value_template: "{{ states('sensor.vacuum_state') }}"
        battery_level_template: "{{ states('sensor.vacuum_battery_level')|int }}"
        fan_speed_template: "{{ states('sensor.vacuum_fan_speed') }}"
        attribute_templates:
          status: >-
            {% if (states('sensor.robot_vacuum_robot_cleaner_movement') == "after" and states('sensor.robot_vacuum_robot_cleaner_cleaning_mode') == "stop")  %}
              Charging to Resume
            {% elif states('sensor.robot_vacuum_robot_cleaner_cleaning_mode') == "auto" %}
              Cleaning
            {% else %}
              Charging
            {% endif %}
```

## Weather

The template weather platform allows you to create weather entities with templates to define the state and attributes.

Weather entities can only be created via YAML.

#### Example state-based configuration.yaml entry

```yaml
template:
  - weather:
      - name: "My Weather Station"
        condition_template: "{{ states('weather.my_region') }}"
        temperature_template: "{{ states('sensor.temperature') | float }}"
        temperature_unit: "°C"
        humidity_template: "{{ states('sensor.humidity') | float }}"
        forecast_daily_template: "{{ state_attr('weather.my_region', 'forecast_data') }}"
```

#### Example trigger-based configuration.yaml entry

```yaml
template:
  - triggers:
      - trigger: state
        entity_id:
          - weather.my_region
          - sensor.temperature
          - sensor.humidity
    weather:
      - name: "My Weather Station"
        condition_template: "{{ states('weather.my_region') }}"
        temperature_template: "{{ states('sensor.temperature') | float }}"
        temperature_unit: "°C"
        humidity_template: "{{ states('sensor.humidity') | float }}"
        forecast_daily_template: "{{ state_attr('weather.my_region', 'forecast_data') }}"
```
apparent_temperature_template template (Optional)

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `apparent_temperature_template` | template (Optional) | The current apparent (feels-like) temperature. |
| `cloud_coverage_template` | template (Optional) | The current cloud coverage. |
| `condition_template` | template (Required) | The current weather condition. |
| `dew_point_template` | template (Optional) | The current dew point. |
| `forecast_daily_template` | template (Optional) | Daily forecast data. |
| `forecast_hourly_template` | template (Optional) | Hourly forecast data. |
| `forecast_twice_daily_template` | template (Optional) | Twice daily forecast data. |
| `humidity_template` | template (Required) | The current humidity. |
| `ozone_template` | template (Optional) | The current ozone level. |
| `precipitation_unit` | string (Optional) | Unit for precipitation output. Valid options: km, mi, ft, m, cm, mm, in, yd. |
| `pressure_template` | template (Optional) | The current air pressure. |
| `pressure_unit` | string (Optional) | Unit for pressure_template output. Valid options: Pa, hPa, kPa, bar, cbar, mbar, mmHg, inHg, psi. |
| `temperature_template` | template (Required) | The current temperature. |
| `temperature_unit` | string (Optional) | Unit for temperature_template output. Valid options: °C, °F, K. |
| `uv_index_template` | template (Optional) | The current UV index. |
| `visibility_template` | template (Optional) | The current visibility. |
| `visibility_unit` | string (Optional) | Unit for visibility_template output. Valid options: km, mi, ft, m, cm, mm, in, yd. |
| `wind_gust_speed_template` | template (Optional) | The current wind gust speed. |
| `wind_speed_template` | template (Optional) | The current wind speed. |
| `wind_speed_unit` | string (Optional) | Unit for wind_speed_template output. Valid options: m/s, km/h, mph, mm/d, in/d, in/h. |
| `wind_bearing_template` | template (Optional) | The current wind bearing. |

Trigger based weather - Weather Forecast from response data 
This example demonstrates how to use an action to call a action with response data and use the response in a template.

set_fan_speed action (Optional)
Defines an action to run when the vacuum is given a command to set the fan speed.

start action Required
Defines an action to run when the vacuum is started.

state template (Optional, default: optimistic)
Defines a template to get the state of the vacuum. Valid value: docked/cleaning/idle/paused/returning/error

stop action (Optional)
Defines an action to run when the vacuum is stopped.

State based vacuum - Control vacuum with Harmony Hub 
This example shows how you can use a Template Vacuum to control an IR vacuum cleaner using the Harmony Hub Remote integration.

vacuum:
  - platform: template
    vacuums:
      living_room_vacuum:
        start:
          - action: remote.send_command
            target:
              entity_id: remote.harmony_hub
            data:
              command: Clean
              device: 52840686
        return_to_base:
          - action: remote.send_command
            target:
              entity_id: remote.harmony_hub
            data:
              command: Home
              device: 52840686
        clean_spot:
          - action: remote.send_command
            target:
              entity_id: remote.harmony_hub
            data:
              command: SpotCleaning
              device: 52840686
YAML
State based vacuum - Custom attributes 
This example shows how to add custom attributes.

vacuum:
  - platform: template
    vacuums:
      living_room_vacuum:
        value_template: "{{ states('sensor.vacuum_state') }}"
        battery_level_template: "{{ states('sensor.vacuum_battery_level')|int }}"
        fan_speed_template: "{{ states('sensor.vacuum_fan_speed') }}"
        attribute_templates:
          status: >-
            {% if (states('sensor.robot_vacuum_robot_cleaner_movement') == "after" and states('sensor.robot_vacuum_robot_cleaner_cleaning_mode') == "stop")  %}
              Charging to Resume
            {% elif states('sensor.robot_vacuum_robot_cleaner_cleaning_mode') == "auto" %}
              Cleaning
            {% else %}
              Charging
            {% endif %}
YAML
Weather 
The template weather platform allows you to create weather entities with templates to define the state and attributes.

Weather entities can only be created via YAML.

# Example state-based configuration.yaml entry
template:
  - weather:
      - name: "My Weather Station"
        condition_template: "{{ states('weather.my_region') }}"
        temperature_template: "{{ states('sensor.temperature') | float }}"
        temperature_unit: "°C"
        humidity_template: "{{ states('sensor.humidity') | float }}"
        forecast_daily_template: "{{ state_attr('weather.my_region', 'forecast_data') }}"
YAML
# Example trigger-based configuration.yaml entry
template:
  - triggers:
      - trigger: state
        entity_id:
        - weather.my_region
        - sensor.temperature
        - sensor.humidity
    weather:
      - name: "My Weather Station"
        condition_template: "{{ states('weather.my_region') }}"
        temperature_template: "{{ states('sensor.temperature') | float }}"
        temperature_unit: "°C"
        humidity_template: "{{ states('sensor.humidity') | float }}"
        forecast_daily_template: "{{ state_attr('weather.my_region', 'forecast_data') }}"
YAML
Configuration Variables weather map Required
List of weather entities

apparent_temperature_template template (Optional)
The current apparent (feels-like) temperature.

cloud_coverage_template template (Optional)
The current cloud coverage.

condition_template template Required
The current weather condition.

dew_point_template template (Optional)
The current dew point.

forecast_daily_template template (Optional)
Daily forecast data.

forecast_hourly_template template (Optional)
Hourly forecast data.

forecast_twice_daily_template template (Optional)
Twice daily forecast data.

humidity_template template Required
The current humidity.

ozone_template template (Optional)
The current ozone level.

precipitation_unit string (Optional)
Unit for precipitation output. Valid options are km, mi, ft, m, cm, mm, in, yd.

pressure_template template (Optional)
The current air pressure.

pressure_unit string (Optional)
Unit for pressure_template output. Valid options are Pa, hPa, kPa, bar, cbar, mbar, mmHg, inHg, psi.

temperature_template template Required
The current temperature.

temperature_unit string (Optional)
Unit for temperature_template output. Valid options are °C, °F, and K.

uv_index_template template (Optional)
The current UV index.

visibility_template template (Optional)
The current visibility.

visibility_unit string (Optional)
Unit for visibility_template output. Valid options are km, mi, ft, m, cm, mm, in, yd.

wind_gust_speed_template template (Optional)
The current wind gust speed.

wind_speed_template template (Optional)
The current wind speed.

wind_speed_unit string (Optional)
Unit for wind_speed_template output. Valid options are m/s, km/h, mph, mm/d, in/d, and in/h.

wind_bearing_template template (Optional)
The current wind bearing.

template:
### Trigger-based weather — Weather Forecast from response data

This example demonstrates how to use an action to call a service with response data and use the response in a template.

```yaml
template:
  - triggers:
      - trigger: time_pattern
        hours: /1
    actions:
      - action: weather.get_forecasts
        data:
          type: hourly
        target:
          entity_id: weather.home
        response_variable: hourly
    sensor:
      - name: Weather Forecast Hourly
        unique_id: weather_forecast_hourly
        state: "{{ now().isoformat() }}"
        attributes:
          forecast: "{{ hourly['weather.home'].forecast }}"
```

> **Tip**: See the Home Assistant video tutorial for how to set up a trigger-based template that uses an action to retrieve the weather forecast (precipitation).


## Combining multiple template entities

The template integration allows defining multiple sections.

#### Example configuration.yaml entry with two sections

```yaml
template:
  # Define state-based template entities
  - sensor:
      ...
  - binary_sensor:
      ...

  # Define trigger-based template entities
  - triggers:
      ...
    sensor:
      ...
    binary_sensor:
      ...
```


## Trigger-based sensor and binary sensor storing webhook information

Template entities can be triggered using any automation trigger, including webhook triggers. Use a trigger-based template entity to store this information in template entities.

```yaml
template:
  - triggers:
      - trigger: webhook
        webhook_id: my-super-secret-webhook-id
    sensor:
      - name: "Webhook Temperature"
        state: "{{ trigger.json.temperature }}"
        unit_of_measurement: °C

      - name: "Webhook Humidity"
        state: "{{ trigger.json.humidity }}"
        unit_of_measurement: %

    binary_sensor:
      - name: "Motion"
        state: "{{ trigger.json.motion }}"
        device_class: motion
```

You can test this trigger entity with the following CURL command:

```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"temperature": 5, "humidity": 34, "motion": true}' \
  http://homeassistant.local:8123/api/webhook/my-super-secret-webhook-id
```

template:

## Template and action variables

State-based and trigger-based template entities have the special template variable `this` available in their templates and actions. The `this` variable is the current state object of the entity and aids self-referencing of an entity’s state and attributes in templates and actions. Trigger-based entities also provide the trigger data.

> **Note**: Self-referencing using `this` provides the state and attributes for the entity before rendering the templates to calculate a new state. In other words, it contains the previous state.

### Self referencing

This example demonstrates how the `this` variable can be used in templates for self-referencing.

```yaml
template:
  - sensor:
      - name: test
        state: "{{ this.attributes.test | default('Value when missing') }}"
        # not: "{{ state_attr('sensor.test', 'test') }}"
        attributes:
          test: "{{ now() }}"
```

## Optimistic mode

For template entities that support interactivity (like number and select), you can enable optimistic mode by setting the `optimistic` parameter to `true`. This affects how the entity’s state updates when you interact with it:

- With optimistic mode **disabled** (default): When you interact with the entity (for example, selecting a new option in a dropdown or setting a new number value), the entity’s state in Home Assistant will only update after the underlying template defined in the state parameter returns the new value.
- With optimistic mode **enabled**: When you interact with the entity, the entity’s state in Home Assistant immediately updates to reflect your change, without waiting for the state template to update. This provides a more responsive UI experience but may not reflect the actual state if the underlying action fails or takes time to complete.

Optimistic mode is particularly useful when:

- The underlying system doesn’t provide immediate feedback
- You want a more responsive UI experience
- You’re confident the action will succeed

When optimistic mode is disabled (default), you get more accuracy but potentially a less responsive UI, as the entity only updates after confirmation from the underlying system.

template:
template:

## Rate limiting updates

When there are entities present in the template and no triggers are defined, the template will be re-rendered when one of the entities changes states. To avoid this taking up too many resources in Home Assistant, rate limiting will be automatically applied if too many states are observed.

> **Tip**: Define a trigger to avoid a rate limit and get more control over entity updates.

When `states` is used in a template by itself to iterate all states on the system, the template is re-rendered each time any state changed event happens if any part of the state is accessed. When merely counting states, the template is only re-rendered when a state is added or removed from the system. On busy systems with many entities or hundreds of thousands state changed events per day, templates may re-render more than desirable.

In the below example, re-renders are limited to once per minute because we iterate over all available entities:

```yaml
template:
  - binary_sensor:
      - name: "Has Unavailable States"
        state: "{{ states | selectattr('state', 'in', ['unavailable', 'unknown', 'none']) | list | count }}"
```

In the below example, re-renders are limited to once per second because we iterate over all entities in a single domain (sensor):

```yaml
template:
  - binary_sensor:
      - name: "Has Unavailable States"
        state: "{{ states.sensor | selectattr('state', 'in', ['unavailable', 'unknown', 'none']) | list | count }}"
```

If the template accesses every state on the system, a rate limit of one update per minute is applied. If the template accesses all states under a specific domain, a rate limit of one update per second is applied. If the template only accesses specific states, receives update events for specifically referenced entities, or the `homeassistant.update_entity` action is used, no rate limit is applied.


## Considerations

### Startup

If you are using the state of a platform that might not be available during startup, the Template Sensor may get an unknown state. To avoid this, use the `states()` function in your template. For example, you should replace `{{ states.sensor.moon.state }}` with this equivalent that returns the state and never results in unknown: `{{ states('sensor.moon') }}`.

The same would apply to the `is_state()` function. You should replace `{{ states.switch.source.state == 'on' }}` with this equivalent that returns true/false and never gives an unknown result:

```jinja
{{ is_state('switch.source', 'on') }}
```

## Using blueprints

If you’re just starting out and are not really familiar with templates, we recommend that you start with blueprint template entities. These are template entities which are ready-made by the community and that you only need to configure.

Each blueprint contains the “recipe” for creating a single template entity, but you can create multiple template entities based on the same blueprint.

To create your first template entity based on a blueprint, open up your `configuration.yaml` file and add:

#### Example configuration.yaml template entity based on a blueprint located in `config/blueprints/homeassistant/inverted_binary_sensor.yaml`

```yaml
template:
  - use_blueprint:
      path: homeassistant/inverted_binary_sensor.yaml # relative to config/blueprints/template/
      input:
        reference_entity: binary_sensor.foo
    name: Inverted foo
    unique_id: inverted_foo
```

If you look at the blueprint definition, you will notice it has one input defined (`reference_entity`), which expects a `binary_sensor` entity ID. When you create a template entity based on that blueprint, you will have to tell it which of your `binary_sensor` entities it should use to fill that spot.

### Importing blueprints

Home Assistant can import blueprints from the Home Assistant forums, GitHub, and GitHub gists.

To import a blueprint, first find a blueprint you want to import.

If you just want to practice importing, you can use this URL:

https://github.com/home-assistant/core/blob/dev/homeassistant/components/template/blueprints/inverted_binary_sensor.yaml

Download the file and place it under `config/blueprints/template/<source or author>/<blueprint name>.yaml`

Use a config similar to the one above to create a new template entity based on the blueprint you just imported.

Make sure to fill in all required inputs.

The blueprint can now be used for creating template entities.


## Event: `event_template_reloaded`

The `event_template_reloaded` event is fired when Template entities have been reloaded and entities thus might have changed. This event has no additional data.

alarm_control_panel_name map Required
disarm action (Optional)

## Legacy Alarm Control Panel configuration format

These formats still work but are no longer recommended. Use modern configuration.

This format is configured as a platform for the alarm_control_panel integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
alarm_control_panel:
  - platform: template
    panels:
      safe_alarm_panel:
        value_template: "{{ states('alarm_control_panel.real_alarm') }}"
        arm_away:
          action: alarm_control_panel.alarm_arm_away
          target:
            entity_id: alarm_control_panel.real_alarm
          data:
            code: !secret alarm_code
        arm_home:
          action: alarm_control_panel.alarm_arm_home
          target:
            entity_id: alarm_control_panel.real_alarm
          data:
            code: !secret alarm_code
        disarm:
          - condition: state
            entity_id: device_tracker.paulus
            state: "home"
          - action: alarm_control_panel.alarm_disarm
            target:
              entity_id: alarm_control_panel.real_alarm
            data:
              code: !secret alarm_code
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `panels` | map (Required) | List of your panels. |
| `alarm_control_panel_name` | map (Required) | The slug of the panel. |
| `name` | string (Optional) | Name to use in the frontend. Default: Template Alarm Control Panel |
| `unique_id` | string (Optional) | An ID that uniquely identifies this alarm control panel. Set this to a unique value to allow customization through the UI. |
| `value_template` | template (Optional) | Defines a template to set the state of the alarm panel. Only the states armed_away, armed_home, armed_night, armed_vacation, arming, disarmed, pending, triggered and unavailable are used. |
| `disarm` | action (Optional) | Defines an action to run when the alarm is disarmed. |
| `arm_away` | action (Optional) | Defines an action to run when the alarm is armed to away mode. |

arm_home action (Optional)
Defines an action to run when the alarm is armed to home mode.

arm_night action (Optional)
Defines an action to run when the alarm is armed to night mode.

arm_vacation action (Optional)
Defines an action to run when the alarm is armed to vacation mode.

arm_custom_bypass action (Optional)
Defines an action to run when the alarm is armed to custom bypass mode.

sensor_name map Required
friendly_name string (Optional)
device_class device_class (Optional, default: None)
availability_template template (Optional, default: true)
delay_on time (Optional)
delay_off time (Optional)

### Additional Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `trigger` | action (Optional) | Defines an action to run when the alarm is triggered. |
| `code_arm_required` | boolean (Optional, default: true) | If true, the code is required to arm the alarm. |
| `code_format` | string (Optional, default: number) | One of number, text or no_code. Format for the code used to arm/disarm the alarm. |

## Legacy Binary Sensor configuration format

These formats still work but are no longer recommended. Use modern configuration.

This format is configured as a platform for the binary_sensor integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
binary_sensor:
  - platform: template
    sensors:
      sun_up:
        friendly_name: "Sun is up"
        value_template: "{{ state_attr('sun.sun', 'elevation') > 0 }}"
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `sensors` | map (Required) | List of your sensors. |
| `sensor_name` | map (Required) | The slug of the sensor. |
| `friendly_name` | string (Optional) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this binary sensor. Set this to a unique value to allow customization through the UI. |
| `device_class` | device_class (Optional, default: None) | Sets the class of the device, changing the device state and icon that is displayed on the frontend. |
| `value_template` | template (Required) | The sensor is on if the template evaluates as True and off otherwise. The actual appearance in the frontend (Open/Closed, Detected/Clear etc) depends on the sensor’s device_class value. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `icon_template` | template (Optional) | Defines a template for the icon of the sensor. |
| `entity_picture_template` | template (Optional) | Defines a template for the entity picture of the sensor. |
| `attribute_templates` | map (Optional) | Defines templates for attributes of the sensor. |
| `attribute: template` | template (Required) | The attribute and corresponding template. |
| `delay_on` | time (Optional) | The amount of time the template state must be met before this sensor will switch to on. This can also be a template. |
| `delay_off` | time (Optional) | The amount of time the template state must be not met before this sensor will switch to off. This can also be a template. |

## Legacy Cover configuration format

This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the cover integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
cover:
  - platform: template
    covers:
      garage_door:
        device_class: garage
        friendly_name: "Garage Door"
        value_template: "{{ states('sensor.garage_door')|float > 0 }}"
        open_cover:
          action: script.open_garage_door
        close_cover:
          action: script.close_garage_door
        stop_cover:
          action: script.stop_garage_door
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `covers` | map (Required) | List of your covers. |
| `friendly_name` | string (Optional) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this cover. Set this to a unique value to allow customization through the UI. |
| `value_template` | template (Optional) | Defines a template to get the state of the cover. Valid output values from the template are open, opening, closing and closed which are directly mapped to the corresponding states. In addition, true is valid as a synonym to open and false as a synonym to closed. If both a value_template and a position_template are specified, only opening and closing are set from the value_template. If the template produces a None value the state will be set to unknown. |
| `position_template` | template (Optional) | Defines a template to get the position of the cover. Legal values are numbers between 0 (closed) and 100 (open). If the template produces a None value the current position will be set to unknown. |
| `icon_template` | template (Optional) | Defines a template to specify which icon to use. |
| `entity_picture_template` | template (Optional) | Defines a template for the entity picture of the cover. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `device_class` | string (Optional) | Sets the class of the device, changing the device state and icon that is displayed on the frontend. |
| `open_cover` | action (Inclusive) | Defines an action to open the cover. If open_cover is specified, close_cover must also be specified. At least one of open_cover and set_cover_position must be specified. |
| `close_cover` | action (Inclusive) | Defines an action to close the cover. |
| `stop_cover` | action (Optional) | Defines an action to stop the cover. |
| `set_cover_position` | action (Optional) | Defines an action to set to a cover position (between 0 and 100). The variable position will contain the entity’s set position. |
| `set_cover_tilt_position` | action (Optional) | Defines an action to set the tilt of a cover (between 0 and 100). The variable tilt will contain the entity’s set tilt position. |
| `optimistic` | boolean (Optional, default: false) | Force cover position to use optimistic mode. |
| `tilt_optimistic` | boolean (Optional, default: false) | Force cover tilt position to use optimistic mode. |
| `tilt_template` | template (Optional) | Defines a template to get the tilt state of the cover. Legal values are numbers between 0 (closed) and 100 (open). If the template produces a None value the current tilt state will be set to unknown. |

## Legacy Fan configuration format

This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the fan integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
fan:
  - platform: template
    fans:
      bedroom_fan:
        friendly_name: "Bedroom fan"
        value_template: "{{ states('input_boolean.state') }}"
        percentage_template: "{{ states('input_number.percentage') }}"
        preset_mode_template: "{{ states('input_select.preset_mode') }}"
        oscillating_template: "{{ states('input_select.osc') }}"
        direction_template: "{{ states('input_select.direction') }}"
        turn_on:
          action: script.fan_on
        turn_off:
          action: script.fan_off
        set_percentage:
          action: script.fans_set_speed
          data:
            percentage: "{{ percentage }}"
        set_preset_mode:
          action: script.fans_set_preset_mode
          data:
            preset_mode: "{{ preset_mode }}"
        set_oscillating:
          action: script.fan_oscillating
          data:
            oscillating: "{{ oscillating }}"
        set_direction:
          action: script.fan_direction
          data:
            direction: "{{ direction }}"
        speed_count: 6
        preset_modes:
          - 'auto'
          - 'smart'
          - 'whoosh'
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `fans` | map (Required) | List of your fans. |
| `friendly_name` | string (Optional) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this fan. Set this to a unique value to allow customization through the UI. |
| `value_template` | template (Required) | Defines a template to get the state of the fan. Valid values: on, off. |
| `percentage_template` | template (Optional) | Defines a template to get the speed percentage of the fan. |
| `preset_mode_template` | template (Optional) | Defines a template to get the preset mode of the fan. |
| `oscillating_template` | template (Optional) | Defines a template to get the osc state of the fan. Valid values: true, false. |
| `direction_template` | template (Optional) | Defines a template to get the direction of the fan. Valid values: forward, reverse. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `turn_on` | action (Required) | Defines an action to run when the fan is turned on. |
| `turn_off` | action (Required) | Defines an action to run when the fan is turned off. |
| `set_percentage` | action (Optional) | Defines an action to run when the fan is given a speed percentage command. |
| `set_preset_mode` | action (Optional) | Defines an action to run when the fan is given a preset command. |
| `set_oscillating` | action (Optional) | Defines an action to run when the fan is given an osc state command. |
| `set_direction` | action (Optional) | Defines an action to run when the fan is given a direction command. |
| `preset_modes` | string \| list (Optional, default: []) | List of preset modes the fan is capable of. This is an arbitrary list of strings and must not contain any speeds. |
| `speed_count` | integer (Optional, default: 100) | The number of speeds the fan supports. Used to calculate the percentage step for the fan.increase_speed and fan.decrease_speed actions. |

## Legacy Light configuration format

This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the light integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
light:
  - platform: template
    lights:
      theater_lights:
        friendly_name: "Theater Lights"
        level_template: "{{ state_attr('sensor.theater_brightness', 'lux')|int }}"
        value_template: "{{ state_attr('sensor.theater_brightness', 'lux')|int > 0 }}"
        temperature_template: "{{states('input_number.temperature_input') | int}}"
        hs_template: "({{states('input_number.h_input') | int}}, {{states('input_number.s_input') | int}})"
        effect_list_template: "{{ state_attr('light.led_strip', 'effect_list') }}"
        turn_on:
          action: script.theater_lights_on
        turn_off:
          action: script.theater_lights_off
        set_level:
          action: script.theater_lights_level
          data:
            brightness: "{{ brightness }}"
        set_temperature:
          action: input_number.set_value
          data:
            value: "{{ color_temp }}"
            entity_id: input_number.temperature_input
        set_hs:
          - action: input_number.set_value
            data:
              value: "{{ h }}"
              entity_id: input_number.h_input
          - action: input_number.set_value
            data:
              value: "{{ s }}"
              entity_id: input_number.s_input
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              transition: "{{ transition | float }}"
              hs_color:
                - "{{ hs[0] }}"
                - "{{ hs[1] }}"
        set_effect:
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              effect: "{{ effect }}"
        supports_transition_template: "{{ true }}"
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `lights` | map (Required) | List of your lights. |
| `friendly_name` | string (Optional) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this light. Set this to a unique value to allow customization through the UI. |
| `value_template` | template (Optional, default: optimistic) | Defines a template to get the state of the light. |
| `level_template` | template (Optional, default: optimistic) | Defines a template to get the brightness of the light. |
| `temperature_template` | template (Optional, default: optimistic) | Defines a template to get the color temperature of the light. |
| `hs_template` | template (Optional, default: optimistic) | Defines a template to get the HS color of the light. Must render a tuple (hue, saturation). |
| `rgb_template` | template (Optional, default: optimistic) | Defines a template to get the RGB color of the light. Must render a tuple or a list (red, green, blue). |
| `rgbw_template` | template (Optional, default: optimistic) | Defines a template to get the RGBW color of the light. Must render a tuple or a list (red, green, blue, white). |
| `rgbww_template` | template (Optional, default: optimistic) | Defines a template to get the RGBWW color of the light. Must render a tuple or a list (red, green, blue, cold white, warm white). |
| `supports_transition_template` | template (Optional, default: false) | Defines a template to get if light supports transition. Should return boolean value (True/False). If this value is True transition parameter in a turn on or turn off call will be passed as a named parameter transition to either of the scripts. |
| `effect_list_template` | template (Inclusive, default: optimistic) | Defines a template to get the list of supported effects. Must render a list. |
| `effect_template` | template (Inclusive, default: optimistic) | Defines a template to get the effect of the light. |
| `min_mireds_template` | template (Optional, default: optimistic) | Defines a template to get the min mireds value of the light. |
| `max_mireds_template` | template (Optional, default: optimistic) | Defines a template to get the max mireds value of the light. |
| `icon_template` | template (Optional) | Defines a template for an icon or picture, e.g., showing a different icon for different states. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `turn_on` | action (Required) | Defines an action to run when the light is turned on. May receive variables brightness and/or transition. |
| `turn_off` | action (Required) | Defines an action to run when the light is turned off. May receive variable transition. |
| `set_level` | action (Optional) | Defines an action to run when the light is given a brightness command. The script will only be called if the turn_on call only has brightness, and optionally transition. Receives variables brightness and optionally transition. |
| `set_temperature` | action (Optional) | Defines an action to run when the light is given a color temperature command. Receives variable color_temp. May also receive variables brightness and/or transition. |
| `set_hs` | action (Optional) | Defines an action to run when the light is given a hs color command. Available variables: hs as a tuple, h and s. |
| `set_rgb` | action (Optional) | Defines an action to run when the light is given an RGB color command. Available variables: rgb as a tuple, r, g and b. |
| `set_rgbw` | action (Optional) | Defines an action to run when the light is given an RGBW color command. Available variables: rgbw as a tuple, rgb as a tuple, r, g, b and w. |
| `set_rgbww` | action (Optional) | Defines an action to run when the light is given an RGBWW color command. Available variables: rgbww as a tuple, rgb as a tuple, r, g, b, cw and ww. |
| `set_effect` | action (Inclusive) | Defines an action to run when the light is given an effect command. Receives variable effect. May also receive variables brightness and/or transition. |

## Legacy Lock configuration format

This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the lock integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
lock:
  - platform: template
    name: Garage door
    value_template: "{{ is_state('sensor.door', 'on') }}"
    lock:
      action: switch.turn_on
      target:
        entity_id: switch.door
    unlock:
      action: switch.turn_off
      target:
        entity_id: switch.door
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `name` | string (Optional, default: Template Lock) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this lock. Set this to a unique value to allow customization through the UI. |
| `value_template` | template (Required) | Defines a template to set the state of the lock. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `code_format_template` | template (Optional, default: None) | Defines a template to get the code_format attribute of the entity. This template must evaluate to a valid Python regular expression or None. If it evaluates to a not-None value, the user is prompted to enter a code when interacting with the lock. The code will be matched against the regular expression, and only if it matches, the lock/unlock actions will be executed. The actual validity of the entered code must be verified within these actions. If there’s a syntax error in the template, the entity will be unavailable. If the template fails to render for other reasons or if the regular expression is invalid, no code will be accepted and the lock/unlock actions will never be invoked. |
| `lock` | action (Required) | Defines an action to run when the lock is locked. |
| `unlock` | action (Required) | Defines an action to run when the lock is unlocked. |
| `open` | action (Optional) | Defines an action to run when the lock is opened. |
| `optimistic` | boolean (Optional, default: false) | Flag that defines if lock works in optimistic mode. |

## Legacy Sensor configuration format

This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the sensor integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
sensor:
  - platform: template
    sensors:
      solar_angle:
        friendly_name: "Sun angle"
        unit_of_measurement: "degrees"
        value_template: "{{ state_attr('sun.sun', 'elevation') }}"

      sunrise:
        value_template: "{{ state_attr('sun.sun', 'next_rising') }}"
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `sensors` | map (Required) | Map of your sensors. |
| `friendly_name` | string (Optional) | Name to use in the frontend. |
| `friendly_name_template` | template (Optional) | Defines a template for the name to be used in the frontend (this overrides friendly_name). |
| `unique_id` | string (Optional) | An ID that uniquely identifies this sensor. Set this to a unique value to allow customization through the UI. |
| `unit_of_measurement` | string (Optional, default: None) | Defines the units of measurement of the sensor, if any. This will also display the value based on the user profile Number Format setting and influence the graphical presentation in the history visualization as a continuous value. |
| `value_template` | template (Required) | Defines a template to get the state of the sensor. |
| `icon_template` | template (Optional) | Defines a template for the icon of the sensor. |
| `entity_picture_template` | template (Optional) | Defines a template for the entity picture of the sensor. |
| `attribute_templates` | map (Optional) | Defines templates for attributes of the sensor. |
| `attribute: template` | template (Required) | The attribute and corresponding template. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the integration. If the template returns true, the device is available. If the template returns any other value, the device will be unavailable. If availability_template is not configured, the integration will always be available. |
| `device_class` | device_class (Optional, default: None) | Sets the class of the device, changing the device state and icon that is displayed on the UI (see below). It does not set the unit_of_measurement. |

## Legacy Switch configuration format

This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the switch integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
switch:
  - platform: template
    switches:
      skylight:
        value_template: "{{ is_state('sensor.skylight', 'on') }}"
        turn_on:
          action: switch.turn_on
          target:
            entity_id: switch.skylight_open
        turn_off:
          action: switch.turn_off
          target:
            entity_id: switch.skylight_close
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `switches` | map (Required) | List of your switches. |
| `friendly_name` | string (Optional) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this switch. Set this to a unique value to allow customization through the UI. |
| `value_template` | template (Optional, default: optimistic) | Defines a template to set the state of the switch. If not defined, the switch will optimistically assume all commands are successful. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `turn_on` | action (Required) | Defines an action or list of actions to run when the switch is turned on. |
| `turn_off` | action (Required) | Defines an action or list of actions to run when the switch is turned off. |
| `icon_template` | template (Optional) | Defines a template for the icon of the switch. |
| `entity_picture_template` | template (Optional) | Defines a template for the picture of the switch. |


## Legacy Vacuum Configuration Format

> **Note**: This format still works but is no longer recommended. Use modern configuration. This format is configured as a platform for the vacuum integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
vacuum:
  - platform: template
    vacuums:
      living_room_vacuum:
        start:
          action: script.vacuum_start
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `vacuums` | map (Required) | List of your vacuums. |
| `friendly_name` | string (Optional) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this vacuum. Set this to a unique value to allow customization through the UI. |
| `value_template` | template (Optional) | Defines a template to get the state of the vacuum. Valid value: docked/cleaning/idle/paused/returning/error. |
| `battery_level_template` | template (Optional) | Defines a template to get the battery level of the vacuum. Legal values are numbers between 0 and 100. |
| `fan_speed_template` | template (Optional) | Defines a template to get the fan speed of the vacuum. |
| `attribute_templates` | map (Optional) | Defines templates for attributes of the sensor. |
| `attribute: template` | template (Required) | The attribute and corresponding template. |
| `availability_template` | template (Optional, default: true) | Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed. |
| `start` | action (Required) | Defines an action to run when the vacuum is started. |
| `pause` | action (Optional) | Defines an action to run when the vacuum is paused. |
| `stop` | action (Optional) | Defines an action to run when the vacuum is stopped. |
| `return_to_base` | action (Optional) | Defines an action to run when the vacuum is given a return to base command. |
| `clean_spot` | action (Optional) | Defines an action to run when the vacuum is given a clean spot command. |
| `locate` | action (Optional) | Defines an action to run when the vacuum is given a locate command. |
| `set_fan_speed` | action (Optional) | Defines an action to run when the vacuum is given a command to set the fan speed. |
| `fan_speeds` | string or list (Optional) | List of fan speeds supported by the vacuum. |


## Legacy Weather Configuration Format

> **Note**: This format still works but is no longer recommended. Use modern configuration. This format is configured as a platform for the weather integration and not directly under the template integration.

#### Example configuration.yaml entry

```yaml
weather:
  - platform: template
    name: "My Weather Station"
    condition_template: "{{ states('weather.my_region') }}"
    temperature_template: "{{ states('sensor.temperature') | float }}"
    temperature_unit: "°C"
    humidity_template: "{{ states('sensor.humidity') | float }}"
    forecast_daily_template: "{{ state_attr('weather.my_region', 'forecast_data') }}"
```

### Configuration Variables

| Variable | Type | Description |
| -------- | ---- | ----------- |
| `name` | template (Required) | Name to use in the frontend. |
| `unique_id` | string (Optional) | An ID that uniquely identifies this weather entity. Set this to a unique value to allow customization through the UI. |
| `condition_template` | template (Required) | The current weather condition. |
| `temperature_template` | template (Required) | The current temperature. |
| `dew_point_template` | template (Optional) | The current dew point. |
| `apparent_temperature_template` | template (Optional) | The current apparent (feels-like) temperature. |
| `temperature_unit` | string (Optional) | Unit for temperature_template output. Valid options: °C, °F, K. |
| `humidity_template` | template (Required) | The current humidity. |
| `attribution_template` | string (Optional) | The attribution to be shown in the frontend. |
| `pressure_template` | template (Optional) | The current air pressure. |
| `pressure_unit` | string (Optional) | Unit for pressure_template output. Valid options: Pa, hPa, kPa, bar, cbar, mbar, mmHg, inHg, psi. |
| `wind_speed_template` | template (Optional) | The current wind speed. |
| `wind_gust_speed_template` | template (Optional) | The current wind gust speed. |
| `wind_speed_unit` | string (Optional) | Unit for wind_speed_template output. Valid options: m/s, km/h, mph, mm/d, in/d, in/h. |
| `wind_bearing_template` | template (Optional) | The current wind bearing. |
| `ozone_template` | template (Optional) | The current ozone level. |
| `cloud_coverage_template` | template (Optional) | The current cloud coverage. |
| `visibility_template` | template (Optional) | The current visibility. |
| `visibility_unit` | string (Optional) | Unit for visibility_template output. Valid options: km, mi, ft, m, cm, mm, in, yd. |
| `forecast_daily_template` | template (Optional) | Daily forecast data. |
| `forecast_hourly_template` | template (Optional) | Hourly forecast data. |
| `forecast_twice_daily_template` | template (Optional) | Twice daily forecast data. |
| `precipitation_unit` | string (Optional) | Unit for precipitation output. Valid options: km, mi, ft, m, cm, mm, in, yd. |

Legacy Cover configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the cover integration and not directly under the template integration.

### Example configuration.yaml entry

```yaml
cover:
  - platform: template
    covers:
      garage_door:
        device_class: garage
        friendly_name: "Garage Door"
        value_template: "{{ states('sensor.garage_door')|float > 0 }}"
        open_cover:
          action: script.open_garage_door
        close_cover:
          action: script.close_garage_door
        stop_cover:
          action: script.stop_garage_door
```

Configuration Variables covers map Required
List of your covers.

friendly_name string (Optional)
Name to use in the frontend.

unique_id string (Optional)
An ID that uniquely identifies this cover. Set this to a unique value to allow customization through the UI.

value_template template (Optional)
Defines a template to get the state of the cover. Valid output values from the template are open, opening, closing and closed which are directly mapped to the corresponding states. In addition, true is valid as a synonym to open and false as a synonym to closed. If both a value_template and a position_template are specified, only opening and closing are set from the value_template. If the template produces a None value the state will be set to unknown.

position_template template (Optional)
Defines a template to get the position of the cover. Legal values are numbers between 0 (closed) and 100 (open). If the template produces a None value the current position will be set to unknown.

icon_template template (Optional)
Defines a template to specify which icon to use.

entity_picture_template template (Optional)
Defines a template for the entity picture of the cover.

availability_template template (Optional, default: true)
Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison is not case sensitive; "TrUe" and "yEs" are allowed.

device_class string (Optional)
Sets the class of the device, changing the device state and icon that is displayed on the frontend.

open_cover action (Inclusive)
Defines an action to open the cover. If open_cover is specified, close_cover must also be specified. At least one of open_cover and set_cover_position must be specified.

close_cover action (Inclusive)
Defines an action to close the cover.

stop_cover action (Optional)
Defines an action to stop the cover.

set_cover_position action (Optional)
Defines an action to set to a cover position (between 0 and 100). The variable position will contain the entity’s set position.

set_cover_tilt_position action (Optional)
Defines an action to set the tilt of a cover (between 0 and 100). The variable tilt will contain the entity’s set tilt position.

optimistic boolean (Optional, default: false)
Force cover position to use optimistic mode.

tilt_optimistic boolean (Optional, default: false)
Force cover tilt position to use optimistic mode.

tilt_template template (Optional)
Defines a template to get the tilt state of the cover. Legal values are numbers between 0 (closed) and 100 (open). If the template produces a None value the current tilt state will be set to unknown.

Legacy Fan configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the fan integration and not directly under the template integration.

### Example configuration.yaml entry

```yaml
fan:
  - platform: template
    fans:
      bedroom_fan:
        friendly_name: "Bedroom fan"
        value_template: "{{ states('input_boolean.state') }}"
        percentage_template: "{{ states('input_number.percentage') }}"
        preset_mode_template: "{{ states('input_select.preset_mode') }}"
        oscillating_template: "{{ states('input_select.osc') }}"
        direction_template: "{{ states('input_select.direction') }}"
        turn_on:
          action: script.fan_on
        turn_off:
          action: script.fan_off
        set_percentage:
          action: script.fans_set_speed
          data:
            percentage: "{{ percentage }}"
        set_preset_mode:
          action: script.fans_set_preset_mode
          data:
            preset_mode: "{{ preset_mode }}"
        set_oscillating:
          action: script.fan_oscillating
          data:
            oscillating: "{{ oscillating }}"
        set_direction:
          action: script.fan_direction
          data:
            direction: "{{ direction }}"
        speed_count: 6
        preset_modes:
          - 'auto'
          - 'smart'
          - 'whoosh'
```

Configuration Variables fans map Required
List of your fans.

friendly_name string (Optional)
Name to use in the frontend.

unique_id string (Optional)
An ID that uniquely identifies this fan. Set this to a unique value to allow customization through the UI.

value_template template Required
Defines a template to get the state of the fan. Valid values: on, off

percentage_template template (Optional)
Defines a template to get the speed percentage of the fan.

preset_mode_template template (Optional)
Defines a template to get the preset mode of the fan.

oscillating_template template (Optional)
Defines a template to get the osc state of the fan. Valid values: true, false

direction_template template (Optional)
Defines a template to get the direction of the fan. Valid values: forward, reverse

availability_template template (Optional, default: true)
Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison not case sensitive; "TrUe" and "yEs" are allowed.

turn_on action Required
Defines an action to run when the fan is turned on.

turn_off action Required
Defines an action to run when the fan is turned off.

set_percentage action (Optional)
Defines an action to run when the fan is given a speed percentage command.

set_preset_mode action (Optional)
Defines an action to run when the fan is given a preset command.

set_oscillating action (Optional)
Defines an action to run when the fan is given an osc state command.

set_direction action (Optional)
Defines an action to run when the fan is given a direction command.

preset_modes string | list (Optional, default: [])
List of preset modes the fan is capable of. This is an arbitrary list of strings and must not contain any speeds.

speed_count integer (Optional, default: 100)
The number of speeds the fan supports. Used to calculate the percentage step for the fan.increase_speed and fan.decrease_speed actions.

Legacy Light configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the light integration and not directly under the template integration.

### Example configuration.yaml entry

```yaml
light:
  - platform: template
    lights:
      theater_lights:
        friendly_name: "Theater Lights"
        level_template: "{{ state_attr('sensor.theater_brightness', 'lux')|int }}"
        value_template: "{{ state_attr('sensor.theater_brightness', 'lux')|int > 0 }}"
        temperature_template: "{{states('input_number.temperature_input') | int}}"
        hs_template: "({{states('input_number.h_input') | int}}, {{states('input_number.s_input') | int}})"
        effect_list_template: "{{ state_attr('light.led_strip', 'effect_list') }}"
        turn_on:
          action: script.theater_lights_on
        turn_off:
          action: script.theater_lights_off
        set_level:
          action: script.theater_lights_level
          data:
            brightness: "{{ brightness }}"
        set_temperature:
          action: input_number.set_value
          data:
            value: "{{ color_temp }}"
            entity_id: input_number.temperature_input
        set_hs:
          - action: input_number.set_value
            data:
              value: "{{ h }}"
              entity_id: input_number.h_input
          - action: input_number.set_value
            data:
              value: "{{ s }}"
              entity_id: input_number.s_input
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              transition: "{{ transition | float }}"
              hs_color:
                - "{{ hs[0] }}"
                - "{{ hs[1] }}"
        set_effect:
          - action: light.turn_on
            data:
              entity_id:
                - light.led_strip
              effect: "{{ effect }}"
        supports_transition_template: "{{ true }}"
```
Configuration Variables lights map Required
List of your lights.

friendly_name string (Optional)
Name to use in the frontend.

unique_id string (Optional)
An ID that uniquely identifies this light. Set this to a unique value to allow customization through the UI.

value_template template (Optional, default: optimistic)
Defines a template to get the state of the light.

level_template template (Optional, default: optimistic)
Defines a template to get the brightness of the light.

temperature_template template (Optional, default: optimistic)
Defines a template to get the color temperature of the light.

hs_template template (Optional, default: optimistic)
Defines a template to get the HS color of the light. Must render a tuple (hue, saturation).

rgb_template template (Optional, default: optimistic)
Defines a template to get the RGB color of the light. Must render a tuple or a list (red, green, blue).

rgbw_template template (Optional, default: optimistic)
Defines a template to get the RGBW color of the light. Must render a tuple or a list (red, green, blue, white).

rgbww_template template (Optional, default: optimistic)
Defines a template to get the RGBWW color of the light. Must render a tuple or a list (red, green, blue, cold white, warm white).

supports_transition_template template (Optional, default: false)
Defines a template to get if light supports transition. Should return boolean value (True/False). If this value is True transition parameter in a turn on or turn off call will be passed as a named parameter transition to either of the scripts.

effect_list_template template (Inclusive, default: optimistic)
Defines a template to get the list of supported effects. Must render a list

effect_template template (Inclusive, default: optimistic)
Defines a template to get the effect of the light.

min_mireds_template template (Optional, default: optimistic)
Defines a template to get the min mireds value of the light.

max_mireds_template template (Optional, default: optimistic)
Defines a template to get the max mireds value of the light.

icon_template template (Optional)
Defines a template for an icon or picture, e.g., showing a different icon for different states.

availability_template template (Optional, default: true)
Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison not case sensitive; "TrUe" and "yEs" are allowed.

turn_on action Required
Defines an action to run when the light is turned on. May receive variables brightness and/or transition.

turn_off action Required
Defines an action to run when the light is turned off. May receive variable transition.

set_level action (Optional)
Defines an action to run when the light is given a brightness command. The script will only be called if the turn_on call only has brightness, and optionally transition. Receives variables brightness and optionally transition.

set_temperature action (Optional)
Defines an action to run when the light is given a color temperature command. Receives variable color_temp. May also receive variables brightness and/or transition.

set_hs action (Optional)
Defines an action to run when the light is given a hs color command. Available variables: hs as a tuple, h and s

set_rgb action (Optional)
Defines an action to run when the light is given an RGB color command. Available variables: rgb as a tuple, r, g and b.

set_rgbw action (Optional)
Defines an action to run when the light is given an RGBW color command. Available variables: rgbw as a tuple, rgb as a tuple, r, g, b and w.

set_rgbww action (Optional)
Defines an action to run when the light is given an RGBWW color command. Available variables: rgbww as a tuple, rgb as a tuple, r, g, b, cw and ww.

set_effect action (Inclusive)
Defines an action to run when the light is given an effect command. Receives variable effect. May also receive variables brightness and/or transition.

Legacy Lock configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the lock integration and not directly under the template integration.

### Example configuration.yaml entry

```yaml
lock:
  - platform: template
    name: Garage door
    value_template: "{{ is_state('sensor.door', 'on') }}"
    lock:
      action: switch.turn_on
      target:
        entity_id: switch.door
    unlock:
      action: switch.turn_off
      target:
        entity_id: switch.door
```

## Configuration Variables 
name string (Optional, default: Template Lock)
Name to use in the frontend.

unique_id string (Optional)
An ID that uniquely identifies this lock. Set this to a unique value to allow customization through the UI.

value_template template Required
Defines a template to set the state of the lock.

availability_template template (Optional, default: true)
Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison not case sensitive; "TrUe" and "yEs" are allowed.

code_format_template template (Optional, default: None)
Defines a template to get the code_format attribute of the entity. This template must evaluate to a valid Python regular expression or None. If it evaluates to a not-None value, the user is prompted to enter a code when interacting with the lock. The code will be matched against the regular expression, and only if it matches, the lock/unlock actions will be executed. The actual validity of the entered code must be verified within these actions. If there’s a syntax error in the template, the entity will be unavailable. If the template fails to render for other reasons or if the regular expression is invalid, no code will be accepted and the lock/unlock actions will never be invoked.

lock action Required
Defines an action to run when the lock is locked.

unlock action Required
Defines an action to run when the lock is unlocked.

open action (Optional)
Defines an action to run when the lock is opened.

optimistic boolean (Optional, default: false)
Flag that defines if lock works in optimistic mode.

Legacy Sensor configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the sensor integration and not directly under the template integration.

### Example configuration.yaml entry

```yaml
sensor:
  - platform: template
    sensors:
      solar_angle:
        friendly_name: "Sun angle"
        unit_of_measurement: "degrees"
        value_template: "{{ state_attr('sun.sun', 'elevation') }}"

      sunrise:
        value_template: "{{ state_attr('sun.sun', 'next_rising') }}"
```

Configuration Variables sensors map Required
Map of your sensors.

friendly_name string (Optional)
Name to use in the frontend.

friendly_name_template template (Optional)
Defines a template for the name to be used in the frontend (this overrides friendly_name).

unique_id string (Optional)
An ID that uniquely identifies this sensor. Set this to a unique value to allow customization through the UI.

unit_of_measurement string (Optional, default: None)
Defines the units of measurement of the sensor, if any. This will also display the value based on the user profile Number Format setting and influence the graphical presentation in the history visualization as a continuous value.

value_template template Required
Defines a template to get the state of the sensor.

icon_template template (Optional)
Defines a template for the icon of the sensor.

entity_picture_template template (Optional)
Defines a template for the entity picture of the sensor.

attribute_templates map (Optional)
Defines templates for attributes of the sensor.

attribute: template template Required
The attribute and corresponding template.

availability_template template (Optional, default: true)
Defines a template to get the available state of the integration. If the template returns true, the device is available. If the template returns any other value, the device will be unavailable. If availability_template is not configured, the integration will always be available.

device_class device_class (Optional, default: None)
Sets the class of the device, changing the device state and icon that is displayed on the UI (see below). It does not set the unit_of_measurement.

## Legacy Switch configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the switch integration and not directly under the template integration.

### Example configuration.yaml entry
switch:
  - platform: template
    switches:
      skylight:
        value_template: "{{ is_state('sensor.skylight', 'on') }}"
        turn_on:
          action: switch.turn_on
          target:
            entity_id: switch.skylight_open
        turn_off:
          action: switch.turn_off
          target:
            entity_id: switch.skylight_close
YAML
Configuration Variables switches map Required
List of your switches.

friendly_name string (Optional)
Name to use in the frontend.

unique_id string (Optional)
An ID that uniquely identifies this switch. Set this to a unique value to allow customization through the UI.

value_template template (Optional, default: optimistic)
Defines a template to set the state of the switch. If not defined, the switch will optimistically assume all commands are successful.

availability_template template (Optional, default: true)
Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison not case sensitive; "TrUe" and "yEs" are allowed.

turn_on action Required
Defines an action or list of actions to run when the switch is turned on.

turn_off action Required
Defines an action or list of actions to run when the switch is turned off.

icon_template template (Optional)
Defines a template for the icon of the switch.

entity_picture_template template (Optional)
Defines a template for the picture of the switch.

Legacy Vacuum configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the vacuum integration and not directly under the template integration.

# Example configuration.yaml entry
vacuum:
  - platform: template
    vacuums:
      living_room_vacuum:
        start:
          action: script.vacuum_start
YAML
Configuration Variables vacuums map Required
List of your vacuums.

friendly_name string (Optional)
Name to use in the frontend.

unique_id string (Optional)
An ID that uniquely identifies this vacuum. Set this to a unique value to allow customization through the UI.

value_template template (Optional)
Defines a template to get the state of the vacuum. Valid value: docked/cleaning/idle/paused/returning/error

battery_level_template template (Optional)
Defines a template to get the battery level of the vacuum. Legal values are numbers between 0 and 100.

fan_speed_template template (Optional)
Defines a template to get the fan speed of the vacuum.

attribute_templates map (Optional)
Defines templates for attributes of the sensor.

attribute: template template Required
The attribute and corresponding template.

availability_template template (Optional, default: true)
Defines a template to get the available state of the entity. If the template either fails to render or returns True, "1", "true", "yes", "on", "enable", or a non-zero number, the entity will be available. If the template returns any other value, the entity will be unavailable. If not configured, the entity will always be available. Note that the string comparison not case sensitive; "TrUe" and "yEs" are allowed.

start action Required
Defines an action to run when the vacuum is started.

pause action (Optional)
Defines an action to run when the vacuum is paused.

stop action (Optional)
Defines an action to run when the vacuum is stopped.

return_to_base action (Optional)
Defines an action to run when the vacuum is given a return to base command.

clean_spot action (Optional)
Defines an action to run when the vacuum is given a clean spot command.

locate action (Optional)
Defines an action to run when the vacuum is given a locate command.

set_fan_speed action (Optional)
Defines an action to run when the vacuum is given a command to set the fan speed.

fan_speeds string | list (Optional)
List of fan speeds supported by the vacuum.

Legacy Weather configuration format 
This format still works but is no longer recommended. Use modern configuration.

This format is configured as a platform for the weather integration and not directly under the template integration.

# Example configuration.yaml entry
weather:
  - platform: template
    name: "My Weather Station"
    condition_template: "{{ states('weather.my_region') }}"
    temperature_template: "{{ states('sensor.temperature') | float }}"
    temperature_unit: "°C"
    humidity_template: "{{ states('sensor.humidity') | float }}"
    forecast_daily_template: "{{ state_attr('weather.my_region', 'forecast_data') }}"
YAML
Configuration Variables name template Required
Name to use in the frontend.

unique_id string (Optional)
An ID that uniquely identifies this weather entity. Set this to a unique value to allow customization through the UI.

condition_template template Required
The current weather condition.

temperature_template template Required
The current temperature.

dew_point_template template (Optional)
The current dew point.

apparent_temperature_template template (Optional)
The current apparent (feels-like) temperature.

temperature_unit string (Optional)
Unit for temperature_template output. Valid options are °C, °F, and K.

humidity_template template Required
The current humidity.

attribution_template string (Optional)
The attribution to be shown in the frontend.

pressure_template template (Optional)
The current air pressure.

pressure_unit string (Optional)
Unit for pressure_template output. Valid options are Pa, hPa, kPa, bar, cbar, mbar, mmHg, inHg, psi.

wind_speed_template template (Optional)
The current wind speed.

wind_gust_speed_template template (Optional)
The current wind gust speed.

wind_speed_unit string (Optional)
Unit for wind_speed_template output. Valid options are m/s, km/h, mph, mm/d, in/d, and in/h.

wind_bearing_template template (Optional)
The current wind bearing.

ozone_template template (Optional)
The current ozone level.

cloud_coverage_template template (Optional)
The current cloud coverage.

visibility_template template (Optional)
The current visibility.

visibility_unit string (Optional)
Unit for visibility_template output. Valid options are km, mi, ft, m, cm, mm, in, yd.

forecast_daily_template template (Optional)
Daily forecast data.

forecast_hourly_template template (Optional)
Hourly forecast data.

forecast_twice_daily_template template (Optional)
Twice daily forecast data.

precipitation_unit string (Optional)
Unit for precipitation output. Valid options are km, mi, ft, m, cm, mm, in, yd.

