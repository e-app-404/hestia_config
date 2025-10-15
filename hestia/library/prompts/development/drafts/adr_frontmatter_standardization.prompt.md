---
mode: "agent"
model: "Claude Sonnet 4"
tools: ['edit', 'search', 'new', 'runCommands', 'usages', 'problems', 'changes', 'fetch', 'githubRepo', 'todos']
description: "Systematically inspect and standardize YAML frontmatter headers across all ADR files to ensure compliance with ADR-0009 governance requirements and improve automated indexing capabilities"
---

# ADR Frontmatter Standardization Prompt

## Objective

Systematically inspect and standardize YAML frontmatter headers across all ADR files to ensure compliance with ADR-0009 governance requirements and improve automated indexing capabilities.

## Context

Architecture Decision Records (ADRs) in this workspace follow specific governance rules defined in ADR-0009. However, analysis reveals inconsistent frontmatter structure across ADR files, with many missing required fields like `slug`, `decision`, and in some cases `related`/`supersedes` arrays.

## Task Overview

Perform a comprehensive audit and update of all ADR frontmatter headers to ensure:

1. **Mandatory fields** are present and properly formatted
2. **Decision summaries** are extracted and included
3. **Slug generation** follows kebab-case conventions
4. **Schema compliance** with ADR-0009 requirements

## Required Fields Analysis

### Mandatory Fields (per ADR-0009)

1. **`id`** - Format: ADR-XXXX (zero-padded)
2. **`title`** - Full descriptive title
3. **`slug`** - Kebab-case derived from title (NEW REQUIREMENT)
4. **`status`** - Lifecycle status (Draft/Proposed/Accepted/etc.)
5. **`date`** - ISO-8601 creation date
6. **`last_updated`** - ISO-8601 last modification date
7. **`decision`** - Brief summary of the architectural decision (NEW REQUIREMENT)

### Optional Fields (context-dependent)

8. **`related`** - Array of related ADR references (empty array if none)
9. **`supersedes`** - Array of superseded ADR references (empty array if none)

### Existing Optional Fields (preserve if present)

- `author`/`authors` - Creator information
- `tags` - Categorization tags
- `implementation_date` - When decision was implemented
- `rollout` - Rollout configuration
- `ci_policy` - CI enforcement settings

## Implementation Strategy

### Phase 1: Analysis

1. **Scan all ADR files** in `/config/hestia/library/docs/ADR/ADR-*.md`
2. **Parse YAML frontmatter** and identify missing required fields
3. **Extract decision summaries** from document content for `decision` field
4. **Generate slugs** from titles using kebab-case convention

### Phase 2: Field Generation Rules

#### Slug Generation

- Convert title to lowercase kebab-case
- Remove "ADR-XXXX:" prefix
- Replace spaces and special chars with hyphens
- Example: "ADR-0024: Canonical Home Assistant Config Path" → `canonical-home-assistant-config-path`

#### Decision Field Extraction

- Look for "## Decision" or "## 2. Decision" sections
- Extract first 1-2 sentences as summary
- If no explicit decision section, extract from opening paragraphs
- Format as concise, actionable summary (max 200 chars)
- Example: "Keep `/config` as the only writable config mount and block automatic Tailscale host mounts."

#### Related/Supersedes Arrays

- Ensure arrays exist (even if empty: `[]`)
- Validate ADR-XXXX reference format
- Cross-reference with document content mentions

### Phase 3: Implementation

1. **Backup strategy** - Create `.bk` files before modification
2. **Atomic updates** - Update frontmatter while preserving document structure
3. **Validation** - Ensure YAML parsability after changes
4. **Cross-reference integrity** - Validate all ADR-XXXX references

## Current Gap Analysis

Based on analysis, the following ADRs need updates:

**Missing slug field (24 files):**

- ADR-0001 through ADR-0007, ADR-0009, ADR-000x, ADR-0011, ADR-0013 through ADR-0015, ADR-0017, ADR-0018, ADR-0020 through ADR-0023, ADR-0027

**Missing decision field (20 files):**

- ADR-0001 through ADR-0007, ADR-0009, ADR-000x, ADR-0018 through ADR-0024, ADR-0026 through ADR-0028

**Missing related/supersedes arrays (various files):**

- ADR-0017, ADR-0019, ADR-0021, ADR-0023, ADR-0024, ADR-0028

## Tools and Approach

### Recommended VS Code Tools

- `edit` - For frontmatter modifications
- `search` - For pattern matching and content extraction
- `new` - For creating backup files
- `changes` - For validating modifications
- `problems` - For syntax validation
- `runCommands` - For batch operations

### Execution Plan

1. **Create backup** of entire ADR directory
2. **Process each ADR file** systematically:
   - Parse existing frontmatter
   - Generate missing fields
   - Update YAML block
   - Validate syntax
3. **Create ADR-0009 addendum** documenting new mandatory fields
4. **Generate summary report** of all changes made

## Quality Assurance

- Ensure YAML syntax remains valid
- Preserve existing field values and order where possible
- Maintain document formatting and content integrity
- Validate all cross-references remain functional
- Test with ADR indexing tools (`/config/bin/adr-index.py`)

## Success Criteria

1. All ADR files contain the 9 required frontmatter fields
2. All slugs follow consistent kebab-case convention
3. All decision fields provide meaningful architectural summaries
4. YAML frontmatter validates successfully across all files
5. ADR governance index regenerates without errors
6. ADR-0009 addendum documents the new requirements

## Example Target Frontmatter Structure

```yaml
---
id: ADR-0024
title: "Canonical Home Assistant Config Path (Single-Source-of-Truth)"
slug: canonical-home-assistant-config-path
status: Accepted
related:
  - ADR-0016
  - ADR-0022
supersedes:
  - ADR-0016
last_updated: 2025-10-15
date: 2025-10-05
decision: "Keep `/config` as the only writable config mount and block automatic Tailscale host mounts to establish single-source-of-truth for HA configuration."
---
```

## Deliverables

1. **Updated ADR files** with complete frontmatter
2. **ADR-0009 addendum** documenting mandatory field requirements
3. **Change summary report** listing all modifications
4. **Validation confirmation** that all tools work with updated structure

Execute this systematically, ensuring each ADR receives appropriate attention for accurate field generation and maintains the architectural integrity of the decision records.
