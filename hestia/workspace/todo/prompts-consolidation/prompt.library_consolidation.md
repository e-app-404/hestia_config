## Prompt Library Consolidation - TODO and Trail

### Inventory and Normalization

Status: PARKED — pre-preparation step created. Do not proceed with mass changes until reviewed.

Trail:
- 2025-09-21: Inventory and normalization plan drafted. Pre-prepare step (convert all prompt files to Markdown with YAML frontmatter stub) marked in-progress.
- Files to process: `hestia/work/prompt.library/catalog/prompts_for_ingestion/*` (many .md, .promptset, .yaml, and csv.md files).
- Rationale: normalize file types and provide deterministic frontmatter for downstream canonicalization into `*.promptset` YAML.

Pre-Preparation actions (next steps):
1. Run deterministic prep script in dry-run mode that:
	- reads each file in `prompts_for_ingestion` and writes a prepped Markdown file with a YAML frontmatter stub containing: title, id, created, persona, tags, source_path, redaction_log.
	- preserves original files untouched; writes outputs to `hestia/work/prompt.library/canonical/prepped/`.
2. Validate frontmatter presence and stub completeness with `tools/prompt_prep/validate_frontmatter.py`.
3. Manually review sample of 20 prepped files and adjust extraction heuristics.

Notes:
- Do not run normalization over the entire catalog without manual review of samples.
- Keep originals in place; prepped outputs read-only until sign-off.

Contact: evertappels for sign-off before bulk apply.

-- End of trail

### Prompt Library Proposed Directory Structure

## Executive Summary

Based on analysis of:
- Current tree structure (243 files across 26 directories)
- Template specifications (`draft_template.promptset`, `sql_room_db_v1.4.promptset`)
- Stated goal of historical preservation with machine/human accessibility
- Ongoing normalization to Markdown+YAML frontmatter

**Recommendation**: Hybrid chronological-functional architecture with clear separation of concerns.

---

## 🎯 Proposed Directory Structure

```
prompts/
├── README.md                          # Navigation guide and conventions
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
│   ├── by_domain/                     # Functional grouping
│   │   ├── governance/
│   │   ├── extraction/
│   │   ├── operational/
│   │   ├── validation/
│   │   ├── diagnostic/
│   │   ├── instructional/
│   │   └── emergency/
│   ├── by_tier/                       # Greek tier classification
│   │   ├── alpha/                     # α - Core system control
│   │   ├── beta/                      # β - Integration workflows
│   │   ├── gamma/                     # γ - Instructions/guidance
│   │   └── omega/                     # Ω - Meta/universal
│   └── by_persona/                    # Persona-specific collections
│       ├── promachos/
│       ├── strategos/
│       ├── kybernetes/
│       └── [other_personas]/
│
├── historical/                        # Time-series archive (read-only)
│   ├── 2025/
│   │   ├── Q1/
│   │   │   ├── batch1/
│   │   │   └── batch2/
│   │   ├── Q2/
│   │   │   ├── batch3/
│   │   │   ├── batch4/
│   │   │   └── batch5/
│   │   └── Q3/
│   │       └── batch6_mac-import/
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

### 1. **Separation of Concerns**
- **active/**: Production promptsets, organized by function
- **catalog/**: Normalized inventory with multi-axis access (domain/tier/persona)
- **historical/**: Immutable time-series archive
- **development/**: Experimental work isolated from production

### 2. **Multiple Access Patterns**
The `catalog/` directory enables three complementary navigation strategies:
- **by_domain/**: "Show me all extraction prompts"
- **by_tier/**: "What are our α-tier governance protocols?"
- **by_persona/**: "What tools does Strategos use?"

### 3. **Temporal Preservation**
- `historical/` maintains quarterly snapshots with batch integrity
- Original file names preserved with batch prefixes intact
- Conversion from historical → catalog creates normalized copies, never moves originals

### 4. **Clear Lifecycle Stages**
```
incoming → migration/incoming
         ↓
normalize → migration/processed (MD + YAML frontmatter)
         ↓
catalog → catalog/by_domain/, by_tier/, by_persona/
         ↓
curate → active/ (production promptsets)
         ↓
archive → historical/YYYY/QX/ (immutable)
```

---

## 📋 Implementation Guidelines

### Phase 1: Structural Migration
1. Create new directory structure (non-destructive)
2. **Preserve** existing `_archive/` and `_meta/` as-is
3. Symlink or copy current `catalog/` contents to appropriate locations
4. Establish migration staging areas

### Phase 2: Normalization Pipeline
1. Process existing batches through conversion:
   - Extract/infer YAML frontmatter
   - Standardize to Markdown body format
   - Assign canonical IDs and metadata
2. Place results in `catalog/by_domain/` (primary location)
3. Create cross-reference symlinks in `by_tier/` and `by_persona/`

### Phase 3: Cataloging Rules
For each normalized prompt in `catalog/`:
- **Filename convention**: `{id}_{slug}.md`
  - Example: `prompt_20250502_003_meta_analysis.md`
- **Frontmatter must include**:
  ```yaml
  id: prompt_20250502_003
  slug: meta_analysis
  tier: α|β|γ|δ|ε|ζ|η|Ω
  domain: [governance|extraction|operational|validation|diagnostic|instructional|emergency]
  persona: [promachos|strategos|kybernetes|etc]
  status: [active|candidate|approved|deprecated]
  tags: [comma, separated, list]
  date: 2025-05-02
  version: "1.0"
  ```
- **Cross-reference via symlinks**:
  - Primary: `catalog/by_domain/governance/prompt_20250502_003_meta_analysis.md`
  - Tier link: `catalog/by_tier/alpha/prompt_20250502_003_meta_analysis.md` → `../../by_domain/...`
  - Persona link: `catalog/by_persona/promachos/prompt_20250502_003_meta_analysis.md` → `../../by_domain/...`

### Phase 4: Promptset Composition
When generating `*.promptset` files:
1. Source from `catalog/` normalized prompts
2. Compose according to `draft_template.promptset` schema
3. Place result in `active/{category}/`
4. Reference catalog entries via relative paths in bindings

---

## 🔄 Migration Workflow Example

**Current State**:

`_archive/batch1/batch1-audit_20250502_001.md`

**After Normalization**:
```
catalog/
├── by_domain/
│   └── operational/
│       └── prompt_20250502_001_cli_tool_audit.md
├── by_tier/
│   └── beta/
│       └── prompt_20250502_001_cli_tool_audit.md → ../../by_domain/operational/...
└── by_persona/
    └── icaria/
        └── prompt_20250502_001_cli_tool_audit.md → ../../by_domain/operational/...

historical/
└── 2025/
    └── Q2/
        └── batch1/
            └── batch1-audit_20250502_001.md (unchanged)
```

**Composed Promptset**:
```yaml
# active/diagnostics/hestia_cli_audit.promptset.yaml
promptset:
  id: hestia_cli_audit.v1
  prompts:
    - id: cli_tool_audit
      bindings:
        - ../../catalog/by_domain/operational/prompt_20250502_001_cli_tool_audit.md
```

---

## 🎨 Human-Friendly Features

### README.md Navigation Guide
Place at `prompts/README.md`:
```markdown
# HESTIA Prompts Directory

## Quick Navigation
- **Need a production promptset?** → `active/{category}/`
- **Looking for a specific prompt?** → `catalog/by_domain/` or use search
- **Want to see historical evolution?** → `historical/YYYY/QX/`
- **Working on new prompts?** → `development/drafts/`

## Directory Purposes
- `active/`: Curated, production-ready promptsets
- `catalog/`: Normalized prompt inventory (searchable)
- `historical/`: Time-series archive (read-only)
- `development/`: Experimental work-in-progress
- `context/`: Supporting materials and seeds
- `migration/`: Normalization pipeline staging
- `_meta/`: Registry governance and schemas
```

### Visual Indicators
Use consistent naming conventions:
- **Production**: `{name}.promptset.yaml` or `{name}.promptset`
- **Normalized**: `prompt_{YYYYMMDD}_{NNN}_{slug}.md`
- **Historical**: `isoweek{N}-{original_name}.{ext}`
- **Draft**: `draft_{name}.promptset`

---

## 🤖 Machine-Friendly Features

### Metadata Extraction
Every normalized file in `catalog/` has:
1. Deterministic filename pattern (parseable)
2. YAML frontmatter (JSON-serializable)
3. Consistent directory structure (predictable paths)

### Automated Discovery
Tools can traverse:
```python
# Find all β-tier prompts
prompts = glob("catalog/by_tier/beta/*.md")

# Find all Strategos prompts
strategos = glob("catalog/by_persona/strategos/*.md")

# Get all governance domain prompts
governance = glob("catalog/by_domain/governance/*.md")
```

### Version Control Compatibility
- Historical batches are immutable (safe for git history)
- Catalog entries are canonical (single source of truth)
- Active promptsets reference catalog (clear dependencies)

---

## 🚀 Migration Priority Recommendations

### Phase 1 (Immediate - Non-disruptive)
1. Create new directory structure alongside existing
2. Copy `_meta/` to preserve governance
3. Create `README.md` navigation guide

### Phase 2 (Normalization - Gradual)
1. Process batch1-batch4 through conversion
2. Populate `catalog/by_domain/` with normalized files
3. Create cross-reference symlinks

### Phase 3 (Active Curation - Selective)
1. Identify production-ready prompts
2. Compose promptsets in `active/`
3. Document composition patterns

### Phase 4 (Historical Archive - Final)
1. Move processed batches to `historical/`
2. Validate all links and references
3. Deprecate `_archive/` gracefully

---
