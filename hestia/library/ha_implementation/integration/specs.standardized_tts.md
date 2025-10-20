---
id: SPECS-TTS-001
title: "TTS Implementation Specification (Room-DB Backed)"
version: "1.0.0"
created: "2025-10-20"
backend: "SQLite via Room-DB (shared domain)"
adr_compliance: "ADR-0001"
storage_capacity: "512KB per registry"
rate_limit_enforcement: "AppDaemon (room_db_updater)"
schema_version: 1
---

# TTS Implementation Specification

## 1. STORAGE ARCHITECTURE

### 1.1 Database Schema
```
table: room_configs
  - room_id: "tts_gate_registry" (TEXT, PK part 1)
  - config_domain: "shared" (TEXT, PK part 2)
  - config_data: JSON string (TEXT, ≤512KB)
  - updated_at: ISO timestamp (TEXT)
  - version: Integer (auto-increment)
```

### 1.2 Registry Structure
```json
{
  "format_version": 1,
  "keys": {
    "": {
      "last_ts": 1729440000.123,
      "count": 2,
      "message": "Last message (optional)",
      "created_at": "2025-10-20T12:00:00+00:00"
    }
  }
}
```

### 1.3 Read Path
```
SQL Sensor (raw JSON string)
  ↓
Template Wrapper (parse to dict)
  ↓
Script Variable (native dict access)
```

### 1.4 Write Path
```
Script Logic (dict manipulation)
  ↓
REST Command (room_db_update_config)
  ↓
AppDaemon Validation (rate limit, schema check)
  ↓
SQLite Transaction (BEGIN IMMEDIATE ... COMMIT)
```

---

## 2. SCRIPT INTERFACES

### 2.1 Core Script: tts_gate_native

**Purpose**: Low-level TTS with Room-DB rate limiting  
**Mode**: parallel (max: 10)  
**Backend**: Room-DB shared domain

#### Parameters
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `key` | string | ✅ | - | Unique deduplication key |
| `message` | string | ✅ | - | TTS message text |
| `media_player` | entity_id | ✅ | - | Target media player |
| `tts_entity` | entity_id | ✅ | - | TTS service entity |
| `volume` | float | ❌ | 0.5 | Volume level (0-1) |
| `language` | string | ❌ | "en" | TTS language code |
| `cooldown_sec` | int | ❌ | 1800 | Cooldown window (seconds) |
| `max_repeats` | int | ❌ | 1 | Allowed repeats within cooldown |

#### Logic Flow
```yaml
1. Read registry from sensor.room_configs_shared_registry_dict
2. Extract entry for key (or default to empty)
3. Calculate:
   - window_ok = (now_ts - last_ts) >= cooldown_sec
   - allow = window_ok OR (count < max_repeats)
4. If allow:
   - Set volume
   - Execute tts.speak
   - Update registry: count = (window_ok ? 1 : count+1), last_ts = now()
   - Write to Room-DB
5. Else:
   - Log "TTS gate blocked"
```

### 2.2 Wrapper Script: tts_announce

**Purpose**: Simplified interface with sensible defaults  
**Mode**: parallel (max: 10)

#### Parameters
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | ✅ | - | TTS message |
| `key` | string | ❌ | auto-generated | Dedup key (MD5 hash if omitted) |
| `media_player` | entity_id | ❌ | from helper | Target player |
| `volume` | float | ❌ | from helper | Volume level |
| `cooldown_sec` | int | ❌ | from helper | Cooldown duration |
| `bypass_gate` | boolean | ❌ | false | Skip rate limiting |

#### Default Sources
```yaml
input_text.default_tts_entity: "tts.google_translate_en_com"
input_text.default_tts_language: "en-ca"
input_text.default_media_player: "media_player.bedroom_google_home_mini_speaker"
input_number.default_tts_volume: 0.5
input_number.default_tts_cooldown: 1800
```

### 2.3 Convenience Scripts

#### tts_system_event
```yaml
Purpose: System events (startup, shutdown, backup)
Cooldown: 300s (5 minutes)
Key Pattern: "system_{event_type}"
```

#### tts_critical
```yaml
Purpose: Urgent alerts (bypasses rate limit)
Cooldown: none (bypass_gate=true)
Volume: 0.7 (louder)
Key Pattern: "critical_{timestamp}"
```

#### tts_maintenance
```yaml
Purpose: Maintenance notifications
Cooldown: 3600s (1 hour)
Key Pattern: "maintenance_{task}"
```

---

## 3. CONFIGURATION TEMPLATES

### 3.1 Service Call: tts_announce
```yaml
action: script.tts_announce
data:
  message: "{{ dynamic_message }}"
  key: "unique_identifier"           # optional
  media_player: "media_player.xyz"   # optional
  volume: 0.6                        # optional
  cooldown_sec: 900                  # optional
  bypass_gate: false                 # optional
```

### 3.2 Service Call: tts_system_event
```yaml
action: script.tts_system_event
data:
  event_type: "startup"
  message: "System started successfully"
```

### 3.3 Service Call: tts_critical
```yaml
action: script.tts_critical
data:
  message: "Critical alert!"
  media_player: "media_player.all_speakers"  # optional
```

### 3.4 Service Call: tts_gate_native (Advanced)
```yaml
action: script.tts_gate_native
data:
  key: "custom_key"
  message: "Custom message"
  media_player: "media_player.speaker"
  tts_entity: "tts.google_translate_en_com"
  volume: 0.5
  language: "en-ca"
  cooldown_sec: 1800
  max_repeats: 2
```

---

## 4. MIGRATION PATTERNS

### 4.1 Direct TTS → Standardized
```yaml
# Before
- action: tts.speak
  target: { entity_id: tts.google_translate_en_com }
  data:
    cache: true
    media_player_entity_id: media_player.speaker
    message: "Test message"
    language: en-ca

# After
- action: script.tts_announce
  data:
    key: "test_key"
    message: "Test message"
```

### 4.2 Volume Control Migration
```yaml
# Before
- action: media_player.volume_set
  target: { entity_id: media_player.speaker }
  data: { volume_level: 0.5 }
- action: tts.speak
  [...]

# After
- action: script.tts_announce
  data:
    message: "..."
    volume: 0.5  # Handled internally
```

### 4.3 Language Override
```yaml
# Use tts_gate_native for non-default languages
- action: script.tts_gate_native
  data:
    key: "french_announcement"
    message: "Bonjour"
    media_player: "media_player.speaker"
    tts_entity: "tts.google_translate_en_com"
    language: "fr"
    cooldown_sec: 300
    max_repeats: 0
```

---

## 5. RATE LIMIT BEHAVIOR

### 5.1 State Machine
```
State: FIRST_CALL
  → Play TTS
  → Set: last_ts=now(), count=1
  → Transition: COOLDOWN

State: COOLDOWN (within cooldown window)
  → If count < max_repeats:
      → Play TTS
      → Increment: count++
      → Stay: COOLDOWN
  → Else:
      → Block TTS
      → Stay: COOLDOWN

State: COOLDOWN_EXPIRED (elapsed >= cooldown_sec)
  → Play TTS
  → Reset: last_ts=now(), count=1
  → Transition: COOLDOWN
```

### 5.2 Examples

#### Example 1: max_repeats=1, cooldown=300s
```
T+0s:   Call 1 → PLAY (count=1)
T+10s:  Call 2 → PLAY (count=2, within repeats)
T+20s:  Call 3 → BLOCK (count=2, limit reached)
T+310s: Call 4 → PLAY (cooldown expired, reset count=1)
```

#### Example 2: max_repeats=0, cooldown=600s
```
T+0s:   Call 1 → PLAY (count=1)
T+10s:  Call 2 → BLOCK (no repeats allowed)
T+610s: Call 3 → PLAY (cooldown expired)
```

---

## 6. ERROR HANDLING

### 6.1 Common Issues
| Error | Cause | Resolution |
|-------|-------|------------|
| `'str object' has no attribute 'get'` | Reading SQL sensor instead of wrapper | Use `sensor.room_configs_shared_registry_dict` |
| `WRITE_RATE_LIMIT` | AppDaemon rate limit | Wait 2+ seconds between writes |
| `SCHEMA_VERSION_MISMATCH` | Wrong schema_expected | Set `schema_expected: 1` |
| `CONFIG_TOO_LARGE` | Registry > 512KB | Prune old keys or increase limit |

### 6.2 Diagnostic Queries
```jinja
{# Check wrapper sensor status #}
{{ states('sensor.room_configs_shared_registry_dict') }}
{{ state_attr('sensor.room_configs_shared_registry_dict', 'payload') is mapping }}

{# Check TTS gate registry keys #}
{{ state_attr('sensor.tts_gate_registry_status', 'keys') }}

{# Check specific key state #}
{% set payload = state_attr('sensor.room_configs_shared_registry_dict', 'payload') %}
{% if payload and 'tts_gate_registry' in payload %}
  {{ payload['tts_gate_registry'].get('your_key') }}
{% endif %}
```

---

## 7. PERFORMANCE CHARACTERISTICS

### 7.1 Latency
```
TTS Call → Room-DB Read:      ~10ms (SQL query)
Registry Update → Room-DB:     ~50-100ms (REST + SQLite write)
Total TTS Delay:               ~60-110ms (negligible)
```

### 7.2 Capacity
```
Max Registry Size:        512 KB
Avg Key Entry Size:       ~100 bytes
Estimated Max Keys:       ~5,000 keys
Recommended Max Keys:     ~1,000 keys (for performance)
```

### 7.3 Maintenance
```
Cleanup Frequency:   Monthly (or as needed)
Prune Strategy:      Remove keys with last_ts > 90 days
Backup Before Prune: Always
```

---

## 8. TESTING CHECKLIST

### 8.1 Basic Functionality
- [ ] Call `script.tts_announce` with message → Plays once
- [ ] Repeat same key within cooldown → Blocks after max_repeats
- [ ] Wait for cooldown expiry → Plays again
- [ ] Check registry via `sensor.tts_gate_registry_status` → Shows keys

### 8.2 Bypass Logic
- [ ] Call `script.tts_critical` → Always plays (no blocking)
- [ ] Use `bypass_gate: true` → Ignores rate limit

### 8.3 Default Overrides
- [ ] Change `input_number.default_tts_volume` → Affects next call
- [ ] Override `volume` in call → Uses provided value

### 8.4 Error Cases
- [ ] Invalid media_player → Logs error, doesn't crash
- [ ] Registry > 512KB → AppDaemon rejects write
- [ ] Concurrent calls (10+) → Queues properly

---

## 9. OPERATIONAL COMMANDS

### 9.1 View Registry State
```yaml
# Developer Tools → Template
{% set payload = state_attr('sensor.room_configs_shared_registry_dict', 'payload') %}
{{ payload.get('tts_gate_registry', {}) | tojson(indent=2) }}
```

### 9.2 Manual Prune Old Keys
```yaml
# Developer Tools → Actions
service: rest_command.room_db_update_config
data:
  room_id: "tts_gate_registry"
  domain: "shared"
  config_data:
    format_version: 1
    keys: {}  # Reset to empty
  schema_expected: 1
```

### 9.3 Check Specific Key
```yaml
# Developer Tools → Template
{% set payload = state_attr('sensor.room_configs_shared_registry_dict', 'payload') %}
{% set reg = payload.get('tts_gate_registry', {}) if payload else {} %}
{{ reg.get('your_key_here', 'NOT_FOUND') }}
```

---

## 10. SCHEMA REFERENCE

### 10.1 REST Command Payload
```json
{
  "room_id": "tts_gate_registry",
  "domain": "shared",
  "config_data": {
    "format_version": 1,
    "keys": {
      "example_key": {
        "last_ts": 1729440000.123,
        "count": 1
      }
    }
  },
  "schema_expected": 1
}
```

### 10.2 Registry Entry
```json
{
  "last_ts": 1729440000.123,
  "count": 2,
  "message": "Optional last message",
  "created_at": "2025-10-20T12:00:00+00:00"
}
```

### 10.3 Sensor Attributes
```yaml
sensor.tts_gate_registry_status:
  state: 5  # Number of keys
  attributes:
    keys: ["key1", "key2", "key3", ...]
    format_version: 1
```

---

## 11. BEST PRACTICES

### 11.1 Key Naming
```yaml
✅ GOOD:
  - "ha_startup"
  - "system_backup_complete"
  - "maintenance_tmp_prune"
  - "alert_temperature_high"

❌ BAD:
  - "test"  # Too generic
  - "message_1234567890"  # Meaningless
  - user-generated strings  # Risk of collision
```

### 11.2 Cooldown Selection
```yaml
System events:      300s (5 minutes)
Maintenance:        3600s (1 hour)
Alerts:             900s (15 minutes)
Critical:           0s (bypass)
```

### 11.3 Volume Levels
```yaml
Normal:     0.5
Alerts:     0.6-0.7
Critical:   0.7-0.8
Quiet:      0.3-0.4
```

---

**END OF SPECIFICATION**
