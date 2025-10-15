# Valetudo Cleaning Package — Quick Runbook

## What this package contains
- Central per-room variables in `domain/variables/room_variables.yaml`.
- Composite per-room sensors (`packages/valetudo/sensors_composite.yaml`) importing macros from `custom_template/template.library.jinja`.
- Deterministic map segment sensor (`packages/valetudo/map_segments_sensor.yaml`) for blueprint lookups.
- Blueprint script instances (`packages/valetudo/scripts_blueprints.yaml`).
- Per-room orchestration scripts (`packages/valetudo/scripts_rooms.yaml`) that gate on `segment_id`, call the blueprint, wait for `cleaning → docked`, and write back to `var.<room>`.
- Core automations (`packages/valetudo/automations_core.yaml`).
- Audit template (`devtools/templates/valetudo_audit.jinja2`).

## Edit first
- Verify `/config/domain/variables/room_variables.yaml` segment_id values.
- Verify `packages/valetudo/map_segments_sensor.yaml` attributes (ID→Name).
- If your robot entity ID is not `vacuum.valetudo_roborocks5`, replace it in `scripts_rooms.yaml` and `automations_core.yaml`.

## Key behaviors
- No `vacuum.send_command` is used; publishing is done via the Valetudo blueprints (MQTT).
- On success, each script updates `last_cleaned`, clears `needs_cleaning`, sets `job_last_*`.
- On failure/timeout, the script sets `needs_cleaning: true`.

## Maintenance
- If Valetudo remaps segments, update both `segment_id` in each `var.<room>` and the attributes in `Valetudo Map Segments`.
- Use the audit template to detect drift and next-due times.
