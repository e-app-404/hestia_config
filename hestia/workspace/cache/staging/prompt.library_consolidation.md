## Prompt Library Consolidation - TODO and Trail

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

