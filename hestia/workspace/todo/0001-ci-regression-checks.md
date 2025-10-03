---
status: open
created_at: 2025-10-03T00:00:00Z
updated_at: 2025-10-03T00:00:00Z
author: copilot
agent: copilot
human_owner: __REPLACE_ME__
priority: medium
labels: [ci, validation, backlog]
---

# Add lightweight CI/regression checks for template provenance & containment

## Description

We should add a lightweight CI job that validates two items:

1. All template-derived entries in `hestia/config/devices/*.conf` contain `integration: template`.
2. Templates in `domain/templates` should not list a parent-area aggregator as an upstream source for a child-area proxy (containment rule).

User opted to postpone implementation but asked this todo be logged for later.

## Proposed change / patch

Create a small Python-based validator and a GitHub Actions workflow to run it on PRs. The validator should:

- Parse YAML files under `hestia/config/devices/*` to detect template-derived entries and ensure `integration: template` exists.
- Parse `domain/templates/*.yaml` and check `upstream_sources` lists for parent->child violations based on the `area_id`/`subarea` attributes present in templates.

## Files changed

- (planned) `hestia/tools/validators/template_provenance_check.py`
- (planned) `.github/workflows/validate-templates.yml`

## Test plan

- Run the validator locally against the repo; it should return exit code 0 on success and non-zero on violations.
- Create test fixtures (small YAML files) for unit tests.

## Notes / references

- Related ADR: WIP-ADR-0000-template_derived_sensor_provenance.md

## Change log

- 2025-10-03: Created by copilot
