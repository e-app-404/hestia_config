---
id: DOCS-ROOMDB-002
title: "Room-DB TTS Migration Guide"
slug: roomdb-tts-migration
status: Accepted
content_type: manual
version: 1.0
date: 2025-10-20
author: "e-app-404"
tags: ["tts", "migration", "roomdb", "ha"]
description: "Guide for migrating existing TTS automations to Room-DB backed implementation"
last_updated: 2025-10-21
---

# MIGRATION GUIDE FOR EXISTING AUTOMATIONS

## Pattern 1: Direct TTS Call → Standardized

```yaml
# ❌ OLD (Direct call, no rate limiting)
- action: tts.speak
  target:
    entity_id: tts.google_translate_en_com
  data:
    cache: true
    media_player_entity_id: media_player.bedroom_google_home_mini_speaker
    message: "Home Assistant successfully rebooted."
    language: en-ca

# ✅ NEW (Standardized, rate-limited, Room-DB backed)
- action: script.tts_announce
  data:
    key: "ha_startup"
    message: "Home Assistant successfully rebooted."
```

## Pattern 2: System Event → Convenience Script

```yaml
# ❌ OLD
- action: tts.speak
  target:
    entity_id: tts.google_translate_en_com
  data:
    cache: true
    media_player_entity_id: media_player.bedroom_google_home_mini_speaker
    message: "{{ some_dynamic_message }}"
    language: en-ca

# ✅ NEW
- action: script.tts_system_event
  data:
    event_type: "startup"  # or "shutdown", "backup", etc.
    message: "{{ some_dynamic_message }}"
```

## Pattern 3: Critical Alert → Bypass Rate Limit

```yaml
# For urgent announcements that must always play
- action: script.tts_critical
  data:
    message: "Critical system alert!"
```
