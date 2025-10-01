# Context Timeline (Pre–Page 26)

## Bootloader & Audit Baseline

- Session boot block defining registry audit, enrichers, canonical export, validation rules.

## Key Findings & Cases

- **Sensor: sensor.sonos_favorites** → `area_id:"evert"` at entity level; area inference must be suppressed; floor inferred from area mapping; meta must say `"core.entity_registry", 1.0`. filecite:turn35file16
- **Binary Sensor: ensuite_shower_detected** → `unique_id:"..._epsilon"` indicates tier; tier should be taken from unique_id token with 1.0 confidence; `area_id` present in registry must be propagated; exemptions for device/manufacturer/serial for logic/template sensors.
- **Root cause on recent/shower** → Join chain emitted `[JOIN-SKIP]` but failed to **propagate** `area_id` to output; meta falsely marked `unresolved`. Patch join_enricher to propagate + annotate. filecite:turn35file14

## Patch Directives (pre‑26)

- **Join Propagation (join_enricher.py):** if registry has `area_id`, copy to output + annotate `"core.entity_registry", 1.0`; suppress further inference. filecite:turn35file17
- **Exemption Correction (area_floor_enricher.py):** do **not** null/override `area_id` for logic/template/virtual when present; only exempt if missing everywhere. filecite:turn35file11
- **Contract Patch Plan:** Authoritative `area_id`; tier via `unique_id`; exemptions for physical fields on logic/template; optional `_meta.source_entity` lineage.
