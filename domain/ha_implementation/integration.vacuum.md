---
title: "Vacuum Integration Guide"
authors: "Home Assistant Team"
source: "https://www.home-assistant.io/integrations/vacuum/"
slug: "vacuum-integration"
tags: ["home-assistant", "ops", "integration"]
original_date: "2025-10-07"
last_updated: "2025-10-07"
url: "https://www.home-assistant.io/integrations/vacuum/"
---

# Vacuum

The Vacuum integration enables the ability to control home cleaning robots within Home Assistant.

> **Note**: This is a building block integration that cannot be added to your Home Assistant directly but is used and provided by other integrations.

A building block integration differs from the typical integration that connects to a device or service. Instead, other integrations that do integrate a device or service into Home Assistant use this vacuum building block to provide entities, services, and other functionality that you can use in your automations or dashboards.

If one of your integrations features this building block, this page documents the functionality the vacuum building block offers.

## The State of a Vacuum Entity

A vacuum entity can have the following states:

- `Cleaning`: The vacuum is currently cleaning.
- `Docked`: The vacuum is currently docked. It is assumed that docked can also mean charging.
- `Error`: The vacuum encountered an error while cleaning.
- `Idle`: The vacuum is not paused, not docked, and does not have any errors.
- `Paused`: The vacuum was cleaning but was paused without returning to the dock.
- `Returning`: The vacuum is done cleaning and is currently returning to the dock, but not yet docked.
- `Unavailable`: The entity is currently unavailable.
- `Unknown`: The state is not yet known.

## Actions

Available actions:

- **vacuum.start**: Start or resume a cleaning task.
- **vacuum.pause**: Pause a cleaning task.
- **vacuum.stop**: Stop the current activity of the vacuum.
- **vacuum.return_to_base**: Tell the vacuum to return home.
- **vacuum.locate**: Locate the vacuum cleaner robot.
- **vacuum.clean_spot**: Tell the vacuum cleaner to do a spot clean-up.
- **vacuum.set_fan_speed**: Set the fan speed of the vacuum. The fan speed can be a label, such as balanced or turbo, or be a number; it depends on the vacuum platform.
- **vacuum.send_command**: Send a platform-specific command to the vacuum cleaner.

### Action Details

#### vacuum.start
Start or resume a cleaning task.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |

#### vacuum.pause
Pause a cleaning task.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |

#### vacuum.stop
Stop the current activity of the vacuum.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |

#### vacuum.return_to_base
Tell the vacuum to return home.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |

#### vacuum.locate
Locate the vacuum cleaner robot.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |

#### vacuum.clean_spot
Tell the vacuum cleaner to do a spot clean-up.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |

#### vacuum.set_fan_speed
Set the fan speed of the vacuum.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |
| `fan_speed`    | No       | Platform-dependent vacuum cleaner fan speed, with speed steps, like `medium`, or by percentage, between 0 and 100. |

#### vacuum.send_command
Send a platform-specific command to the vacuum cleaner.

| Data Attribute | Optional | Description |
|----------------|----------|-------------|
| `entity_id`    | Yes      | Only act on specific vacuum. Use `entity_id: all` to target all. |
| `command`      | No       | Command to execute. |
| `params`       | Yes      | Parameters for the command. |
