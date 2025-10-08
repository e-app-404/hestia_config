I'll revise the document to remove symlink dependencies and align with the ADR standards you've provided.

# Prompt Library Consolidation - TODO and Trail

## Current Status

**Status**: PARKED — Pre-preparation step created. Do not proceed with mass changes until reviewed.

---

## Trail Log

### 2025-09-21: Inventory and Normalization Plan Drafted

**Objective**: Pre-prepare step (convert all prompt files to Markdown with YAML frontmatter stub) marked in-progress.

**Files to Process**: 
- Source: `hestia/work/prompt.library/catalog/prompts_for_ingestion/*`
- File types: `.md`, `.promptset`, `.yaml`, `.csv.md`

**Rationale**: Normalize file types and provide deterministic frontmatter for downstream canonicalization into `*.promptset` YAML.

---

## Pre-Preparation Actions (Next Steps)

### Step 1: Run Deterministic Prep Script (Dry-Run Mode)

**Script Behavior**:
- Read each file in `prompts_for_ingestion`
- Write prepped Markdown file with YAML frontmatter stub containing:
  - `title`
  - `id`
  - `slug`
  - `created`
  - `persona`
  - `tier`
  - `domain`
  - `status`
  - `tags`
  - `source_path`
  - `redaction_log`
- Preserve original files untouched
- Write outputs to `hestia/work/prompt.library/canonical/prepped/`

### Step 2: Validate Frontmatter

**Tool**: `tools/prompt_prep/validate_frontmatter.py`

**Purpose**: Verify frontmatter presence and stub completeness across all prepped files.

### Step 3: Manual Review

**Action**: Review sample of 20 prepped files and adjust extraction heuristics as needed.

---

## Important Notes

⚠️ **Do Not Run Normalization** over the entire catalog without manual review of samples.

✅ **Keep Originals in Place**: Prepped outputs should be read-only until sign-off.

📧 **Contact**: evertappels for sign-off before bulk apply.

---

---

# Prompt Library Proposed Directory Structure

## Executive Summary

**Analysis Foundation**:
- Current tree structure: 243 files across 26 directories
- Template specifications: `draft_template.promptset`, `sql_room_db_v1.4.promptset`
- Goal: Historical preservation with machine/human accessibility
- Ongoing work: Normalization to Markdown + YAML frontmatter

**Recommendation**: Hybrid chronological-functional architecture with clear separation of concerns and **zero symlink dependencies** (per ADR-0015).

---

## 🎯 Proposed Directory Structure

```
prompts/
├── README.md                          # Navigation guide and conventions
│
├── _meta/                             # Registry governance (existing, preserved)
│   ├── metaschema_prompt_registry.md
│   ├── prompt_registry_meta.json
│   └── registry_*.yaml                # Validation, governance, templates
│
├── active/                            # Production-ready promptsets
│   ├── governance/
│   │   ├── kybernetes_governance_review.promptset.yaml
│   │   └── promachos_conversation_audit.promptset.yaml
│   ├── diagnostics/
│   │   ├── ha_log_analysis.promptset
│   │   └── home_assistant_diagnostician.promptset
│   ├── ha_config/
│   │   ├── motion_automation_blueprint.promptset
│   │   └── enhanced-lighting-prompt.md
│   ├── specialized/
│   │   ├── bb8-addon/
│   │   │   └── ha_bb8_addon_diagnostics.promptset
│   │   └── sql_room_db/
│   │       └── sql_room_db_v1.4.promptset (current production)
│   └── utilities/
│       ├── library_restructure_ai_optimization.promptset
│       └── valetudo_optimization_comprehensive_v2.promptset
│
├── catalog/                           # Normalized prompt inventory (MD+YAML)
│   ├── by_domain/                     # Functional grouping (primary location)
│   │   ├── governance/
│   │   ├── extraction/
│   │   ├── operational/
│   │   ├── validation/
│   │   ├── diagnostic/
│   │   ├── instructional/
│   │   └── emergency/
│   ├── by_tier/                       # Greek tier classification (hard copies)
│   │   ├── alpha/                     # α - Core system control
│   │   ├── beta/                      # β - Integration workflows
│   │   ├── gamma/                     # γ - Instructions/guidance
│   │   └── omega/                     # Ω - Meta/universal
│   └── by_persona/                    # Persona-specific collections (hard copies)
│       ├── promachos/
│       ├── strategos/
│       ├── kybernetes/
│       └── [other_personas]/
│
├── historical/                        # Time-series archive (read-only)
│   ├── 2025/
│   │   ├── Q1/
│   │   │   ├── isoweek01/
│   │   │   ├── isoweek02/
│   │   │   └── ...
│   │   ├── Q2/
│   │   │   ├── isoweek14/
│   │   │   ├── isoweek15/
│   │   │   └── ...
│   │   └── Q3/
│   │       ├── isoweek27/
│   │       └── ...
│   └── legacy/                        # Pre-normalization artifacts
│       ├── raw_imports/
│       └── conversion_logs/
│
├── development/                       # Work-in-progress and experimental
│   ├── drafts/
│   │   └── draft_template.promptset
│   ├── testing/
│   │   └── test_exactly_forty_characters_long.test
│   └── experimental/
│       └── [new_prompt_concepts]/
│
├── context/                           # Supporting materials (preserved)
│   ├── conversations/                 # GPT interaction logs
│   ├── seeds/                         # Bootstrap/hydration data
│   └── scaffolds/                     # Architectural templates
│
└── migration/                         # Normalization workflow staging
    ├── incoming/                      # Files awaiting processing
    ├── processed/                     # Successfully normalized
    ├── failed/                        # Requires manual intervention
    └── reports/                       # Conversion statistics/logs
```

---

## 🔑 Key Design Principles

### 1. Separation of Concerns

- **active/**: Production promptsets, organized by function
- **catalog/**: Normalized inventory with multi-axis access (domain/tier/persona)
- **historical/**: Immutable time-series archive
- **development/**: Experimental work isolated from production

### 2. Multiple Access Patterns via Hard Copies

Per **ADR-0015**, the `catalog/` directory provides three complementary navigation strategies using **hard copies** instead of symlinks:

- **by_domain/**: Primary canonical location for all prompts
- **by_tier/**: **Hard copies** organized by Greek tier classification
- **by_persona/**: **Hard copies** organized by persona

**Rationale**: 
- Eliminates symlink-related issues with file watchers, backups, and cross-platform compatibility
- Ensures snapshot/tarball integrity (ADR-0015 §4)
- Maintains deterministic structure for audits and automation (ADR-0008)
- Enables independent updates without cascading failures

### 3. Temporal Preservation

- `historical/` maintains quarterly snapshots with ISO week organization
- Original file names preserved with ISO week prefixes intact
- Conversion from historical → catalog creates normalized copies with appropriate placement

### 4. Clear Lifecycle Stages

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

---

## 📋 Implementation Guidelines

### Phase 1: Structural Migration

1. Create new directory structure (non-destructive)
2. **Preserve** existing `_archive/` and `_meta/` as-is
3. Copy current `catalog/` contents to `catalog/by_domain/` (primary location)
4. Establish migration staging areas

### Phase 2: Normalization Pipeline

1. Process existing batches through conversion:
   - Extract/infer YAML frontmatter
   - Standardize to Markdown body format
   - Assign canonical IDs and metadata
2. Place results in `catalog/by_domain/` (primary canonical location)
3. Generate hard copies in `by_tier/` and `by_persona/` based on metadata

### Phase 3: Cataloging Rules

For each normalized prompt in `catalog/`:

**Filename Convention**: `{id}_{slug}.md`
- Example: `prompt_20250502_003_meta_analysis.md`

**Frontmatter Requirements** (per ADR-0009 §5):
```yaml
---
id: prompt_20250502_003
slug: meta_analysis
title: "Meta Analysis Protocol"
date: 2025-05-02
tier: α|β|γ|δ|ε|ζ|η|Ω
domain: [governance|extraction|operational|validation|diagnostic|instructional|emergency]
persona: [promachos|strategos|kybernetes|etc]
status: [active|candidate|approved|deprecated]
tags: [comma, separated, list]
version: "1.0"
source_path: "original/path/to/source.md"
redaction_log: []
author: "Author Name"
related: []
last_updated: 2025-05-02T00:00:00+01:00
---
```

**File Organization Strategy**:
- **Primary (canonical)**: `catalog/by_domain/{domain}/prompt_{id}_{slug}.md`
- **Tier copy**: `catalog/by_tier/{tier}/prompt_{id}_{slug}.md` (hard copy)
- **Persona copy**: `catalog/by_persona/{persona}/prompt_{id}_{slug}.md` (hard copy)

**Copy Management**:
- Automated tooling maintains consistency between primary and copies
- Updates to primary location trigger regeneration of tier/persona copies
- CI validates that copies match primary via hash comparison

### Phase 4: Promptset Composition

When generating `*.promptset` files:

1. Source from `catalog/by_domain/` (primary canonical location only)
2. Compose according to `draft_template.promptset` schema
3. Place result in `active/{category}/`
4. Reference catalog entries via **absolute paths** to primary location:
   ```yaml
   bindings:
     - /prompts/catalog/by_domain/operational/prompt_20250502_001_cli_tool_audit.md
   ```

---

## 🔄 Migration Workflow Example

### Current State

```
_archive/batch1/batch1-audit_20250502_001.md
```

### After Normalization

```
catalog/
├── by_domain/                          # PRIMARY CANONICAL LOCATION
│   └── operational/
│       └── prompt_20250502_001_cli_tool_audit.md
├── by_tier/                            # HARD COPIES
│   └── beta/
│       └── prompt_20250502_001_cli_tool_audit.md (copied from by_domain)
└── by_persona/                         # HARD COPIES
    └── icaria/
        └── prompt_20250502_001_cli_tool_audit.md (copied from by_domain)

historical/
└── 2025/
    └── Q2/
        └── isoweek18/
            └── isoweek18-audit_20250502_001.md (unchanged original)
```

### Composed Promptset

```yaml
# active/diagnostics/hestia_cli_audit.promptset.yaml
promptset:
  id: hestia_cli_audit.v1
  prompts:
    - id: cli_tool_audit
      bindings:
        # Reference primary canonical location only
        - /prompts/catalog/by_domain/operational/prompt_20250502_001_cli_tool_audit.md
```

---

## 🎨 Human-Friendly Features

### README.md Navigation Guide

Place at `prompts/README.md`:

```markdown
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
```

---

## 🤖 Machine-Friendly Features

### Metadata Extraction

Every normalized file in `catalog/` has:

1. Deterministic filename pattern (parseable)
2. ADR-0009 compliant YAML frontmatter (JSON-serializable)
3. Consistent directory structure (predictable paths)
4. Hash-based integrity validation between copies

### Automated Discovery

Tools can traverse using standard patterns:

```python
# Find all β-tier prompts (from primary location)
prompts = glob("catalog/by_domain/**/prompt_*_*.md")
beta_prompts = [p for p in prompts if get_tier(p) == "β"]

# Find all Strategos prompts (via hard copies for convenience)
strategos = glob("catalog/by_persona/strategos/*.md")

# Get all governance domain prompts (primary canonical)
governance = glob("catalog/by_domain/governance/*.md")
```

### Copy Synchronization Automation

**Tool**: `tools/catalog/sync_copies.py`

```python
# Pseudocode for copy synchronization
def sync_catalog_copies():
    """Maintain by_tier and by_persona as hard copies of by_domain"""
    for prompt in glob("catalog/by_domain/**/*.md"):
        metadata = extract_frontmatter(prompt)
        
        # Generate tier copy path
        tier_path = f"catalog/by_tier/{metadata['tier']}/{basename(prompt)}"
        copy_if_different(prompt, tier_path)
        
        # Generate persona copy path
        persona_path = f"catalog/by_persona/{metadata['persona']}/{basename(prompt)}"
        copy_if_different(prompt, persona_path)
```

### Version Control Compatibility

- Historical batches are immutable (safe for git history)
- Primary canonical entries in `by_domain/` are single source of truth
- Copies in `by_tier/` and `by_persona/` tracked separately
- Active promptsets reference primary location only
- No symlink-related git issues (per ADR-0015)

---

## 🚀 Migration Priority Recommendations

### Phase 1 (Immediate - Non-disruptive)

1. Create new directory structure alongside existing
2. Copy `_meta/` to preserve governance
3. Create `README.md` navigation guide
4. Establish `migration/` staging areas
5. Implement `tools/catalog/sync_copies.py` utility

### Phase 2 (Normalization - Gradual)

1. Process batch1-batch4 through conversion
2. Populate `catalog/by_domain/` with normalized files (primary location)
3. Generate hard copies in `by_tier/` and `by_persona/`
4. Validate frontmatter completeness per ADR-0009

### Phase 3 (Active Curation - Selective)

1. Identify production-ready prompts
2. Compose promptsets in `active/`
3. Document composition patterns
4. Test promptset bindings to primary locations
5. Validate no symlink dependencies remain

### Phase 4 (Historical Archive - Final)

1. Move processed batches to `historical/` with ISO week organization
2. Validate all references point to primary canonical locations
3. Run hash validation on all copies
4. Deprecate `_archive/` gracefully
5. Generate migration completion report

---

## 📊 Acceptance Criteria

Post-migration validation must confirm:

1. **Structure Compliance**
   - No symlinks exist anywhere in `prompts/` directory tree (ADR-0015 compliance)
   - All normalized prompts have ADR-0009 compliant frontmatter
   - Directory structure matches specification exactly

2. **File Organization**
   - Primary canonical files exist in `catalog/by_domain/` for all prompts
   - Hard copies in `by_tier/` and `by_persona/` match primaries (hash validation)
   - No orphaned files in any directory

3. **Reference Integrity**
   - All promptset bindings reference `by_domain/` primary locations
   - No relative path references that could break on copy
   - CI validates binding paths exist and are accessible

4. **Performance Metrics**
   - Discovery Time: <30s to find any prompt by domain/tier/persona
   - Composition Time: <5min to create new promptset from catalog
   - Normalization Success: >95% automated conversion rate
   - Copy Consistency: 100% hash match between primary and copies
   - Documentation Coverage: Every directory has purpose statement
   - Historical Traceability: ISO week mapping for all archived prompts

5. **Automation & Tooling**
   - `sync_copies.py` successfully maintains consistency
   - CI validates no symlinks on every commit
   - Pre-commit hooks prevent symlink introduction
   - Hash validation passes for all tier/persona copies

---

## 🔧 Enforcement & Validation

### Pre-Commit Hooks

**Tool**: `.git/hooks/pre-commit`

```bash
#!/usr/bin/env bash
# Enforce ADR-0015: No symlinks in prompts/ tree
set -euo pipefail

echo "🔍 Checking for symlinks in prompts/..."
if git ls-files -s prompts/ | awk '$1==120000{exit 1}'; then
    echo "✅ No symlinks detected"
else
    echo "❌ ERROR: Symlinks detected in prompts/ directory"
    echo "   This violates ADR-0015. Remove symlinks and use hard copies instead."
    exit 1
fi

echo "🔍 Validating copy consistency..."
python tools/catalog/validate_copies.py || {
    echo "❌ ERROR: Copy validation failed"
    echo "   Run: python tools/catalog/sync_copies.py"
    exit 1
}

echo "✅ All validation checks passed"
```

### CI Validation Pipeline

**Tool**: `.github/workflows/validate-prompts.yml`

```yaml
name: Validate Prompt Structure

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check for symlinks (ADR-0015)
        run: |
          if git ls-files -s prompts/ | awk '$1==120000{exit 1}'; then
            echo "✅ No symlinks detected"
          else
            echo "❌ Symlinks found in prompts/ - violates ADR-0015"
            exit 1
          fi
      
      - name: Validate frontmatter (ADR-0009)
        run: python tools/prompt_prep/validate_frontmatter.py
      
      - name: Validate copy consistency
        run: python tools/catalog/validate_copies.py
      
      - name: Validate promptset bindings
        run: python tools/catalog/validate_bindings.py
```

### Validation Tools

**Tool 1**: `tools/catalog/validate_copies.py`

```python
#!/usr/bin/env python3
"""Validate that tier/persona copies match primary domain files"""

import hashlib
import sys
from pathlib import Path

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    catalog = Path("prompts/catalog")
    errors = []
    
    for primary in (catalog / "by_domain").rglob("*.md"):
        # Extract metadata to find tier and persona
        tier, persona = extract_metadata(primary)
        
        # Validate tier copy
        tier_copy = catalog / "by_tier" / tier / primary.name
        if tier_copy.exists():
            if file_hash(primary) != file_hash(tier_copy):
                errors.append(f"Hash mismatch: {primary.name} (tier)")
        else:
            errors.append(f"Missing tier copy: {tier_copy}")
        
        # Validate persona copy
        persona_copy = catalog / "by_persona" / persona / primary.name
        if persona_copy.exists():
            if file_hash(primary) != file_hash(persona_copy):
                errors.append(f"Hash mismatch: {primary.name} (persona)")
        else:
            errors.append(f"Missing persona copy: {persona_copy}")
    
    if errors:
        print("❌ Copy validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ All copies validated successfully")

if __name__ == "__main__":
    main()
```

**Tool 2**: `tools/catalog/validate_bindings.py`

```python
#!/usr/bin/env python3
"""Validate that all promptset bindings reference primary domain locations"""

import sys
import yaml
from pathlib import Path

def main():
    errors = []
    
    for promptset in Path("prompts/active").rglob("*.promptset*"):
        data = yaml.safe_load(promptset.read_text())
        
        for prompt in data.get("prompts", []):
            for binding in prompt.get("bindings", []):
                path = Path(binding)
                
                # Check if binding references primary domain location
                if "by_domain" not in binding:
                    errors.append(
                        f"{promptset.name}: Binding does not reference "
                        f"primary domain location: {binding}"
                    )
                
                # Verify file exists
                if not path.exists():
                    errors.append(
                        f"{promptset.name}: Binding path does not exist: {binding}"
                    )
    
    if errors:
        print("❌ Binding validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ All bindings validated successfully")

if __name__ == "__main__":
    main()
```

---

## 📈 Benefits Analysis

| Benefit | Implementation | Impact |
|---------|----------------|--------|
| **Historical Preservation** | Immutable `historical/` with ISO week organization | High - Precise audit trail |
| **Multi-axis Access** | Hard-copied catalog structure | High - Flexible discovery without symlink issues |
| **Clear Lifecycle** | Staged migration pipeline | Medium - Process clarity |
| **Composition Efficiency** | Normalized catalog + templates | High - Reduces duplication |
| **Human Readability** | Intuitive naming and README | High - Onboarding and maintenance |
| **Machine Parsability** | Consistent metadata and structure | High - Automation-friendly |
| **Version Control** | Separation of concerns, no symlinks | High - Cleaner git diffs, no symlink issues |
| **Temporal Precision** | ISO week dating system | High - Standardized time references |
| **Backup Integrity** | No symlinks, deterministic structure | High - Reliable snapshots (ADR-0015 §4) |
| **Cross-platform Compatibility** | No symlink dependencies | High - Works reliably across Samba/NAS/Windows |

---

## ⚠️ Potential Challenges & Mitigations

### Storage Overhead from Hard Copies
**Challenge**: Multiple copies of same file increase storage usage  
**Mitigation**: 
- Prompts are text files (typically <50KB each)
- Total overhead estimated at <100MB for entire catalog
- Benefits of avoiding symlink issues outweigh storage cost
- CI can detect and remove truly orphaned copies

### Maintaining Copy Consistency
**Challenge**: Keeping tier/persona copies synchronized with primary  
**Mitigation**: 
- Automated `sync_copies.py` tool runs on every update
- CI validates hash consistency before merge
- Pre-commit hooks prevent inconsistent states
- Clear documentation on update workflow

### Learning Curve
**Challenge**: New contributors must understand structure and why no symlinks  
**Mitigation**: 
- Comprehensive README with rationale
- Link to ADR-0015 in navigation guide
- Examples and automation tools reduce manual effort

### Migration Effort
**Challenge**: Requires batch processing and validation  
**Mitigation**: 
- Phased approach with clear acceptance criteria
- Automated tooling for most operations
- Validation scripts catch issues early

---

## 🔐 TOKEN_BLOCK

```yaml
TOKEN_BLOCK:
  accepted:
    - PROMPT_LIBRARY_STRUCTURE_V2
    - NO_SYMLINKS_POLICY
    - HARD_COPY_NAVIGATION
    - PRIMARY_DOMAIN_CANONICAL
    - ISO_WEEK_TEMPORAL_ORGANIZATION
    - ADR_0015_COMPLIANT
    - ADR_0009_COMPLIANT
    - ADR_0013_MERGE_COMPATIBLE
    - HASH_VALIDATED_COPIES
    - AUTOMATED_SYNC_TOOLING
  requires:
    - ADR_SCHEMA_V1
    - ADR_0009_FRONTMATTER
    - ADR_0015_SYMLINK_POLICY
    - DETERMINISTIC_FILE_ORGANIZATION
  produces:
    - NORMALIZED_PROMPT_CATALOG
    - TIER_NAVIGATION_COPIES
    - PERSONA_NAVIGATION_COPIES
    - HISTORICAL_ISO_WEEK_ARCHIVE
    - VALIDATION_REPORTS
  drift:
    - DRIFT: symlink_detected_in_prompts
    - DRIFT: copy_hash_mismatch
    - DRIFT: missing_tier_copy
    - DRIFT: missing_persona_copy
    - DRIFT: binding_not_to_primary
    - DRIFT: adr0009_frontmatter_invalid
    - DRIFT: orphaned_file_detected
    - DRIFT: iso_week_mismatch_in_historical
```

---

**Document Version**: 2.0  
**Last Updated**: 2025-09-25  
**Status**: Ready for Review  
**Compliance**: ADR-0015, ADR-0009, ADR-0013

---

**End of Document**