Title: Wire `*_motion_recent_beta` into `*_occupancy_beta` (no loops; keep existing behavior)

Context:
- There is no mmWave in this project; do NOT introduce any mmWave dependencies.
- Lighting automations rely on `*_occupancy_beta`. We need each `*_occupancy_beta` to assert based on *recent motion* from `*_motion_recent_beta` (with a short grace) in addition to its existing logic.
- Avoid feedback loops. `*_motion_recent_beta` must depend ONLY on `*_motion_real_time` (plus timing), never on any occupancy entity.

Change scope (files):
- `domain/templates/motion_logic.yaml`
- `domain/templates/occupancy_logic.yaml`

Tasks:

A) Ensure “recent motion” entities exist
For each room prefix `X` that has `binary_sensor.X_motion_real_time`:
- Define (or keep unchanged if already present) `binary_sensor.X_motion_recent_beta` in `domain/templates/motion_logic.yaml`:

  template:
    - binary_sensor:
        - name: <Titleized X> Recent Motion (β)
          unique_id: X_motion_recent_beta
          device_class: motion
          state: >
            {{ is_state('binary_sensor.X_motion_real_time', 'on') }}
          delay_off: "00:00:30"

Notes:
- If `X_motion_recent_beta` already exists, do not create a duplicate. Preserve its existing `delay_off` if present.
- This block must NOT reference any occupancy entity (no loops).

B) Wire recent motion into occupancy
For each `binary_sensor.X_occupancy_beta` defined in `domain/templates/occupancy_logic.yaml`:
- Take the current `state:` Jinja expression (call it `S`).
- Replace it with: `{{ is_state('binary_sensor.X_motion_recent_beta', 'on') or ( S ) }}`

Rules:
- Preserve all existing conditions within `S` (e.g., shower, door, media, etc.).
- Keep any existing `delay_off` and other keys on `X_occupancy_beta` unchanged.
- If `X_motion_recent_beta` is already included in the expression, make no change (idempotent).

C) Example (Ensuite)

1) `domain/templates/motion_logic.yaml`
- Ensure the following block exists (skip if an equivalent definition already exists):

  template:
    - binary_sensor:
        - name: Ensuite Recent Motion (β)
          unique_id: ensuite_recent_motion_beta
          device_class: motion
          state: >
            {{ is_state('binary_sensor.ensuite_motion_real_time', 'on') }}
          delay_off: "00:00:30"

2) `domain/templates/occupancy_logic.yaml`
- Suppose the current block is:

  template:
    - binary_sensor:
        - name: Ensuite Occupancy (β)
          unique_id: ensuite_occupancy_beta
          device_class: occupancy
          state: >
            {{ <EXISTING JINJA EXPRESSION S> }}
          delay_off: "00:00:15"

- Update ONLY the `state:` to wrap existing logic with recent motion:

  state: >
    {{
      is_state('binary_sensor.ensuite_motion_recent_beta', 'on')
      or (
        <EXISTING JINJA EXPRESSION S>
      )
    }}

D) Idempotency and safety checks
- Do not add duplicate `template:` headers. Merge into existing `template:` lists as appropriate.
- Do not modify unrelated entities or conditions.
- Ensure there is no reference from any `*_motion_recent_beta` back into any `*_occupancy_*` (no loops).

E) Acceptance criteria
- When `binary_sensor.X_motion_real_time` toggles ON, `binary_sensor.X_occupancy_beta` turns ON immediately.
- With motion stopped, `X_occupancy_beta` remains ON at least for the grace from `X_motion_recent_beta.delay_off`, then follows its own `delay_off` (if any).
- `ha core check` (or project CI config validation) passes.

F) Quick verification commands (textual grep checks)
- Verify all occupancy betas include recent motion:
  grep -R "state:.*X_motion_recent_beta" domain/templates/occupancy_logic.yaml
- Verify recent motion entities are defined for all rooms with `*_motion_real_time`:
  grep -R "_motion_recent_beta" domain/templates/motion_logic.yaml
- Loop guard (recent motion must not reference occupancy):
  grep -R "occupancy" domain/templates/motion_logic.yaml | grep -i "_motion_recent_beta" || echo "OK (no loops found)"

Commit message:
feat(occupancy): wire *_motion_recent_beta into *_occupancy_beta with 30s grace; preserve existing logic; avoid loops

- Define/ensure binary_sensor.X_motion_recent_beta from X_motion_real_time (default delay_off 30s)
- Amend X_occupancy_beta to OR in X_motion_recent_beta while preserving existing conditions and delays
- No feedback loops; no new external dependencies; idempotent changes
