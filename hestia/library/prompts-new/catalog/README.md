# Prompt Catalog

Normalized prompt inventory with multi-axis access patterns.

## Directory Structure

### by_domain/ (Primary Canonical Location)
**This is the single source of truth for all prompts.**

- `governance/`: Policy, ADR, and governance prompts
- `extraction/`: Data extraction and parsing prompts
- `operational/`: Workflow and automation prompts
- `validation/`: Quality assurance and verification prompts
- `diagnostic/`: Debugging and analysis prompts
- `instructional/`: Guides, tutorials, and documentation prompts
- `emergency/`: Critical and urgent response prompts

### by_tier/ (Hard Copies for Navigation)
Greek tier classification with **hard copies** from `by_domain/`:

- `alpha/`: α - Core system control prompts
- `beta/`: β - Integration workflow prompts
- `gamma/`: γ - Instructional and guidance prompts
- `omega/`: Ω - Meta and universal prompts

### by_persona/ (Hard Copies for Navigation)
Persona-specific collections with **hard copies** from `by_domain/`:

- `promachos/`: Governance and meta-system prompts
- `strategos/`: Strategy and planning prompts
- `kybernetes/`: Navigation and pilot prompts
- `icaria/`: Repair and fix prompts
- `nomia/`: Validation and rule enforcement prompts
- `heurion/`: Discovery and analysis prompts

## File Naming Convention

**Format**: `prompt_{YYYYMMDD}_{HASH}_{slug}.md`

**Example**: `prompt_20251008_e61d30_valetudo-optimization.md`

## YAML Frontmatter Requirements

Every file must have ADR-0009 compliant frontmatter:

```yaml
---
id: prompt_20251008_001
slug: example-prompt
title: "Example Prompt Title"
date: 2025-10-08
tier: β
domain: operational
persona: kybernetes
status: candidate
tags: [automation, workflow]
version: "1.0"
source_path: "original/path/to/source.md"
author: "Author Name"
related: []
last_updated: 2025-10-08T00:00:00+01:00
redaction_log: []
---
```

## Copy Management

- **Primary location**: `by_domain/` contains authoritative versions
- **Navigation copies**: `by_tier/` and `by_persona/` contain hard copies
- **Synchronization**: Automated via `/config/hestia/tools/catalog/sync_copies.py`
- **Validation**: Hash-based consistency checks via `validate_copies.py`

## Important Notes

- **No symlinks**: ADR-0015 compliance requires hard copies only
- **Update workflow**: Always update primary in `by_domain/` first, then sync copies
- **Reference standard**: All promptsets reference `by_domain/` paths only

## Tools

- **Place in catalog**: `/config/hestia/tools/catalog/place_in_catalog.py`
- **Sync copies**: `/config/hestia/tools/catalog/sync_copies.py`
- **Validate copies**: `/config/hestia/tools/catalog/validate_copies.py`