# HESTIA Prompts Directory

## Quick Navigation

- **Need a production promptset?** → `active/{category}/`
- **Looking for a specific prompt?** → `catalog/by_domain/` (primary location)
- **Browse by tier or persona?** → `catalog/by_tier/` or `catalog/by_persona/`
- **Want to see historical evolution?** → `historical/YYYY/QX/isoweekNN/`
- **Working on new prompts?** → `development/drafts/`

## Directory Purposes

- `active/`: Curated, production-ready promptsets
- `catalog/by_domain/`: **Primary canonical location** for normalized prompts
- `catalog/by_tier/`: Hard copies organized by Greek tier (α, β, γ, etc.)
- `catalog/by_persona/`: Hard copies organized by persona
- `historical/`: Time-series archive (read-only)
- `development/`: Experimental work-in-progress
- `context/`: Supporting materials and seeds
- `migration/`: Normalization pipeline staging
- `_meta/`: Registry governance and schemas

## File Naming Conventions

- **Production**: `{name}.promptset.yaml` or `{name}.promptset`
- **Normalized**: `prompt_{YYYYMMDD}_{NNN}_{slug}.md`
- **Historical**: `isoweek{NN}-{original_name}.{ext}`
- **Draft**: `draft_{name}.promptset`

## Important Notes

- **No symlinks** are used in this directory structure (per ADR-0015)
- `by_tier/` and `by_persona/` contain **hard copies** for navigation
- Always reference `by_domain/` for canonical source in promptsets
- CI automation maintains consistency between primary and copies

## Architecture Compliance

- **ADR-0008**: Deterministic processing and IDs
- **ADR-0009**: YAML frontmatter governance compliance
- **ADR-0015**: Zero symlink dependencies (hard copies only)
- **ADR-0018**: Proper workspace lifecycle management

## Lifecycle Workflow

```
incoming → migration/incoming
         ↓
normalize → migration/processed (MD + YAML frontmatter)
         ↓
catalog → catalog/by_domain/ (primary canonical location)
         ↓
replicate → catalog/by_tier/ + catalog/by_persona/ (hard copies)
         ↓
curate → active/ (production promptsets)
         ↓
archive → historical/YYYY/QX/isoweekNN/ (immutable)
```

## Tool References

- **Normalization**: `/config/hestia/tools/prompt_prep/prep_prompts.py`
- **Validation**: `/config/hestia/tools/prompt_prep/validate_frontmatter.py`
- **Catalog Placement**: `/config/hestia/tools/catalog/place_in_catalog.py`
- **Copy Sync**: `/config/hestia/tools/catalog/sync_copies.py`
- **Copy Validation**: `/config/hestia/tools/catalog/validate_copies.py`

---

**Document Version**: 1.0  
**Created**: 2025-10-08  
**Compliance**: PROMPT-LIB-CONSOLIDATION-V2  
**Canonical Path**: `/config/hestia/library/prompts`