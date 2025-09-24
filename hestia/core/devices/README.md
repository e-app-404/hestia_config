Devices (authoritative as-built records)
--------------------------------------

Purpose:
- `hestia/core/devices/` contains authoritative, human-curated `as_built` records
  and operational notes for each device. Files here are the single source of truth
  for device configuration decisions, hardware models, and validation results.

Naming and placement rules:
- `<device>.conf` — primary as-built record. Keep minimal transient data here.
- `*-update.conf` or `*.extract.cfg` — discovery or extracted snapshots may be
  stored under `core/config/` to separate machine-driven artifacts from the
  curated `as_built` files.

Workflow:
- When a device is discovered, place the parsed snapshot in `core/config/` and
  make amendments to the authoritative `core/devices/<device>.conf` as needed.
