# Room-DB Project Instructions (Pin This)

**Project:** Room-DB Centralized Configuration System  
**Version:** 3.1  
**Last Updated:** 2025-10-18  
**Status:** Production Active  

---

## 🎯 Project Mission

Centralize room configuration management for Home Assistant using a **SQLite-backed AppDaemon system** that powers:
1. **Activity Tracking** - Monitor occupancy/motion patterns
2. **Motion Lighting** - Dynamic timeout and presence-aware automation
3. **Vacuum Control** - Intelligent cleaning schedules with activity-based triggers

**Core Principle:** Single source of truth for all room state, eliminating 63% of legacy helper entities while enabling cross-domain intelligence.

---

## 🏗️ System Architecture

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend** | AppDaemon | 4.5.11 | Python apps for real-time event processing |
| **Database** | SQLite3 | WAL mode | Room configuration persistence |
| **Integration** | Home Assistant | 2025.10.1 | REST commands, SQL sensors, automations |
| **Protocol** | REST API | HTTP/JSON | Write operations (AppDaemon endpoints) |
| **Schema** | YAML | - | Canonical room definitions (area_mapping.yaml) |

### Data Flow Architecture

```
Occupancy Sensor (on)
  ↓
AppDaemon ActivityTracker
  ↓
REST: room_db_update_config
  ↓
SQLite: room_configs table
  ↓
SQL Sensor: SELECT json_group_object()
  ↓
Template: dict wrapper (from_json)
  ↓
Motion Automation: read timeout/presence_multiplier
  ↓
Vacuum Intelligence: activity_threshold_hours
```

---

## 📁 Critical File Locations

### AppDaemon Apps (Active)
```
/config/hestia/workspace/patches/appdaemon/
├── apps.yaml                       # App registration & configuration
├── room_db_updater.py             # Core REST API & validation
├── activity_tracker.py            # Occupancy monitoring (8 rooms)
├── valetudo_default_activity.py   # Vacuum job orchestration
└── area_mapping.yaml              # ⭐ CANONICAL room definitions (workspace copy)
```

**Note:** `/config/appdaemon/` is **DEPRECATED** - see `/config/appdaemon/DEPRECATED.md`

### Canonical Area Mapping
```
/config/www/
├── area_mapping.yaml                        # ⭐ PRIMARY canonical definitions
├── area_mapping.yaml.20251018_162250.bak   # Timestamped backup
├── area_mapping.yaml.20251018_185856.bak   # Timestamped backup
└── area_mapping.yaml.bak-20251018          # Daily backup
```

**Source of Truth:** `/config/www/area_mapping.yaml` is read by `room_db_updater.py`

### Database Files
```
/config/
├── room_database.db           # Main SQLite database (20 KB)
├── room_database.db-shm       # Shared memory file (32 KB, auto-managed)
├── room_database.db-wal       # Write-ahead log (0 bytes, auto-managed)
├── room_database_copy.db      # Manual backup
└── database_init.sql          # Schema initialization script
```

### Home Assistant Packages
```
/config/packages/
├── room_database/
│   ├── room_db_src.yaml                  # SQL sensors, REST commands, shell fallbacks
│   ├── room_db_diag.yaml                 # Diagnostic REST sensors for endpoint testing
│   └── activity_tracker_templates.yaml   # Activity decay sensors (minutes since activity)
│
├── motion_lighting_v2/
│   ├── motion_light_automations.yaml           # Motion-triggered room automations
│   ├── motion_light_templates.yaml             # Timeout/bypass sensors per room
│   ├── motion_light_simple_automations.yaml    # Simplified blueprint-based automations
│   └── adaptive_light_sleep_scheduler_automations.yaml  # Sleep mode schedules
│
└── vacuum_control_v2/
    └── valetudo_default.yaml            # Vacuum scripts & automations
```

---

## 🗄️ Database Schema

### Table: `room_configs`
```sql
CREATE TABLE room_configs (
    room_id        TEXT NOT NULL,      -- Canonical room ID (bedroom, kitchen, etc.)
    config_domain  TEXT NOT NULL,      -- Domain: activity_tracking, motion_lighting, vacuum_control, shared
    config_data    TEXT NOT NULL,      -- JSON blob (single-encoded)
    updated_at     TIMESTAMP,          -- Auto-updated on write
    PRIMARY KEY (room_id, config_domain)
);
```

### Table: `schema_version`
```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY        -- Current: 1
);
```

### Domain Schemas

#### `activity_tracking`
```json
{
  "last_activity": "2025-10-18T14:35:15+00:00",
  "activity_source": "binary_sensor.bedroom_occupancy_beta",
  "trigger_count": 42
}
```

#### `motion_lighting`
```json
{
  "timeout": 120,
  "bypass": false,
  "illuminance_threshold": 10,
  "presence_timeout_multiplier": 3.0,
  "last_triggered": "2025-10-18T14:30:00+00:00",
  "trigger_count": 15
}
```

#### `vacuum_control`
```json
{
  "segment_id": 17,
  "needs_cleaning": 1,
  "last_cleaned": "2025-10-17T09:00:00+00:00",
  "cleaning_frequency_days": 3,
  "activity_threshold_hours": 12
}
```

---

## 🔧 REST API Endpoints

### Primary (Global AppDaemon Routes)
```
POST http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_update_config
GET  http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_health
GET  http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_test
```

### Alternate (App-Scoped Routes)
```
POST http://a0d7b954-appdaemon:5050/api/app/room_db_updater/update_config
GET  http://a0d7b954-appdaemon:5050/api/app/room_db_updater/health
GET  http://a0d7b954-appdaemon:5050/api/app/room_db_updater/index
```

### Write Request Schema
```yaml
# Home Assistant: Developer Tools → Actions
service: rest_command.room_db_update_config
data:
  room_id: "bedroom"                    # Must exist in area_mapping.yaml
  domain: "activity_tracking"           # Must be in allowed_domains
  config_data:                          # Native dict (REST layer applies |tojson)
    last_activity: "{{ now().isoformat() }}"
    activity_source: "binary_sensor.bedroom_occupancy_beta"
    trigger_count: 1
  schema_expected: 1                    # Schema version guard
```

---

## 📊 SQL Sensor Pattern (ADR-0008 Compliant)

### Core Pattern
```yaml
# File: /config/packages/room_database/room_db_src.yaml

sql:
  - name: "Room Configs — Activity Tracking"
    db_url: sqlite:////config/room_database.db
    query: >
      SELECT 'ok' AS state,
             json_group_object(
               room_id,
               CASE WHEN json_valid(config_data) = 1
                    THEN json(config_data)
                    ELSE NULL
               END
             ) AS payload
      FROM room_configs
      WHERE config_domain = 'activity_tracking';
    column: state
```

**Key Requirements:**
- ✅ State is SHORT (e.g., "ok", count)
- ✅ JSON in `payload` attribute only
- ✅ Use `json()` function to emit clean JSON (not double-encoded strings)
- ✅ Exclude from recorder to prevent bloat

### Dict Wrapper Template
```yaml
# File: /config/packages/room_database/activity_tracker_templates.yaml

template:
  - sensor:
      - name: "Room Configs Activity Tracking Dict"
        state: "ok"
        attributes:
          payload: >-
            {% set raw = state_attr('sensor.room_configs_activity_tracking', 'payload') %}
            {% if raw is string %}
              {{ raw | from_json }}
            {% else %}
              {{ raw }}
            {% endif %}
```

**Purpose:** Ensures payload is always a dict, never a quoted string (handles both states gracefully).

---

## 🏠 Canonical Room Definitions

### Source of Truth: `/config/www/area_mapping.yaml`

**11 Canonical Room IDs:**
```
bedroom, ensuite, kitchen, living_room, downstairs, upstairs, 
entrance, powder_room, desk, wardrobe, laundry_room
```

### Room ID → Sensor Mapping (ActivityTracker)
```python
# File: /config/hestia/workspace/patches/appdaemon/activity_tracker.py

self.room_sensors = {
    "bedroom": "binary_sensor.bedroom_occupancy_beta",
    "kitchen": "binary_sensor.kitchen_occupancy_beta",
    "living_room": "binary_sensor.living_room_occupancy_beta",
    "ensuite": "binary_sensor.ensuite_occupancy_beta",
    "downstairs": "binary_sensor.hallway_downstairs_occupancy_beta",  # Canonical shorter
    "upstairs": "binary_sensor.hallway_upstairs_occupancy_beta",      # Canonical shorter
    "entrance": "binary_sensor.entrance_motion_beta",                 # Motion proxy
    "desk": "binary_sensor.desk_occupancy_beta",
}
```

**Critical Rule:** Canonical room IDs in `area_mapping.yaml` may be shorter than sensor entity IDs. The mapping bridges this gap.

---

## 🔒 Validation & Safety Guardrails

### Room ID Validation
```python
# File: /config/hestia/workspace/patches/appdaemon/room_db_updater.py

# 1. Regex validation
ROOM_ID_RE = re.compile(r"^[a-z0-9_]+$")

# 2. Canonical mapping check
canonical_mapping_file = "/config/www/area_mapping.yaml"  # Primary source
# Fallback paths checked in order:
# - /config/www/area_mapping.yaml
# - /config/domain/architecture/area_mapping.yaml

# 3. Loaded from YAML at runtime (cached in _canonical_rooms)
```

### Domain Validation
```python
# File: /config/hestia/workspace/patches/appdaemon/apps.yaml

allowed_domains: ["motion_lighting", "vacuum_control", "shared", "activity_tracking"]
```

### Rate Limiting
- **Per-domain throttle:** 2-5 seconds (configurable via `write_rate_limit_seconds`)
- **Tracked via:** `_last_write[(room, domain)] = timestamp`
- **Error message format:** `"WRITE_RATE_LIMIT (room=bedroom, domain=motion_lighting, rate=2s, since_last=1.2s)"`

### Size Limits
- **Max payload:** 4096 bytes (JSON string length after encoding)
- **Enforced before:** Database write

### Schema Version Guard
- **Current version:** 1
- **Checked on:** Every write operation
- **Error if mismatch:** Prevents writes with incompatible schema

---

## 🎨 Design Patterns & Best Practices

### 1. Single-Encoded JSON (Critical)
```yaml
# ✅ CORRECT (Home Assistant YAML)
config_data:
  timeout: 120
  bypass: false

# ❌ WRONG (Don't manually encode)
config_data: '{"timeout": 120, "bypass": false}'
```

**Rule:** Pass native dicts/objects. The REST command layer applies `| tojson`.

### 2. Occupancy Over Motion
**Preference Order:**
1. `binary_sensor.<room>_occupancy_beta` (aggregate, stable)
2. `binary_sensor.<room>_motion_beta` (transient, noisy)
3. Door contacts as motion proxies (entrance)

### 3. Presence Enhancement (Asymmetric)
```yaml
# File: /config/packages/motion_lighting_v2/motion_light_automations.yaml

# Presence NEVER blocks activation (untracked housemate exists)
# Presence ONLY enhances timeout/brightness

effective_timeout: >
  {% set base = room_config.get('timeout', 120) | int %}
  {% set multiplier = room_config.get('presence_timeout_multiplier', 1.0) | float %}
  {% set occupancy_on = is_state('binary_sensor.bedroom_occupancy_beta', 'on') %}
  {{ (base * multiplier) | int if occupancy_on else base }}
```

### 4. Error Context Enrichment
```python
# All errors include: room_id, domain, rate window, since_last
msg = f"WRITE_RATE_LIMIT (room={room_id}, domain={domain}, rate={rate}s, since_last={since:.1f}s)"
```

### 5. Notification Deduplication
```python
# File: /config/hestia/workspace/patches/appdaemon/room_db_updater.py

notification_id = f"roomdb_err__{domain}__{room_id}"
# Result: Multiple errors for same room/domain roll up to one notification
```

---

## 🚀 Deployment Workflow

### 1. AppDaemon Code Changes
```bash
# Edit AppDaemon apps
vim /config/hestia/workspace/patches/appdaemon/activity_tracker.py

# Restart AppDaemon add-on
ha addons restart a0d7b954_appdaemon

# Verify logs
ha addons logs a0d7b954_appdaemon | grep "ActivityTracker initialized"
# Expected: ActivityTracker initialized - monitoring 8 rooms
```

### 2. Home Assistant Package Changes
```bash
# Edit packages
vim /config/packages/room_database/room_db_src.yaml

# Reload YAML (no restart needed)
# Developer Tools → YAML → Reload All YAML Configuration

# Verify sensors exist
# Developer Tools → States → sensor.room_configs_activity_tracking
```

### 3. Area Mapping Changes
```bash
# Edit canonical mapping
vim /config/www/area_mapping.yaml

# Restart AppDaemon (reloads mapping cache)
ha addons restart a0d7b954_appdaemon

# Verify room count
ha addons logs a0d7b954_appdaemon | grep "canonical rooms"
# Expected: Loaded 11 canonical rooms from /config/www/area_mapping.yaml
```

### 4. Database Schema Changes
```bash
# Stop AppDaemon (releases database lock)
ha addons stop a0d7b954_appdaemon

# Apply schema changes
sqlite3 /config/room_database.db < /config/database_init.sql

# Restart AppDaemon
ha addons start a0d7b954_appdaemon
```

---

## 🧪 Testing & Validation

### Health Check
```yaml
# Developer Tools → Actions
service: rest_command.room_db_health
data: {}

# Expected Response
{
  "status": "healthy",
  "db_path": "/config/room_database.db",
  "canonical_rooms_count": 11,
  "allowed_domains": ["motion_lighting", "vacuum_control", "shared", "activity_tracking"]
}
```

### Write Test
```yaml
service: rest_command.room_db_update_config
data:
  room_id: bedroom
  domain: activity_tracking
  config_data:
    last_activity: "{{ now().isoformat() }}"
    activity_source: "test"
    trigger_count: 0
  schema_expected: 1

# Check logs
# Expected: Successfully updated config for room 'bedroom', domain 'activity_tracking'
```

### Read Test
```jinja
{# Developer Tools → Template #}
{% set activity = state_attr('sensor.room_configs_activity_tracking_dict', 'payload') %}
{{ activity.bedroom }}

{# Expected Output #}
{
  "last_activity": "2025-10-18T14:35:15+00:00",
  "activity_source": "test",
  "trigger_count": 0
}
```

### Activity Trigger Test
```yaml
# Developer Tools → States
# Entity: binary_sensor.bedroom_occupancy_beta
# Set state to: on
# Wait 3 seconds

# Check logs
ha addons logs a0d7b954_appdaemon | grep "Activity logged.*bedroom"
# Expected: Activity logged: bedroom from binary_sensor.bedroom_occupancy_beta (count: 1)
```

---

## 🐛 Common Issues & Solutions

### Issue: "not enough values to unpack"
**Cause:** Trying to unpack `call_service()` return value  
**Fix:** Don't assign/unpack; AppDaemon's `call_service()` returns `None`

```python
# ❌ WRONG
result = self.call_service(...)

# ✅ CORRECT
self.call_service(...)
```

### Issue: "room_id not in canonical mapping"
**Cause:** Room doesn't exist in `/config/www/area_mapping.yaml` or stale cache  
**Fix:** 
1. Add room to `area_mapping.yaml` nodes
2. Restart AppDaemon: `ha addons restart a0d7b954_appdaemon`
3. Verify: `ha addons logs a0d7b954_appdaemon | grep "Loaded.*canonical rooms"`

### Issue: Double-encoded JSON strings
**Cause:** Applying `| tojson` in automation AND REST command  
**Fix:** Remove `| tojson` from automation; REST command handles it

```yaml
# ❌ WRONG
config_data: >-
  {{ {'timeout': 120} | tojson }}

# ✅ CORRECT
config_data:
  timeout: 120
```

### Issue: SQL sensor shows quoted string not dict
**Cause:** Missing `json()` function in SQL query  
**Fix:** Use `json(config_data)` not raw `config_data`

```sql
-- ❌ WRONG (in /config/packages/room_database/room_db_src.yaml)
SELECT config_data AS payload

-- ✅ CORRECT  
SELECT CASE WHEN json_valid(config_data) = 1
            THEN json(config_data)
            ELSE NULL
       END AS payload
```

### Issue: Rate limit errors flooding logs
**Cause:** Multiple rapid writes to same domain  
**Fix:** Increase `write_rate_limit_seconds` in `/config/hestia/workspace/patches/appdaemon/apps.yaml` OR add delays between writes

```yaml
# File: /config/hestia/workspace/patches/appdaemon/apps.yaml
room_db_updater:
  write_rate_limit_seconds: 5  # Increase from 2 to 5
```

### Issue: "Dashboards Disabled" or Dashboard warnings
**Cause:** HADashboard feature checking for dashboard files  
**Status:** This is cosmetic and can be ignored OR disable dashboards in `/config/appdaemon/appdaemon.yaml`

```yaml
# File: /config/appdaemon/appdaemon.yaml
# Comment out or remove:
# hadashboard:
```

---

## 📈 Performance Characteristics

### Write Latency
- **REST call:** ~50-100ms
- **SQLite write:** ~5-10ms (WAL mode)
- **SQL sensor update:** ~30s polling interval
- **Template propagation:** Immediate (state change)

### Database Size
- **Per room/domain:** ~150-300 bytes
- **11 rooms × 3 domains:** ~1-10 KB total
- **Current size:** 20 KB (includes metadata)
- **Negligible impact** on system performance

### AppDaemon Memory
- **Base:** ~40 MB
- **Per app:** ~2-5 MB
- **Total (4 apps):** ~50-60 MB

---

## 🎯 Behavioral Guidelines for AI Assistance

### When Proposing Changes

1. **Always show unified diffs** (`---`/`+++` format)
2. **Preserve existing patterns** unless explicitly broken
3. **Use correct file paths** from the structure above
4. **Provide rollback instructions** for risky changes
5. **Reference exact file locations** (no ambiguity)

### File Path References

```bash
# ✅ CORRECT - Use full paths
vim /config/hestia/workspace/patches/appdaemon/room_db_updater.py
vim /config/packages/room_database/room_db_src.yaml
vim /config/www/area_mapping.yaml

# ❌ WRONG - Avoid deprecated paths
vim /config/appdaemon/apps/room_db_updater.py  # DEPRECATED
```

### Code Style Preferences

```python
# ✅ Explicit error context
self.error(f"Failed for {room}: {e}")

# ✅ Guard clauses early
if not room_id:
    raise ValueError("room_id required")

# ✅ Dict.get() with defaults
timeout = config.get('timeout', 120)

# ✅ Type hints where useful
def _validate_room(self, room_id: str) -> None:
```

### Documentation Standards

- **Inline comments:** Why, not what (code shows what)
- **Docstrings:** Public methods only
- **YAML comments:** Purpose of non-obvious config
- **Commit messages:** `fix: rate limit error context` not `updates`

### Anti-Patterns to Avoid

❌ Over-engineering (KISS principle)  
❌ Premature optimization  
❌ Breaking changes without migration path  
❌ Adding dependencies without justification  
❌ Duplicating functionality that exists elsewhere  
❌ Using deprecated `/config/appdaemon/` paths  

---

## 🔮 Future Enhancements (Backlog)

### Phase 1: Intelligence Layer
- [ ] **Stale room detection** - Query rooms with `last_activity > threshold`
- [ ] **Vacuum prioritization** - Sort by activity age + needs_cleaning flag
- [ ] **Presence correlation** - Desk activity → bedroom presence boost

### Phase 2: Observability
- [ ] **Grafana dashboard** - Activity heatmaps, trigger counts, vacuum stats
- [ ] **Trend analysis** - "Kitchen activity increased 30% this week"
- [ ] **Anomaly detection** - "No bedroom activity for 8 hours (unusual)"

### Phase 3: Advanced Features
- [ ] **Multi-domain reads** - `GET /api/appdaemon/room_db_query?room=bedroom&domains=activity_tracking,motion_lighting`
- [ ] **Bulk writes** - Atomic update of multiple rooms
- [ ] **Historical snapshots** - Time-series table for activity trends
- [ ] **Web UI** - React dashboard for room config management

---

## 📚 Reference Documentation

### Related ADRs
- **ADR-0008:** SQL Sensor Normalization (JSON in attributes only)
- **ADR-0020:** AppDaemon Endpoint Routes (global vs app-scoped)
- **ADR-0021:** Presence Policy (asymmetric enhancement, never blocking)

### External Resources
- [AppDaemon Docs](https://appdaemon.readthedocs.io/)
- [SQLite JSON Functions](https://www.sqlite.org/json1.html)
- [HA SQL Integration](https://www.home-assistant.io/integrations/sql/)
- [Valetudo API](https://valetudo.cloud/pages/integrations/home-assistant-integration.html)

### Key Commits
- `2025-10-18`: Initial room_db_updater implementation
- `2025-10-18`: Activity tracker app deployment
- `2025-10-18`: area_mapping.yaml v3.1 with hierarchy
- `2025-10-18`: Migration from `/config/appdaemon/` to `/config/hestia/workspace/patches/appdaemon/`

---

## 🆘 Emergency Procedures

### System Down / Database Corruption
```bash
# 1. Stop AppDaemon
ha addons stop a0d7b954_appdaemon

# 2. Backup database
cp /config/room_database.db /config/room_database_backup_$(date +%Y%m%d_%H%M%S).db

# 3. Restore from backup if needed
cp /config/room_database_copy.db /config/room_database.db

# 4. Reinitialize schema (will preserve existing data)
sqlite3 /config/room_database.db < /config/database_init.sql

# 5. Restart AppDaemon
ha addons start a0d7b954_appdaemon
```

### Rollback to Shell Commands (Fallback)
```yaml
# File: /config/packages/room_database/room_db_src.yaml
# Shell commands are already defined as emergency fallback

service: shell_command.update_room_config
data:
  room_id: bedroom
  domain: motion_lighting
  config_data: '{"timeout": 120}'
  schema_expected: 1
```

### Restore Deprecated AppDaemon Location
```bash
# If needed to temporarily restore old location:
cp /config/hestia/workspace/patches/appdaemon/room_db_updater.py \
   /config/appdaemon/apps/room_db_updater.py

cp /config/hestia/workspace/patches/appdaemon/apps.yaml \
   /config/appdaemon/apps/apps.yaml

# Then restart AppDaemon
ha addons restart a0d7b954_appdaemon
```

---

## ✅ Success Criteria

System is **fully operational** when:

- [x] AppDaemon logs show all 4 apps initialized
- [x] `room_db_health` returns `status: healthy`
- [x] SQL sensors exist with `payload` attributes (dicts not strings)
- [x] Activity tracker writes on occupancy trigger
- [x] Motion automations read from Room-DB
- [x] Vacuum app can queue rooms from `needs_cleaning=1`
- [x] No rate limit errors under normal operation
- [x] Database size < 100 KB
- [x] All files in correct locations (not deprecated paths)

---

## 🎓 Onboarding Checklist (New Contributors)

- [ ] Read this entire document
- [ ] Understand data flow diagram
- [ ] Review file structure and correct paths
- [ ] Inspect `/config/www/area_mapping.yaml` structure
- [ ] Review one app (`activity_tracker.py`) in detail
- [ ] Run health check successfully
- [ ] Execute a test write operation
- [ ] Trigger activity tracking via sensor
- [ ] Review AppDaemon logs for patterns
- [ ] Understand ADR-0008 compliance requirements
- [ ] Verify no use of deprecated `/config/appdaemon/` paths

---

**Last Validated:** 2025-10-18  
**Maintainer:** Evert  
**Project Chat:** [Link to this Claude project]  
**Critical Paths:** Use `/config/hestia/workspace/patches/appdaemon/` (NOT `/config/appdaemon/`)

---

*Pin this document and refer to it before making any changes to Room-DB components.*
