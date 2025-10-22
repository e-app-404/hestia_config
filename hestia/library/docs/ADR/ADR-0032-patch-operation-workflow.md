---
id: ADR-0032
title: Patch Operation Workflow (Todos, Staging, Patches, Plans, Ledger)
slug: patch-operations-workflow
date: 2025-10-21
authors:
  - copilot-gpt-5
  - e-app-404
decision: Reduce ambiguity around patch request lifecycle and storage locations by formalizing the workflow and directory structure.
status: Accepted
references:
  - ADR-0009-adr-governance-formatting
  - ADR-0018-normalization-and-determinism-rules
  - ADR-0024-canonical-config-path
  - ADR-0027-file-writing-governance
ledger: hestia/workspace/operations/logs/patch-ledger.jsonl
last_updated: 2025-10-22
related:
  - ADR-0009
  - ADR-0018
  - ADR-0024
  - ADR-0027
supersedes: []
---

## ADR-0032 — Patch Operation Workflow (Todos, Staging, Patches, Plans, Ledger)

## Context

To reduce ambiguity around where patch requests and artifacts live, we are formalizing the patch operation workflow and directory structure used by humans and AI agents. This ADR clarifies the lifecycle from request → staging → plan → merge, the canonical storage locations, and the required logging/ledger behavior.

## Table of Contents

- [Context](#context)
- [Table of Contents](#table-of-contents)
- [Considerations](#considerations)
- [Decision](#decision)
    - [1) Patch Requests (tickets)](#1-patch-requests-tickets)
    - [2) In-Progress Patch Files (pending integration)](#2-in-progress-patch-files-pending-integration)
    - [3) Persistent Patch Artifacts (approved/kept)](#3-persistent-patch-artifacts-approvedkept)
    - [4) Patch Plans (structured playbooks)](#4-patch-plans-structured-playbooks)
    - [5) Logs and Reports](#5-logs-and-reports)
    - [6) Patch Ledger (new)](#6-patch-ledger-new)
- [Agent Directive (Copilot Behavior)](#agent-directive-copilot-behavior)
- [Directory Summary](#directory-summary)
- [Consequences](#consequences)
- [Alternatives Considered](#alternatives-considered)
- [Adoption Plan](#adoption-plan)
- [Token Blocks](#token-blocks)
- [References](#references)

## Considerations

Key constraints from existing governance:
- ADR-0024: All paths must use the single canonical config mount: /config
- ADR-0027: All file modifications use governed write patterns (write-broker, atomic replace, backup-before-modify)
- ADR-0009: ADR documents must include machine-parseable front matter and follow the standardized structure
- ADR-0018: Workspace lifecycle, normalization, and determinism rules apply to artifacts and reports

## Decision

Adopt the following canonical directories and workflow for patch operations:

### 1) Patch Requests (tickets)
- Location: `/config/hestia/workspace/todo/`
- Format: Markdown using `TODO_TEMPLATE.md` with metadata (title, author, human_owner, status, priority, description, proposed_patch, test_plan)
- Naming: `000N-short-slug.md` (zero-padded sequence)

### 2) In-Progress Patch Files (pending integration)
- Location: `/config/hestia/workspace/staging/`
- Purpose: Temporary holding area for diffs/patches while under review or testing
- Naming: `<UTC>__<tool|agent>__<label>.<ext>` (example: `20251021T120000Z__copilot__ha_config_fix.diff`)
- Migration: Once approved, move to `patches/` (see below) and remove from `staging/`

### 3) Persistent Patch Artifacts (approved/kept)
- Location: `/config/hestia/workspace/patches/`
- Purpose: Long-lived patch records, migration artifacts, and official patch documents committed via PR
- Guidance: Include a brief README/header per artifact describing purpose and scope

### 4) Patch Plans (structured playbooks)
- Location: `/config/hestia/workspace/operations/patch_plans/`
- Content: Idempotent, step-by-step patch recipes with scope guards, validation, and ADR references
- Example content exists (e.g., system_instruction alignment plan)

### 5) Logs and Reports
- Operations logs: `/config/hestia/workspace/operations/logs/`
- Global reporting: `/config/hestia/reports/<YYYY-MM-DD>/` with `_index.jsonl` aggregation per reporting system

### 6) Patch Ledger (new)
- Purpose: Append-only ledger of patch requests and their lifecycle states (open, in-progress, closed), including provenance and links to todos, staging artifacts, plans, and PRs
- Location: `/config/hestia/workspace/operations/logs/patch-ledger.jsonl`
- Format: JSON Lines (one JSON object per line) with fields such as:
  - `timestamp_utc`, `id`, `source` (operator|agent), `actor`, `title`, `status`, `todo_path`, `staging_paths`, `patch_path`, `plan_path`, `pr_url`, `notes`
- Indexing: Optionally mirrored or summarized into `/config/hestia/reports/<YYYY-MM-DD>/` as part of daily reports

## Agent Directive (Copilot Behavior)

When the operator submits a patch request (pastes a diff, drops a patch file in chat, or links to patch instructions), Copilot must:
1. Create or update a todo in `hestia/workspace/todo/` using the template (include `agent: copilot` and `human_owner:`)
2. Store the patch file under `hestia/workspace/staging/` using the naming convention
3. Append an entry to `/config/hestia/workspace/operations/logs/patch-ledger.jsonl` with relevant metadata
4. If applicable, link a patch plan under `hestia/workspace/operations/patch_plans/`
5. For approved/persistent artifacts, migrate into `hestia/workspace/patches/` and update the ledger status

Notes:
- Do not modify runtime configs directly; use ADR‑0027 write-broker governed flows when changes are applied
- Never include secrets in todos or patch artifacts; use vault URIs

## Directory Summary

- `/config/hestia/workspace/todo/` — patch requests and operational todos
- `/config/hestia/workspace/staging/` — in-progress patch artifacts (temporary)
- `/config/hestia/workspace/patches/` — persistent patch artifacts (committed)
- `/config/hestia/workspace/operations/patch_plans/` — structured patch recipes
- `/config/hestia/workspace/operations/logs/` — execution logs and `patch-ledger.jsonl`
- `/config/hestia/reports/<YYYY-MM-DD>/` — comprehensive reports (with `_index.jsonl` aggregator)

## Consequences

- Improves traceability and auditability of patch operations.
- Clarifies responsibilities for agents vs humans.
- Encourages idempotent, governed changes aligned with ADR‑0027.

## Alternatives Considered

- Use only `/config/hestia/reports/` for ledgering — rejected: reports are time-bucketed; a dedicated ledger in operations/logs provides a stable, append-only stream with optional mirroring into reports.

## Adoption Plan

1. Agents update their instruction files to implement the Directive above.
2. Maintain the ledger at `/config/hestia/workspace/operations/logs/patch-ledger.jsonl`.
3. Validate new todos and staging artifacts appear in their canonical directories.

## Token Blocks

```yaml
TOKEN_BLOCK:
  accepted:
    - PATCH_TODO_CREATED
    - PATCH_STAGED_ARTIFACT
    - PATCH_LEDGER_APPENDED
    - PATCH_PLAN_LINKED
    - PATCH_MIGRATED_TO_PERSISTENT
  requires:
    - ADR_SCHEMA_V1
    - ADR_0009_COMPLIANCE
    - GOVERNED_WRITES_ADR_0027
  produces:
    - TODO_ARTIFACT
    - STAGING_ARTIFACT
    - PATCH_LEDGER_ENTRY
    - PATCH_PLAN
  drift:
    - DRIFT: missing_todo
    - DRIFT: missing_ledger_entry
    - DRIFT: untracked_staging_artifact
    - DRIFT: direct_runtime_write_bypassing_broker
```

## References

- ADR‑0024 — Canonical config path
- ADR‑0027 — File writing governance and path enforcement
- ADR‑0009 — ADR governance and formatting policy
- ADR‑0018 — Normalization & determinism rules
