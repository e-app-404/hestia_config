# Development

Work-in-progress and experimental prompts isolated from production.

## Directory Structure

- `drafts/`: Draft promptsets and templates under development
- `testing/`: Test prompts and validation samples
- `experimental/`: Experimental concepts and prototypes

## Purpose

- **Isolation**: Keep experimental work separate from production catalog
- **Iteration**: Safe space for prompt development and refinement
- **Testing**: Validate new approaches before normalization

## File Conventions

- **Drafts**: `draft_{name}.promptset`
- **Tests**: `test_{description}.{ext}`
- **Experiments**: `experiment_{name}_{date}.{ext}`

## Workflow

1. **Create** initial drafts in `drafts/`
2. **Test** and validate in `testing/`
3. **Experiment** with new approaches in `experimental/`
4. **Graduate** successful prompts to normalization pipeline
5. **Archive** completed experiments

## Example

```
development/
├── drafts/
│   ├── draft_ha_automation_template.promptset
│   └── draft_diagnostic_framework.md
├── testing/
│   ├── test_frontmatter_validation.md
│   └── test_exactly_forty_characters_long.test
└── experimental/
    ├── experiment_ai_prompt_optimization_20251008.md
    └── experiment_persona_detection_heuristics.py
```

## Graduation Criteria

Before moving to production pipeline:
- [ ] Functional validation complete
- [ ] ADR compliance verified
- [ ] Metadata requirements met
- [ ] No conflicts with existing catalog