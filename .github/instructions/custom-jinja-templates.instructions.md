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
- Task: `Hestia: Patch HA templates`
- Then run: `ADR-0024: Validate HA YAML & Core`

### Examples
Good
```text
Guard inputs, use filters (|float, |round), and apply whitespace control in macros.
```

Bad
```text
Use of Python functions (e.g., int(value*100)) with no availability/type guards.
```
