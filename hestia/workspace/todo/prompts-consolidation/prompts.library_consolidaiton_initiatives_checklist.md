# Main Initiatives for Prompt Library Consolidation

## 1. Infrastructure Setup

Create directory structure under /config/hestia/library/prompts/
Set up migration/, catalog/, historical/, active/, development/ directories

## 2. Tool Development (5 scripts)

prep_prompts.py - Normalize files to MD+YAML with enhanced metadata
validate_frontmatter.py - Check completeness and ADR-0009 compliance
place_in_catalog.py - Place in by_domain/ + generate hard copies
sync_copies.py - Maintain tier/persona copy consistency
validate_copies.py - Hash-based integrity validation

## 3. Normalization Pipeline

Copy files to migration/incoming/
Run prep script (dry-run → manual review 20 files → full run)
Validate frontmatter
Place in catalog with hard copies

## 4. Enforcement & Automation

Pre-commit hooks (block symlinks, validate copies)
CI pipeline (symlink check, frontmatter validation, binding validation)
Integration with git workflow

## 5. Historical Archiving

Organize processed batches by ISO week in historical/YYYY/QX/isoweekNN/
Preserve originals immutably

## 6. Active Curation (later phase)

Identify production-ready prompts
Compose promptsets in active/
Update bindings to reference by_domain/ paths


Critical Path: #2 (Tools) → #3 (Pipeline) → #4 (Enforcement) → #5 (Archive) → #6 (Curation)