---
id: PROMPT-LIB-CONSOLIDATION-V2
title: "Prompt Library Consolidation - Architecture and Implementation"
date: 2025-10-08
status: Implemented
author: "AI Assistant"
related:
  - ADR-0008
  - ADR-0009
  - ADR-0015
  - ADR-0018
supersedes: []
last_updated: 2025-10-08
tags: ["prompts", "library", "consolidation", "governance", "workspace"]
workspace_allocation:
  primary: "/config/hestia/library/prompts"
  tools: "/config/hestia/tools/prompt_prep"
  working: "/config/hestia/workspace/todo"
---

# Prompt Library Consolidation - Architecture and Implementation

## Table of Contents

1. [Current Status](#current-status)
2. [Context](#context)
3. [Decision](#decision)
4. [Implementation Trail](#implementation-trail)
5. [Architecture](#architecture)
6. [Enforcement](#enforcement)
7. [Token Block](#token-block)

## Current Status

**Status**: IMPLEMENTED — Tools created and validated, ready for production execution.

**Canonical Path**: `/config/hestia/library/prompts`

**Compliance**: ADR-0008 (determinism), ADR-0009 (governance), ADR-0015 (no symlinks), ADR-0018 (workspace lifecycle)

---

## Context

### 2025-09-21: Inventory and Normalization Plan Drafted

**Objective**: Pre-prepare step (convert all prompt files to Markdown with YAML frontmatter stub) marked in-progress.

**Files to Process**: 
- Source: `/config/hestia/library/prompts/catalog/prompts_for_ingestion/*`
- File types: `.md`, `.promptset`, `.yaml`, `.csv.md`

**Rationale**: Normalize file types and provide deterministic frontmatter for downstream canonicalization into `*.promptset` YAML.

---

## Pre-Preparation Actions (Next Steps)

### Step 1: Run Deterministic Prep Script (Dry-Run Mode)

**Script Behavior**:
- Read each file in `prompts_for_ingestion`
- Write prepped Markdown file with YAML frontmatter stub containing:
  - `id`
  - `slug`
  - `title`
  - `date`
  - `tier`
  - `domain`
  - `persona`
  - `status`
  - `tags`
  - `version`
  - `source_path`
  - `author`
  - `related`
  - `last_updated`
  - `redaction_log`
- Preserve original files untouched
- Write outputs to `/config/hestia/library/prompts/migration/processed/`

### Step 2: Validate Frontmatter

**Tool**: `/config/tools/prompt_prep/validate_frontmatter.py`

**Purpose**: Verify frontmatter presence and stub completeness across all prepped files.

### Step 3: Manual Review

**Action**: Review sample of 20 prepped files and adjust extraction heuristics as needed.

### Step 4: Catalog Placement

**Tool**: `/config/tools/catalog/place_in_catalog.py`

**Purpose**: Place validated prompts in catalog structure with hard copies for tier and persona navigation.

### Step 5: Validate Copy Consistency

**Tool**: `/config/tools/catalog/validate_copies.py`

**Purpose**: Ensure hash-based consistency between primary canonical files and their navigation copies.

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
- **Canonical path**: `/config/hestia/library/prompts`

**Recommendation**: Hybrid chronological-functional architecture with clear separation of concerns and **zero symlink dependencies** (per ADR-0015).

---

## 🎯 Proposed Directory Structure

```
/config/hestia/library/prompts/
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
│   ├── by_domain/                     # Functional grouping (primary canonical location)
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
   - Extract/infer YAML frontmatter with all required fields
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
author: "Author Name"
related: []
last_updated: 2025-05-02T00:00:00+01:00
redaction_log: []
---
```

**File Organization Strategy**:
- **Primary (canonical)**: `/config/hestia/library/prompts/catalog/by_domain/{domain}/prompt_{id}_{slug}.md`
- **Tier copy**: `/config/hestia/library/prompts/catalog/by_tier/{tier}/prompt_{id}_{slug}.md` (hard copy)
- **Persona copy**: `/config/hestia/library/prompts/catalog/by_persona/{persona}/prompt_{id}_{slug}.md` (hard copy)

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
     - /config/hestia/library/prompts/catalog/by_domain/operational/prompt_20250502_001_cli_tool_audit.md
   ```

---

## 🔄 Migration Workflow Example

### Current State

```
/config/hestia/library/prompts/_archive/batch1/batch1-audit_20250502_001.md
```

### After Normalization

```
/config/hestia/library/prompts/
├── catalog/
│   ├── by_domain/                          # PRIMARY CANONICAL LOCATION
│   │   └── operational/
│   │       └── prompt_20250502_001_cli_tool_audit.md
│   ├── by_tier/                            # HARD COPIES
│   │   └── beta/
│   │       └── prompt_20250502_001_cli_tool_audit.md (copied from by_domain)
│   └── by_persona/                         # HARD COPIES
│       └── icaria/
│           └── prompt_20250502_001_cli_tool_audit.md (copied from by_domain)
│
└── historical/
    └── 2025/
        └── Q2/
            └── isoweek18/
                └── isoweek18-audit_20250502_001.md (unchanged original)
```

### Composed Promptset

```yaml
# /config/hestia/library/prompts/active/diagnostics/hestia_cli_audit.promptset.yaml
promptset:
  id: hestia_cli_audit.v1
  prompts:
    - id: cli_tool_audit
      bindings:
        # Reference primary canonical location only
        - /config/hestia/library/prompts/catalog/by_domain/operational/prompt_20250502_001_cli_tool_audit.md
```

---

## 🎨 Human-Friendly Features

### README.md Navigation Guide

Place at `/config/hestia/library/prompts/README.md`:

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
prompts = glob("/config/hestia/library/prompts/catalog/by_domain/**/prompt_*_*.md")
beta_prompts = [p for p in prompts if get_tier(p) == "β"]

# Find all Strategos prompts (via hard copies for convenience)
strategos = glob("/config/hestia/library/prompts/catalog/by_persona/strategos/*.md")

# Get all governance domain prompts (primary canonical)
governance = glob("/config/hestia/library/prompts/catalog/by_domain/governance/*.md")
```

### Copy Synchronization Automation

**Tool**: `/config/tools/catalog/sync_copies.py`

```python
#!/usr/bin/env python3
"""Maintain by_tier and by_persona as hard copies of by_domain"""

import shutil
from pathlib import Path
from typing import Dict
import yaml

CATALOG_ROOT = Path("/config/hestia/library/prompts/catalog")

def extract_frontmatter(filepath: Path) -> Dict:
    """Extract YAML frontmatter from markdown file"""
    content = filepath.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    return {}

def copy_if_different(src: Path, dest: Path) -> bool:
    """Copy file only if different or missing"""
    if not dest.exists() or src.read_bytes() != dest.read_bytes():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return True
    return False

def sync_catalog_copies():
    """Synchronize tier and persona copies from primary domain files"""
    by_domain = CATALOG_ROOT / "by_domain"
    by_tier = CATALOG_ROOT / "by_tier"
    by_persona = CATALOG_ROOT / "by_persona"
    
    stats = {"updated": 0, "created": 0, "errors": 0}
    
    for primary in by_domain.rglob("*.md"):
        try:
            metadata = extract_frontmatter(primary)
            
            # Generate tier copy
            tier = metadata.get('tier')
            if tier:
                tier_path = by_tier / tier / primary.name
                if copy_if_different(primary, tier_path):
                    stats["updated" if tier_path.exists() else "created"] += 1
            
            # Generate persona copy
            persona = metadata.get('persona')
            if persona:
                persona_path = by_persona / persona / primary.name
                if copy_if_different(primary, persona_path):
                    stats["updated" if persona_path.exists() else "created"] += 1
                    
        except Exception as e:
            print(f"Error processing {primary}: {e}")
            stats["errors"] += 1
    
    print(f"Sync complete: {stats['created']} created, {stats['updated']} updated, {stats['errors']} errors")
    return stats["errors"] == 0

if __name__ == "__main__":
    import sys
    sys.exit(0 if sync_catalog_copies() else 1)
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
5. Implement `/config/tools/catalog/sync_copies.py` utility

**Commands**:
```bash
# Create directory structure
mkdir -p /config/hestia/library/prompts/{migration/{incoming,processed,failed,reports},catalog/{by_domain,by_tier,by_persona},active,development/{drafts,testing,experimental},context/{conversations,seeds,scaffolds},historical/2025/{Q1,Q2,Q3,Q4}}

# Create tooling directories
mkdir -p /config/tools/{prompt_prep,catalog}

# Preserve existing governance
cp -r /config/hestia/library/prompts/_meta /config/hestia/library/prompts/_meta.backup
```

### Phase 2 (Normalization - Gradual)

1. Process batch1-batch4 through conversion
2. Populate `catalog/by_domain/` with normalized files (primary location)
3. Generate hard copies in `by_tier/` and `by_persona/`
4. Validate frontmatter completeness per ADR-0009

**Commands**:
```bash
# Copy current files to migration incoming
cp -r /config/hestia/library/prompts/catalog/* /config/hestia/library/prompts/migration/incoming/

# Run prep script in dry-run mode
python3 /config/tools/prompt_prep/prep_prompts.py \
  --source /config/hestia/library/prompts/migration/incoming \
  --output /config/hestia/library/prompts/migration/processed \
  --dry-run

# Validate frontmatter
python3 /config/tools/prompt_prep/validate_frontmatter.py \
  --prep-dir /config/hestia/library/prompts/migration/processed \
  --report-path /config/hestia/library/prompts/migration/reports/validation_report_$(date +%Y%m%d_%H%M%S).json

# After manual review and approval, run without dry-run
python3 /config/tools/prompt_prep/prep_prompts.py \
  --source /config/hestia/library/prompts/migration/incoming \
  --output /config/hestia/library/prompts/migration/processed

# Place in catalog with hard copies
python3 /config/tools/catalog/place_in_catalog.py \
  --processed-dir /config/hestia/library/prompts/migration/processed \
  --catalog-root /config/hestia/library/prompts/catalog \
  --generate-copies

# Validate copy consistency
python3 /config/tools/catalog/validate_copies.py
```

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

**Commands**:
```bash
# Archive processed batches by ISO week
for batch in /config/hestia/library/prompts/migration/incoming/batch*; do
  ISOWEEK=$(date -r "$batch" +%Gw%V)
  YEAR=$(date -r "$batch" +%Y)
  QUARTER=$(( ($(date -r "$batch" +%-m) - 1) / 3 + 1 ))
  mkdir -p /config/hestia/library/prompts/historical/$YEAR/Q$QUARTER/$ISOWEEK
  mv "$batch" /config/hestia/library/prompts/historical/$YEAR/Q$QUARTER/$ISOWEEK/
done

# Final validation
python3 /config/tools/catalog/validate_copies.py --strict
python3 /config/tools/catalog/validate_bindings.py
```

---

## 📊 Acceptance Criteria

Post-migration validation must confirm:

1. **Structure Compliance**
   - No symlinks exist anywhere in `/config/hestia/library/prompts/` directory tree (ADR-0015 compliance)
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

**Tool**: `/config/hestia/library/prompts/.git/hooks/pre-commit`

```bash
#!/usr/bin/env bash
# Enforce ADR-0015: No symlinks in prompts/ tree
set -euo pipefail

PROMPT_ROOT="/config/hestia/library/prompts"

echo "🔍 Checking for symlinks in prompt library..."
if git ls-files -s "$PROMPT_ROOT" | awk '$1==120000{exit 1}'; then
    echo "✅ No symlinks detected"
else
    echo "❌ ERROR: Symlinks detected in prompt library"
    echo "   This violates ADR-0015. Remove symlinks and use hard copies instead."
    exit 1
fi

echo "🔍 Validating copy consistency..."
python3 /config/tools/catalog/validate_copies.py || {
    echo "❌ ERROR: Copy validation failed"
    echo "   Run: python3 /config/tools/catalog/sync_copies.py"
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
          if git ls-files -s /config/hestia/library/prompts | awk '$1==120000{exit 1}'; then
            echo "✅ No symlinks detected"
          else
            echo "❌ Symlinks found in prompt library - violates ADR-0015"
            exit 1
          fi
      
      - name: Validate frontmatter (ADR-0009)
        run: python3 /config/tools/prompt_prep/validate_frontmatter.py
      
      - name: Validate copy consistency
        run: python3 /config/tools/catalog/validate_copies.py
      
      - name: Validate promptset bindings
        run: python3 /config/tools/catalog/validate_bindings.py
```

### Validation Tools

**Tool 1**: `/config/tools/catalog/validate_copies.py`

```python
#!/usr/bin/env python3
"""Validate that tier/persona copies match primary domain files"""

import hashlib
import sys
from pathlib import Path
import yaml

CATALOG_ROOT = Path("/config/hestia/library/prompts/catalog")

def file_hash(path: Path) -> str:
    """Calculate SHA-256 hash of file"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from markdown file"""
    content = filepath.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    return {}

def main():
    errors = []
    
    for primary in (CATALOG_ROOT / "by_domain").rglob("*.md"):
        try:
            # Extract metadata to find tier and persona
            metadata = extract_frontmatter(primary)
            tier = metadata.get('tier')
            persona = metadata.get('persona')
            
            # Validate tier copy
            if tier:
                tier_copy = CATALOG_ROOT / "by_tier" / tier / primary.name
                if tier_copy.exists():
                    if file_hash(primary) != file_hash(tier_copy):
                        errors.append(f"Hash mismatch: {primary.name} (tier)")
                else:
                    errors.append(f"Missing tier copy: {tier_copy}")
            
            # Validate persona copy
            if persona:
                persona_copy = CATALOG_ROOT / "by_persona" / persona / primary.name
                if persona_copy.exists():
                    if file_hash(primary) != file_hash(persona_copy):
                        errors.append(f"Hash mismatch: {primary.name} (persona)")
                else:
                    errors.append(f"Missing persona copy: {persona_copy}")
                    
        except Exception as e:
            errors.append(f"Error processing {primary.name}: {e}")
    
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

**Tool 2**: `/config/tools/catalog/validate_bindings.py`

```python
#!/usr/bin/env python3
"""Validate that all promptset bindings reference primary domain locations"""

import sys
import yaml
from pathlib import Path

PROMPT_ROOT = Path("/config/hestia/library/prompts")
ACTIVE_DIR = PROMPT_ROOT / "active"

def main():
    errors = []
    
    for promptset in ACTIVE_DIR.rglob("*.promptset*"):
        try:
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
        except Exception as e:
            errors.append(f"Error processing {promptset.name}: {e}")
    
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

**Tool 3**: `/config/tools/catalog/place_in_catalog.py`

```python
#!/usr/bin/env python3
"""Place normalized prompts in catalog structure with hard copies"""

import shutil
import sys
from pathlib import Path
import yaml

def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from markdown file"""
    content = filepath.read_text()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1])
    return {}

def place_prompt(prompt_file: Path, catalog_root: Path, generate_copies: bool = True):
    """Place prompt in catalog with optional hard copies"""
    metadata = extract_frontmatter(prompt_file)
    
    # Validate required metadata
    required_fields = ['domain', 'tier', 'persona']
    missing = [f for f in required_fields if f not in metadata]
```python
    if missing:
        print(f"⚠️  Skipping {prompt_file.name}: missing metadata fields: {missing}")
        return False
    
    # Primary canonical location
    domain = metadata['domain']
    domain_dir = catalog_root / 'by_domain' / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    primary_path = domain_dir / prompt_file.name
    
    # Copy to primary location
    shutil.copy2(prompt_file, primary_path)
    print(f"✅ Placed {prompt_file.name} in by_domain/{domain}/")
    
    if generate_copies:
        # Generate hard copy for tier navigation
        tier = metadata['tier']
        tier_dir = catalog_root / 'by_tier' / tier
        tier_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(primary_path, tier_dir / prompt_file.name)
        print(f"   📋 Created tier copy in by_tier/{tier}/")
        
        # Generate hard copy for persona navigation
        persona = metadata['persona']
        persona_dir = catalog_root / 'by_persona' / persona
        persona_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(primary_path, persona_dir / prompt_file.name)
        print(f"   📋 Created persona copy in by_persona/{persona}/")
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Place normalized prompts in catalog')
    parser.add_argument('--processed-dir', required=True, help='Directory with processed prompts')
    parser.add_argument('--catalog-root', required=True, help='Root of catalog structure')
    parser.add_argument('--generate-copies', action='store_true', help='Generate tier/persona copies')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    processed_dir = Path(args.processed_dir)
    catalog_root = Path(args.catalog_root)
    
    if not processed_dir.exists():
        print(f"❌ Processed directory does not exist: {processed_dir}")
        sys.exit(1)
    
    stats = {'placed': 0, 'skipped': 0, 'errors': 0}
    
    for prompt_file in processed_dir.glob("*.md"):
        try:
            if args.dry_run:
                print(f"[DRY RUN] Would place: {prompt_file.name}")
                stats['placed'] += 1
            else:
                if place_prompt(prompt_file, catalog_root, args.generate_copies):
                    stats['placed'] += 1
                else:
                    stats['skipped'] += 1
        except Exception as e:
            print(f"❌ Error placing {prompt_file.name}: {e}")
            stats['errors'] += 1
    
    print(f"\n📊 Summary: {stats['placed']} placed, {stats['skipped']} skipped, {stats['errors']} errors")
    sys.exit(0 if stats['errors'] == 0 else 1)

if __name__ == "__main__":
    main()
```

**Tool 4**: `/config/tools/prompt_prep/prep_prompts.py`

```python
#!/usr/bin/env python3
"""
Prompt Library Pre-Preparation Script
Converts all prompt files to Markdown with YAML frontmatter stub
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
import hashlib
import sys

class PromptPrepper:
    def __init__(self, source_dir, output_dir, dry_run=True):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.processed_files = []
        
    def _generate_slug(self, title):
        """Generate URL-safe slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _generate_id(self, filepath):
        """Generate deterministic ID from file path"""
        # Try to extract existing ID from filename
        match = re.search(r'prompt_(\d{8}_\d{3})', filepath.name)
        if match:
            return f"prompt_{match.group(1)}"
        
        # Generate fallback ID using hash
        hash_suffix = hashlib.md5(str(filepath).encode()).hexdigest()[:6]
        date_prefix = datetime.now().strftime('%Y%m%d')
        return f"prompt_{date_prefix}_{hash_suffix}"
    
    def _extract_title(self, filename, content):
        """Extract title from filename or first heading"""
        # Try to find first markdown heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Fallback to cleaned filename
        title = filename.stem.replace('_', ' ').replace('-', ' ')
        title = re.sub(r'^(batch\d+-|prompt_\d+_\d+_)', '', title, flags=re.IGNORECASE)
        return title.title()
    
    def _detect_tier(self, content, filename):
        """Detect tier from content patterns"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Look for explicit tier declarations
        tier_match = re.search(r'tier:\s*([αβγδεζημΩ])', content)
        if tier_match:
            return tier_match.group(1)
        
        # Heuristic detection based on keywords
        if any(kw in content_lower for kw in ['governance', 'emergency', 'critical', 'core system']):
            return 'α'
        elif any(kw in content_lower for kw in ['integration', 'operational', 'workflow', 'extraction']):
            return 'β'
        elif any(kw in content_lower for kw in ['instruction', 'guide', 'template', 'documentation']):
            return 'γ'
        
        # Default to beta if uncertain
        return 'β'
    
    def _detect_domain(self, content, filename):
        """Detect domain from content patterns"""
        content_lower = content.lower()
        
        # Domain keyword mapping
        domain_keywords = {
            'governance': ['governance', 'policy', 'adr', 'architecture decision'],
            'extraction': ['extract', 'parse', 'mining', 'data extraction'],
            'operational': ['operational', 'workflow', 'pipeline', 'automation'],
            'validation': ['validation', 'verify', 'check', 'quality assurance'],
            'diagnostic': ['diagnostic', 'debug', 'troubleshoot', 'analyze'],
            'instructional': ['instruction', 'guide', 'tutorial', 'how-to'],
            'emergency': ['emergency', 'critical', 'urgent', 'immediate']
        }
        
        # Score each domain
        scores = {}
        for domain, keywords in domain_keywords.items():
            scores[domain] = sum(1 for kw in keywords if kw in content_lower)
        
        # Return domain with highest score, or 'operational' as default
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'operational'
    
    def _detect_persona(self, content):
        """Detect persona from content patterns"""
        content_lower = content.lower()
        
        personas = {
            'promachos': ['promachos', 'governance', 'meta'],
            'strategos': ['strategos', 'strategy', 'planning'],
            'kybernetes': ['kybernetes', 'pilot', 'navigation'],
            'icaria': ['icaria', 'repair', 'fix'],
            'nomia': ['nomia', 'validation', 'rules'],
            'heurion': ['heurion', 'discovery', 'analysis']
        }
        
        for persona, keywords in personas.items():
            if any(kw in content_lower for kw in keywords):
                return persona
        
        return 'generic'
    
    def _detect_status(self, content):
        """Detect status from content patterns"""
        content_lower = content.lower()
        
        if 'deprecated' in content_lower:
            return 'deprecated'
        elif 'approved' in content_lower or 'active' in content_lower:
            return 'approved'
        elif 'draft' in content_lower or 'proposed' in content_lower:
            return 'candidate'
        
        return 'candidate'
    
    def _extract_author(self, content):
        """Extract author from content"""
        match = re.search(r'author:\s*["\']?([^"\'\n]+)["\']?', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return 'Unknown'
    
    def _extract_tags(self, filename, content):
        """Extract tags from content and filename"""
        tags = []
        
        # Extract from YAML frontmatter if exists
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    if 'tags' in metadata:
                        tags.extend(metadata['tags'])
            except:
                pass
        
        # Extract from filename
        filename_lower = filename.lower()
        tag_keywords = ['diagnostic', 'validation', 'extraction', 'automation', 
                       'governance', 'emergency', 'instructional']
        tags.extend([kw for kw in tag_keywords if kw in filename_lower])
        
        return list(set(tags))  # Remove duplicates
    
    def extract_metadata(self, filepath, content):
        """Extract metadata using heuristics"""
        filename = filepath.name
        
        # Extract title from filename or first heading
        title = self._extract_title(filename, content)
        
        # Generate deterministic ID
        file_id = self._generate_id(filepath)
        
        # Generate slug from title
        slug = self._generate_slug(title)
        
        # Detect tier from content patterns
        tier = self._detect_tier(content, filename)
        
        # Detect domain from content patterns
        domain = self._detect_domain(content, filename)
        
        # Detect persona from content patterns  
        persona = self._detect_persona(content)
        
        # Detect status from content patterns
        status = self._detect_status(content)
        
        # Extract author
        author = self._extract_author(content)
        
        # Extract tags from content and filename
        tags = self._extract_tags(filename, content)
        
        return {
            'id': file_id,
            'slug': slug,
            'title': title,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'tier': tier,
            'domain': domain,
            'persona': persona,
            'status': status,
            'tags': tags,
            'version': '1.0',
            'source_path': str(filepath.relative_to(self.source_dir)),
            'author': author,
            'related': [],
            'last_updated': datetime.now().isoformat(),
            'redaction_log': []
        }
    
    def _create_prepped_content(self, metadata, original_content, filepath):
        """Create prepped markdown with frontmatter"""
        # Remove existing frontmatter if present
        content = original_content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Create new frontmatter
        frontmatter = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        
        return f"---\n{frontmatter}---\n\n{content}\n"
    
    def process_file(self, filepath):
        """Process a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = self.extract_metadata(filepath, content)
            
            # Create output filename (always .md)
            output_name = f"{metadata['id']}_{metadata['slug']}.md"
            output_path = self.output_dir / output_name
            
            # Generate prepped content
            prepped_content = self._create_prepped_content(metadata, content, filepath)
            
            if self.dry_run:
                print(f"[DRY RUN] Would create: {output_name}")
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(prepped_content)
                # Make read-only
                os.chmod(output_path, 0o444)
                print(f"✅ Created: {output_name}")
            
            self.processed_files.append({
                'source': str(filepath),
                'output': str(output_path),
                'metadata': metadata
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            return False
    
    def process_directory(self):
        """Process all files in source directory"""
        stats = {'processed': 0, 'failed': 0}
        
        for filepath in self.source_dir.rglob('*'):
            if filepath.is_file():
                if self.process_file(filepath):
                    stats['processed'] += 1
                else:
                    stats['failed'] += 1
        
        return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare prompts with frontmatter')
    parser.add_argument('--source', required=True, help='Source directory')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    prepper = PromptPrepper(args.source, args.output, args.dry_run)
    stats = prepper.process_directory()
    
    print(f"\n📊 Summary: {stats['processed']} processed, {stats['failed']} failed")
    
    if not args.dry_run:
        print(f"✅ Output written to: {args.output}")
        print("⚠️  Files are read-only until sign-off")

if __name__ == "__main__":
    main()
```

**Tool 5**: `/config/tools/prompt_prep/validate_frontmatter.py`

```python
#!/usr/bin/env python3
"""
Validate YAML frontmatter completeness and consistency
"""

import yaml
import sys
from pathlib import Path
import json

class FrontmatterValidator:
    REQUIRED_FIELDS = [
        'id', 'slug', 'title', 'date', 'tier', 'domain', 
        'persona', 'status', 'tags', 'version', 'source_path', 
        'author', 'related', 'last_updated', 'redaction_log'
    ]
    
    VALID_TIERS = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'μ', 'Ω']
    
    VALID_DOMAINS = [
        'governance', 'extraction', 'operational', 'validation',
        'diagnostic', 'instructional', 'emergency'
    ]
    
    VALID_STATUSES = [
        'draft', 'proposed', 'candidate', 'approved', 'active',
        'deprecated', 'superseded', 'rejected', 'withdrawn'
    ]
    
    def validate_file(self, md_file):
        """Validate a single markdown file"""
        try:
            content = md_file.read_text()
            
            if not content.startswith('---'):
                return {
                    'valid': False,
                    'issues': ['Missing frontmatter delimiter']
                }
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {
                    'valid': False,
                    'issues': ['Malformed frontmatter']
                }
            
            metadata = yaml.safe_load(parts[1])
            issues = []
            
            # Check required fields
            for field in self.REQUIRED_FIELDS:
                if field not in metadata:
                    issues.append(f"Missing required field: {field}")
            
            # Validate tier
            if 'tier' in metadata and metadata['tier'] not in self.VALID_TIERS:
                issues.append(f"Invalid tier: {metadata['tier']}")
            
            # Validate domain
            if 'domain' in metadata and metadata['domain'] not in self.VALID_DOMAINS:
                issues.append(f"Invalid domain: {metadata['domain']}")
            
            # Validate status
            if 'status' in metadata and metadata['status'] not in self.VALID_STATUSES:
                issues.append(f"Invalid status: {metadata['status']}")
            
            # Validate ID format
            if 'id' in metadata:
                import re
                if not re.match(r'^prompt_\d{8}_[\w]+$', metadata['id']):
                    issues.append(f"Invalid ID format: {metadata['id']}")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"Validation error: {str(e)}"]
            }
    
    def validate_directory(self, prep_dir):
        """Validate all prepped files in directory"""
        results = {
            'valid': [],
            'invalid': [],
            'statistics': {
                'total': 0,
                'valid_count': 0,
                'invalid_count': 0,
                'tier_distribution': {},
                'domain_distribution': {},
                'persona_distribution': {}
            }
        }
        
        for md_file in Path(prep_dir).glob('*.md'):
            results['statistics']['total'] += 1
            validation = self.validate_file(md_file)
            
            if validation['valid']:
                results['valid'].append(str(md_file))
                results['statistics']['valid_count'] += 1
                
                # Collect statistics
                metadata = validation.get('metadata', {})
                tier = metadata.get('tier', 'unknown')
                domain = metadata.get('domain', 'unknown')
                persona = metadata.get('persona', 'unknown')
                
                results['statistics']['tier_distribution'][tier] = \
                    results['statistics']['tier_distribution'].get(tier, 0) + 1
                results['statistics']['domain_distribution'][domain] = \
                    results['statistics']['domain_distribution'].get(domain, 0) + 1
                results['statistics']['persona_distribution'][persona] = \
                    results['statistics']['persona_distribution'].get(persona, 0) + 1
            else:
                results['invalid'].append({
                    'file': str(md_file),
                    'issues': validation['issues']
                })
                results['statistics']['invalid_count'] += 1
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate prompt frontmatter')
    parser.add_argument('--prep-dir', required=True, help='Directory with prepped prompts')
    parser.add_argument('--report-path', help='Path for JSON report output')
    
    args = parser.parse_args()
    
    validator = FrontmatterValidator()
    results = validator.validate_directory(args.prep_dir)
    
    # Print summary
    print(f"\n📊 Validation Summary:")
    print(f"   Total files: {results['statistics']['total']}")
    print(f"   ✅ Valid: {results['statistics']['valid_count']}")
    print(f"   ❌ Invalid: {results['statistics']['invalid_count']}")
    
    if results['statistics']['tier_distribution']:
        print(f"\n   Tier Distribution:")
        for tier, count in sorted(results['statistics']['tier_distribution'].items()):
            print(f"      {tier}: {count}")
    
    if results['statistics']['domain_distribution']:
        print(f"\n   Domain Distribution:")
        for domain, count in sorted(results['statistics']['domain_distribution'].items()):
            print(f"      {domain}: {count}")
    
    # Print invalid files
    if results['invalid']:
        print(f"\n❌ Invalid Files:")
        for item in results['invalid']:
            print(f"   {Path(item['file']).name}:")
            for issue in item['issues']:
                print(f"      - {issue}")
    
    # Write JSON report if requested
    if args.report_path:
        report_path = Path(args.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Report written to: {report_path}")
    
    sys.exit(0 if results['statistics']['invalid_count'] == 0 else 1)

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
    - ENHANCED_FRONTMATTER_EXTRACTION
    - CATALOG_PLACEMENT_AUTOMATED
  requires:
    - ADR_SCHEMA_V1
    - ADR_0009_FRONTMATTER
    - ADR_0015_SYMLINK_POLICY
    - DETERMINISTIC_FILE_ORGANIZATION
    - PYTHON3_RUNTIME
    - BASH_5_RUNTIME
  produces:
    - NORMALIZED_PROMPT_CATALOG
    - TIER_NAVIGATION_COPIES
    - PERSONA_NAVIGATION_COPIES
    - HISTORICAL_ISO_WEEK_ARCHIVE
    - VALIDATION_REPORTS
    - MIGRATION_STATISTICS
  drift:
    - DRIFT: symlink_detected_in_prompts
    - DRIFT: copy_hash_mismatch
    - DRIFT: missing_tier_copy
    - DRIFT: missing_persona_copy
    - DRIFT: binding_not_to_primary
    - DRIFT: adr0009_frontmatter_invalid
    - DRIFT: orphaned_file_detected
    - DRIFT: iso_week_mismatch_in_historical
    - DRIFT: missing_required_metadata_field
    - DRIFT: invalid_tier_value
    - DRIFT: invalid_domain_value
    - DRIFT: invalid_status_value
```

---

## Token Block

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
    - ADR_0024_CANONICAL_PATH
    - HASH_VALIDATED_COPIES
    - AUTOMATED_SYNC_TOOLING
    - ENHANCED_FRONTMATTER_EXTRACTION
    - CATALOG_PLACEMENT_AUTOMATED
  requires:
    - ADR_SCHEMA_V1
    - ADR_0009_FRONTMATTER
    - ADR_0015_SYMLINK_POLICY
    - ADR_0024_CANONICAL_CONFIG_PATH
    - DETERMINISTIC_FILE_ORGANIZATION
    - PYTHON3_RUNTIME
    - BASH_5_RUNTIME
  produces:
    - NORMALIZED_PROMPT_CATALOG
    - TIER_NAVIGATION_COPIES
    - PERSONA_NAVIGATION_COPIES
    - HISTORICAL_ISO_WEEK_ARCHIVE
    - VALIDATION_REPORTS
    - MIGRATION_STATISTICS
  drift:
    - DRIFT: symlink_detected_in_prompts
    - DRIFT: copy_hash_mismatch
    - DRIFT: missing_tier_copy
    - DRIFT: missing_persona_copy
    - DRIFT: binding_not_to_primary
    - DRIFT: adr0009_frontmatter_invalid
    - DRIFT: orphaned_file_detected
    - DRIFT: iso_week_mismatch_in_historical
    - DRIFT: missing_required_metadata_field
    - DRIFT: invalid_tier_value
    - DRIFT: invalid_domain_value
    - DRIFT: invalid_status_value
    - DRIFT: non_canonical_tool_path
```

---

**Document Version**: 2.1  
**Last Updated**: 2025-10-08  
**Status**: Implemented  
**Compliance**: ADR-0015, ADR-0009, ADR-0024  
**Canonical Path**: `/config/hestia/library/prompts`