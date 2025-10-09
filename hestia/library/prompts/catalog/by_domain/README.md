# Primary Canonical Location

This directory contains the authoritative versions of all normalized prompts in the HESTIA library.

## ⚠️  IMPORTANT: Single Source of Truth

**This is the primary canonical location** - all other locations (`by_tier/`, `by_persona/`) contain hard copies for navigation purposes only.

## Directory Organization

Prompts are organized by functional domain:

- `governance/`: Policy, ADR, and governance prompts
- `extraction/`: Data extraction and parsing prompts  
- `operational/`: Workflow and automation prompts
- `validation/`: Quality assurance and verification prompts
- `diagnostic/`: Debugging and analysis prompts
- `instructional/`: Guides, tutorials, and documentation prompts
- `emergency/`: Critical and urgent response prompts

## Update Workflow

1. **Always update files in this directory first**
2. **Run sync tool** to update copies: `/config/hestia/tools/catalog/sync_copies.py`
3. **Validate consistency** with: `/config/hestia/tools/catalog/validate_copies.py`

## Reference Standard

- All promptset bindings should reference files in this directory
- Never reference tier or persona copies directly
- Use absolute paths: `/config/hestia/library/prompts/catalog/by_domain/{domain}/{filename}`

## Compliance

- ADR-0015: No symlink dependencies (hard copies used for navigation)
- PROMPT-LIB-CONSOLIDATION-V2: Primary canonical location specification