### Patch Plan — Workspace Mode Detection & SSH-First Governance

Status: proposed
Owner: e-app-404
Agent: copilot
Created: 2025-10-21T16:01:00Z

Scope
-----
Implement environment detection, portable ADR bundling, governance clarifications, and VS Code automation per the staged plan:
- Staged plan: `/config/hestia/workspace/staging/20251021T160000Z__copilot__ssh_workspace_mode_patch_plan.md`

Steps (idempotent)
------------------
1. Add `/config/bin/detect-workspace-mode` (executable)
2. Amend `.vscode/tasks.json` to run detection on folder open; add `ADR: Bundle (portable)` task
3. Keep `bin/adr-tarball` as the portable Make alternative (already present)
4. Clarify governance in ADR‑0024, ADR‑0018, ADR‑0027, ADR‑0026 as proposed
5. Validate end-to-end: detection output, ADR bundle, ADR verification

Validation
----------
- `Workspace: Detect Mode (auto)` runs on open; `.vscode/workspace_mode.json` has mode=ssh
- `ADR: Bundle (portable)` produces tarball, `MANIFEST.json`, and `SHA256SUMS`
- ADR linter passes (frontmatter strict)

Notes
-----
- Use governed writes (ADR‑0027) for any file modifications to runtime configs
- No secrets in artifacts; use vault URIs when needed
