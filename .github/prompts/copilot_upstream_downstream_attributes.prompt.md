---
mode: "agent"
model: "GPT-4o"
description: "Trace sensor lineage in Home Assistant templates and harden entity attributes with upstream/downstream references"
tools: ["edit", "search"]
---

You are in **sensor lineage tracing agent mode**.

## Objective

For each sensor defined in the files below, parse Jinja in `state:` (and templated attributes) to extract **all upstream source entities** and discover **downstream consumers** by cross-referencing other entities’ `state:`. Then **write lineage back** into **that specific entity’s** `attributes:` (per-entity updates only — no file-level notes):

- Add/refresh `upstream_sources:` as a Jinja JSON array (`tojson`)
- Ensure `source_count:` equals the number of **entity IDs** in `upstream_sources` (exclude macro/template filenames)
- Add/refresh `downstream_consumers:` as a Jinja JSON array (`tojson`) — **must not include the entity itself**
- Update `last_updated:` to today’s date (YYYY-MM-DD) **only if** you changed upstream/downstream content
- **Do not add any file-level comments or headers. No “Updated … for entities in this file” lines.**

## Scope (only edit these files)

Reference and modify these Home Assistant template files:

- `domain/templates/illuminance_logic.yaml`

<!--
- `domain/templates/motion_logic.yaml`
- `domain/templates/desk_presence_inferred.yaml`
- `domain/templates/ensuite_presence_inferred.yaml`
- `domain/templates/illuminance_logic.yaml`
- `domain/templates/presence_logic.yaml`
- `domain/templates/occupancy_logic.yaml`
-->

## Entities to consider

- Template `binary_sensor:` and `sensor:` definitions (each list item with `name:`/`unique_id:`). Treat each list item as a separate entity for parsing **and** for write-back.

## DEFINITIVE upstream capture rules (ALL sources)

Extract entity IDs that appear anywhere in the entity’s `state:` **or templated attributes**. Include sources referenced:

1. **Directly** in Jinja calls:
   - `states('entity_id')`, `is_state('entity_id', ...)`, `state_attr('entity_id','...')`
   - `expand('group.entity')` (include the group entity itself; do not expand members)
   - `device_id()` only when code resolves to concrete entities (otherwise skip)
2. **Inside Jinja variables**, e.g.:
   - `{% set desk = is_state('binary_sensor.desk_occupancy_beta','on') %}` → include `binary_sensor.desk_occupancy_beta`
   - `{% set src = state_attr('person.evert','source') %}` → include **`person.evert`** as upstream; do **not** attempt to include the dynamic `src` value
3. **In Jinja data structures**, e.g.:
   - `sources = [{'entity': 'binary_sensor.x', ...}, ...]` → include each `'entity'` value
4. **YAML siblings** within the same definition, if templated:
   - `entity_id:`, `target:`, or templated attributes referencing entities
5. **Macros/includes** used in `state:`:
   - Record macro file (e.g., `"template.library.jinja"`) in `upstream_sources` **but do not count it** in `source_count`

**Normalization**

- Valid domains: `binary_sensor.`, `sensor.`, `light.`, `switch.`, `person.`, `input_*`, `group.`, `zone.`, `camera.`
- Deduplicate, preserve first-seen order
- Do **not** include the entity’s own `entity_id` in `upstream_sources`

## Downstream capture rules (NO self)

Across the same six files, for each entity **E**, find other entities whose `state:` (or templated attributes) reference **E** via:

- `states('E')`, `is_state('E', ...)`, `state_attr('E','...')`, inclusion in `sources=[...]`, etc.
- Deduplicate. **Do not include E itself** in its `downstream_consumers`.

## Attribute write-back rules (PER-ENTITY ONLY)

- Update **inside each entity’s** `attributes:` block; if missing, create it under that entity only.
- **Never** add file-level comments or summaries.
- Arrays must be valid, non-empty **Jinja JSON**:

  This is good:

  ```yaml
  upstream_sources: >-
    {{ ['entity.one', 'entity.two'] | tojson }}
  downstream_consumers: >-
    {{ ['entity.three'] | tojson }}
  ```

  These are bad:

  ```yaml
  upstream_sources: {{ ['entity.one', 'entity.two'] | tojson }}
  downstream_consumers: >-
    {{ [] | tojson }}
  ```

* `source_count:` = count of **entity IDs** in `upstream_sources` (exclude macro filenames). Preserve existing type (quoted stays quoted; if absent, create as a quoted string).
* Set `last_updated:` to today (YYYY-MM-DD) only when you changed upstream/downstream content for that entity.

## House style & safety

- 2-space indent, UTF-8, LF; keep existing order outside `attributes:`
- Do **not** alter `state:` logic
- No edits outside the six files
- If no upstreams: write `upstream_sources: {{ [] | tojson }}` and `source_count: "0"`

## Output requirements (STRICT)

1. Emit **unified diffs** per changed file (one diff block per file).

   - **Diffs must not include any added file-level comments or headers.**

2. Emit a **Machine Findings Log** (newline-delimited JSON). Each line:

   - `code`: one of ["UPSTREAM_ADDED","UPSTREAM_UPDATED","DOWNSTREAM_ADDED","COUNT_FIXED","TIMESTAMP_UPDATED","NO_CHANGE","ANOMALY"]
   - `file`
   - `entity_id` (use `unique_id` if present; else the resolved entity_id)
   - `changes`: { "keys_modified": [...] }
   - `evidence`: { "upstream": [{ "ref": "...", "line": n? }], "downstream": [{ "ref": "...", "line": n? }] }
   - `anomalies`: e.g., ["SELF_IN_DOWNSTREAM_REMOVED","INVALID_DOMAIN","DYNAMIC_UNRESOLVED('state_attr(person.evert,source)')"]

**Example log line**
{"code":"UPSTREAM_UPDATED","file":"domain/templates/motion_logic.yaml","entity_id":"binary_sensor.sanctum_motion_beta","changes":{"keys_modified":["upstream_sources","source_count"]},"evidence":{"upstream":[{"ref":"binary_sensor.bedroom_motion_beta","line":42},{"ref":"binary_sensor.ensuite_motion_beta","line":43}]},"anomalies":[]}

## Begin

Parse the file(s) indicated in the Scope, apply **per-entity** updates in-memory, and output unified diffs followed by the Machine Findings Log.
