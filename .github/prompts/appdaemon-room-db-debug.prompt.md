---
description: 'Diagnose and fix AppDaemon Room-DB API 404s; discover actual routes, update HA configs, validate end-to-end.'
mode: "agent"
model: "GPT-5"
tools: ['edit', 'search', 'runCommands', 'runTasks', 'GitKraken/*', 'pylance mcp server/*', 'usages', 'problems', 'changes', 'githubRepo', 'ms-python.python/getPythonEnvironmentInfo', 'ms-python.python/getPythonExecutableCommand', 'ms-python.python/installPythonPackage', 'ms-python.python/configurePythonEnvironment', 'extensions', 'todos']
---

# Debug AppDaemon Room-DB endpoints (404) fast

## Primary Directive
Resolve the 404 responses for the Room-DB AppDaemon endpoints by discovering the actual registered routes and aligning Home Assistant REST sensors/commands accordingly. Validate end-to-end health (health/test/update_config), confirm SQL sensors remain healthy, and leave an audit trail.

## Scope & Preconditions
- Platform: Home Assistant OS; AppDaemon add-on at port 5050; app name room_db_updater.
- Problem: All probed URLs return 404 despite add-on reachability.
- Constraints: Prefer least-invasive changes first; preserve ADR-0024 canonical paths and ADR-0027 write governance.

## Inputs
- Repo paths to inspect/update:
  - AppDaemon log excerpt: `/config/hestia/config/diagnostics/appdaemon.log`
  - HA diagnostics/template: `/config/hestia/library/templates/devtools/adaptive-motion-lighting/room_db_diag.jinja2`
  - HA package probes: `/config/packages/room_database/room_db_diag.yaml`, `/config/packages/room_database/room_db_src.yaml`
  - Motion lighting templates: `/config/packages/motion_lighting_v2/motion_light_templates.yaml`
  - System configs and references:
    - `/config/hestia/config/system/addons.conf` (AppDaemon section)
    - `/config/hestia/config/diagnostics/2025-10-18T06-57-utc_room_db_diag.yaml` (latest diag report)
    - `/config/hestia/config/diagnostics/network_probes.toml`
    - `/config/hestia/config/system/relationships.conf`
  - AppDaemon app code (outside repo, mounted in add-on): `/addon_configs/a0d7b954_appdaemon/apps/room_db_updater.py`
  - Database + mapping: `/config/room_database.db`, `/config/www/area_mapping.yaml`

## Workflow (fast path)
1) Route Discovery
   - Read AppDaemon logs and/or room_db_updater.py to list exact register_endpoint paths.
   - If not obvious, add a temporary index route in room_db_updater.py that enumerates endpoints (e.g., GET /index).
   - Validate with curl from the HA SSH terminal using add-on hostname `a0d7b954-appdaemon:5050`.

2) Update HA REST Probes
   - In `room_db_diag.yaml`, set sensors to the discovered working paths for: health, test, update_config.
   - Keep alternates commented for future reference.
   - Reload templates/REST integration; validate values become 200/JSON.

3) Verify SQL + Template Health
   - Confirm `sensor.room_configs_motion_lighting(_dict)` and `sensor.room_configs_vacuum_control(_dict)` states are ok.
   - Ensure DevTools template `room_db_diag.jinja2` prints a single JSON reflecting endpoint 200s and SQL counts.

4) Audit + Docs
   - Append to `/config/hestia/config/system/maintenance_log.conf` a session entry with routes discovered and files updated.
   - Update `/config/hestia/config/system/addons.conf` endpoint URLs and notes.

## Output Expectations
- Endpoints responding with 200 and JSON payloads for health/test/update_config.
- `room_db_diag.jinja2` output shows present: true and state: ok (or JSON status) for working routes.
- Updated configs under version control, with notes in maintenance_log.

## Validation
- Curl examples (run in HA SSH terminal):
  - curl -sS http://a0d7b954-appdaemon:5050/api/app/<resolved_app_name>/<resolved_path>/health | jq .
  - curl -sS http://a0d7b954-appdaemon:5050/api/app/<resolved_app_name>/<resolved_path>/test | jq .
  - curl -sS -X POST http://a0d7b954-appdaemon:5050/api/app/<resolved_app_name>/<resolved_path>/update_config -H 'Content-Type: application/json' -d '{"dry_run": true}' | jq .

## Quality & Safety
- Comply with ADR-0024 paths and ADR-0027 write governance (use write-broker if needed).
- Avoid breaking SQL sensors; do not modify DB without explicit instruction.
- Keep changes minimal and documented.

## Notes
- Compare against the latest diagnostic report: `/config/hestia/config/diagnostics/2025-10-18T06-57-utc_room_db_diag.yaml`.
- If route prefix differs (e.g., `/room_db/health` nested), mirror that exactly in HA sensors.
