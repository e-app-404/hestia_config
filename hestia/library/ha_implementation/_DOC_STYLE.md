---
# Document style and canonical frontmatter for hestia/workspace/operations/guides/ha_implementation

This file provides a canonical YAML frontmatter template and a short Markdown style guide for files in this folder. Apply the frontmatter block to the top of every Markdown document in this directory.

## Canonical frontmatter

Place this exact YAML block at the top of each file (adjust values as needed):

---
title: "<Short descriptive title>"
authors: "<Author or organization>"
source: "<Upstream source or notes>"
slug: "<short-slug>"
tags: ["home-assistant", "ops", "integration"]
original_date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
url: "<original upstream URL if any>"
---

Required keys: title, authors, slug, original_date, last_updated. Optional: source, tags, url.

## Minimal Markdown style guide

- File encoding: UTF-8, LF line endings.
- Headings: Use a single top-level H1 per document (# Title). Use H2/H3 for sections (##, ###). Do not use multiple H1s.
- Code blocks: Use fenced code blocks with language tag (```yaml, ```bash, ```json, etc.). Indentations inside code fences must be preserved.
- YAML examples: Wrap sample YAML blocks in ```yaml fences and ensure the snippet is valid YAML.
- Lists: Use `- ` for bullets. Keep single blank line between paragraphs and lists.
- Images and links: Use standard Markdown syntax. Avoid raw HTML unless necessary.
- Emojis and short icons: Allowed, but avoid as-only headings. Keep documentation professional.
- Admonitions: Use blockquotes `> **Note**:` for simple notes. If a richer admonition system is required, keep it consistent across files.

## Linting

Run a markdown linter (remark or markdownlint) before committing. Example commands:

```bash
# npm-based remark
npm install -D remark-cli remark-preset-lint-recommended
npx remark . --frail

# markdownlint (node)
npm install -D markdownlint-cli
npx markdownlint '**/*.md'
```

## Applying frontmatter programmatically

Use a small script or editor macro to insert the canonical frontmatter and update `last_updated`.

---
