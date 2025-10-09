---
id: prompt_template_example
slug: example-prompt-template
title: "Example Prompt Template"
date: 2025-10-08
tier: β
domain: instructional
persona: kybernetes
status: candidate
tags: [template, example, documentation]
version: "1.0"
source_path: "templates/example_template.md"
author: "HESTIA System"
related: []
last_updated: 2025-10-08T00:00:00+01:00
redaction_log: []
---

# Example Prompt Template

This is an example of a properly normalized prompt file with ADR-0009 compliant YAML frontmatter.

## Purpose

Demonstrate the standard structure and metadata format for all prompts in the HESTIA library.

## Required Elements

### YAML Frontmatter
- All 15 required fields per ADR-0009
- Proper tier, domain, and persona classification
- ISO 8601 timestamp format
- Semantic tags for discovery

### Content Structure
- Clear title and purpose
- Structured sections
- Actionable content
- Proper markdown formatting

## Usage

This template can be copied and modified for new prompt development in the `development/drafts/` directory before normalization.

## Compliance Notes

- ✅ ADR-0009: Complete YAML frontmatter
- ✅ ADR-0015: No symlink dependencies
- ✅ PROMPT-LIB-CONSOLIDATION-V2: Content-based slug generation