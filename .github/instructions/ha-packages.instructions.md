---
description: 'Guidance for writing and reviewing Home Assistant packages YAML under packages/**'
applyTo: 'packages/**/*.yaml'
---

## Home Assistant Packages YAML

### General Instructions
- Normalize YAML per ADR-0008: UTF-8, LF line endings, 2 spaces, single newline at EOF.
- Use canonical paths only (ADR-0024). Do not introduce host-specific paths.
- Keep a clear purpose per package; avoid cross-cutting concerns in one file.
- Prefer includes/anchors for reuse; keep duplication low and intent obvious.

### Best Practices
- Organize integrations under `packages/integrations/` for discoverability.
- Co-locate automations/templates/services that belong to a feature in the same package.
- Document non-obvious logic with 1–2 line comments; avoid over-commenting.
- Keep entity IDs stable and descriptive; align with ADR-0021 tiers where relevant.

### Code Standards
- Indentation 2 spaces; no tabs. Sort keys A→Z where semantics permit (ADR-0008).
- Use filters in Jinja templates and guard unknown/unavailable (ADR-0002, ADR-0020).
- Never hardcode credentials; use `secrets.yaml` or vault URIs.

### Common Patterns
- Use !include and !include_dir_* for modularity.
- For complex templates, move logic to `custom_templates` macros and import.
- Recorder exclusions belong in `packages/integrations/recorder.yaml` (ADR-0014).

### Security
- No plaintext secrets; use placeholders or `vault://` URIs exactly per schema.
- Review `rest_command`/`command_line` actions for SSRF or shell injection risks.

### Examples

**Good example:**

```yaml
homeassistant:
  customize: {}
template:
  - sensor:
      - name: 'System Git Push Status'
        state: "{{ states('sensor.system_git_push_state') }}"
- sensor:  # unsorted, wrong indent
  - id: system_git_push
    alias: 'System: Git Push on Change'
    trigger:
      - platform: state
        entity_id: sensor.pending_git_changes
        to: 'on'
    action:
      - service: shell_command.git_push
```

**Bad example:**

```yaml
homeassistant:
    customize: {}  # wrong indent
template:
- sensor:  # unsorted, wrong indent
  - name: 'Push'
    state: "{{ abs(states('sensor.x')) }}"  # function not filter; no guards
automation:
  - alias: Do it
    trigger: []
    action:
      - service: shell_command.git_push
      - service: notify.mobile_app  # unrelated side effect
```
  - name: 'Push'
    state: "{{ abs(states('sensor.x')) }}"  # function not filter; no guards
automation:
  - alias: Do it
    trigger: []
    action:
      - service: shell_command.git_push
      - service: notify.mobile_app  # unrelated side effect

### References
- /config/.workspace/governance_index.md
- /config/.github/instructions/instructions.instructions.md
- /config/.github/instructions/copilot-instructions.md
- /config/hestia/config/system/hestia.toml
- /config/hestia/library/docs/ADR/ADR-0024-canonical-config-path.md
- /config/hestia/library/docs/ADR/ADR-0008-normalization-and-determinism-rules.md
- /config/hestia/library/docs/ADR/ADR-0014-oom-and-recorder-policy.md
- /config/hestia/library/docs/ADR/ADR-0002-jinja-patterns.md
- /config/hestia/library/docs/ADR/ADR-0020-ha-config-error-canonicalization.md
