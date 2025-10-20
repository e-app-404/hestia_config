---
id: ADR-0008
title: Syntax-Aware Normalization & Determinism Rules for Config Artifacts
slug: syntax-aware-normalization-determinism-rules-for-config-artifacts
status: Accepted
related:
- ADR-0013
supersedes:
- ADR-0001
last_updated: '2025-10-15'
date: 2025-09-12
decision: 'Adopt a **syntax-aware** normalization profile and a **deterministic packaging**
  process that together guarantee: 1) Byte-stable outputs for identical inputs, 2)
  Minimal diffs (whitespace and ordering normalized), 3) A single canonical SHA256
  for each release.'
author:
- Evert Appels
tags:
- architecture
- adr
- normalization
- determinism
- yaml
- json
- ini
- xml
- csv
- packaging
---

# ADR-0008: Syntax-Aware Normalization & Determinism Rules for Config Artifacts

## Context:

Network + switch configurations (YAML/JSON/INI/XML/CSV) must be _drop-in_, diff-friendly, and reproducible across runs. Past issues included mixed formatting, stray BOMs, unstable key ordering, and non-deterministic release tarballs.

## Decision

Adopt a **syntax-aware** normalization profile and a **deterministic packaging** process that together guarantee:

1. Byte-stable outputs for identical inputs,
2. Minimal diffs (whitespace and ordering normalized),
3. A single canonical SHA256 for each release.

## Scope

Applies to all generated or merged artifacts under `/out/**`, including:

- `merged/config/hestia/core/**` (YAML, INI where applicable),
- `merged/switch/**` (XML, CSV, INI-style),
- `REPORT.md`, `CHANGELOG.md`, `manifest.sha256`,
- Relationship graph (`.json`) and notes (`.md`).

## Normalization Rules (by format)

### Common (all text files)

- **Encoding:** UTF-8
- **Line endings:** `LF`
- **Trailing newline:** exactly one at EOF
- **Indentation:** 2 spaces (tabs forbidden)
- **Trim:** no trailing spaces; remove redundant blank lines (>1)
- **Comments:** preserved; deduplicate identical consecutive comment lines
- **Secrets:** preserved verbatim unless explicitly instructed to redact

### YAML (`.yaml`, `.yml`)

- `key: value` (colon + one space)
- **Maps:** sort keys A→Z at each object level
- **Lists:** block style (`- item`), one per line
- **Anchors/aliases:** allowed; keep anchor names stable
- **Booleans:** `true`/`false` (lowercase); null as `null`
- **Numbers:** no leading `+`; preserve integers vs floats
- **Dates:** ISO-8601 strings only (no implicit datetime types)

### JSON (`.json`)

- Minified? **No** — pretty print with 2-space indent
- Sort object keys A→Z recursively
- No trailing commas
- Numbers and booleans per RFC 8259; `null` for empty

### INI (e.g., `smb.conf`)

- Section headers `[section]`
- Keys as `key = value` (exactly one space around `=`)
- Empty values allowed; no duplicate keys per section (last-writer wins)
- Preserve comment leaders `#` and `;` as found

### XML (e.g., Netgear backups)

- Canonicalize attribute order A→Z
- Remove volatile nodes/attrs (timestamps, session IDs)
- Collapse insignificant whitespace
- Booleans as `true`/`false`
- XML declaration present (`<?xml version="1.0" encoding="UTF-8"?>`)

### CSV (e.g., `ports.csv`)

- Header row required
- Delimiter `,` (comma), no BOM
- Quote fields only when needed
- Newline at EOF, no trailing delimiter on lines

## Deterministic Packaging

### Canonical file ordering

- Directory traversal sorted A→Z
- Within a directory, list files A→Z; case-sensitive

### Reproducible tarball

- Command template:

```
export TZ=UTC
tar --sort=name
--mtime='UTC 2025-09-12 00:00:00'
--owner=0 --group=0 --numeric-owner
-czf /out/<name>.tar.gz
-C /out merged REPORT.md CHANGELOG.md manifest.sha256 adr graph notes switch
```

- Record the **single** resulting SHA256 in `REPORT.md` and `CHANGELOG.md` headers.

### Property-hash (content determinism proof)

- Compute SHA256 of a **canonical concatenation**:
- Sorted list of file paths, each followed by `\n`
- For each file (same order): path `\0` + file bytes
- Publish as `Determinism-Property-Hash:` in `REPORT.md`.

## Validation Gates

- No BOMs; all files end with LF + single newline
- YAML/JSON keys sorted; INI uses `key = value`
- XML canonicalized; CSV header present and rows uniform
- `manifest.sha256` covers every file in the release
- Tarball is reproducible (sha256 stable across rebuilds)

## Tooling Notes

- Sorting/normalization must be implemented within our merge pipeline (static, no external calls).
- Date/mtime must be **locked** to the release epoch for reproducibility.

## Consequences

- Cleaner diffs, easier reviews, reliable rollbacks.
- Slightly higher CPU during sort/pretty-print stages (acceptable).

## Rollback

- If normalization introduces breakage, revert to prior tarball (keep last 3 releases) and file a fix-forward patch; inputs remain untouched.

## Acceptance Criteria

- All gates pass; property-hash produced
- Tarball SHA256 stable across two consecutive builds with identical inputs
- `manifest.sha256` verifies 100%

TOKEN_BLOCK:
signals: - TOKEN_BLOCK_OK
