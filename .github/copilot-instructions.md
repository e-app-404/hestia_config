# Workspace Mode Hints for Assistants

Read `.vscode/workspace_mode.json` to tailor responses:

- mode=ssh: Treat `/config` on the HA host as canonical; avoid recommending SMB steps. Prefer running tasks and scripts on the host.
- mode=smb: Mounted shares may be incomplete; prefer read-only exploration and avoid authoritative edits. Recommend switching to Remote‑SSH for mutating operations.
- Always reference canonical paths under `/config` and governed entrypoints under `/config/bin`.

Also follow ADR‑0032 Patch Operation Workflow:
- Create/update a TODO in `hestia/workspace/todo/`
- Stage patch artifacts in `hestia/workspace/staging/`
- Append to `hestia/workspace/operations/logs/patch-ledger.jsonl`
- Link/create a plan in `hestia/workspace/operations/patch_plans/`
- Migrate approved artifacts to `hestia/workspace/patches/` and update the ledger status
