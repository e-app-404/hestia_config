---
description: 'Standards for authoring Jinja templates/macros under custom_templates/**'
applyTo: 'custom_templates/**/*.{jinja,jinja2,yaml}'
---

## Custom Jinja Templates

### General Instructions
- Keep macros pure and composable; avoid side effects.
- Always guard state and types (ADR-0002, ADR-0020).
- Use whitespace control to prevent empty string noise.

### Best Practices
- Centralize shared macros in `template.library.jinja`.
- Provide thin wrappers per use-case and reuse base macros.
- Name macros with clear inputs/outputs; document via comments.

### Code Standards
- Prefer filters over functions (| float, | int, | abs, | round).
- Whitespace control with `{%- ... -%}` where output must be tight.
- Avoid overly long inline expressions; set vars first.

### Common Patterns
- Availability/health macros wrapping state checks.
- Date/time parsing guarded with `as_datetime` and none checks.

### Security
- Never fetch URLs or run commands from Jinja.
- Don’t leak secrets through rendered outputs.

### Performance
- Minimize repeated states() calls; cache in local vars.

### Testing (quick checks)
- Task: Hestia: Patch HA templates
- Then run: ADR-0024: Validate HA YAML & Core

### Examples
Good
```jinja
{%- macro pct(value) -%}
{%- set v = (value | float(0.0)) -%}
{%- if v is not number -%}0{%- else -%}{{ (v * 100) | round(0) }}{%- endif -%}
{%- endmacro -%}
```

Bad
```jinja
{% macro pct(value) %}
{{ '{{' }} int(value*100) {{ '}}' }} {# no guards, function not filter #}
{% endmacro %}
```

### References
- /config/hestia/library/docs/ADR/ADR-0002-jinja-patterns.md
- /config/hestia/library/docs/ADR/ADR-0020-ha-config-error-canonicalization.md
- /config/.github/instructions/copilot-instructions.md
- /config/hestia/config/system/hestia.toml
