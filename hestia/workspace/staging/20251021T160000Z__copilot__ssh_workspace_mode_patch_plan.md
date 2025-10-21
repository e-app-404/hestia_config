SSH Workspace + Copilot Mode Detection — Unified Governance Patch Plan
======================================================================

Source: operator submission via chat (2025-10-21)
Agent: copilot

Scope
-----
One consolidated plan that (1) lets Copilot/VS Code auto‑register the current operating mode (SSH vs. mount), (2) updates ADRs to reflect SSH‑first governance, (3) replaces Makefile dependencies with portable shims, and (4) wires VS Code tasks to run automatically on folder open.

Baseline paths: repository root = `/config`; workspace file = `/config/.vscode/hass-live.code-workspace`.

Plan Content
------------
```markdown
# SSH Workspace + Copilot Mode Detection — Unified Governance Patch Plan

**Scope:** One consolidated plan that (1) lets Copilot/VS Code auto‑register the current operating mode (SSH vs. mount), (2) updates ADRs to reflect SSH‑first governance, (3) replaces Makefile dependencies with portable shims, and (4) wires VS Code tasks to run automatically on folder open.

**Baseline paths:** repository root = `/config`; workspace file = `/config/.vscode/hass-live.code-workspace`.

---

## 1) Auto‑detect & register workspace mode

### 1.1 New file: `/config/bin/detect-workspace-mode`

```bash
#!/usr/bin/env bash
set -euo pipefail

# Usage: bin/detect-workspace-mode [<workspace_root>]
ROOT="${1:-$(pwd -P)}"
ROOT="$(cd "$ROOT" && pwd -P)"
mkdir -p "$ROOT/.vscode"

# Heuristics
OS="$(uname -s 2>/dev/null || echo unknown)"
USER_NAME="${USER:-$(id -un 2>/dev/null || echo unknown)}"
HOST_NAME="$(hostname 2>/dev/null || echo unknown)"
IN_SSH="${SSH_CONNECTION:-}${SSH_CLIENT:-}"
VSCODE_AGENT="${VSCODE_AGENT_FOLDER:-}${VSCODE_IPC_HOOK_CLI:-}"
MOUNT_INFO=""
MODE="local"

# Detect SMB mount on macOS
if [[ "$OS" == "Darwin" ]]; then
  # try to read mount type for ROOT
  MOUNT_POINT="$ROOT"
  # normalize to volume root if inside //Volumes/*
  case "$MOUNT_POINT" in
    /Volumes/*) : ;;
    *) MOUNT_POINT="/Volumes/config";;
  esac
  if mount | grep -E "on[[:space:]]$MOUNT_POINT[[:space:]]" | grep -qi "smbfs"; then
    MODE="smb"
  fi
fi

# Detect VS Code Remote over SSH (takes precedence)
if [[ -n "$IN_SSH" ]] || [[ -n "$VSCODE_AGENT" ]] || [[ -d "$HOME/.vscode-server" ]] || [[ -d "$HOME/.vscode-server-insiders" ]]; then
  MODE="ssh"
fi

# Additional HA OS hints (alpine busybox, /config exists, root user)
if [[ -d /config ]] && command -v ha >/dev/null 2>&1; then
  MODE="ssh"
fi

# Compose payload
NOW="$(date -u +%FT%TZ 2>/dev/null || true)"
cat >"$ROOT/.vscode/workspace_mode.json" <<JSON
{
  "timestamp": "$NOW",
  "mode": "$MODE",
  "os": "$OS",
  "user": "$USER_NAME",
  "host": "$HOST_NAME",
  "root": "$ROOT"
}
JSON

cat >"$ROOT/.vscode/workspace_context.md" <<MD
# Workspace Context
- Mode: **$MODE**
- Host: **$HOST_NAME**
- User: **$USER_NAME**
- OS: **$OS**
- Root: **$ROOT**
- Generated: **$NOW**
MD

echo "workspace_mode=$MODE root=$ROOT host=$HOST_NAME"
```

> **Purpose:** Writes machine‑readable `.vscode/workspace_mode.json` + a human `.vscode/workspace_context.md`.

### 1.2 Wire detection to run automatically

**New/Amend file:** `/config/.vscode/tasks.json`

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Workspace: Detect Mode (auto)",
      "type": "shell",
      "command": "bash -lc './bin/detect-workspace-mode \"${workspaceFolder}\"'",
      "runOptions": { "runOn": "folderOpen" },
      "presentation": { "reveal": "never", "panel": "dedicated" },
      "problemMatcher": []
    },
    {
      "label": "ADR: Bundle (portable)",
      "type": "shell",
      "command": "bash -lc './bin/adr-tarball'",
      "presentation": { "reveal": "always", "panel": "shared" },
      "problemMatcher": []
    }
  ]
}
```

**Amend file:** `/config/.vscode/hass-live.code-workspace`

```jsonc
{
  "folders": [
    { "path": ".." }
  ],
  "settings": {
    "explorer.excludeGitIgnore": false,
    "files.exclude": {},
    "search.exclude": {},
    "files.watcherExclude": {}
  }
}
```

**New file:** `/config/.vscode/extensions.json`

```json
{
  "recommendations": [
    "ms-vscode-remote.remote-ssh",
    "github.copilot-chat"
  ]
}
```

---

## 2) Portable CLI shim (replace Makefile dependency)

### 2.1 New file: `/config/bin/adr-tarball`

[See repository: shim already present and wired]

---

## 3) Governance ADR patches (unified)

[Proposed diffs across ADR‑0024/0018/0027/0026]

---

## 4) Environment‑aware dependencies

Proposed `requirements-ssh.txt` minimal set (repo already has a richer HA‑friendly set).

---

## 5) Copilot/Assistant awareness

Add `.vscode/workspace_mode.json` and `.vscode/workspace_context.md`; optional `.github/copilot-instructions.md` note.

---

## 6) Validation steps (post‑patch)

- On folder open, detection writes workspace_mode.json
- ADR bundle task produces tarball + manifest + SHA256
- ADR patches present and pass repo lint
- Copilot Chat references workspace mode file when asked
```
