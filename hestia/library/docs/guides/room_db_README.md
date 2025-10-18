# Room-DB System — Operator Guide

This guide documents the Room-DB system backed by the AppDaemon app `room_db_updater` and the Home Assistant configuration in this repo. It covers endpoint usage, diagnostics, and examples for modifying motion lighting and vacuum control configs per room.

- AppDaemon add-on host: `http://a0d7b954-appdaemon:5050`
- Canonical, working endpoints (global):
  - GET `/api/appdaemon/room_db_health`
  - GET `/api/appdaemon/room_db_test`
  - POST `/api/appdaemon/room_db_update_config`
- Data sources:
  - SQLite DB: `/config/room_database.db`
  - Area mapping (canonical rooms): `/config/www/area_mapping.yaml`

## Quick diagnostic snapshot

Paste the following Jinja templates into Home Assistant → Developer Tools → Template.

1) Compact setup diagnostic (file: `hestia/library/templates/devtools/adaptive-motion-lighting/room_db_setup_diag.jinja2`)
- Shows endpoint health, SQL dict readiness, and counts.

2) Endpoint/matrix diagnostic (file: `hestia/library/templates/devtools/adaptive-motion-lighting/room_db_diag.jinja2`)
- Shows presence and states for app-scoped vs appdaemon vs compat sensors.

### Example diagnostic JSON shape

```
{
  "endpoints": {
    "health": {
      "entity": "sensor.appdaemon_health_appdaemon_global",
      "message": "",
      "present": "False",
      "state": "missing",
      "status": ""
    },
    "test": {
      "entity": "sensor.appdaemon_test_appdaemon_global",
      "message": "",
      "present": "False",
      "state": "missing",
      "status": ""
    }
  },
  "recommendations": [
    "If endpoints.health.state != healthy, check AppDaemon logs and endpoint URLs.",
    "If endpoints.test.state != test_success, confirm handler registration and path.",
    "If any *_dict sensor is missing/unavailable, check SQL sensors and recorder exclusions.",
    "Ensure /config/www/area_mapping.yaml exists and covers all canonical rooms.",
    "Consider pruning 404 probe sensors once global endpoints are stable."
  ],
  "sql_payloads": {
    "motion_lighting": {
      "dict_state": "missing",
      "entity": "sensor.room_configs_motion_lighting_dict",
      "missing_rooms": [],
      "present": "False",
      "rooms_count": 0
    },
    "rooms_needing_cleaning": {
      "count": 0,
      "entity": "sensor.rooms_needing_cleaning",
      "present": "False",
      "state": "missing"
    },
    "vacuum_control": {
      "dict_state": "missing",
      "entity": "sensor.room_configs_vacuum_control_dict",
      "missing_rooms": [],
      "present": "False",
      "rooms_count": 0
    }
  },
  "timestamp": "2025-10-18T10:13:00.281956+01:00"
}
```

## Home Assistant entities (read)

- Health: `sensor.appdaemon_health_appdaemon_global`
- Test: `sensor.appdaemon_test_appdaemon_global`
- Motion Lighting dict: `sensor.room_configs_motion_lighting_dict`
- Vacuum Control dict: `sensor.room_configs_vacuum_control_dict`
- Rooms needing cleaning: `sensor.rooms_needing_cleaning`

Note: Legacy/app-scoped probe sensors may show `404: Not Found`. Treat the global sensors as canonical.

## REST commands (write)

These are defined in `packages/room_database/room_db_src.yaml` and use the global endpoints. Examples below can be run via Developer Tools → Services, selecting `rest_command.<name>` and passing `data`.

- `rest_command.room_db_health` (GET): convenience read via REST (uses HA rest_command)
- `rest_command.room_db_test` (GET): test route
- `rest_command.room_db_update_config` (POST): write/update room config

### Example: health (GET)

Example response from `rest_command.room_db_health`:

```
content:
  status: healthy
  db_path: /config/room_database.db
  canonical_rooms_count: 21
  allowed_domains:
    - vacuum_control
    - shared
    - motion_lighting
  app_init_error: null
status: 200
headers:
  Content-Type: application/json; charset=utf-8
  Content-Length: "181"
  Date: Sat, 18 Oct 2025 09:16:13 GMT
  Server: Python/3.12 aiohttp/3.11.18
```

### Example: test (GET)

Expected JSON (shape may include additional fields):

```
{
  "status": "test_success",
  "message": "Test endpoint is working",
  "app_name": "room_db_updater"
}
```

### Example: update_config (POST)

Contract:
- Inputs:
  - room_id: string (lowercase a–z, 0–9, underscore)
  - domain: one of ["motion_lighting", "vacuum_control", "shared"]
  - config_data: JSON object (<=4KB), domain-specific keys
  - schema_expected: integer (default 1)
- Success: HTTP 200, body may include confirmation
- Errors: 400/422 with message (e.g., SCHEMA_VERSION_MISMATCH, DOMAIN_NOT_ALLOWED, BAD_ROOM_ID, CONFIG_TOO_LARGE, WRITE_RATE_LIMIT)

Example payloads you can send via `rest_command.room_db_update_config`:

1) Motion lighting — set timeout and brightness
```
{
  "room_id": "kitchen",
  "domain": "motion_lighting",
  "config_data": {"timeout": 120, "brightness": 180},
  "schema_expected": 1
}
```

2) Vacuum control — mark needs cleaning
```
{
  "room_id": "kitchen",
  "domain": "vacuum_control",
  "config_data": {"needs_cleaning": 1},
  "schema_expected": 1
}
```

3) Shared — set a common flag used by both domains
```
{
  "room_id": "kitchen",
  "domain": "shared",
  "config_data": {"quiet_hours": {"start": "22:00", "end": "07:00"}},
  "schema_expected": 1
}
```

## Troubleshooting checklist

- Endpoints show 404 on legacy sensors but globals are healthy
  - Use the global entities as the source of truth.
- Update/write fails immediately in succession
  - The app enforces write rate-limits (~2s per domain/room). Wait and retry.
- BAD_ROOM_ID or DOMAIN_NOT_ALLOWED
  - Ensure `room_id` exists in `/config/www/area_mapping.yaml` and `domain` is allowed.
- SQL dict sensors show missing/unavailable
  - Check Home Assistant logs for SQL integration errors and confirm the DB exists at `/config/room_database.db`.
- AppDaemon issues
  - Restart the add-on and check logs. Successful startup shows endpoint registrations and 200s for health/test.

## Developer notes

- Endpoints are instance-global (`/api/appdaemon/<endpoint>`). Avoid generic names (health, test, update_config) to prevent handler collisions. Use the unique `room_db_*` endpoints defined above.
- App-scoped/compat endpoints are present in code for compatibility but may be disabled by the add-on routing.
- Recorder policy excludes the dict sensors by default to prevent DB bloat.

## Quick commands (optional)

Curl from HA terminal (or from any host that can resolve the add-on hostname):

```
# Health
curl -s http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_health | jq .

# Test
curl -s http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_test | jq .

# Update config (example)
curl -s -X POST \
  -H 'Content-Type: application/json' \
  -d '{"room_id":"kitchen","domain":"motion_lighting","config_data":{"timeout":120},"schema_expected":1}' \
  http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_update_config | jq .
```
