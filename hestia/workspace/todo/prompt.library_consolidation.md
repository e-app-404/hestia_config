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

### Proposed Directory Structure

Rationale: based on analysis of:

- Current tree structure (243 files across 26 directories)
- Template specifications (draft_template.promptset, sql_room_db_v1.4.promptset)
Stated goal of historical preservation with machine/human accessibility
Ongoing normalization to Markdown+YAML frontmatter


Recommendation: Hybrid chronological-functional architecture with clear separation of concerns.

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

