# Active Promptsets

Production-ready promptsets organized by functional category.

## Directory Structure

- `governance/`: Governance and meta-prompts
- `diagnostics/`: System diagnostic and analysis prompts
- `ha_config/`: Home Assistant configuration prompts
- `specialized/`: Domain-specific prompts (bb8-addon, sql_room_db, etc.)
- `utilities/`: General utility and optimization prompts

## File Conventions

- **Format**: `{name}.promptset.yaml` or `{name}.promptset`
- **Bindings**: Reference primary canonical locations in `../catalog/by_domain/`
- **No symlinks**: All references use absolute paths to avoid symlink dependencies

## Example Structure

```yaml
# example.promptset.yaml
promptset:
  id: example_v1
  title: "Example Promptset"
  bindings:
    - /config/hestia/library/prompts/catalog/by_domain/operational/prompt_20250502_001_example.md
```

## Compliance

- ADR-0015: No symlink dependencies
- PROMPT-LIB-CONSOLIDATION-V2: Active curation standards