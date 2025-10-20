# Registry Governance (_meta)

This directory contains **schemas, validators, and governance references** for the HESTIA prompt library.

## Canonical References
- **Promptset JSON Schema**: `/config/hestia/library/prompts/_meta/promptset_schema.yaml`
- **Persona Registry**: `/config/hestia/library/docs/governance/persona_registry.yaml`
- **System Instruction**: `/config/hestia/library/docs/governance/system_instruction.yaml`
- **Promptset Documentation**: `/config/hestia/library/docs/architecture/promptset_docs.md`

## Policies
- **ADR-0009**: YAML frontmatter compliance
- **ADR-0015**: No symlink dependencies (hard copies only)
- **COPIES**: STANDBY — `by_domain/` is the single canonical source
- **Logs**: `/config/hestia/library/prompts/logs/`
- **Reports**: `/config/hestia/library/prompts/reports/`

> Note: Historical placeholders like `architecture_doctrine.yaml` or `_meta/prompt_schema.md` are **removed/migrated** and must not be referenced.