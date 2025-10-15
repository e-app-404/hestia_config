---
mode: 'agent'
description: 'Diagnose and fix Home Assistant + AppDaemon room_db SQL integration issues'
tools: ['search/codebase', 'file']
---

You are operating in **Investigative + Repair Mode** for a Home Assistant + AppDaemon project that implements a SQL-backed room configuration layer ("room_db") powering adaptive motion lighting and Valetudo vacuum control.

## Objective

1. **Diagnose & fix** end-to-end issues preventing REST writes and downstream behaviors (vacuum not starting, motion configs not updating).
2. **Harden assumptions** (DB path, endpoints, JSON shapes) and align all components to a single authoritative shape.
3. Produce **surgical code diffs** (unified diff format) + a **machine-optimized findings log** for quick review.

## Strict constraints & standards

- No broad refactors; **minimal, testable edits** only.
- Preserve ADR-0008 YAML normalization, keep SQL sensors **SELECT-only** and state short; JSON in **attributes**.
- Ensure JSON stays **single-encoded** end to end.
- Writes must go via **AppDaemon REST** (not shell), unless we explicitly choose the shell fallback.
- **One DB path** everywhere: `/config/room_database.db`.
- **Endpoint** must be stable and documented.

## Files available in this project (open & inspect all where relevant)

Reference these workspace files for investigation:

- [`database_init.sql`](${workspaceFolder}/database_init.sql)
- [`packages/package_room_database.yaml`](${workspaceFolder}/packages/package_room_database.yaml)
- [`packages/vacuum_control_v2/vac_scripts.yaml`](${workspaceFolder}/packages/vacuum_control_v2/vac_scripts.yaml)
- [`packages/vacuum_control_v2/vac_mqtt_commands.yaml`](${workspaceFolder}/packages/vacuum_control_v2/vac_mqtt_commands.yaml)
- [`packages/motion_lighting_v2/motion_light_templates.yaml`](${workspaceFolder}/packages/motion_lighting_v2/motion_light_templates.yaml)
- [`packages/motion_lighting_v2/motion_light_automations.yaml`](${workspaceFolder}/packages/motion_lighting_v2/motion_light_automations.yaml)
- [`packages/motion_lighting_v2/adaptive_light_sleep_scheduler_automations.yaml`](${workspaceFolder}/packages/motion_lighting_v2/adaptive_light_sleep_scheduler_automations.yaml)
- AppDaemon config: `appdaemon.yaml`, `apps.yaml`
- AppDaemon app: `room_db_updater.py`
- Database: `room_database.db` (treat as present/expected)

## Known symptoms to verify

- Service call `rest_command.room_db_update_config` previously failed with:
  > extra keys not allowed @ data['sequence'][0]...
  > (Likely user passed an **automation action** instead of a **service payload**; still confirm rest_command definition & payload shape.)
- REST **404** on empty POST (expected), but 404 with payload indicates **route mismatch** or AppDaemon not registering endpoint as expected.
- Vacuum "spot-test" (`script.clean_room_with_sql_tracking`) does not start cleaning; probably **no room config** read or **topic mismatch**.
- Earlier DB alignment check (HA Dev Tools Template vs AppDaemon view) implied **two DBs** or **path mismatch**; must confirm both sides truly use `/config/room_database.db`.
- Motion templates needed double-encoding guards in past; SQL should now emit **real JSON** (use `json(config_data)` in queries).

## Target shapes (conformance contract)

### REST command (in `package_room_database.yaml`)

- Endpoint (primary): `http://a0d7b954-appdaemon:5050/api/appdaemon/room_db/update_config`
- Health: `http://a0d7b954-appdaemon:5050/api/appdaemon/room_db/health`
- Payload JSON:
  ```json
  {
    "room_id": "<slug>",
    "domain": "motion_lighting|vacuum_control|shared",
    "config_data": { ... },      // native object, rest_command does |tojson
    "schema_expected": 1
  }
  ```

### SQL sensors (same file)

* `db_url: sqlite:////config/room_database.db`
* Use `json(config_data)` or `CASE WHEN json_valid(...) THEN json(...)`.
* State short: `"ok"` or numeric count; JSON only in `payload` attribute.

### AppDaemon (`room_db_updater.py`)

* Registers **GET** `/api/appdaemon/room_db/health`
* Registers **POST** `/api/appdaemon/room_db/update_config`
* Validations:
  * `room_id: ^[a-z0-9_]+$` and **exists** in canonical mapping if provided
  * `domain` allowlist: motion_lighting, vacuum_control, shared
  * `schema_version == 1` guard
  * transaction: `BEGIN IMMEDIATE ... COMMIT`
  * rate limit ≥ 2s per domain
  * payload ≤ 4096 bytes
* Writes to `/config/room_database.db`.

### Automations (`motion_light_automations.yaml`)

* **Use REST**, not shell:
  ```yaml
  - service: rest_command.room_db_update_config
    data:
      room_id: "<room>"
      domain: "motion_lighting"
      config_data: >-
        {{ dict(room_config, **{
          'last_triggered': now().isoformat(),
          'trigger_count': (room_config.get('trigger_count', 0) | int) + 1
        }) }}
  ```
* **DO NOT** `| tojson` here (rest_command handles JSON).
* Presence logic:
  * Prefer per-room `binary_sensor.<room>_occupancy_beta` if exists else fallback to `person.evert == home`.
  * `effective_timeout = timeout * presence_multiplier` when occupancy is on; else `timeout`.

## Investigation checklist (perform in order)

1. **REST endpoints**
   * Open `room_db_updater.py`: verify routes paths (health + update_config) match **exactly** `/api/appdaemon/room_db/...`.
   * If different, fix code OR change `package_room_database.yaml` URLs to match. Prefer fixing code to canonical path above.

2. **DB path alignment**
   * Open `apps.yaml` and `appdaemon.yaml`: confirm the app config points to **/config/room_database.db**.
   * Open `room_db_updater.py`: confirm the sqlite path is **/config/room_database.db**.
   * Open `package_room_database.yaml`: confirm all SQL `db_url` use **sqlite:////config/room_database.db**.
   * If any discrepancy, normalize all to the path above.

3. **SQL sensors JSON encoding**
   * In `package_room_database.yaml` ensure `json(config_data)` (or guarded `CASE WHEN json_valid`) is used so HA gets **clean JSON** in `payload`.

4. **Automations write path**
   * In `motion_light_automations.yaml`, replace **any** `shell_command.update_room_config` with `rest_command.room_db_update_config`.
   * Remove `| tojson` from `config_data` in automations.

5. **Presence logic**
   * In each room's automation, add:
     ```yaml
     occupancy_entity: "binary_sensor.<room>_occupancy_beta"
     occupancy_on: >-
       {% set e = occupancy_entity %}
       {% if e and states(e) in ['on','off','unknown','unavailable'] %}
         {{ is_state(e, 'on') }}
       {% else %}
         {{ is_state('person.evert','home') }}
       {% endif %}
     presence_multiplier: "{{ room_config.get('presence_timeout_multiplier', 1.0) | float }}"
     effective_timeout: "{{ (timeout * presence_multiplier) | int if occupancy_on else timeout }}"
     ```
   * Ensure `delay` uses `effective_timeout`.

6. **Vacuum**
   * Verify `vac_scripts.yaml` uses base topic from `vac_mqtt_commands.yaml` (`input_text.valetudo_base_topic`).
   * Confirm each vacuum-eligible room has a `segment_id` in DB; if missing, script will publish empty/invalid segment.

7. **Health surfaces**
   * If defined, confirm `rest_command.room_db_health` returns 200 OK.
   * Confirm SQL sensors states are `ok` and their `attributes.payload` evaluate to **mapping**, not a quoted string.

## Expected deliverables

Make the fixes and produce:

1. **Unified diffs** for every file you change.

2. A **machine-optimized findings log** (one JSON object per line) with fields:
   * `code` (stable ID), `severity` (INFO/WARN/ERROR), `file`, `line` (if applicable), `message`, `suggested_fix` (short), `fixed` (true/false).
   * Example line:
     ```json
     {"code":"REST_ENDPOINT_MISMATCH","severity":"ERROR","file":"room_db_updater.py","line":72,"message":"Endpoint mounted at /api/app/room_db/update_config but HA expects /api/appdaemon/room_db/update_config","suggested_fix":"Change route base to /api/appdaemon/room_db","fixed":true}
     ```

3. A **post-fix smoke plan** (5 steps) that uses Home Assistant Developer Tools:
   * Call `rest_command.room_db_update_config` with:
     ```yaml
     room_id: bedroom
     domain: motion_lighting
     config_data: {timeout: 240, bypass: false, illuminance_threshold: 10, presence_timeout_multiplier: 3.0}
     ```
   * Verify `sensor.room_configs_motion_lighting` → `attributes.payload.bedroom.timeout == 240`.
   * Run `script.clean_room_with_sql_tracking` with `room: "kitchen"`.
   * Confirm MQTT publish payload contains the configured `segment_id`.
   * Trigger a motion event and confirm write-back increments `trigger_count`.

Work systematically through the investigation checklist, show the diffs, then the findings log, then the smoke plan.