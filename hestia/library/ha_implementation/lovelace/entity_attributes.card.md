---
title: "Entity Attributes Card - Display Entity Attribute Values"
authors: "Home Assistant Community"
source: "HACS Integration"
slug: "entity-attributes-card"
tags: ["home-assistant", "lovelace", "cards", "entity-attributes", "attributes"]
original_date: "2020-01-01"
last_updated: "2025-10-16"
url: "https://github.com/custom-cards/entity-attributes-card"
---

# Entity Attributes Card - Display Entity Attribute Values

Entity attributes card allows you to show basic attributes from multiple entities in a table format with customizable filtering and display options.

## Table of Contents

- [Configuration](#configuration)
  - [Card Options](#card-options)
  - [Filter Options](#filter-options)
- [Examples](#examples)
  - [Basic Configuration](#basic-configuration)
  - [Embedded in Entities Card](#embedded-in-entities-card)
- [References](#references)

## Configuration

### Card Options

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `type` | string | **Required** | `custom:entity-attributes-card` |
| `title` | string | optional | A title for the card |
| `heading_name` | string | `'Attributes'` | Heading of the attribute column |
| `heading_state` | string | `'States'` | Heading of the states column |
| `filter` | object | **Required** | A filter object that can contain `include` and `exclude` sections |

### Filter Options

The `include` and `exclude` sections can be simple lists (format `[domain].[entity].[attribute]`) or objects of the type below. `[attribute]` can also be a pattern.

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `key` | string | **Required** | A pattern for the attribute. Example: `media_player.bedroom.media_title` |
| `name` | string | optional | A string to replace the actual attribute name with |
| `unit` | string | optional | A string to append an arbitrary unit to the value |

## Examples

### Basic Configuration

```yaml
- type: custom:entity-attributes-card
  title: Attributes Card
  heading_name: List
  heading_state: States
  filter:
    include:
      - key: climate.hvac.*
      - key: media_player.bedroom.app_name
        name: Application
      - key: media_player.bedroom.media_title
        name: Media center
      - climate.heatpump.current_temperature
      - vacuum.xiaomi_mi_robot.battery_level
        unit: %
```

### Embedded in Entities Card

How to embed this card inside an `entities` card:

![Embedded Example](https://user-images.githubusercontent.com/7738048/42446481-1ac27c1e-837f-11e8-94e7-02ef35f2d853.png)

```yaml
- type: entities
  title: Entities card
  entities:
    - media_player.bedroom
    - type: custom:entity-attributes-card
      entity: media_player.bedroom
      filter:
        include:
          - media_player.bedroom.app_name
          - media_player.bedroom.media_title
    - sensor.short_name
    - sensor.battery_sensor
```

## References

- [Entity Attributes Card GitHub Repository](https://github.com/custom-cards/entity-attributes-card)
- [Home Assistant Lovelace Cards Documentation](https://www.home-assistant.io/lovelace/)
- [HACS - Home Assistant Community Store](https://hacs.xyz/)
- [Home Assistant Entity State and Attributes](https://www.home-assistant.io/docs/configuration/state_object/)
