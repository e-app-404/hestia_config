# Migration Pipeline

Normalization workflow staging area for prompt library consolidation.

## Directory Structure

- `incoming/`: Files awaiting processing
- `processed/`: Successfully normalized prompts with YAML frontmatter
- `failed/`: Files requiring manual intervention
- `reports/`: Conversion statistics and validation logs

## Workflow Stages

### 1. Incoming Stage (`incoming/`)
- **Purpose**: Stage files for normalization
- **Sources**: Current catalog, batches, manual uploads
- **Format**: Mixed (`.md`, `.promptset`, `.yaml`, `.csv.md`)

### 2. Processing
- **Tool**: `/config/hestia/tools/prompt_prep/prep_prompts.py`
- **Action**: Extract metadata, generate YAML frontmatter, create content-based slugs
- **Output**: Normalized `.md` files with ADR-0009 compliant frontmatter

### 3. Processed Stage (`processed/`)
- **Purpose**: Hold successfully normalized files
- **Format**: Markdown with YAML frontmatter
- **Status**: Ready for catalog placement

### 4. Failed Stage (`failed/`)
- **Purpose**: Hold files requiring manual intervention
- **Causes**: Missing metadata, parsing errors, validation failures
- **Action**: Manual review and correction required

### 5. Reporting (`reports/`)
- **Purpose**: Track processing statistics and validation results
- **Format**: JSON reports with timestamps
- **Contents**: Success/failure counts, metadata extraction results, validation status

## File Naming Conventions

### Incoming
- Original names preserved: `{original_name}.{ext}`

### Processed  
- Normalized names: `prompt_{YYYYMMDD}_{HASH}_{slug}.md`
- Example: `prompt_20251008_e61d30_valetudo-optimization.md`

### Failed
- Original names with suffix: `{original_name}.failed.{ext}`

### Reports
- Timestamped: `{operation}_report_{YYYYMMDD_HHMMSS}.json`

## Processing Commands

### Dry Run (Recommended First)
```bash
python3 /config/hestia/tools/prompt_prep/prep_prompts.py \
  --source /config/hestia/library/prompts/migration/incoming \
  --output /config/hestia/library/prompts/migration/processed \
  --dry-run
```

### Full Processing
```bash
python3 /config/hestia/tools/prompt_prep/prep_prompts.py \
  --source /config/hestia/library/prompts/migration/incoming \
  --output /config/hestia/library/prompts/migration/processed
```

### Validation
```bash
python3 /config/hestia/tools/prompt_prep/validate_frontmatter.py \
  --prep-dir /config/hestia/library/prompts/migration/processed \
  --report-path /config/hestia/library/prompts/migration/reports/validation_report_$(date +%Y%m%d_%H%M%S).json
```

## Quality Gates

Before catalog placement:
- [ ] YAML frontmatter validation passes
- [ ] All required metadata fields present
- [ ] Content-based slug generation successful
- [ ] No processing errors in reports
- [ ] Manual review of sample (20 files minimum)

## Tools Integration

- **prep_prompts.py**: Content-based normalization with intelligent metadata extraction
- **validate_frontmatter.py**: ADR-0009 compliance verification
- **place_in_catalog.py**: Catalog placement with hard copy generation