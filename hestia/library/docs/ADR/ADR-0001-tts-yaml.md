---
id: ADR-0001
title: Templated TTS YAML Snippet
slug: templated-tts-yaml-snippet
status: Accepted
related: []
supersedes: []
last_updated: "2025-10-15"
date: 2025-09-11
decision: "Standardize TTS YAML actions using templated structure with media_player_entity_id, message, and language parameters for consistent automated assistant usage."
author: "e-app-404"
tags:
  - architecture
  - tts
  - yaml
  - template
  - adr
  - text-to-speech
  - media_player
  - automation
  - jinja
---

# ADR-0001: Templated TTS YAML Snippet

## Table of Contents

1. Context
2. Template
3. Permutations
4. Usage Guidance
5. Last updated

## 1. Context

This ADR provides a machine-friendly, implementation-agnostic template for Home Assistant text-to-speech (TTS) YAML actions. The template is designed for use by automated assistants and tools, supporting all required permutations for runtime population and activation.

## 2. Template

```yaml
- action: tts.speak
  data:
    cache: true
    media_player_entity_id: "{{ media_player_entity_id }}"
    message: "{{ message }}"
    language: "{{ language }}"
  # Optionally, add delay after TTS
- delay:
    minutes: "{{ delay_minutes | default(0) }}"
```

## 3. Permutations

- `media_player_entity_id`: Entity ID of the target media player (e.g., `media_player.bedroom_google_home_mini_speaker`).
- `message`: TTS message string, may include Jinja2 templates (e.g., `{{ friendly_name }} was left open at {{ now().strftime('%H:%M:%S') }}`).
- `language`: Language code (e.g., `en`, `en-ca`, `fr`).
- `cache`: Boolean, defaults to `true`.
- `delay_minutes`: Optional integer for post-TTS delay.

## 4. Usage Guidance

- Populate all template fields at runtime with contextually relevant values.
- The template supports any media player, message, and language.
- Delay is optional and can be omitted if not needed.
- Use Jinja2 templating for dynamic message content.

---

_Last updated: 2025-09-11_

<!-- TOKEN_BLOCK
title: ADR-0001
purpose: tts-template
-->
