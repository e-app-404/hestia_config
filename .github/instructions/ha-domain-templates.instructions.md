---
description: 'Rules for domain templates in domain/templates/** with Jinja guardrails'
applyTo: 'domain/templates/**/*.yaml'
---

## HA Domain Templates YAML

### General Instructions
- Templates must guard unknown/unavailable values (ADR-0002, ADR-0020).
- Use filters (e.g., | float, | int, | abs) rather than Python functions in Jinja.
- Keep outputs single, deterministic, and typed appropriately for HA.

### Best Practices
- Normalize state reads: set local vars, then compute.
- Encapsulate reusable logic in `custom_templates` macros when complexity grows.
- Name sensors/macros descriptively and consistently.

### Code Standards
- Indentation 2 spaces; sort keys; avoid trailing spaces (ADR-0008).
- Avoid heavy computation in templates; offload to helpers when possible.

### Common Patterns
- Gate input and types; example guards used in repo DevTools templates.
- Use as_datetime with none checks for time parsing.

### Security
- Never execute shell or fetch URLs from templates.
- Avoid leaking secrets through attributes or states.

### Performance
- Minimize repeated states() calls; cache values in local variables.

### Testing (quick checks)
- Task: Hestia: Patch HA templates
- Task: ADR-0024: Validate HA YAML & Core

### Examples

**Good example:**

```yaml
template:
  - sensor:
      - name: 'Occupancy Score'
        unit_of_measurement: '%'
        state: >-
          {% set raw = states('sensor.motion_factor') %}
          {% if raw in ['unknown','unavailable',''] %} 0
          {% else %}
            {{ (raw | float(0) * 100) | round(0) }}
          {% endif %}
```

**Bad example:**

```yaml
template:
  - sensor:
      - name: 'Occupancy Score'
        state: "{{ int(states('sensor.motion_factor')*100) }}"  # no guards; function not filter
```

### References
- [ADR-0002] (/config/hestia/library/docs/ADR/ADR-0002-jinja-patterns.md)
- [ADR-0020] (/config/hestia/library/docs/ADR/ADR-0020-ha-config-error-canonicalization.md)
- [ADR-0008] (/config/hestia/library/docs/ADR/ADR-0008-normalization-and-determinism-rules.md)
- [Copilot Instructions] (/config/.github/instructions/copilot-instructions.md)
- [Governance Index] (/config/.workspace/governance_index.md)
- [Hestia Configuration] (/config/hestia/config/system/hestia.toml)
