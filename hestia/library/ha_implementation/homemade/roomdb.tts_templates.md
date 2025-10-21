---
id: DOCS-ROOMDB-003
title: "TTS Implementation Templates (Room-DB Backed)"
slug: roomdb-tts-templates
content_type: templates
version: 1.0
date: 2025-10-20
author: "e-app-404"
description: "Templates for TTS implementation using Room-DB"
tags: ["tts", "roomdb", "ha", "templates"]
last_updated: 2025-10-21
---

# Standardized TTS Configuration Templates (Room-DB Backed)

## Default TTS Configuration & Helpers

The following YAML snippets are already included in `configuration.yaml` but can be adapted 
and split as needed.

### Helpers: Default Settings

<!-- TODO: descriptive information. Move inline comments to this section -->

```yaml
input_text:
  default_tts_entity:
    name: "Default TTS Entity"
    initial: "tts.google_translate_en_com"
    max: 255

  default_tts_language:
    name: "Default TTS Language"
    initial: "en-ca"
    max: 10

  default_media_player:
    name: "Default Media Player"
    initial: "media_player.bedroom_google_home_mini_speaker"
    max: 255

input_number:
  default_tts_volume:
    name: "Default TTS Volume"
    min: 0
    max: 1
    step: 0.05
    initial: 0.5
    mode: slider

  default_tts_cooldown:
    name: "Default TTS Cooldown (seconds)"
    min: 0
    max: 86400
    step: 60
    initial: 1800
    mode: slider
```

### Wrapper Script: TTS Announce (Simplified Interface)

<!-- TODO: descriptive information. Move inline comments to this section -->

```yaml
script:
  tts_announce:
    alias: "TTS Announce (Standardized)"
    description: "Simplified TTS interface using Room-DB gate with sensible defaults"
    mode: parallel
    max: 10
    fields:
      message:
        name: Message
        description: "What to announce"
        required: true
        selector: { text: { multiline: true } }
      key:
        name: Deduplication Key
        description: "Unique key for rate limiting (auto-generated if omitted)"
        required: false
        selector: { text: { multiline: false } }
      media_player:
        name: Media Player
        description: "Override default media player"
        required: false
        selector: { entity: { domain: media_player } }
      volume:
        name: Volume
        description: "Override default volume (0-1)"
        required: false
        selector: { number: { min: 0, max: 1, step: 0.05 } }
      cooldown_sec:
        name: Cooldown
        description: "Override default cooldown (seconds)"
        required: false
        selector: { number: { min: 0, max: 86400, step: 60 } }
      bypass_gate:
        name: Bypass Rate Limit
        description: "Force announcement (ignore cooldown)"
        default: false
        selector: { boolean: {} }
    sequence:
      - variables:
          # Use defaults from input helpers if not provided
          final_key: >-
            {{ key if key is defined and key else
               ('auto_' + (message | hash('md5'))[:8]) }}
          final_player: >-
            {{ media_player if media_player is defined and media_player else
               states('input_text.default_media_player') }}
          final_volume: >-
            {{ volume if volume is defined and volume is not none else
               states('input_number.default_tts_volume') | float }}
          final_cooldown: >-
            {{ cooldown_sec if cooldown_sec is defined and cooldown_sec is not none else
               states('input_number.default_tts_cooldown') | int }}
          final_tts: "{{ states('input_text.default_tts_entity') }}"
          final_language: "{{ states('input_text.default_tts_language') }}"

      - choose:
          # Option 1: Bypass gate (force announcement)
          - conditions: "{{ bypass_gate | bool }}"
            sequence:
              - action: media_player.volume_set
                target:
                  entity_id: "{{ final_player }}"
                data:
                  volume_level: "{{ final_volume }}"

              - action: tts.speak
                target:
                  entity_id: "{{ final_tts }}"
                data:
                  cache: true
                  media_player_entity_id: "{{ final_player }}"
                  message: "{{ message }}"
                  language: "{{ final_language }}"

        # Option 2: Use Room-DB gate (default)
        default:
          - action: script.tts_gate_native
            data:
              key: "{{ final_key }}"
              message: "{{ message }}"
              media_player: "{{ final_player }}"
              tts_entity: "{{ final_tts }}"
              volume: "{{ final_volume }}"
              language: "{{ final_language }}"
              cooldown_sec: "{{ final_cooldown }}"
              max_repeats: 1
```

### Convenience Scripts: Common Announcement Types

<!-- TODO: descriptive information. Move inline comments to this section -->

```yaml
script:
  tts_system_event:
    alias: "TTS: System Event"
    description: "Announce system events (startup, shutdown, etc)"
    mode: parallel
    max: 5
    fields:
      event_type:
        name: Event Type
        required: true
        selector: { text: {} }
      message:
        name: Message
        required: true
        selector: { text: { multiline: true } }
    sequence:
      - action: script.tts_announce
        data:
          key: "system_{{ event_type }}"
          message: "{{ message }}"
          cooldown_sec: 300
          bypass_gate: false

  tts_critical:
    alias: "TTS: Critical Alert"
    description: "Critical announcements (bypasses rate limit)"
    mode: parallel
    max: 10
    fields:
      message:
        name: Message
        required: true
        selector: { text: { multiline: true } }
      media_player:
        name: Media Player
        required: false
        selector: { entity: { domain: media_player } }
    sequence:
      - action: script.tts_announce
        data:
          key: "critical_{{ now().timestamp() | int }}"
          message: "{{ message }}"
          media_player: "{{ media_player if media_player is defined else none }}"
          volume: 0.7
          bypass_gate: true

  tts_maintenance:
    alias: "TTS: Maintenance Notification"
    description: "Maintenance-related announcements"
    mode: parallel
    max: 5
    fields:
      task:
        name: Task Name
        required: true
        selector: { text: {} }
      message:
        name: Message
        required: true
        selector: { text: { multiline: true } }
    sequence:
      - action: script.tts_announce
        data:
          key: "maintenance_{{ task }}"
          message: "{{ message }}"
          cooldown_sec: 3600
          bypass_gate: false
```

### Migration Examples: Convert Existing TTS Calls

<!-- TODO: descriptive information. Move inline comments to this section -->

```yaml
automation:
  # Example 1: Home Assistant Startup (Migrated)
  - alias: "Home Assistant Start - TTS Announce (Standardized)"
    id: ha_start_tts_standardized
    mode: single
    triggers:
      - trigger: homeassistant
        event: start
    actions:
      - action: script.tts_system_event
        data:
          event_type: "startup"
          message: "Home Assistant successfully rebooted."

  # Example 2: Shutdown Announcement (Migrated)
  - alias: "Home Assistant Shutdown - TTS Announce (Standardized)"
    id: ha_shutdown_tts_standardized
    mode: single
    triggers:
      - trigger: homeassistant
        event: shutdown
    actions:
      - action: script.tts_system_event
        data:
          event_type: "shutdown"
          message: "Home Assistant will shut down at {{ now().strftime('%Y-%m-%d %H:%M:%S') }}"

  # Example 3: Maintenance Task (Migrated)
  - alias: "Hestia On Shutdown - TTS Announce (Standardized)"
    id: hestia_shutdown_prune_tts_standardized
    mode: single
    triggers:
      - trigger: homeassistant
        event: shutdown
    actions:
      - action: script.tts_maintenance
        data:
          task: "tmp_prune"
          message: "Home Assistant will perform scheduled cleanup of temporary files during shutdown."

  # Example 4: Critical Alert Example
  - alias: "Critical System Alert - TTS Example"
    id: critical_alert_tts_example
    mode: single
    triggers:
      - trigger: numeric_state
        entity_id: sensor.system_cpu_temperature
        above: 85
    actions:
      - action: script.tts_critical
        data:
          message: "Warning! System temperature has exceeded 85 degrees Celsius."
```
