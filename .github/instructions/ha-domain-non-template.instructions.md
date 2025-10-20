---
description: 'Guidelines for non-template domain YAML under domain/* (automations, helpers, groups, sensors, etc.)'
applyTo: 'domain/{automations,binary_sensors,command_line,frontend,geo_location,groups,helpers,lights,notify,persons,scripts,sensors,weather,zones}/**/*.yaml'
---

## HA Domain YAML (non-template)

### General Instructions
- One responsibility per file/folder; avoid mixing unrelated domains.
- Use stable IDs (automation/script ids should be durable across edits).
- Follow canonical naming and tier mappings where applicable (ADR-0021).

### Best Practices
- Reference entities via helpers/groups to reduce churn.
- Keep actions idempotent and safe (service calls with guards).
- Comment non-obvious triggers/conditions succinctly.

### Code Standards
- 2-space indent; sort keys; stable ordering for triggers/conditions/actions.
- Avoid hardcoded host paths; rely on HA entities/services.

### Common Patterns
- Group lights/sensors under domain/groups for reuse.
- External or shared config should live in packages rather than here.

### Security
- Scrutinize command_line/rest_command: parameterize inputs; avoid injection.

### Performance
- Limit high-frequency triggers; prefer meaningful state changes.
- Use delays/throttle windows judiciously.

### Testing (quick checks)
- Task: ADR-0024: Validate HA YAML & Core

### Examples

**Good example:**

```yaml
automation:
  - id: ha_sysadmin_auto_restart
    alias: 'System: Auto-Restart on Config Change'
    mode: single
    trigger:
      - platform: state
        entity_id: sensor.ha_config_changed
        to: 'on'
    action:
      - service: homeassistant.restart
```

**Bad example:**

```yaml
automation:
- alias: Restart
  trigger: []  # empty
  action:
    - service: shell_command.rm_rf  # unsafe and non-existent
```

### References
- [ADR Governance Index](/config/.workspace/governance_index.md)
- [ADR-0024](/config/hestia/library/docs/ADR/ADR-0024-canonical-config-path.md)
- [ADR-0008](/config/hestia/library/docs/ADR/ADR-0008-normalization-and-determinism-rules.md)
- [ADR-0021](/config/hestia/library/docs/ADR/ADR-0021-motion-occupancy-presence-signals.md)
- [Hestia Configuration](/config/hestia/config/system/hestia.toml)
