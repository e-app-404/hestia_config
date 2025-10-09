# Tier Navigation (Hard Copies)

This directory contains **hard copies** of prompts organized by Greek tier classification for easy navigation.

## ⚠️  NAVIGATION ONLY: These are Hard Copies

Files in this directory are **hard copies** from `/catalog/by_domain/` (the primary canonical location). 

**Do not edit files here directly** - always update the primary location first, then sync copies.

## Tier Classification

- `alpha/`: **α** - Core system control prompts (governance, emergency, critical)
- `beta/`: **β** - Integration workflow prompts (operational, automation, extraction)  
- `gamma/`: **γ** - Instructional and guidance prompts (tutorials, documentation, guides)
- `omega/`: **Ω** - Meta and universal prompts (frameworks, meta-system)

## Tier Assignment Criteria

### Alpha (α) - Core System Control
- Governance and policy prompts
- Emergency response prompts
- Critical system control
- Meta-system administration

### Beta (β) - Integration Workflows  
- Operational automation
- Data extraction and processing
- Integration workflows
- Pipeline management

### Gamma (γ) - Instructions & Guidance
- User guides and tutorials
- Documentation generation
- Instructional templates
- How-to prompts

### Omega (Ω) - Meta & Universal
- Framework definitions
- Universal patterns
- Meta-prompt systems
- Cross-cutting concerns

## Copy Synchronization

Copies are maintained automatically:
- **Sync tool**: `/config/hestia/tools/catalog/sync_copies.py`
- **Validation**: `/config/hestia/tools/catalog/validate_copies.py`
- **Source**: Primary canonical files in `/catalog/by_domain/`

## Usage

Browse by tier for quick discovery, but always reference primary canonical paths in promptsets:
```yaml
# Correct reference
bindings:
  - /config/hestia/library/prompts/catalog/by_domain/governance/prompt_20251008_001_policy.md

# Incorrect - do not reference tier copies
bindings:
  - /config/hestia/library/prompts/catalog/by_tier/alpha/prompt_20251008_001_policy.md
```