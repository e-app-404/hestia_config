---
mode: "agent"
model: "Claude Sonnet 4"
description: "Standardize Home Assistant implementation documentation to _DOC_STYLE.md guidelines for machine-parseable structure"
tools: ["edit", "search", "runCommands", "problems"]
---

# Standardize HA Implementation Documentation

Format and restructure Home Assistant implementation documentation files to comply with `/config/hestia/library/ha_implementation/_DOC_STYLE.md` guidelines, ensuring machine-parseable structure optimized for LLM consumption and code extraction.

## Mission

Transform documentation files in `/config/hestia/library/ha_implementation/` to:

1. **Apply canonical YAML frontmatter** with required and optional metadata fields
2. **Restructure content hierarchy** with proper H1/H2/H3 heading organization
3. **Standardize code block formatting** with proper language fencing for YAML, JSON, bash
4. **Generate table of contents** for navigation and machine parsing
5. **Optimize for code extraction** enabling LLMs to reliably extract YAML configurations

## Scope & Preconditions

- **Target Directory**: `/config/hestia/library/ha_implementation/` and subdirectories
- **File Types**: Markdown files (\*.md) containing Home Assistant configuration examples
- **Reference Standard**: `_DOC_STYLE.md` canonical formatting guidelines
- **Optimization Goal**: Machine-parseable structure for automated code extraction
- **Preservation**: Maintain all technical content while improving structure

## Inputs

- **Target File**: `${input:target_file:${file}}` - Documentation file to standardize
- **Update Timestamp**: `${input:update_date:2025-10-16}` - Last updated date for frontmatter
- **Author Override**: `${input:author:}` - Optional author override (leave blank to preserve existing)
- **Add TOC**: `${input:add_toc:true}` - Generate table of contents (true/false)

## Workflow

### 1. Pre-Analysis Phase

- **Read target file** and analyze current structure
- **Check existing frontmatter** for preservation of key metadata
- **Identify code blocks** requiring language-specific fencing
- **Map content hierarchy** to determine H2/H3 section organization
- **Validate compliance** against \_DOC_STYLE.md requirements

### 2. Frontmatter Standardization

Apply canonical YAML frontmatter block:

```yaml
---
title: "<descriptive title from content>"
authors: "<preserve existing or extract from content>"
source: "<upstream source if applicable>"
slug: "<kebab-case-slug>"
tags: ["home-assistant", "configuration", "<domain-specific>"]
original_date: "<preserve existing or estimate>"
last_updated: "${update_date}"
url: "<original upstream URL if any>"
---
```

**Required fields**: title, authors, slug, original_date, last_updated
**Optional fields**: source, tags, url (preserve if present)

### 3. Content Structure Analysis

- **Identify single H1** (document title) - create if missing
- **Map H2 sections** for major topics (Usage, Configuration, Examples)
- **Organize H3 subsections** under appropriate H2 parents
- **Locate code examples** requiring proper fencing
- **Find inline code** needing backtick formatting

### 4. Table of Contents Generation

If `add_toc=true`, generate structured TOC:

```markdown
## Table of Contents

- [Usage](#usage)
  - [Basic Configuration](#basic-configuration)
  - [Advanced Options](#advanced-options)
- [Examples](#examples)
  - [Simple Example](#simple-example)
  - [Complex Configuration](#complex-configuration)
- [Reference](#reference)
```

### 5. Code Block Standardization

Transform all code examples to properly fenced blocks:

**YAML Examples**:

```yaml
# Properly fenced YAML with syntax highlighting
type: custom:auto-entities
card:
  type: entities
filter:
  include:
    - domain: light
```

**JSON Examples**:

```json
{
  "entity_id": "light.bedroom",
  "state": "on"
}
```

**Bash Commands**:

```bash
# Command examples with proper shell highlighting
ha core check
```

### 6. Content Hierarchy Optimization

- **Single H1**: Document title matching frontmatter
- **H2 Sections**: Major functional areas (Usage, Configuration, Examples, Reference)
- **H3 Subsections**: Specific features or examples under H2 parents
- **No H4+**: Keep hierarchy flat for machine parsing
- **Consistent formatting**: Standard spacing and structure

### 7. Machine-Parsing Optimization

- **Code extraction markers**: Ensure YAML blocks are cleanly separated
- **Section identifiers**: Clear H2/H3 anchors for content navigation
- **Consistent terminology**: Standardize technical terms across sections
- **Example grouping**: Cluster related configuration examples
- **Reference linking**: Maintain internal document links

## Output Expectations

### Success Criteria

- **Valid frontmatter**: All required fields present with accurate metadata
- **Single H1**: Document title properly formatted
- **Structured hierarchy**: Clear H2/H3 organization without gaps
- **Fenced code blocks**: All YAML/JSON/bash properly tagged
- **Table of contents**: Generated and linked (if requested)
- **Machine-readable**: LLMs can reliably extract code examples

### Content Structure

```markdown
---
# Canonical frontmatter block
---

# Document Title

## Table of Contents

<!-- Generated TOC if requested -->

## Usage

<!-- Primary usage information -->

### Basic Configuration

<!-- Simple examples -->

### Advanced Options

<!-- Complex configurations -->

## Examples

<!-- Practical implementation examples -->

### Example Name

<!-- Specific use case with fenced code -->

## Reference

<!-- API documentation, links, additional resources -->
```

### Quality Validation

- [ ] Frontmatter contains all required fields
- [ ] Single H1 heading matches document title
- [ ] H2/H3 hierarchy is logical and complete
- [ ] All code blocks are properly fenced with language tags
- [ ] YAML examples are syntactically valid
- [ ] Table of contents links correctly to sections
- [ ] No raw HTML unless absolutely necessary
- [ ] Consistent spacing and formatting throughout

## Error Handling

### Common Issues

- **Missing frontmatter**: Add canonical block with estimated metadata
- **Multiple H1s**: Convert extras to H2/H3 as appropriate
- **Unfenced code**: Identify language and apply proper fencing
- **Broken hierarchy**: Reorganize sections into logical H2/H3 structure
- **Invalid YAML**: Fix syntax errors in configuration examples

### Validation Steps

- **YAML syntax check**: Validate all fenced YAML blocks
- **Link verification**: Ensure internal links resolve correctly
- **Frontmatter validation**: Confirm all required fields present
- **Hierarchy check**: Verify logical H1→H2→H3 progression

## Safety Guardrails

- **Content preservation**: Maintain all technical information and examples
- **Metadata retention**: Preserve existing author and date information when available
- **Link integrity**: Maintain all external and internal references
- **Example accuracy**: Ensure code examples remain functionally correct
- **Backup consideration**: Recommend creating backup before major restructuring

## Integration Points

- **\_DOC_STYLE.md**: Primary reference for formatting standards
- **Home Assistant docs**: Maintain compatibility with HA documentation patterns
- **Machine parsing**: Optimize structure for automated code extraction
- **Cross-references**: Preserve links to related implementation files
- **Version control**: Structure changes for clear diff review

## Usage Examples

### Basic Usage

Run on current file:

```
/standardize-ha-docs
```

### With Parameters

Specify custom options:

```
/standardize-ha-docs: target_file=/config/hestia/library/ha_implementation/lovelace/auto_entities.card.md, add_toc=true, update_date=2025-10-16
```

### Batch Processing

Process multiple files in sequence by running the prompt for each target file in the implementation library.

## Related Resources

- **Style Guide**: `/config/hestia/library/ha_implementation/_DOC_STYLE.md`
- **Target Directory**: `/config/hestia/library/ha_implementation/`
- **YAML Validation**: Home Assistant configuration checker
- **Markdown Linting**: remark-cli or markdownlint for syntax validation
