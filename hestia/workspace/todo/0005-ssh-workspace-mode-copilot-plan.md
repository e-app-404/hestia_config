---
status: open
created_at: 2025-10-21T16:02:00Z
updated_at: 2025-10-21T16:02:00Z
author: e-app-404
agent: copilot
human_owner: e-app-404
priority: medium
labels: ["adr-0032", "governance", "workspace-mode", "ssh"]
---

# SSH Workspace + Copilot Mode Detection — Unified Governance Patch Plan

## Description
Operator provided a unified patch plan to detect workspace mode (SSH vs mount), prefer SSH‑first governance, rely on portable CLI shims instead of Make, and wire VS Code tasks to run on folder open.

## Proposed change / patch
Plan staged at:
- `/config/hestia/workspace/staging/20251021T160000Z__copilot__ssh_workspace_mode_patch_plan.md`

Patch plan registered at:
- `/config/hestia/workspace/operations/patch_plans/20251021T160100Z-workspace_mode_and_governance_unified.md`

## Files changed (planned)
- Add: `/config/bin/detect-workspace-mode`
- Amend: `/config/.vscode/tasks.json` (run detection on folder open; add ADR bundle task)
- Keep: `/config/bin/adr-tarball` (portable shim)
- Amend: ADRs 0024/0018/0027/0026 with SSH‑first clarifications

## Test plan
1) Open via Remote‑SSH; verify `.vscode/workspace_mode.json` shows `mode=ssh`
2) Run task "ADR: Bundle (portable)"; expect tarball, manifest, SHA256
3) Run ADR linter (strict) — should pass

## Notes / references
- ADR‑0032 (patch operation workflow)
- ADR‑0024 (canonical /config path)
- ADR‑0027 (write governance)
- ADR‑0018 (workspace lifecycle)

## Change log
- 2025-10-21: created (author: e-app-404, agent: copilot)
