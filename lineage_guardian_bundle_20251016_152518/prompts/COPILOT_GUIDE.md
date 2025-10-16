
# Copilot Coaching Script — Hestia Lineage Guardian

You’re assisting on a modular YAML lineage tool. Expand parsers, harden regexes, and make the corrector safe and idempotent.

## Targets to read

* `lineage_guardian/utils.py` — regexes, helpers
* `lineage_guardian/models.py` — dataclasses
* `lineage_guardian/graph_scanner.py` — extract upstream refs & macros from Jinja in `state:` blocks
* `lineage_guardian/lineage_validator.py` — compute violations vs declared `attributes.upstream_sources`/`downstream_consumers`/`source_count`
* `lineage_guardian/lineage_corrector.py` — plan-only now; implement ruamel-based merges later (non-destructive, backup-first)
* `lineage_guardian/graph_integrity_checker.py` — bidirectional checks & health score
* `lineage_guardian/lineage_report.py` — markdown + JSON

## Parsing rules (strict)

* Extract **entity_ids** from:

  * `states('domain.object')`
  * `is_state('domain.object', 'on')`
  * `state_attr('domain.object','attr')`
  * Jinja lists: `{% set sources = [{'entity': 'binary_sensor.foo'}, ...] %}`
* Valid domains only: `binary_sensor,sensor,light,switch,automation,script,person,input_boolean,device_tracker`
* Capture macro includes: `{% from 'template.library.jinja' import ... %}` as **macro dependencies** (not counted in source_count).
* Ignore MQTT topics (`zigbee2mqtt/...`) — not HA entities.

## Corrector rules

* Never delete existing arrays; **merge** missing items.
* `source_count` must equal number of **entity IDs** in `upstream_sources` (exclude macros).
* Update `last_updated` (YYYY-MM-DD) only if upstream/downstream changed.
* If `ruamel.yaml` present, write in-place with backups (suffix `.lineage_backup_{ISO}`) using atomic replace. Else, write a plan patch into `./.artifacts/_plan/`.

## Deliverables

* All README commands should work.
* Tight unit tests for `utils.extract_entities_from_state_block`.
* Keep changes minimal and reversible.

