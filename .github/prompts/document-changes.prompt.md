---
mode: 'agent'
model: GPT-4.1
tools: ['edit/createFile', 'edit/editFiles', 'search/fileSearch', 'search/textSearch', 'search/listDirectory', 'search/codebase', 'search/searchResults', 'runCommands', 'problems', 'changes']
description: 'Document recent changes across the workspace: update maintenance logs, relationships, and relevant config docs with evidence and acceptance checks.'
---
# /document_changes — Workspace Documentation Updater

Mission
- Update central docs under /config/hestia/config/* to reflect major changes, maintenance work, network/system info.
- Produce atomic, reviewable patches with acceptance criteria.

Scope & Preconditions
- Required context files (read-only):
  - /config/hestia/config/system/maintenance_log.conf
  - /config/hestia/config/system/relationships.conf
  - /config/hestia/config/system/hestia.toml
  - /config/home-assistant.log
- Optional:
  - /config/.workspace/governance_index.md
  - /config/hestia/reports/*/*
  - /config/hestia/library/context/meta/*

Inputs
- ${input:summary:short summary of changes}
- ${input:areas:comma-separated areas to update e.g., maintenance,relationships}
- ${selection} (optional detailed notes)

Workflow
1) Collect evidence
- Summarize recent commits and relevant reports/meta artifacts.
- Extract key timestamps, components, endpoints, and acceptance confirmations.

2) Generate patches
- maintenance_log.conf: append a new session with date, focus, actions_completed, validations, governance, success_validation, confidence_level.
- relationships.conf: update service statuses/paths (e.g., appdaemon_api) to reflect current reality.
- Any other specified config docs under /config/hestia/config/system/* (idempotent edits only).

3) Output
- A list of unified diffs ready to apply.
- A YAML checklist with acceptance criteria for reviewers.

Quality guardrails
- Evidence-first; cite paths to reports/log lines used.
- ADR-compliant (ADR-0024, ADR-0027, ADR-0008).
- No secrets; never modify vault URIs.
- Atomic patches; avoid broad reformatting.

Acceptance criteria
- New session in maintenance_log.conf is well-structured and machine-parsable.
- relationships.conf updates reflect verified endpoints/health.
- All changes limited to /config.
- Validation steps included (e.g., grep/curl checks, config validation).
