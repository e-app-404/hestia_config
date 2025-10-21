Hestia operations directory
===========================

Purpose
-------
This directory contains operational sub-systems used to plan, validate, and track changes to the workspace. It complements the staging and patches areas under `hestia/workspace/` and the todo queue.

Where to put things
-------------------
- Patch requests (tickets):
  - Use `hestia/workspace/todo/` and the `TODO_TEMPLATE.md`.
  - Include a short summary, owner, status, and (when safe) a `proposed_patch` diff snippet.

- In-progress patch files (pending integration):
  - Place temporary artifacts in `hestia/workspace/staging/` while under review.
  - Naming pattern: `<UTC>__<tool|agent>__<label>.<ext>` (example: `20251021T120000Z__copilot__ha_config_fix.diff`).
  - Remove or migrate to `patches/` once approved.

- Persistent patch artifacts (kept in repo):
  - Store in `hestia/workspace/patches/` with a concise README or header comment explaining purpose and scope.
  - These files are considered part of the long-lived workspace history and should be landed via PR.

- Patch plans (playbooks):
  - Author structured plans in `hestia/workspace/operations/patch_plans/`.
  - Plans should be idempotent and reference ADRs and canonical paths (ADR‑0024).

- Logs and reports:
  - Runtime logs for operations live in `hestia/workspace/operations/logs/`.
  - Comprehensive reports also aggregate under `/config/hestia/reports/<YYYY-MM-DD>/` per the reporting system.

Governance notes
----------------
- Follow ADR‑0024 for canonical paths (use `/config`); avoid host aliases.
- For any file modifications, prefer the governed write flow (ADR‑0027). Patch proposals should reflect atomic replace patterns and backup-before-modify where applicable.
- Do not include secrets in patch requests or artifacts; use vault URIs where necessary.

Related directories
-------------------
- `hestia/workspace/todo/` — patch requests and operational todos
- `hestia/workspace/staging/` — temporary queue for review/triage
- `hestia/workspace/patches/` — persistent patch artifacts
- `hestia/workspace/operations/patch_plans/` — structured patch recipes
- `hestia/workspace/operations/logs/` — execution logs

Last updated: 2025‑10‑21