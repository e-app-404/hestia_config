---
title: "Purifier Card - Air Purifier Control Card"
authors: "@denysdovhan"
source: "https://github.com/denysdovhan/purifier-card"
slug: "purifier-card"
tags: ["home-assistant", "lovelace", "cards", "purifier", "air-quality"]
original_date: "2021-01-01"
last_updated: "2025-10-16"
url: "https://github.com/denysdovhan/purifier-card"
---

# Purifier Card - Air Purifier Control Card

Air Purifier card for Home Assistant Lovelace UI that displays the state and allows control of your air purifier.

## Table of Contents

- [Usage](#usage)
  - [Configuration](#configuration)
  - [Card Options](#card-options)
  - [AQI Object](#aqi-object)
  - [Stats Object](#stats-object)
  - [Shortcuts Object](#shortcuts-object)
- [Examples](#examples)
- [Theming](#theming)
- [Animations](#animations)
- [Supported Models](#supported-models)
- [References](#references)

## Usage

### Configuration

This card can be configured using the Lovelace UI editor or YAML configuration.

For UI configuration:
1. Add a new card to your dashboard
2. Search for "Custom: Purifier Card" in the list
3. Choose your purifier entity
4. Configure the options as needed

### Card Options

| Name               |   Type    | Default      | Description                                      |
| ------------------ | :-------: | ------------ | ------------------------------------------------ |
| `type`             | `string`  | **Required** | `custom:purifier-card`                           |
| `entity`           | `string`  | **Required** | An entity_id within the `fan` domain.            |
| `show_name`        | `boolean` | `true`       | Show friendly name of the purifier.              |
| `show_state`       | `boolean` | `true`       | Show state of the purifier.                      |
| `show_preset_mode` | `boolean` | `true`       | Show preset mode of the purifier in the header.  |
| `show_toolbar`     | `boolean` | `true`       | Show toolbar with shortcuts.                     |
| `compact_view`     | `boolean` | `false`      | Compact view without image.                      |
| `aqi`              | `object`  | Optional     | Custom entity or attribute for AQI value.        |
| `stats`            |  `array`  | Optional     | Custom per state stats for your purifier cleaner |
| `shortcuts`        | `object`  | Optional     | Custom shortcuts for your purifier cleaner.      |

### `aqi` object

| Name        |   Type   | Default  | Description                                         |
| ----------- | :------: | -------- | --------------------------------------------------- |
| `entity_id` | `string` | Optional | An entity_id with state, i.e. `sensor.current_aqi`. |
| `attribute` | `string` | Optional | An attribute which should be used to get AQI value. |
| `unit`      | `string` | Optional | An unit of measurement to display.                  |

You can also combine `attribute` with `entity_id` to extract an attribute value of specific entity.

### `stats` object

You can use any attribute of purifier or even any entity by `entity_id` to display by stats section. Not only that, but you can also combine `attribute` with `entity_id` to extract an attribute value of specific entity:

| Name             |   Type   | Default  | Description                                                                                          |
| ---------------- | :------: | -------- | ---------------------------------------------------------------------------------------------------- |
| `entity_id`      | `string` | Optional | An entity_id with state, i.e. `sensor.purifier_aqi`.                                                 |
| `attribute`      | `string` | Optional | Attribute name of the stat, i.e. `filter_left`.                                                      |
| `value_template` | `string` | Optional | Jinja2 template returning a value. `value` variable represents the `entity_id` or `attribute` state. |
| `unit`           | `string` | Optional | Unit of measure, i.e. `hours`.                                                                       |
| `subtitle`       | `string` | Optional | Friendly name of the stat, i.e. `Filter`.                                                            |

### `shortcuts` object

You can define [custom scripts][ha-scripts] for custom actions or add shortcuts for switching presets and percentages via `shortcuts` option.

| Name           |   Type   | Default  | Description                                                                                     |
| -------------- | :------: | -------- | ----------------------------------------------------------------------------------------------- |
| `name`         | `string` | Optional | Friendly name of the shortcut, i.e. `Switch to Auto`.                                           |
| `icon`         | `string` | Optional | Any icon for shortcut button.                                                                   |
| `service`      | `string` | Optional | A service to call, i.e. `script.clean_air`.                                                     |
| `target`       | `object` | Optional | A `HassServiceTarget`, to define a target for the current service call.                         |
| `service_data` | `object` | Optional | `service_data` for `service` call                                                               |
| `percentage`   | `object` | Optional | A `percentage` to switch to, i.e. `27`, etc. See `entity`'s `percentage_step` for valid values. |
| `preset_mode`  | `object` | Optional | A `speed` to switch to, i.e. `Auto`, etc                                                        |

The card will automatically try to figure out which one of shortcuts is currently active. The shortcut will be highlighted when:

1. It's a service.
2. `entity`'s `percentage` attribute is equal to `shortcut`'s `percentage`.
3. `entity`'s `preset_mode` attribute is equal to `shortcut`'s `preset_mode`.

## Theming

This card can be styled by changing the values of these CSS properties (globally or per-card via [`card-mod`][card-mod]):

| Variable                    | Default value                                                    | Description                          |
| --------------------------- | ---------------------------------------------------------------- | ------------------------------------ |
| `--pc-background`           | `var(--ha-card-background, var(--card-background-color, white))` | Background of the card               |
| `--pc-primary-text-color`   | `var(--primary-text-color)`                                      | Vacuum name, stats values, etc       |
| `--pc-secondary-text-color` | `var(--secondary-text-color)`                                    | Status, stats units and titles, etc  |
| `--pc-icon-color`           | `var(--secondary-text-color)`                                    | Colors of icons                      |
| `--pc-slider-path-color`    | `var(--round-slider-path-color)`                                 | Color of the slider path             |
| `--pc-slider-bar-color`     | `var(--round-slider-bar-color)`                                  | Color of the slider bar              |
| `--pc-toolbar-background`   | `var(--vc-background)`                                           | Background of the toolbar            |
| `--pc-toolbar-text-color`   | `var(--secondary-text-color)`                                    | Color of the toolbar texts           |
| `--pc-toolbar-icon-color`   | `var(--secondary-text-color)`                                    | Color of the toolbar icons           |
| `--pc-divider-color`        | `var(--entities-divider-color, var(--divider-color))`            | Color of dividers                    |
| `--pc-spacing`              | `10px`                                                           | Paddings and margins inside the card |

### Styling via theme

Here is an example of customization via theme. Read more in the [Frontend documentation](https://www.home-assistant.io/integrations/frontend/).

```yaml
my-custom-theme:
  pc-background: '#17A8F4'
  pc-spacing: 5px
```

### Styling via card-mod

You can use [`card-mod`][card-mod] to customize the card on per-card basis, like this:

```yaml
type: 'custom:purifier-card'
style: |
  ha-card {
    --pc-background: #17A8F4;
    --pc-spacing: 5px;
  }
  ...
```

## Animations

The card includes CSS animations to provide visual feedback when the purifier is active.

## Supported Models

This card relies on basic fan services, like `toggle`, `turn_on`, `turn_off`, etc. It should work with any air purifier, however I can physically test it only with my own purifier.

If this card works with your air purifier, please open a PR and your model to the list (in alphabetical order).

- Air Purifier 4 Pro
- Air Purifier 3/3H
- Air Purifier 2/2H/2S
- Air Purifier Pro
- Blueair Classic 480i/680i
- Coway Airmega 300S/400S ([using IoCare custom component](https://github.com/RobertD502/home-assistant-iocare))
- Dyson Pure Cool/Cool Link/Cool Desk/Cool Link Desk ([using Dyson custom integration](https://github.com/libdyson-wg/ha-dyson))
- Dyson Pure Humidify+Cool ([using Dyson custom integration](https://github.com/libdyson-wg/ha-dyson))
- Dyson Purifier Hot+Cool HP2 De-NOx ([using Dyson custom integration](https://github.com/libdyson-wg/ha-dyson))
- Honeywell H-Cat Air Purifier ([using Local Tuya integration](https://github.com/xZetsubou/hass-localtuya))
- Ikea Starkvind
- Levoit Air Purifier (Core 200S) (partially)
- Levoit Air Purifier (Core 400S)
- Philips AirPurifier AC3858/50 (partially)
- Philips AirPurifier AC4221/11 ([using philips-airpurifier-coap cutom component](https://github.com/kongo09/philips-airpurifier-coap))
- SmartMI Air Purifier
- Winix AM90 Wi-Fi Air Purifier
- [_Your purifier?_](https://github.com/denysdovhan/purifier-card/edit/master/README.md)

## References

- [Purifier Card GitHub Repository](https://github.com/denysdovhan/purifier-card)
- [Home Assistant Lovelace Cards Documentation](https://www.home-assistant.io/lovelace/)
- [Home Assistant Fan Integration](https://www.home-assistant.io/integrations/fan/)
- [HACS - Home Assistant Community Store](https://hacs.xyz/)
