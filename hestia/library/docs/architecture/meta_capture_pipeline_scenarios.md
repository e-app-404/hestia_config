---
Title: Meta-Capture Pipeline — Non-Ideal Scenarios & Playbooks
Slug: meta-capture-scenarios
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

# Non-Ideal Scenarios & Operator Playbooks

## 1) Duplicate Intake File
- Symptom: Same content appears again (new filename) or same file left in staging.
- Detection: Intake Scanner computes SHA256; ledger shows previously processed hash.
- Action:
  - If same SHA, different name: mark as duplicate → archive with `.duplicate.<UTC>`.
  - If same file unchanged: ignore (log-only).
- Report: One-line entry in `_index.jsonl` with outcome=duplicate.

## 2) Unknown Top-Level Key
- Symptom: New section at root (e.g., `custom_metrics:`) not in routing.
- Detection: Classifier collects unknown sections; Router cannot route → E-ROUTE-404.
- Action: Validation level `orange`; move to quarantine with a recommended routing snippet for hestia.toml.
- Report: Include section names and suggested `[automation.meta_capture.routing]` additions.

## 3) Invalid YAML / Decode Error
- Symptom: Parser error, mixed tabs/spaces, or truncated file.
- Detection: YAML decode failure → E-YAML-DEC-001.
- Action: `red`; move to quarantine with short excerpt and line number if available.
- Report: Parsing error details; suggest re-stage after fixing.

## 4) Oversized Intake File
- Symptom: File exceeds configured `max_file_size_mb`.
- Detection: Intake Scanner compares size to threshold.
- Action: `red`; quarantine; recommend splitting by topic/domain.
- Report: Size stats and policy reference.

## 5) Unknown `exports` Topic or Path Mismatch
- Symptom: `exports[].topic` not in mapping or `target_path` not matching canonical mapping.
- Detection: Router validates topic/path against configured map.
- Action: `orange`; quarantine with suggested diff (topic→path).
- Report: Show expected vs provided.

## 6) Pin Conflict (`# @pin`)
- Symptom: APU wants to modify pinned key in canonical file.
- Detection: Validator checks target snapshot for `@pin` comments.
- Action: `red`; block; emit exact key path and file.
- Report: Include guidance for unpinning process (PR, review, ADR note) if truly needed.

## 7) Secret Detected
- Symptom: Patch content includes token/password/private key.
- Detection: Secret detection rules (regex + allowlist) flag value.
- Action: `red`; block; do not write. Recommend vault reference migration.
- Report: Redacted preview and remediation steps per ADR-0027.

## 8) Unstable Device Path
- Symptom: `/dev/ttyUSB*` paths in incoming content.
- Detection: Validator checks for unstable device path patterns.
- Action: `orange`; suggest rewrite to `/dev/serial/by-id/...`.
- Report: Include candidate rewrite if known from inventory.

## 9) Timestamp Skew
- Symptom: `x-origin.timestamp` far in the future/past.
- Detection: Compare to skew window (e.g., ±24h).
- Action: `yellow`; proceed with warning; prefer canonical values when in doubt.
- Report: Show skew magnitude and current UTC.

## 10) Relationships Duplicates
- Symptom: Identical relationship entries across multiple captures.
- Detection: Atomizer or Validator dedupes set-like items.
- Action: `green`; merge once, note dedupe count.
- Report: Show deduped entries count.

## 11) Suggested Commands with Secrets
- Symptom: CLI entries include tokens or credentials inline.
- Detection: Secret detection triggers in Validator.
- Action: `orange` or `red` depending on severity; move sensitive parts to vault or redact.
- Report: Provide safe redaction pattern (e.g., `__REDACTED__`) and vault guidance.

## 12) Conflicting Host/Container Paths
- Symptom: Inconsistent `db_path` and `host_path` mappings.
- Detection: Validator compares to known mapping rules (container /config ⇄ host /addon_configs/... ).
- Action: `orange`; quarantine with mapping correction suggestion.
- Report: Show both paths and expected equivalence.

---

# Operator Quick Reference

- Unknown section → add routing → re-stage
- Duplicate content → no action required
- YAML decode error → fix syntax → re-stage
- Oversized file → split by topic/domain
- Secret detected → vault reference migration → re-stage
- Pin conflict → manual PR to unpin or adjust policy
- Unstable device path → rewrite to serial-by-id
- Path mismatch → fix container/host mapping

