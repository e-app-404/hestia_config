---
Title: Meta-Capture Pipeline — Component Contracts
Slug: meta-capture-component-contracts
Status: Draft
Authors:
  - Workspace Engineering
  - GitHub Copilot (assisted)
Last_Updated: 2025-10-19
Related_ADRs:
  - ADR-0013
  - ADR-0027
  - ADR-0008
---

# Component Contracts (I/O, Error Modes, Success Criteria)

## 1) Intake Scanner
- Inputs: `intake_paths[]`, `since_ts?`, `topics?`
- Outputs: `queue[]` of file descriptors `{path, size, mtime, sha256}`
- Errors: permission_denied, unreadable_yaml, too_large
- Success: found ≥0 new items

## 2) Schema Validator
- Inputs: file descriptor + parsed YAML
- Checks: presence of `exports` or `extracted_config` or `transient_state`
- Outputs: `schema_ok: bool`, `errors[]`
- Errors: E-SCHEMA-001 (missing), E-YAML-DEC-001 (parse)
- Success: schema_ok

## 3) Classifier
- Inputs: parsed YAML
- Outputs: `sections_present: Set[str]`
- Errors: none (best-effort)
- Success: non-empty or marked as noop

## 4) Router
- Inputs: sections, hestia.toml routing
- Outputs: `routing_plan[]` of {section, target_path, operation}
- Errors: E-ROUTE-404 (no route), E-ROUTE-409 (ambiguous)
- Success: all sections routed or soft-noop

## 5) Atomizer
- Inputs: routing_plan + source content
- Outputs: `apus[]` (Atomic Patch Units)
- Errors: E-ATOM-001 (oversized), E-ATOM-002 (empty), E-ATOM-003 (id collision)
- Success: ≥1 apu created when content exists

## 6) Validator (Traffic Light)
- Inputs: apu + target snapshot
- Outputs: `level: green|yellow|orange|red`, `reasons[]`
- Checks: pin guard, secret detection, path stability, merge diff analysis, schema
- Errors: E-VAL-00x (per check)
- Success: non-red or red with actionable reasons

## 7) Merger
- Inputs: apu (green/yellow), write-broker
- Outputs: updated target file, before/after diff
- Errors: E-WRITE-001 (permission), E-WRITE-002 (atomic write failure)
- Success: file updated atomically, backup created

## 8) Disposer
- Inputs: source file + outcome
- Outputs: archived or quarantined file path
- Errors: E-DISP-001 (move failed)
- Success: source removed from intake, not re-ingested

## 9) Reporter
- Inputs: run metadata, apus, outcomes
- Outputs: log file path, JSONL index update
- Errors: E-REP-001 (write failed)
- Success: report visible in `/config/hestia/reports/_index.jsonl`

---

# Edge Cases
- Empty `exports` list → noop
- Conflicting host/container paths → orange (requires mapping verification)
- Duplicate `relationships` entries → dedupe at atomizer level
- Suggested commands with secrets → redact and flag yellow/orange

# Success Criteria
- Re-running with same inputs yields idempotent results
- No plaintext secrets end up in canonical config (ADR-0027)
- Archive/quarantine prevents re-ingestion loops
- Deterministic ordering and formatting per ADR-0008
