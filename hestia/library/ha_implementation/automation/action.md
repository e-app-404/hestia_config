---
title: "Automation actions"
description: "Automations result in action."
---
---
title: "Automation actions"
authors: "Hestia / Home Assistant docs"
source: "Local Hestia copy"
slug: "automation-actions"
tags: ["home-assistant", "automation"]
original_date: "2025-10-15"
last_updated: "2025-10-15"
url: ""
---

# Automation actions

The action of an automation is what is being executed when an automation fires. The action part follows the [script syntax](/docs/scripts/) which can be used to interact with anything via other actions or events.

For actions, you can specify the `entity_id` that it should apply to and optional parameters (to specify for example the brightness).

You can also perform the action to activate [a scene](/integrations/scene/) which will allow you to define how you want your devices to be and have Home Assistant perform the right action.

```yaml
# Example: change the light in the kitchen and living room to 150 brightness and color red.
- triggers:
  - platform: sun
    event: sunset
  actions:
    - service: light.turn_on
      target:
        entity_id:
          - light.kitchen
          - light.living_room
      data:
        brightness: 150
        rgb_color: [255, 0, 0]

# Example: notify on mobile device
- triggers:
  - platform: sun
    event: sunset
    offset: -00:30
  variables:
    notification_action: notify.paulus_iphone
  actions:
    - service: "{{ notification_action }}"
      data:
        message: "Beautiful sunset!"
    - delay: "00:00:35"
    - service: notify.notify
      data:
        message: "Oh wow you really missed something great."
```

Conditions can also be part of an action. You can combine multiple actions and conditions in a single action, and they will be processed in the order you put them in. If the result of a condition is false, the action will stop there so any action after that condition will not be executed.

```yaml
- alias: "Office at evening"
  trigger:
    - platform: state
      entity_id: sensor.office_occupancy
      to: "on"
  action:
    - service: notify.notify
      data:
        message: "Testing conditional actions"
    - condition: or
      conditions:
        - condition: numeric_state
          entity_id: sun.sun
          attribute: elevation
          below: 4
        - condition: numeric_state
          entity_id: sensor.office_illuminance
          below: 10
    - service: scene.turn_on
      target:
        entity_id: scene.office_at_evening
```