# WIP ADR-0000: Template-derived sensor provenance

Status: WIP
Date: 2025-10-03
Authors: Hestia contributors (drafted by Copilot)

Context
-------
Home Assistant installations in this workspace produce a growing number of template-derived entities (binary_sensor, sensor, etc.) used for aggregation, fusion, and proxying of physical device signals. These template entities are logically useful, but currently lack a consistent provenance and metadata convention in the Hestia device indices. This makes tracing, debugging, and policy enforcement (for example: which integration creates an entity, how to treat template-derived entities in aggregation, and how to represent them in device registries) harder than necessary.

Decision drivers
----------------
- Template-derived entities are not physical hardware; they are logical constructs created by our automation/templates.
- We want to easily distinguish physical device entities from template-derived entities in `hestia/config/devices/*.conf` and other indices.
- Some consumers and diagnostic tooling may rely on manufacturer/model/device_id semantics to group and filter devices; we need to decide how (or whether) to reuse those fields for templates.
- We may later model a virtual device (room-shaped object) to act as a device proxy for groups of template-derived entities.

Proposed, early-stage conventions (WIP)
-------------------------------------
- integration: template
  - This field must be set for all template-derived entries in `hestia/config/devices/*.conf`.
- manufacturer: {$subsystem}
  - Use the logical subsystem name as the manufacturer string (for example: `theia`, `orpheus`, `hermes`). This helps group template entities by the owning subsystem while keeping a human readable anchor.
- model: template-proxy
  - A static model string identifying the entity as a template-derived proxy.
- device_id: <leave empty for now>
  - Defer assigning device_id until a virtual device proxy object design is agreed. Avoid fabricating device_id values that might collide with real devices.
- provenance: template (optional)
  - Redundant with `integration: template`. The added value: an explicit `provenance` key is a semantic hint that can be extended in future to include `provenance: template:generated-by-copilot` or `provenance: template:manual` without overloading `integration`.
  - Decision: document tradeoffs here; for now `provenance` is optional. If consumers need richer provenance beyond `integration`, we can enable it later.

Example (informal)
-------------------
- entity_id: sensor.bedroom_illuminance_beta
  integration: template
  manufacturer: hermes
  model: template-proxy
  provenance: template
  device_name: bedroom_illuminance_beta

Consequences
------------
- Short term: device conf files will clearly show which entries are templates, which helps tooling and human reviewers.
- Medium term: having `manufacturer` set to the subsystem makes it simpler to implement filters and dashboards by subsystem ownership.
- Long term: when we design a virtual device proxy, we can assign device_ids and move template-derived entities under that device, enabling richer device-level metadata and lifecycle management.

Next steps
----------
- Park automated mass-editing of device conf files until the virtual device design is agreed (per user request).
- Create a formal ADR describing the virtual device proxy design once stakeholders agree.
- Optionally, add lightweight validations (CI) to ensure `integration: template` is present for template-derived entries; user decided to postpone CI now but asked for a ticket.

Notes
-----
This document is a draft WIP to capture early-stage thinking. It is intentionally conservative: we avoid inventing device identifiers and instead record human-friendly grouping via `manufacturer` as subsystem names. Revisit this ADR when we decide whether to create a virtual device object to hold template-derived entities.
