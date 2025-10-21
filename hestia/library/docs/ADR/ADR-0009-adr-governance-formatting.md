---
id: ADR-0009
title: ADR Governance, Redaction, and Formatting Policy
slug: adr-governance-redaction-formatting-policy
status: Accepted
related:
- ADR-0001
- ADR-0004
- ADR-0008
- ADR-0017
- ADR-0018
supersedes: []
last_updated: '2025-10-15'
date: 2025-09-13
decision: All ADRs must comply with standardized structure, formatting, and machine-parseability
  requirements including mandatory frontmatter fields, token blocks, and redaction
  procedures.
author: "e-app-404"
tags:
- governance
- formatting
- redaction
- tokens
- automation
- adr
- policy
- metadata
rollout:
  include_scan:
    phase_A:
      mode: report
      start: '2025-09-25T00:00:00+01:00'
      end: '2025-09-27T00:00:00+01:00'
    phase_B:
      mode: fail
      start: '2025-09-27T00:00:01+01:00'
ci_policy:
  include_scan:
    mode: fail
    start: '2025-09-27T00:00:01+01:00'
  packaging:
    deterministic: true
    manifest: sha256
---

## ADR-0009: ADR Governance, Redaction, and Formatting Policy

## Table of Contents

1. Context
2. Decision
3. Lifecycle & Status Model
4. Identification, Slugs, and Filenames
5. Required Front-Matter (Schema v1)
6. Redaction & Supersession
7. Definition & Generation Rules
8. Machine-Parseable Blocks
9. Enforcement
10. Token Block

## 1. Context

The project requires robust, machine-friendly governance for ADRs, including clear rules for redaction, definition, generation, and formatting. This ensures consistency, auditability, and automation for all architectural decisions.

## 2. Decision

- All ADRs must comply with standardized structure, formatting, and machine-parseability requirements.
- Redaction, definition, and generation of ADRs must follow explicit, documented procedures.
- Token blocks and machine-parseable markers are mandatory for governance automation.

## 3. Lifecycle & Status Model

**Allowed `status` values (canonical):**

- `Draft` → `Proposed` → `Accepted` → (`Amended`)\* → `Deprecated` → `Superseded`
- Terminal: `Rejected`, `Withdrawn`
- _`Amended` applies to Accepted ADRs when a follow-up ADR narrows/clarifies scope without replacing it._

**Rules**

- Only `Draft` and `Proposed` may change text substantially without a superseding ADR.
- Moving from `Accepted` requires either `Amended`, `Deprecated`, or `Superseded` with links.
- `Approved` (legacy) is treated as an alias of `Accepted` in automation but SHOULD NOT be used.

**Maintenance fields**

- `last_updated` (ISO-8601) MUST change on any edit.
- Optional: `last_reviewed` (ISO-8601) for periodic audits; ADRs older than 365 days SHOULD be reviewed.

## 4. Identification, Slugs, and Filenames

- **ID format**: `ADR-XXXX` (zero-padded, monotonically increasing).
- **Title format**: "ADR-XXXX: Short, Imperative Summary".
- **Slug**: derived from the short summary, kebab-case, ASCII only.
- **Filename**: `docs/ADR/ADR-XXXX-<slug>.md` (enforced by tooling).
- **Cross-links**: any ID in `related`, `supersedes`, or body MUST match `ADR-\d{4}`.

## 5. Required Front-Matter (Schema v1)

**Required** keys: `id`, `title`, `slug`, `status`, `related`, `supersedes`, `last_updated`, `date`, `decision`

**Optional** keys (recommended): `author`, `tags`, `implementation_date`, `rollout`, `ci_policy`

**Field Specifications:**

- `id`: Format ADR-XXXX (zero-padded, monotonically increasing)
- `title`: Full descriptive title including ADR-XXXX prefix
- `slug`: Kebab-case derived from title summary (exclude ADR-XXXX prefix)
- `status`: Canonical lifecycle value (Draft/Proposed/Accepted/etc.)
- `related`: Array of related ADR-XXXX references (empty array if none)
- `supersedes`: Array of superseded ADR-XXXX references (empty array if none)
- `last_updated`: ISO-8601 date, MUST change on any edit
- `date`: ISO-8601 creation/original decision date
- `decision`: Brief summary of architectural decision (max 200 chars)

**Constraints**

**YAML Formatting Rules**

- Indentation: Use spaces only (no tabs) for all YAML front-matter. Indent lists with two spaces per level.
- Key Order: Required keys MUST appear in the following order:

  1. `id`
  2. `title`
  3. `slug`
  4. `status`
  5. `related`
  6. `supersedes`
  7. `last_updated`
  8. `date`
  9. `decision`

- New ADRs must use the canonical template, including YAML front-matter and section headers.
- ADR numbers are assigned sequentially and referenced in the index.
- ADRs must be generated with clear context, decision rationale, consequences, and enforcement details.

## 6. Formatting Standards

- Use Markdown for all ADRs.
- Start with a YAML front-matter block containing title, date, status, author, related, supersedes, last_updated.
- Use clear section headers (`##`) for Context, Decision, Consequences, Enforcement, etc.
- Include a Table of Contents for ADRs longer than one page.
- All code, token, and marker blocks must be fenced with triple backticks and specify the language (`yaml` or `json`).

## 7. Machine-Parseable Blocks

- Every ADR that defines tokens, drift codes, or governance signals must include a fenced `TOKEN_BLOCK:` YAML code block at the end.
- CRTP markers, whitelists, and other governance signals must use fenced YAML/JSON blocks labeled with the marker type.
- Example:
  **TOKEN_BLOCK schema (v1)**
  - `accepted` (list of UPPER_SNAKE tokens)
  - `produces` (optional list)
  - `requires` (optional list)
  - `drift` (list of `DRIFT: <kebab>` codes)

## 8. Enforcement

- Git hooks and CI must validate ADR structure, formatting, and presence of machine-parseable blocks.
- ADR index automation should extract metadata and token blocks for governance and reporting.
- Non-compliant ADRs are flagged and must be corrected before merge.

## 9. Token Block

```yaml
TOKEN_BLOCK:
  accepted:
    - ADR_FORMAT_OK
    - ADR_REDACTION_OK
    - ADR_GENERATION_OK
    - TOKEN_BLOCK_OK
  requires:
    - ADR_SCHEMA_V1
  drift:
    - DRIFT: adr_format_invalid
    - DRIFT: missing_token_block
    - DRIFT: adr_redaction_untracked
```
