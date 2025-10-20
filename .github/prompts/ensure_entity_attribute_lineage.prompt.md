---
mode: "agent"
model: "GPT-4o"
description: "Cross-file lineage enrichment for HA template entities with non-destructive per-entity merges"
tools: ["search", "edit", "changes"]
---

# OPERATING MODE

You are in **Cross-File Lineage Enrichment** mode.

## Scope (only edit these files)

Reference and modify these Home Assistant template files:

- `domain/templates/motion_logic.yaml`
- `domain/templates/mqtt_native.yaml`
- `domain/templates/occupancy_logic.yaml`

<!--
- `domain/templates/tracking_logic.yaml`
- `domain/templates/humidity_logic.yaml`
- `domain/templates/temperature_logic.yaml`
- `domain/templates/illuminance_decay.yaml`
- `domain/templates/mqtt_native.yaml`
- `domain/templates/motion_logic.yaml`
- `domain/templates/desk_presence_inferred.yaml`
- `domain/templates/ensuite_presence_inferred.yaml`
- `domain/templates/illuminance_logic.yaml`
- `domain/templates/presence_logic.yaml`
- `domain/templates/occupancy_logic.yaml`
-->

## TODAY (date string, no time)

TODAY: "2025-10-16"

## OBJECTIVE

Discover cross-file lineage and **append** (non-destructively) to each entity’s `attributes:`:

- `upstream_sources: >-  {{ ['entity.a','entity.b','template.library.jinja'] | tojson }}`
- `downstream_consumers: >-  {{ ['binary_sensor.x','sensor.y'] | tojson }}`
- `source_count:` equals the number of **entity IDs** in `upstream_sources` (exclude macros/includes like `"template.library.jinja"`)
- `last_updated:` set to TODAY **only if** the entity’s upstream or downstream is changed

## SCOPE & GUARDRails

- Edit **multiple files**, but **only** within per-entity blocks (template `binary_sensor:` / `sensor:` list items with `name:` or `unique_id:`).
- **Per-entity write-backs only.** Never add file-level comments or headers.
- **Non-destructive merge policy:** preserve existing arrays and order; **append** new items (deduped). Do not remove existing lineage entries.
- Keep 2-space indentation, LF newlines, and do not alter `state:` logic.
- Only valid HA domains in arrays (binary*sensor.*, sensor._, light._, person._, switch.\*, input_\*).
  Macro/include filenames (e.g., `"template.library.jinja"`) are allowed **only** in `upstream_sources`, but they **do not** count toward `source_count`.

## HOW TO EXTRACT LINEAGE

For each entity in every FILE:

1. **Upstream (producers referenced by this entity):**
   - Parse the entity’s `state:` Jinja for explicit references:
     - `states('entity')`, `state_attr('entity','...')`, `is_state('entity','...')`
     - Structured lists/dicts like `sources = [{'entity': 'domain.object', ...}, ...]`
     - Inline `entity_id:` or `target:` within this entity block
   - Detect macro/include dependencies:
     `{% from 'template.library.jinja' import ... %}` or `{% include 'x.jinja' %}`
     → record the filename (e.g., `"template.library.jinja"`) in `upstream_sources` but **exclude** from `source_count`.
2. **Downstream (consumers of this entity):**
   - Search **across all FILES** for other entities whose `state:` refers to this entity’s ID via the same patterns above or in `sources = [...]`.
   - Add these consumer entity IDs to this entity’s `downstream_consumers`.
   - Do not include the entity itself; if present, remove and record an anomaly in the log.

## WRITE-BACK RULES (PER-ENTITY)

- If `attributes:` exists, **merge** keys; else create `attributes:`.
- Arrays must be **Jinja JSON**:

```jinja2
upstream_sources: >-
  {{ ['binary_sensor.foo','sensor.bar','template.library.jinja'] | tojson }}
downstream_consumers: >-
  {{ ['binary_sensor.baz'] | tojson }}

```

### Merging policy

- Read existing arrays (if present). Treat them as sets for dedupe.
- Keep existing items in their current order.
- Append new items (sorted A→Z for _just_ the newly-added tail).
- Never remove existing entries.
- `source_count:` must exactly match the number of **entity IDs** in `upstream_sources` (exclude macros). Keep prior quoting style (if quoted, keep quoted).
- `last_updated:` → set to TODAY **only if** upstream/downstream changed for that entity; otherwise do not touch it.

## VALIDATION

- Deduplicate arrays; filter to valid domains for entity IDs; allow macro/include filenames only in upstream.
- If zero upstreams, write:
- `upstream_sources: >-  {{ [] | tojson }}`
- `source_count: "0"`
- If you discover consumers in other files, add them to the producer’s `downstream_consumers` in the producer’s file (and, if the consumer’s upstream is missing this producer, append there too—non-destructively).

## OUTPUT (STRICT)

Emit **exactly two sections** and nothing else:

1. `### Unified Diffs`

- Unified diffs for **all files that changed** (one diff block per file). No banners or prose.

2. `### Machine Findings Log`

- Newline-delimited JSON (one per entity updated), fields:
  - `code`: one of ["UPSTREAM_UPDATED","DOWNSTREAM_ADDED","COUNT_FIXED","TIMESTAMP_UPDATED","MERGE_NOOP","ANOMALY"]
  - `file`: the file you edited
  - `entity_id`: the entity_id if determinable; else `unique_id`; else a stable slug from `name`+domain
  - `changes`: {"keys_modified":[...]}
  - `evidence`: {
    "upstream":[{"ref":"entity.or.macro","file":"...","line":N?}, ...],
    "downstream":[{"ref":"entity","file":"...","line":N?}, ...],
    "macros":[{"file":"template.library.jinja"}]?
    }
  - `anomalies`: e.g., ["SELF_IN_DOWNSTREAM_REMOVED","INVALID_ENTITY_ID('…')","MACRO_NOT_COUNTED"]

## HARD BLOCKERS

- Do **not** add any file-level comment like:
- "Updated upstream_sources for entities in this file"
- Do **not** overwrite existing arrays; always merge/dedupe/append.
- Do **not** change `state:` blocks.

## EXECUTION PLAN

1. Load all FILES; index entities (capture domain, unique_id, name, file path).
2. For each entity, parse `state:` to extract upstream + macros; record evidence (file+line).
3. Build cross-file downstream edges by searching other entities’ `state:` for references.
4. Apply per-entity merges across all affected files.
5. Recompute `source_count` and `last_updated` where appropriate.
6. Output Unified Diffs and Machine Findings Log.

## BEGIN
