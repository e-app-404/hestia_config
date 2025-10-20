# Hybrid Strategy Implementation Guide
## TTS & Plex Migration to Room-DB Storage

---

## Overview

**Objective**: Migrate TTS gate registry and Plex media indexes from `input_text` helpers (4KB limit) to Room-DB SQLite storage (512KB per entry).

**Strategy**: Hybrid approach using existing `shared` domain with increased size limit.

**Timeline**: 45-60 minutes for full deployment + validation.

---

## Pre-Migration Checklist

- [ ] **Backup current state**
  ```bash
  # Backup existing helper values
  ha-cli state list | grep -E "(input_text.tts_gate|input_text.plex)" > /config/backup_helpers_state.txt
  
  # Backup database
  cp /config/room_database.db /config/room_database.db.backup
  ```

- [ ] **Verify AppDaemon is running**
  ```bash
  ha addons info a0d7b954_appdaemon
  # Check status: started
  ```

- [ ] **Check current REST endpoint health**
  ```bash
  curl -X GET "http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_health"
  # Expected: {"status": "healthy", ...}
  ```

---

## Implementation Steps

### Phase 1: Infrastructure Update (15 min)

#### 1.1 Update AppDaemon Configuration

**File**: `/config/appdaemon/apps/apps.yaml`

**Action**: Change line 10 from `max_config_size_bytes: 4096` to `max_config_size_bytes: 524288`

**Verification**:
```bash
grep max_config_size_bytes /config/appdaemon/apps/apps.yaml
# Expected output: max_config_size_bytes: 524288
```

**Restart AppDaemon**:
```bash
ha addons restart a0d7b954_appdaemon
# Wait 30 seconds for initialization
```

#### 1.2 Add Shared Media Registry Sensors

**File**: Create `/config/packages/shared_media_registry.yaml`

**Action**: Copy content from artifact `shared_media_registry.yaml`

**Verification**:
```bash
ls -lh /config/packages/shared_media_registry.yaml
# Expected: File exists, ~5KB size
```

#### 1.3 Add Recorder Exclusions

**File**: Append to `/config/recorder.yaml` (or create if not exists)

**Action**: Copy content from artifact `recorder_exclusions_media.yaml`

**Note**: If you have existing `recorder:` config, merge the `exclude:` sections.

**Verification**:
```bash
grep -A 20 "exclude:" /config/recorder.yaml | grep "sensor.room_configs_shared_registry"
# Expected: Match found
```

**Reload Configuration**:
- Navigate to **Developer Tools → YAML → Reload All YAML Configuration**
- Or: `ha core restart` (if recorder changes require restart)

---

### Phase 2: TTS Gate Migration (10 min)

#### 2.1 Replace TTS Gate Package

**File**: Replace `/config/packages/package_tts_gate_native.yaml`

**Action**: Copy content from artifact `package_tts_gate_native.yaml (Room-DB)`

**Verification**:
```bash
grep "sensor.room_configs_shared_registry" /config/packages/package_tts_gate_native.yaml
# Expected: Multiple matches (script reads from SQL sensor)
```

**Reload Scripts**:
- **Developer Tools → YAML → Reload Scripts**

#### 2.2 Seed TTS Registry (Optional)

If you have existing TTS keys in `input_text.tts_gate_registry`, migrate them:

```yaml
# Developer Tools → Services
service: rest_command.room_db_update_config
data:
  room_id: "tts_gate_registry"
  domain: "shared"
  config_data:
    ha_startup:
      last_ts: 1729368000
      count: 1
    fridge_left_open:
      last_ts: 1729368100
      count: 0
  schema_expected: 1
```

---

### Phase 3: Plex Migration (15 min)

#### 3.1 Replace Plex Template Package

**File**: Replace `/config/packages/package_plex.yaml`

**Action**: Copy content from artifact `package_plex.yaml (Room-DB)`

**Verification**:
```bash
grep "sensor.room_configs_shared_registry" /config/packages/package_plex.yaml
# Expected: Multiple matches
```

#### 3.2 Add Plex Upsert Scripts

**File**: Create `/config/packages/plex_roomdb_scripts.yaml`

**Action**: Copy content from artifact `plex_roomdb_scripts.yaml`

**Verification**:
```bash
ls -lh /config/packages/plex_roomdb_scripts.yaml
# Expected: File exists, ~6KB size
```

**Reload Configuration**:
- **Developer Tools → YAML → Reload All YAML Configuration**

#### 3.3 Seed Plex Indexes (Initial Data)

**Option A**: Run example refresh script
```yaml
# Developer Tools → Services
service: script.plex_refresh_all_indexes
```

**Option B**: Manual upsert with real Plex data
```yaml
service: script.plex_tv_index_upsert
data:
  payload:
    shows:
      "Breaking Bad": {"seasons": 5, "total_episodes": 62}
    seasons:
      "Breaking Bad": [1, 2, 3, 4, 5]
    episodes:
      - show: "Breaking Bad"
        season: 1
        episode: 1
        title: "Pilot"
        added_at: "2024-01-15T10:00:00Z"
    updated: "2024-10-20T12:00:00Z"
```

---

### Phase 4: Validation (15 min)

#### 4.1 Verify SQL Sensor Operation

**Developer Tools → States**
```
Entity: sensor.room_configs_shared_registry
Expected State: "ok"
Expected Attributes:
  payload:
    tts_gate_registry: {...}  # If seeded
    plex_tv_index: {...}      # If seeded
    plex_movie_index: {...}   # If seeded
```

#### 4.2 Test TTS Gate Script

```yaml
# Developer Tools → Services
service: script.tts_gate_native
data:
  key: "test_migration"
  message: "TTS gate migration successful"
  media_player: media_player.your_speaker
  tts_entity: tts.google_translate
  language: en
  cooldown_sec: 300
  max_repeats: 1
```

**Expected Outcomes**:
1. TTS announcement plays
2. `sensor.tts_gate_registry_status` state increments
3. `sensor.tts_gate_registry_status` attributes.keys includes `test_migration`

**Verify in Database**:
```sql
SELECT * FROM room_configs 
WHERE config_domain = 'shared' 
  AND room_id = 'tts_gate_registry';
```

#### 4.3 Test Plex Template Sensors

**Developer Tools → States**
```
Entity: sensor.plex_tv_index_count
Expected: Numeric state (episode count)

Entity: sensor.plex_movie_index_count
Expected: Numeric state (movie count)

Entity: sensor.plex_tv_index_compat
Attributes should include: shows, seasons, episodes, updated
```

#### 4.4 Test Cooldown Logic

**Immediate Retry** (should be blocked):
```yaml
service: script.tts_gate_native
data:
  key: "test_migration"  # Same key as 4.2
  message: "This should not play"
  media_player: media_player.your_speaker
  tts_entity: tts.google_translate
  cooldown_sec: 300
  max_repeats: 0
```

**Expected**: No TTS plays, system log shows "TTS gate blocked"

---

## Post-Migration Tasks

### Cleanup Old Helpers (After 30-Day Soak)

Once confident in Room-DB storage:

1. **Remove old input_text helpers** (UI or YAML):
   - `input_text.tts_gate_registry`
   - `input_text.plex_tv_index`
   - `input_text.plex_movie_index`

2. **Remove old input_number helpers** (if any):
   - `input_number.plex_tv_episode_count`
   - `input_number.plex_movie_count`

3. **Archive old Variable-based packages**:
   ```bash
   mkdir -p /config/archive/variable_migration
   mv /config/packages/package_tts_gate.yaml /config/archive/variable_migration/
   # (If you had old Variable-based Plex package)
   ```

---

## Troubleshooting

### Issue: SQL Sensor Shows "unavailable"

**Diagnosis**:
```sql
-- Check if shared registry entries exist
SELECT room_id, length(config_data) as size 
FROM room_configs 
WHERE config_domain = 'shared';
```

**Resolution**: Seed initial data using scripts (Phase 3.3)

---

### Issue: "extra keys not allowed @ data['sequence']"

**Cause**: Passing automation action structure instead of service data

**Fix**: Ensure REST command calls use correct payload:
```yaml
# CORRECT
service: rest_command.room_db_update_config
data:
  room_id: "..."
  domain: "shared"
  config_data: {...}
  schema_expected: 1

# WRONG (automation syntax)
service: rest_command.room_db_update_config
data:
  - service: ...  # Don't nest service calls
```

---

### Issue: "413 Payload Too Large"

**Diagnosis**: Payload exceeds 512KB

**Check payload size**:
```yaml
# Template Tool
{{ state_attr('sensor.room_configs_shared_registry', 'payload')['plex_tv_index'] | tojson | length }}
```

**Resolution**: If truly >512KB, implement chunking strategy (contact for guidance)

---

### Issue: Rate Limit Errors (429)

**Symptom**: `{"status":"retry","error":"WRITE_RATE_LIMIT"}`

**Resolution**: Wait 2+ seconds between writes, or increase `write_rate_limit_seconds` in `apps.yaml`

---

## Rollback Procedure

If issues arise during migration:

1. **Restore AppDaemon config**:
   ```bash
   # Change back to: max_config_size_bytes: 4096
   vi /config/appdaemon/apps/apps.yaml
   ha addons restart a0d7b954_appdaemon
   ```

2. **Restore original package files**:
   ```bash
   cp /config/backup/package_tts_gate_native.yaml.bak /config/packages/package_tts_gate_native.yaml
   cp /config/backup/package_plex.yaml.bak /config/packages/package_plex.yaml
   ```

3. **Remove new files**:
   ```bash
   rm /config/packages/shared_media_registry.yaml
   rm /config/packages/plex_roomdb_scripts.yaml
   ```

4. **Reload HA configuration**:
   - **Developer Tools → YAML → Reload All YAML Configuration**

---

## Success Criteria

- [x] AppDaemon restarts without errors
- [x] SQL sensor `sensor.room_configs_shared_registry` shows state "ok"
- [x] TTS gate script writes successfully to Room-DB
- [x] TTS cooldown logic functions correctly
- [x] Plex template sensors show correct counts
- [x] Plex upsert scripts execute without errors
- [x] Recorder excludes new sensors (check `homeassistant.log` for no large JSON writes)
- [x] Database size remains reasonable (<50MB for typical home setup)

---

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| TTS storage capacity | 4KB (80 keys) | 512KB (~5000 keys) |
| Plex TV index capacity | 4KB (fragmented) | 512KB (~5000 episodes) |
| Plex movie capacity | 4KB (fragmented) | 512KB (~3000 movies) |
| Write reliability | Helper race conditions | ACID transactions |
| Template complexity | High (selectattr chains) | Low (direct dict access) |
| Infrastructure count | 3 systems | 1 unified (Room-DB) |

---

## Support & References

- **Room-DB ADR**: See project ADR-0008, ADR-0027
- **TTS ADR**: See ADR-0001 for TTS action template compliance
- **Migration Guide**: See `MIGRATION_TTS_GATE.md` for original context

---

_Implementation guide version: 1.0_  
_Last updated: 2025-10-20_
