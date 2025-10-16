---
mode: "agent"
description: "Parse Home Assistant template YAMLs to extract room sensor entities and create machine-operable inventory"
tools: ["edit", "search", "todos"]
---

You are in **investigative parsing mode**.

## Objective

Parse the following Home Assistant template YAMLs to extract, per room, the entities involved in **motion**, **occupancy**, **presence**, and **illuminance** (plus any **proxy/derived sensors**), and emit a concise, machine-operable inventory.

## Input files

Reference these Home Assistant template files for parsing:

- `domain/templates/presence_logic.yaml`
- `domain/templates/occupancy_logic.yaml`
- `domain/templates/motion_logic.yaml`
- `domain/templates/desk_presence_inferred.yaml`
- `domain/templates/ensuite_presence_inferred.yaml`
- `domain/templates/illuminance_logic.yaml`

> If any file is missing, continue with those that exist and report the missing ones in the anomalies section.

## What to extract (per room)

Collect all entity_ids that participate in these roles:

- **motion**: e.g., binary*sensor.\_motion*, _motion_beta_, _motion_proxy_, template-derived motion
- **occupancy**: e.g., binary*sensor.\_occupancy*, _occupancy_beta_, inferred occupancy from templates
- **presence**: person.\* and any template sensor that is used as a presence gate
- **illuminance**: sensor._illuminance_ and derived illuminance proxies
- **proxies/derived**: any template or composite sensor used as input to the above roles (including _\_proxy, _\_inferred, template outputs)

Also extract:

- **preferred_tier** (if discoverable): prefer \*\_beta entities over older tiers when multiple candidates exist.
- **room_slug**: infer from entity_id naming (e.g., bedroom, kitchen, living_room, downstairs, upstairs, ensuite, desk, hallway). If ambiguous, keep best-effort and flag in anomalies.

## Parsing rules & hints

- YAML may contain **Jinja** templates. Resolve **entity_ids** that appear in:
  - `entity_id:` fields, `target:` lists, `states('...')`, `state_attr('...','...')`, `is_state('...','...')`, or string interpolation used to reference entities.
- Follow chains: if a template sensor A references B, include B as a **proxy/derived** for the same room.
- Normalize duplicates; keep unique lists. Preserve **source file and line numbers** for each finding when possible.
- If a room has >1 candidate for a role (e.g., multiple motion sensors), keep them all and choose one **preferred** using this precedence:
  1. _\_beta, 2) _\_proxy (if proxy is the canonical path in code), 3) plain _\_motion or _\_occupancy.
     Emit both the **all** list and the **preferred** choice per role.

## Output format (STRICT)

Emit **only** the following two blocks, in this order:

### 1) Machine JSON (single JSON object)

Key: room_slug → value: object with fields:

- motion: { all: string[], preferred: string|null }
- occupancy: { all: string[], preferred: string|null }
- presence: { all: string[], preferred: string|null }
- illuminance: { all: string[], preferred: string|null }
- proxies: string[] # template/derived sensors used by above roles
- sources: { [entity_id]: [{file: string, line: number}] } # evidence map
- notes: string[] # optional brief notes

Example shape (illustrative):
{
"bedroom": {
"motion": { "all": ["binary_sensor.bedroom_motion_beta"], "preferred": "binary_sensor.bedroom_motion_beta" },
"occupancy": { "all": ["binary_sensor.bedroom_occupancy_beta"], "preferred": "binary_sensor.bedroom_occupancy_beta" },
"presence": { "all": ["person.evert"], "preferred": "person.evert" },
"illuminance": { "all": ["sensor.bedroom_illuminance_beta"], "preferred": "sensor.bedroom_illuminance_beta" },
"proxies": ["binary_sensor.bedroom_motion_proxy"],
"sources": { "binary_sensor.bedroom_motion_beta": [{"file":"/config/domain/templates/motion_logic.yaml","line":42}] },
"notes": []
},
"kitchen": { ... }
}

### 2) Compact table (Markdown)

Columns: room | motion.preferred | occupancy.preferred | presence.preferred | illuminance.preferred | counts(motion/occupancy/presence/illuminance/proxies)

Example:
| room | motion | occupancy | presence | illuminance | counts |
|-------------|------------------|------------------------------|--------------|-------------------------------|-------------------|
| bedroom | bin*s.bed...*β | bin*s.bed...\_occupancy*β | person.evert | sens.bed...*illuminance*β | m:1 o:1 p:1 i:1 x:1 |
| living*room | bin_s.living... | bin_s.living...\_occupancy*β | person.evert | sens.living...*illuminance*β | m:1 o:1 p:1 i:1 x:0 |

> Use “\_β” only as a visual hint in the table (optional). Keep full entity_ids in the JSON.

## Anomalies report (embed inside JSON under a top-level key "\_anomalies", not in the table)

Detect and list:

- Missing files
- Rooms with **no** motion or occupancy entity
- Entities referenced via Jinja that couldn’t be concretely resolved
- Conflicts where multiple “preferred” candidates qualify equally
- Any non-standard device_class that could cause HA validation issues
- Any obvious typos in entity_ids (nonexistent domains, invalid chars)

Shape:
"\_anomalies": [
{"type":"MISSING_FILE","file":"/config/domain/templates/occupancy_logic.yaml"},
{"type":"UNRESOLVED_JINJA","room":"hallway_downstairs","expression":"states(entity_id_var)"},
{"type":"NO_OCCUPANCY","room":"ensuite"}
]

## Constraints

- Do not modify any files.
- Be concise; no extra commentary outside the two required blocks.
- If you cannot determine a room_slug, use "unknown_<hash>" and add an anomaly.

## Now perform the parse and emit the two required blocks in order.
