---
id: ADR-0020
title: "Home Assistant Configuration Error Canonicalization"
date: 2025-09-30
author: Strategos GPT
status: Accepted
last_updated: 2025-09-30
supersedes:
  - None
related:
  - ADR-0002 (Jinja patterns)
  - ADR-0009 (ADR governance formatting)
  - ADR-0016 (Canonical HA edit root)
references:
  - hestia/library/error_patterns.yml (Machine-readable error patterns)
  - hestia/tools/template_patcher/ (Template fixing tools)
  - custom_templates/template.library.jinja (Jinja macro library)
  - .githooks/pre-commit (Git hooks for validation)
decision_note: 
  - Establish centralized repository of common Home Assistant configuration errors and proven solutions.
  - Provide machine-readable error pattern documentation for automated detection and fixing.
  - Focus on systematic prevention through tooling and validation.
---

# ADR-0020 — Home Assistant Configuration Error Canonicalization

> Establish a centralized, machine-readable repository of common Home Assistant configuration errors with proven detection methods and automated fixes to prevent recurring issues and improve configuration reliability.

## Context

Home Assistant configurations grow complex over time, leading to recurring patterns of configuration errors that:
- Cause runtime failures or unexpected behavior
- Are difficult to detect without specific knowledge
- Result in wasted debugging time across team members
- Lack systematic documentation of proven solutions

The recent discovery of Jinja macro whitespace control issues exemplifies this problem: macros returning empty strings due to missing `{%-` and `-%}` whitespace control, which is difficult to debug through normal HA validation.

## Decision

Create a systematic approach to configuration error management with three components:

### 1. Machine-Readable Error Pattern Database

Establish `hestia/library/error_patterns.yml` as the canonical source of known error patterns:

```yaml
error_patterns:
  pattern_name:
    symptoms: ["symptom1", "symptom2"]
    detection: "detection_method"  
    regex_pattern: "detection_regex"
    fix_pattern: "fix_regex_or_description"
    severity: "low|medium|high|critical"
    category: "jinja|yaml|entity|integration"
    examples:
      incorrect: "example_of_wrong_code"
      correct: "example_of_fixed_code"
    validation_method: "how_to_verify_fix"
```

### 2. Automated Detection and Fixing Tools

Enhance existing template patchers and create new validation tools:
- `hestia/tools/template_patcher/` for Jinja-specific fixes
- Make targets for validation (`make config-validate`)  
- Pre-commit hooks for prevention
- CI integration for continuous validation

### 3. Documentation Standards

Each error pattern must include:
- **Root cause analysis** with technical explanation
- **Detection symptoms** observable by users
- **Proven fix** with before/after examples
- **Prevention strategy** to avoid recurrence
- **Validation method** to confirm resolution

## Error Pattern: Jinja Macro Whitespace Control

### Root Cause
Jinja2 macro definitions without whitespace control (`{%-` and `-%}`) generate unwanted whitespace and newlines in output, causing macros to return empty strings or padded values instead of clean 'on'/'off' states.

### Symptoms
- Template developer tools showing quoted empty results: `" "`
- Macros appearing to work but returning falsy values
- Boolean comparisons failing unexpectedly
- Inconsistent template output formatting

### Detection Method
**Developer Tools Test:**
```jinja
{% from 'template.library.jinja' import macro_name %}
Result: "{{ macro_name(params) }}"
```
If result shows quoted whitespace or empty content, whitespace control is needed.

**Automated Detection:**
```bash
grep -r "{% macro.*[^-]%}" custom_templates/
```

### Solution Pattern

**❌ Incorrect:**
```jinja
{% macro preference_select(sources) %}
  {% set result = 'off' %}
  {{ result }}
{% endmacro %}
```

**✅ Correct:**
```jinja
{% macro preference_select(sources) -%}
  {%- set result = 'off' -%}
  {{- result -}}
{%- endmacro %}
```

### Validation Method
1. Test macro in HA Developer Tools template panel
2. Verify output is clean string without quotes/whitespace
3. Confirm boolean comparisons work as expected

## Implementation

### Phase 1: Error Pattern Database
- ✅ Created `hestia/library/error_patterns.yml` with jinja_whitespace_control pattern
- Document additional patterns as discovered
- Establish pattern submission process

### Phase 2: Tooling Enhancement  
- Enhanced template patcher with whitespace detection
- Added Make target for validation
- Integrated into pre-commit hooks

### Phase 3: Prevention Integration
- CI validation pipeline
- Documentation in ADR format
- Team training on common patterns

## Validation Criteria

- [ ] Error patterns are machine-readable and actionable
- [ ] Automated tools successfully detect and fix known patterns
- [ ] Documentation follows ADR-0009 governance standards  
- [ ] Prevention mechanisms reduce recurrence of documented errors
- [ ] Team members can easily contribute new error patterns

## Rollback Procedure

If canonicalization introduces issues:
1. Disable automated fixing tools
2. Revert to manual error resolution
3. Remove problematic error patterns from database
4. Document lessons learned for future patterns

## Governance

Per ADR-0009 requirements:
- **Status**: Accepted (addresses systematic configuration reliability)
- **Scope**: All Home Assistant configuration files in hestia workspace
- **Review**: Quarterly review of error patterns and tooling effectiveness
- **Updates**: Version control all changes to error pattern database

## Future Extensions

### Planned Error Pattern Categories
- **YAML Structure**: Indentation, key naming, list formatting
- **Entity References**: Invalid entity IDs, state comparisons
- **Integration Config**: Common integration misconfiguration
- **Automation Logic**: Trigger/condition/action pattern issues

### Integration Opportunities  
- Home Assistant Config Check integration
- VS Code extension for real-time detection
- Documentation integration with existing ADRs
- Metrics collection on error pattern frequency

## Acceptance Criteria

1. **Documentation**: All error patterns follow machine-readable format
2. **Tooling**: Automated detection and fixing works for documented patterns  
3. **Prevention**: Pre-commit hooks prevent introduction of known patterns
4. **Governance**: Regular review process established per ADR-0009
5. **Adoption**: Team members actively use and contribute to error database

## Changelog

- **2025-09-30**: Initial ADR creation with Jinja whitespace control pattern
- **2025-09-30**: Implemented tooling enhancements and Make target integration

---

*This ADR establishes systematic approach to configuration error management, starting with Jinja template patterns and expanding to comprehensive HA configuration reliability.*