# Room‑DB: State of the Code (2025‑10‑18)

Audience: Machine operators and maintainers
Scope: AppDaemon Room‑DB endpoints, HA REST/Template wiring, diagnostics, and operator workflows

## Executive summary
- Issue resolved: All 404/500 endpoint errors were eliminated by standardizing on unique global AppDaemon endpoints: `/api/appdaemon/room_db_health`, `/api/appdaemon/room_db_test`, `/api/appdaemon/room_db_update_config`.
- Current status: Healthy. Global sensors in HA report `healthy` and `test_success`. SQL dictionary sensors are available for motion lighting and vacuum control.
- Operator tooling: New diagnostics templates, an Operator README with copy‑paste Developer Tools Actions, and suggested shell commands are in place.
- Next steps focus: Validate per‑room configs end‑to‑end (writes → dict sensors → automations), then prune legacy probes and finalize dashboards.

## What changed (high‑level)
- AppDaemon app was confirmed to register and serve unique global endpoints. HA configs were updated to use these.
- Added diagnostics and documentation for quick operator validation and troubleshooting.
- Network probes and suggested commands updated for fast checks.

## Artifacts created/updated
- HA runtime configs
  - `packages/room_database/room_db_src.yaml`: REST commands now target global room_db_* endpoints
  - `packages/room_database/room_db_diag.yaml`: diagnostics adjusted; direct test prefers global
- Diagnostics templates
  - `hestia/library/templates/devtools/adaptive-motion-lighting/room_db_setup_diag.jinja2` (new)
  - `hestia/library/templates/devtools/adaptive-motion-lighting/room_db_diag.jinja2` (existing; kept)
- Operator documentation
  - `hestia/library/docs/guides/room_db_README.md` (new): endpoints, examples, Actions snippets
  - `hestia/library/docs/guides/room_db_state_of_code.md` (this file)
- System/ops
  - `hestia/config/system/addons.conf`: canonical endpoints recorded
  - `hestia/config/system/homeassistant.conf`: configuration update entry added
  - `hestia/config/diagnostics/network_probes.toml`: added global health probe, annotated legacy 404s
  - `hestia/config/system/suggested_commands.conf`: curl examples added
  - `hestia/config/system/maintenance_log.conf`: session entries added for audit

## Validations and health checks (current status)
- AppDaemon logs show:
  - “Global endpoints registered: room_db_health, room_db_update_config, room_db_test”
  - Repeated 200 OK for health/test endpoints after restart
- HA sensors:
  - `sensor.appdaemon_health_appdaemon_global` → healthy
  - `sensor.appdaemon_test_appdaemon_global` → test_success
- YAML and template checks: PASS (template patcher and workspace validator)
- Probes:
  - Global health probe configured: `/api/appdaemon/room_db_health` (expected 200)
  - App‑scoped probes left as expected 404 (documented)

## Operator quick‑start
- Developer Tools → Template
  - Run `room_db_setup_diag.jinja2` to confirm endpoints and SQL dicts
- Developer Tools → Actions (YAML)
  - Use copy‑paste sequences from the README to perform health/test calls and configuration updates
- Terminal (Advanced SSH)
  - `roomdb_health` / `roomdb_test` commands in `suggested_commands.conf`

## Current limitations and notes
- Write rate limiting: The app enforces ~2s delay per domain/room to prevent write storms. Rapid double writes will produce `WRITE_RATE_LIMIT` (use a 2s delay between writes in Actions).
- Legacy endpoints: App‑scoped and compat routes may remain 404 in this environment; globals are canonical.

## Next steps (actionable)
1) Per‑room verification (motion lighting)
   - Use Actions to set a small config (e.g., timeout/brightness), confirm it reflects in `sensor.room_configs_motion_lighting_dict`, then trigger motion to observe behavior.
2) Per‑room verification (vacuum control)
   - Toggle `needs_cleaning` and validate `sensor.rooms_needing_cleaning` and dict updates. Run one manual automation cycle.
3) Prune old diagnostics
   - Remove 404‑prone sensors once stability is confirmed (keep the global ones + setup diag template).
4) Optional: Rate‑limit configurability
   - If desired, add `rate_limit_seconds` to app config to tune write guard.
5) Optional: Dashboard polish
   - Add Lovelace card with buttons for common updates and health/test calls.

## ADR and governance compliance
- ADR‑0024 (Canonical /config path): All references use canonical paths and add‑on hostnames
- ADR‑0027 (Write governance): Edits applied atomically with audit trail; documentation captured in maintenance log
- ADR‑0020 / ADR‑0002 (Template patterns): Templates normalized and guarded against common errors
- ADR‑0018 (Workspace lifecycle): Network probes and documentation integrated with diagnostics library

## Contact points
- AppDaemon add‑on: `a0d7b954_appdaemon` @ http://a0d7b954-appdaemon:5050
- Global endpoints: `/api/appdaemon/room_db_health`, `/api/appdaemon/room_db_test`, `/api/appdaemon/room_db_update_config`
- DB: `/config/room_database.db`
- Mapping: `/config/www/area_mapping.yaml`

## Appendix: copy‑paste Actions (examples)
- Health + Test
```
- service: rest_command.room_db_health
- service: rest_command.room_db_test
```
- Update motion lighting
```
- service: rest_command.room_db_update_config
  data:
    room_id: bedroom
    domain: motion_lighting
    config_data:
      timeout: 120
      brightness: 180
    schema_expected: 1
```
- Vacuum: set/clear needs_cleaning
```
- service: rest_command.room_db_update_config
  data:
    room_id: kitchen
    domain: vacuum_control
    config_data:
      needs_cleaning: 1
    schema_expected: 1
- delay: "00:00:02"
- service: rest_command.room_db_update_config
  data:
    room_id: kitchen
    domain: vacuum_control
    config_data:
      needs_cleaning: 0
      last_cleaned: "{{ now().isoformat() }}"
    schema_expected: 1
```
