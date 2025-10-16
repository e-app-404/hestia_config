---
mode: "agent"
model: GPT-4o
description: "Parse Home Assistant template YAMLs to extract room sensor entities and create machine-operable inventory"
tools: ['edit', 'search', 'runTasks', 'todos']
---

# Prompt for Copilot — Upstream/Downstream Trace & Attribute Hardening


You are in **sensor lineage tracing mode**.

## Objective
For each sensor defined in the following Home Assistant template YAMLs, parse the `state:` Jinja to extract **upstream source entities**, and discover **downstream consumers** by scanning cross-references. Then, **write the lineage back into each entity’s attributes**:
- Add/refresh `upstream_sources:` (JSON array emitted via Jinja `tojson`)
- Ensure `source_count:` matches the number of **entity IDs** in `upstream_sources` (exclude macro/template references from the count)
- Add/refresh `downstream_consumers:` (JSON array via Jinja `tojson`)
- Update `last_updated:` to today’s date **only if** you modified the block

## Scope (only edit these files)
- /config/domain/templates/presence_logic.yaml
- /config/domain/templates/occupancy_logic.yaml
- /config/domain/templates/motion_logic.yaml
- /config/domain/templates/desk_presence_inferred.yaml
- /config/domain/templates/ensuite_presence_inferred.yaml
- /config/domain/templates/illuminance_logic.yaml

## Entity types to trace
- Template `binary_sensor:` and `sensor:` blocks (and any nested lists under them)
- Treat each list item with `name:` / `unique_id:` as one entity definition

## How to detect **upstream sources**
Parse each entity’s `state:` Jinja for concrete references to other entities. Collect any entity_id that appears in:
- `states('entity_id')`, `state_attr('entity_id','...')`, `is_state('entity_id','...')`, `device_id('...')` (only if it implies entity targets)
- Static lists/dicts in Jinja like `sources = [{'entity': 'binary_sensor.x', ...}, ...]`
- Direct YAML `entity_id:` or `target:` if present inside the same definition
- Macros and includes: if the `state:` block uses `{% from 'template.library.jinja' import ... %}` or `{% include %}`, also capture the macro file name as a non-entity dependency (e.g., `"template.library.jinja"`) **but do not count it** toward `source_count`

Normalize and **deduplicate** entity_ids. Keep only valid Home Assistant domains (e.g., `binary_sensor.`, `sensor.`, `light.`, `person.`). Ignore variables or unresolved dynamic references.

## How to detect **downstream consumers**
Within the same file set, find all other entities whose `state:` Jinja references the current entity’s `entity_id` via any of:
- `states('this_entity')`, `state_attr('this_entity','...')`, `is_state('this_entity','...')`
- Included in a `sources = [...]` list
Record each consumer’s `entity_id` under `downstream_consumers`. Deduplicate.

## Attribute write-back rules
- If `attributes:` exists: **merge** or insert keys; do not remove unrelated attributes
- If missing: create `attributes:` and add the keys
- **Formatting for arrays** must be Jinja JSON, e.g.:
```

upstream_sources: >-
{{ ['binary_sensor.foo', 'sensor.bar'] | tojson }}
downstream_consumers: >-
{{ ['binary_sensor.baz'] | tojson }}

```
- `source_count:` must reflect **only the number of entity IDs in upstream_sources** (exclude macro/include filenames). Preserve existing type (if it was quoted, keep quoted; if numeric, keep numeric). If absent, create as a quoted string.
- `last_updated:` set to **today in ISO** (YYYY-MM-DD) **only if** you changed any upstream/downstream content for that entity. Otherwise leave as-is.

## House style & safety
- Keep **2-space indentation**, UTF-8, LF newlines, keys sorted A→Z inside attributes **only for newly added keys** (do not re-order existing keys globally)
- Preserve comments and existing order outside of the `attributes:` block
- Do not change `state:` logic
- No changes outside the six files
- If an entity already has these keys, update in place (merge & dedupe)
- If an entity has **zero** upstream sources, write `upstream_sources: {{ [] | tojson }}` and `source_count: "0"`

## Output requirements (STRICT)
1) Emit **unified diffs** for each changed file (one diff block per file).
2) Then emit a **Machine Findings Log** (newline-delimited JSON objects), where each line has:
 - code: one of ["UPSTREAM_ADDED","UPSTREAM_UPDATED","DOWNSTREAM_ADDED","COUNT_FIXED","TIMESTAMP_UPDATED","NO_CHANGE","ANOMALY"]
 - file, entity_id (unique_id if present else a stable slug), changes: {keys_modified:[...]}
 - evidence: {upstream:[{ref, line?}], downstream:[{ref, line?}]}
 - anomalies? e.g., unresolved dynamic reference, invalid entity domain, etc.

Example log line:
{"code":"UPSTREAM_UPDATED","file":"/config/domain/templates/motion_logic.yaml","entity_id":"binary_sensor.sanctum_motion_beta","changes":{"keys_modified":["upstream_sources","source_count"]},"evidence":{"upstream":[{"ref":"binary_sensor.bedroom_motion_beta","line":42},{"ref":"binary_sensor.ensuite_motion_beta","line":43}]}, "anomalies":[]}

## Reference shape (illustrative)
- If macro used: include "template.library.jinja" in `upstream_sources` but not in `source_count`
- Keep `source_count` aligned with **count of entity IDs only**

## Begin
Parse the six files, apply changes in-memory, and output unified diffs followed by the Machine Findings Log.