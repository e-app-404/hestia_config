### Assumptions

* Your macOS username is `evertappels`.
* The Home Assistant SMB share is `//evertappels@homeassistant.local/config`.
* The APFS synthetic mapping is `config	homeassistant` with backing dir `/System/Volumes/Data/homeassistant`.
* The repository root is inside `/config` and is the working directory for development.
* Two external repos (“omega registry”, “bb8 addon”) provide **read-only** ADR imports under `library/docs/ADR-imports/**`.

---

## Touchpoints Checklist (comprehensive)

* **macOS host**

  * APFS synthetic `/config` firmlink to Data path.
  * LaunchAgent to mount SMB at `/System/Volumes/Data/homeassistant`.
  * Keychain item for SMB credentials.
  * Guard script (RO/RW), health script, logs to `~/Library/Logs`.
  * Sleep/wake resilience via `KeepAlive.NetworkState` + interval retries.
  * Spotlight off on backing dir; permissions sane default (`-f 0644 -d 0755`).
* **Tooling & developer UX**

  * `.env` (POSIX) with `CONFIG_ROOT=/config` + legacy alias mapping to `/config`.
  * VS Code workspace and tasks pinned to `/config`.
  * `bin/vscode-env-smoke` to prove terminal/task env.
  * Pre-commit with path-drift linter.
  * Drift fixer (narrow scope, idempotent).
* **Containers/devcontainer/compose**

  * Devcontainer mounts workspace → `/config`.
  * Compose maps host Data path → `/config`; root user to avoid UID mismatches.
  * Healthchecks confirm `/config` is a directory inside containers.
* **CI/CD**

  * Container-first workflow with bind to `/config`.
  * Linter runs in CI; tool bootstrap (ripgrep) handled.
  * macOS smoke job (no bind mounts) runs linter only.
  * Cache none (deterministic, low-cost).
* **Home Assistant specifics**

  * `shell_command` uses `/config/tools/...` only.
  * Recorder/DB/secrets under `/config`.
  * `custom_components` paths naturally under `/config`.
* **Logs/telemetry**

  * LaunchAgent logs `~/Library/Logs/hestia.mount.{out,err}`.
* **Cross-repo ADR imports**

  * Linter exclusions for `library/docs/ADR-imports/**` and `ADR/deprecated/**`.
  * Machine-readable ADR supersession fields aligned.
* **Security**

  * Least privilege: RO allowed with `REQUIRE_CONFIG_WRITABLE=0`.
  * Keychain used for SMB password.
* **Performance**

  * SMB `nobrowse`, `-f 0644 -d 0755`.
  * VS Code `files.watcherExclude` and `search.exclude` for caches.
  * Local Python venv under workspace (inside `/config`) is acceptable.

---

## Patch Set

### `bin/require-config-root`

```bash
#!/usr/bin/env bash
# ADR-0024 guard: verify canonical /config root with RO/RW modes
set -euo pipefail

: "${CONFIG_ROOT:=/config}"
: "${REQUIRE_CONFIG_WRITABLE:=1}"

if [[ ! -d "$CONFIG_ROOT" ]]; then
  echo "[guard] ERROR: $CONFIG_ROOT missing or not a directory" >&2
  exit 2
fi

if [[ "$REQUIRE_CONFIG_WRITABLE" = "1" && ! -w "$CONFIG_ROOT" ]]; then
  echo "[guard] ERROR: $CONFIG_ROOT not writable; set REQUIRE_CONFIG_WRITABLE=0 for RO contexts" >&2
  exit 3
fi

# Warn if symlink (APFS synthetic may not report as symlink)
if [[ -L "$CONFIG_ROOT" ]]; then
  echo "[guard] WARN: $CONFIG_ROOT is a symlink; ADR-0024 prefers synthetic firmlink via /etc/synthetic.conf" >&2
fi

# Resolution log (portable)
if command -v realpath >/dev/null 2>&1; then
  echo "[guard] OK: $(realpath "$CONFIG_ROOT")"
else
  python3 - <<'PY' 2>/dev/null || echo "[guard] OK: $CONFIG_ROOT"
import os; print("[guard] OK:", os.path.realpath("/config"))
PY
fi
```

---

### `tools/lint_paths.sh`

```bash
#!/usr/bin/env bash
# Fail on legacy aliases; exclude historical & imported ADRs.
set -euo pipefail

PATTERN='\$HOME/|~/hass|/Volumes/|/n/ha|actions-runner/.+?/hass'

# Exclusions (globs)
EXCLUDES=(
  '!**/*.md'
  '!ADR/deprecated/**'
  '!docs/history/**'
  '!library/docs/ADR-imports/**'
  '!**/.git/**'
  '!**/.venv/**'
  '!**/node_modules/**'
  '!**/*.png' '!**/*.jpg' '!**/*.svg' '!**/*.ico'
)

if command -v rg >/dev/null 2>&1; then
  if rg -nE "$PATTERN" --hidden "${EXCLUDES[@]}" .; then
    echo 'ERROR: Disallowed path alias detected. Use /config only.' >&2
    exit 1
  fi
else
  echo "[lint] ripgrep not found; falling back to grep (slower)." >&2
  MATCHES=$(git ls-files | grep -vE '\.md$|^ADR/deprecated/|^docs/history/|^library/docs/ADR-imports/|^\.git/|^\.venv/|node_modules/|\.png$|\.jpg$|\.svg$|\.ico$' \
    | xargs grep -nE "$PATTERN" -- 2>/dev/null || true)
  if [[ -n "${MATCHES}" ]]; then
    echo "${MATCHES}"
    echo 'ERROR: Disallowed path alias detected. Use /config only.' >&2
    exit 1
  fi
fi

echo "OK: path lint passed"
```

---

### `tools/fix_path_drift.sh`

```bash
#!/usr/bin/env bash
# Narrow, idempotent replacement to /config. Backs up touched files.
set -euo pipefail

# Choose sed (BSD or GNU)
if command -v gsed >/dev/null 2>&1; then SED=gsed; else SED=sed; fi

# Target files (scripts/yaml/json only)
FILES=$(git ls-files \
  ':config/**' ':hestia/**' ':tools/**' ':scripts/**' \
  ':.github/**' ':.devcontainer/**' ':.vscode/**' \
  | grep -E '\.(sh|bash|zsh|py|yaml|yml|json)$' || true)

if [[ -z "${FILES}" ]]; then
  echo "No candidate files found."
  exit 0
fi

for f in $FILES; do
  # Skip historical/imported ADRs just in case
  [[ "$f" == ADR/deprecated/* ]] && continue
  [[ "$f" == docs/history/* ]] && continue
  [[ "$f" == library/docs/ADR-imports/* ]] && continue

  before=$(cksum "$f" | awk '{print $1}')
  cp -p "$f" "$f.bak_adr0024" || true

  $SED -E -i '' \
    -e 's#\$(HOME)/hass#\/config#g' \
    -e 's#\~\/hass#\/config#g' \
    -e 's#(/Volumes(/[^ ]*)?)\/HA\/Config#\/config#g' \
    -e 's#(/Volumes(/[^ ]*)?)\/Config#\/config#g' \
    -e 's#\/n\/ha#\/config#g' \
    -e 's#actions-runner\/[^ ]*\/hass#config#g' \
    "$f"

  after=$(cksum "$f" | awk '{print $1}')
  if [[ "$before" != "$after" ]]; then
    echo "Patched: $f"
  else
    rm -f "$f.bak_adr0024" || true
  fi
done

echo "Fix completed."
```

---

### `bin/config-health`

```bash
#!/usr/bin/env bash
# Binary health: check path node type, realpath, RO/RW.
set -euo pipefail

TARGET="${1:-/config}"

if [[ ! -d "$TARGET" ]]; then
  echo "FAIL: $TARGET not a directory"
  exit 2
fi

os="$(uname -s)"
if [[ "$os" == "Darwin" ]]; then
  nodetype=$(stat -f %HT "$TARGET")
  echo "node: $nodetype"
else
  nodetype=$(stat -c %F "$TARGET")
  echo "node: $nodetype"
fi

python3 - <<PY
import os, sys
p=sys.argv[1]
print("realpath:", os.path.realpath(p))
print("readable:", os.access(p, os.R_OK))
print("writable:", os.access(p, os.W_OK))
PY
```

---

### `bin/vscode-env-smoke`

```bash
#!/usr/bin/env bash
# Print effective VS Code terminal/task env and validate CONFIG_ROOT.
set -euo pipefail

echo "pwd: $(pwd)"
echo "SHELL: ${SHELL:-}"
echo "CONFIG_ROOT: ${CONFIG_ROOT:-<unset>}"
echo "HA_MOUNT: ${HA_MOUNT:-<unset>}"
echo "HA_MOUNT_OPERATOR: ${HA_MOUNT_OPERATOR:-<unset>}"

if [[ "${CONFIG_ROOT:-}" != "/config" ]]; then
  echo "FAIL: CONFIG_ROOT must be /config"
  exit 1
fi

if [[ ! -d /config ]]; then
  echo "FAIL: /config not a directory"
  exit 2
fi

python3 - <<'PY'
import os
print("vscode-env-smoke realpath(/config):", os.path.realpath("/config"))
PY

echo "OK"
```

---

### `bin/ha-mount.sh` (macOS user script)

```bash
#!/usr/bin/env bash
# Mount HA config share to Data-backed path per ADR-0024.
# Uses macOS Keychain item "ha.smb.config" (generic password).
set -euo pipefail

MNT="/System/Volumes/Data/homeassistant"
SMB_HOST="${HA_SMB_HOST:-homeassistant.local}"
SMB_SHARE="${HA_SMB_SHARE:-config}"
SMB_USER="${HA_SMB_USER:-evertappels}"
KEYCHAIN_ITEM="${HA_SMB_KEYCHAIN_ITEM:-ha.smb.config}"
LOG="${HOME}/Library/Logs/hestia.mount.out"

mkdir -p "$MNT" "$(dirname "$LOG")"

# Reachability check
is_up() { /usr/sbin/scutil -r "$SMB_HOST" | grep -q 'Reachable'; }

# Unmount if stale
if mount | grep -q " on ${MNT} "; then
  echo "$(date) [mount] ${MNT} already mounted" >>"$LOG"
  exit 0
fi

# Retrieve password from Keychain
if ! PASS="$(/usr/bin/security find-generic-password -s "$KEYCHAIN_ITEM" -w 2>/dev/null)"; then
  echo "$(date) [mount] ERROR: Keychain item '$KEYCHAIN_ITEM' not found" >>"$LOG"
  exit 4
fi

# Retry with backoff until host reachable
tries=0
until is_up; do
  tries=$((tries+1))
  sleep 5
  if (( tries > 24 )); then
    echo "$(date) [mount] ERROR: host $SMB_HOST not reachable" >>"$LOG"
    exit 5
  fi
done

# Attempt mount (note: password exposure risk in ps output is brief but real)
# File/dir modes and nobrowse for Finder
OPTS="-f 0644 -d 0755 -o nobrowse"
URL="//${SMB_USER}:${PASS}@${SMB_HOST}/${SMB_SHARE}"

if /sbin/mount_smbfs $OPTS "$URL" "$MNT" >>"$LOG" 2>&1; then
  echo "$(date) [mount] OK: ${SMB_HOST}/${SMB_SHARE} -> ${MNT}" >>"$LOG"
  exit 0
else
  echo "$(date) [mount] ERROR: mount_smbfs failed" >>"$LOG"
  exit 6
fi
```

---

### `~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.hestia.mount.homeassistant</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/evertappels/bin/ha-mount.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StartInterval</key><integer>60</integer>
  <key>StandardOutPath</key><string>/Users/evertappels/Library/Logs/hestia.mount.out</string>
  <key>StandardErrorPath</key><string>/Users/evertappels/Library/Logs/hestia.mount.err</string>
</dict></plist>
```

---

### `.env`

```bash
# =====================================================================
# ADR-0024 COMPLIANT .env — canonical /config paths only
# Source with:  . ./.env
# =====================================================================

CONFIG_ROOT=/config

# Legacy aliases (compat window)
HA_MOUNT=/config
HA_MOUNT_OPERATOR=/config

PYTHONUNBUFFERED=1
PIP_DISABLE_PIP_VERSION_CHECK=1

# Canonical projects root (local default; unused by HA path selection)
PROJECTS_ROOT=${PROJECTS_ROOT:-$HOME/Projects}

# Workspace root detection for auxiliary tooling
WORKSPACE_ROOT=${WORKSPACE_ROOT:-${GITHUB_WORKSPACE:-$PWD}}

# Hestia canonical roots - ADR-0024 compliant
DIR_HESTIA=/config/hestia
DIR_PACKAGES=/config/packages
DIR_DOMAINS=/config/domains
TEMPLATE_CANONICAL=/config/custom_templates/template.library.jinja

HESTIA_CONFIG=/config/hestia/config
HESTIA_LIBRARY=/config/hestia/library
HESTIA_TOOLS=/config/hestia/tools
HESTIA_WORKSPACE=/config/hestia/workspace

HESTIA_ADR=/config/hestia/library/docs/ADR
HESTIA_PLAYBOOKS=/config/hestia/library/docs/playbooks
HESTIA_BLUEPRINTS=/config/hestia/library/templates/blueprints
HESTIA_DEVICES=/config/hestia/config/devices
HESTIA_NETWORK=/config/hestia/config/network
HESTIA_VAULT=/config/hestia/workspace/archive/vault
HESTIA_BACKUPS=/config/hestia/workspace/archive/vault/backups
HESTIA_CACHE=/config/hestia/workspace/cache
HESTIA_SCRATCH=/config/hestia/workspace/cache/scratch
HESTIA_PROMPTS=/config/hestia/library/prompts
HESTIA_GOVERNANCE=/config/hestia/library/docs/governance
HESTIA_TODO=/config/hestia/workspace/todo
HESTIA_LOGS=/config/hestia/workspace/operations/logs
HESTIA_SCRIPTS=/config/hestia/tools/scripts
HESTIA_UTILS=/config/hestia/tools/utils

# Cross-repo ADRs (read-only imports)
ADR_HA_Hestia=/config/hestia/library/docs/ADR
ADR_HA_Omega=${OMEGA_ADR_DIR:-/config/hestia/library/docs/ADR-imports/omega}
ADR_BB8=${BB8_DOCS_ADR_DIR:-/config/hestia/library/docs/ADR-imports/bb8}
```

---

### `.vscode/tasks.json`

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "ADR-0024: Health",
      "type": "shell",
      "command": "${workspaceFolder}/bin/config-health /config",
      "options": {
        "env": {
          "CONFIG_ROOT": "/config",
          "HA_MOUNT": "/config",
          "HA_MOUNT_OPERATOR": "/config"
        },
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": []
    },
    {
      "label": "ADR-0024: Lint Paths",
      "type": "shell",
      "command": "${workspaceFolder}/tools/lint_paths.sh",
      "options": {
        "env": {
          "CONFIG_ROOT": "/config"
        },
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": []
    },
    {
      "label": "ADR-0024: Fix Path Drift (dry-run echo)",
      "type": "shell",
      "command": "echo 'Review changes in VCS after running tools/fix_path_drift.sh'",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": []
    },
    {
      "label": "ADR-0024: VS Code Env Smoke",
      "type": "shell",
      "command": "${workspaceFolder}/bin/vscode-env-smoke",
      "options": {
        "env": {
          "CONFIG_ROOT": "/config",
          "HA_MOUNT": "/config",
          "HA_MOUNT_OPERATOR": "/config"
        },
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": []
    }
  ]
}
```

---

### `.vscode/hass-live.code-workspace`

```json
{
  "folders": [
    { "path": "." }
  ],
  "settings": {
    "terminal.integrated.env.osx": {
      "PATH": "/opt/homebrew/bin:${env:PATH}",
      "CONFIG_ROOT": "/config",
      "HA_MOUNT": "/config",
      "HA_MOUNT_OPERATOR": "/config"
    },
    "terminal.integrated.cwd": "${workspaceFolder}",
    "terminal.integrated.splitCwd": "workspaceRoot",
    "terminal.integrated.inheritEnv": true,

    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.terminal.useEnvFile": true,
    "python.envFile": "${workspaceFolder}/.env",

    "files.watcherExclude": {
      "**/hestia/workspace/cache/**": true,
      "**/hestia/workspace/archive/**": true,
      "**/.venv/**": true,
      "**/node_modules/**": true
    },
    "search.exclude": {
      "**/hestia/workspace/cache/**": true,
      "**/hestia/workspace/archive/**": true,
      "**/.venv/**": true,
      "**/node_modules/**": true
    }
  }
}
```

---

### `.devcontainer/devcontainer.json`

```json
{
  "name": "HA @ /config (ADR-0024)",
  "image": "ghcr.io/home-assistant/home-assistant:stable",
  "runArgs": [
    "--volume=${localWorkspaceFolder}:/config",
    "--user=0:0"
  ],
  "workspaceMount": "source=${localWorkspaceFolder},target=/config,type=bind",
  "workspaceFolder": "/config",
  "features": {},
  "postCreateCommand": "echo 'config mounted at /config'; /bin/true",
  "remoteUser": "root",
  "customizations": {
    "vscode": {
      "settings": {
        "terminal.integrated.env.linux": {
          "CONFIG_ROOT": "/config",
          "HA_MOUNT": "/config",
          "HA_MOUNT_OPERATOR": "/config"
        }
      },
      "extensions": [
        "ms-python.python",
        "ms-azuretools.vscode-docker",
        "tamasfe.even-better-toml",
        "redhat.vscode-yaml"
      ]
    }
  }
}
```

---

### `docker-compose.yml`

```yaml
version: "3.9"
services:
  ha:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: ha-dev
    user: "0:0"
    volumes:
      - /System/Volumes/Data/homeassistant:/config
    environment:
      - TZ=UTC
    healthcheck:
      test: ["CMD", "bash", "-lc", "[ -d /config ] || exit 1" ]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
```

---

### `.github/workflows/ha-canonical-guard.yml`

```yaml
name: ADR-0024 Canonical Guard

on:
  push:
    branches: [ "**" ]
  pull_request:
    branches: [ "**" ]

jobs:
  guard-linux-container:
    runs-on: ubuntu-latest
    container:
      image: ubuntu:24.04
      options: --volume ${{ github.workspace }}:/config
    steps:
      - uses: actions/checkout@v4
      - name: Bootstrap tools
        run: |
          apt-get update && apt-get install -y ripgrep bash python3
      - name: Lint paths
        working-directory: /config
        run: tools/lint_paths.sh
      - name: Config health
        working-directory: /config
        run: bin/config-health /config

  guard-macos-smoke:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ripgrep
        run: brew install ripgrep || true
      - name: Lint paths (no /config bind here)
        run: tools/lint_paths.sh
```

---

### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: adr0024-path-lint
        name: ADR-0024 Path Lint
        entry: tools/lint_paths.sh
        language: system
        pass_filenames: false
        stages: [commit, push]
```

---

### `config/includes/shell_command.yaml`

```yaml
# ADR-0024 canonical paths only
ha_git_push: "/config/tools/ha_git_push.sh /config"
```

---

### `configuration.yaml` (include snippet)

```yaml
# Ensure this line exists in your root configuration.yaml
shell_command: !include config/includes/shell_command.yaml
```

---

### `ADR/deprecated/README.md`

```markdown
# Deprecated ADRs

Files in this directory are retained for historical reference.
Each document must include:

- `status: Superseded`
- `superseded_by: ADR-0024`

Parsing and linting tools ignore this directory.
```

---

## Apply Plan (idempotent)

> Run from repository root (which resides at `/config`).

1. **Create directories**

```bash
mkdir -p bin tools ~/Library/LaunchAgents ~/Library/Logs \
         config/includes ADR/deprecated .vscode .devcontainer
```

2. **Write files**

```bash
# Core scripts
install -m 0755 bin/require-config-root bin/require-config-root
install -m 0755 bin/config-health bin/config-health
install -m 0755 bin/vscode-env-smoke bin/vscode-env-smoke
install -m 0755 tools/lint_paths.sh tools/lint_paths.sh
install -m 0755 tools/fix_path_drift.sh tools/fix_path_drift.sh

# macOS mount script and LaunchAgent
install -m 0755 bin/ha-mount.sh /Users/evertappels/bin/ha-mount.sh
cp -f ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist 2>/dev/null || true
cat > ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.hestia.mount.homeassistant</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/evertappels/bin/ha-mount.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StartInterval</key><integer>60</integer>
  <key>StandardOutPath</key><string>/Users/evertappels/Library/Logs/hestia.mount.out</string>
  <key>StandardErrorPath</key><string>/Users/evertappels/Library/Logs/hestia.mount.err</string>
</dict></plist>
PLIST
```

3. **Dev/CI config**

```bash
# Environment and editors
cp -f .env .env.bak_adr0024 2>/dev/null || true
cat > .env <<'ENV'
# (file contents exactly as in Patch Set)
CONFIG_ROOT=/config
HA_MOUNT=/config
HA_MOUNT_OPERATOR=/config
PYTHONUNBUFFERED=1
PIP_DISABLE_PIP_VERSION_CHECK=1
PROJECTS_ROOT=${PROJECTS_ROOT:-$HOME/Projects}
WORKSPACE_ROOT=${WORKSPACE_ROOT:-${GITHUB_WORKSPACE:-$PWD}}
DIR_HESTIA=/config/hestia
DIR_PACKAGES=/config/packages
DIR_DOMAINS=/config/domains
TEMPLATE_CANONICAL=/config/custom_templates/template.library.jinja
HESTIA_CONFIG=/config/hestia/config
HESTIA_LIBRARY=/config/hestia/library
HESTIA_TOOLS=/config/hestia/tools
HESTIA_WORKSPACE=/config/hestia/workspace
HESTIA_ADR=/config/hestia/library/docs/ADR
HESTIA_PLAYBOOKS=/config/hestia/library/docs/playbooks
HESTIA_BLUEPRINTS=/config/hestia/library/templates/blueprints
HESTIA_DEVICES=/config/hestia/config/devices
HESTIA_NETWORK=/config/hestia/config/network
HESTIA_VAULT=/config/hestia/workspace/archive/vault
HESTIA_BACKUPS=/config/hestia/workspace/archive/vault/backups
HESTIA_CACHE=/config/hestia/workspace/cache
HESTIA_SCRATCH=/config/hestia/workspace/cache/scratch
HESTIA_PROMPTS=/config/hestia/library/prompts
HESTIA_GOVERNANCE=/config/hestia/library/docs/governance
HESTIA_TODO=/config/hestia/workspace/todo
HESTIA_LOGS=/config/hestia/workspace/operations/logs
HESTIA_SCRIPTS=/config/hestia/tools/scripts
HESTIA_UTILS=/config/hestia/tools/utils
ADR_HA_Hestia=/config/hestia/library/docs/ADR
ADR_HA_Omega=${OMEGA_ADR_DIR:-/config/hestia/library/docs/ADR-imports/omega}
ADR_BB8=${BB8_DOCS_ADR_DIR:-/config/hestia/library/docs/ADR-imports/bb8}
ENV

# VS Code
cat > .vscode/tasks.json <<'TASKS'
{ "version":"2.0.0",
  "tasks":[
    {"label":"ADR-0024: Health","type":"shell","command":"${workspaceFolder}/bin/config-health /config","options":{"env":{"CONFIG_ROOT":"/config","HA_MOUNT":"/config","HA_MOUNT_OPERATOR":"/config"},"cwd":"${workspaceFolder}"},"problemMatcher":[]},
    {"label":"ADR-0024: Lint Paths","type":"shell","command":"${workspaceFolder}/tools/lint_paths.sh","options":{"env":{"CONFIG_ROOT":"/config"},"cwd":"${workspaceFolder}"},"problemMatcher":[]},
    {"label":"ADR-0024: Fix Path Drift (dry-run echo)","type":"shell","command":"echo 'Review changes in VCS after running tools/fix_path_drift.sh'","options":{"cwd":"${workspaceFolder}"},"problemMatcher":[]},
    {"label":"ADR-0024: VS Code Env Smoke","type":"shell","command":"${workspaceFolder}/bin/vscode-env-smoke","options":{"env":{"CONFIG_ROOT":"/config","HA_MOUNT":"/config","HA_MOUNT_OPERATOR":"/config"},"cwd":"${workspaceFolder}"},"problemMatcher":[]}
  ]
}
TASKS

cat > .vscode/hass-live.code-workspace <<'WS'
{ "folders":[{"path":"."}],
  "settings":{
    "terminal.integrated.env.osx":{"PATH":"/opt/homebrew/bin:${env:PATH}","CONFIG_ROOT":"/config","HA_MOUNT":"/config","HA_MOUNT_OPERATOR":"/config"},
    "terminal.integrated.cwd":"${workspaceFolder}",
    "terminal.integrated.splitCwd":"workspaceRoot",
    "terminal.integrated.inheritEnv":true,
    "python.defaultInterpreterPath":"${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment":true,
    "python.terminal.useEnvFile":true,
    "python.envFile":"${workspaceFolder}/.env",
    "files.watcherExclude":{"**/hestia/workspace/cache/**":true,"**/hestia/workspace/archive/**":true,"**/.venv/**":true,"**/node_modules/**":true},
    "search.exclude":{"**/hestia/workspace/cache/**":true,"**/hestia/workspace/archive/**":true,"**/.venv/**":true,"**/node_modules/**":true}
  }
}
WS

# Devcontainer
cat > .devcontainer/devcontainer.json <<'DC'
{
  "name": "HA @ /config (ADR-0024)",
  "image": "ghcr.io/home-assistant/home-assistant:stable",
  "runArgs": ["--volume=${localWorkspaceFolder}:/config","--user=0:0"],
  "workspaceMount": "source=${localWorkspaceFolder},target=/config,type=bind",
  "workspaceFolder": "/config",
  "remoteUser": "root",
  "customizations": { "vscode": { "settings": { "terminal.integrated.env.linux": { "CONFIG_ROOT": "/config","HA_MOUNT": "/config","HA_MOUNT_OPERATOR": "/config" } },
  "extensions": ["ms-python.python","ms-azuretools.vscode-docker","tamasfe.even-better-toml","redhat.vscode-yaml"] } }
}
DC

# Compose
cat > docker-compose.yml <<'COMP'
version: "3.9"
services:
  ha:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: ha-dev
    user: "0:0"
    volumes:
      - /System/Volumes/Data/homeassistant:/config
    environment:
      - TZ=UTC
    healthcheck:
      test: ["CMD", "bash", "-lc", "[ -d /config ] || exit 1" ]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
COMP

# CI workflow
mkdir -p .github/workflows
cat > .github/workflows/ha-canonical-guard.yml <<'YML'
name: ADR-0024 Canonical Guard
on:
  push: { branches: [ "**" ] }
  pull_request: { branches: [ "**" ] }
jobs:
  guard-linux-container:
    runs-on: ubuntu-latest
    container:
      image: ubuntu:24.04
      options: --volume ${{ github.workspace }}:/config
    steps:
      - uses: actions/checkout@v4
      - name: Bootstrap tools
        run: apt-get update && apt-get install -y ripgrep bash python3
      - name: Lint paths
        working-directory: /config
        run: tools/lint_paths.sh
      - name: Config health
        working-directory: /config
        run: bin/config-health /config
  guard-macos-smoke:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ripgrep
        run: brew install ripgrep || true
      - name: Lint paths (no /config bind here)
        run: tools/lint_paths.sh
YML

# Pre-commit
cat > .pre-commit-config.yaml <<'PC'
repos:
  - repo: local
    hooks:
      - id: adr0024-path-lint
        name: ADR-0024 Path Lint
        entry: tools/lint_paths.sh
        language: system
        pass_filenames: false
        stages: [commit, push]
PC

# HA shell_command include
mkdir -p config/includes
cat > config/includes/shell_command.yaml <<'SC'
ha_git_push: "/config/tools/ha_git_push.sh /config"
SC

# Ensure configuration.yaml references the include (no destructive edits)
grep -q 'shell_command:' configuration.yaml 2>/dev/null || \
  printf "\n# ADR-0024 include\nshell_command: !include config/includes/shell_command.yaml\n" >> configuration.yaml
```

4. **Load LaunchAgent (user context)**

```bash
launchctl unload ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist
```

5. **Synthetic mapping (idempotent)**

```bash
# Ensure Data-backed directory exists
sudo mkdir -p /System/Volumes/Data/homeassistant
sudo chown "$USER":staff /System/Volumes/Data/homeassistant
# Re-materialize synthetic entries after first setup or OS update
sudo automount -vc
```

6. **Optional: disable Spotlight indexing on backing dir**

```bash
mdutil -i off /System/Volumes/Data/homeassistant 2>/dev/null || true
```

---

## Validation Suite

### macOS host (binary)

```bash
# Firmlink presence and health
bin/config-health /config

# Guard in RO mode
REQUIRE_CONFIG_WRITABLE=0 bin/require-config-root

# LaunchAgent status & recent log tail
launchctl list | grep -q com.hestia.mount.homeassistant && echo OK
tail -n 20 ~/Library/Logs/hestia.mount.out 2>/dev/null || true

# Linter
tools/lint_paths.sh

# VS Code env smoke (run from VS Code integrated terminal or here)
CONFIG_ROOT=/config bin/vscode-env-smoke
```

### Linux / CI container (binary)

```bash
# Executed in container job with /config bind
cd /config
tools/lint_paths.sh
bin/config-health /config
```

### Compose (binary)

```bash
docker compose up -d
docker inspect -f '{{json .State.Health}}' ha-dev | jq .
docker exec ha-dev bash -lc '[ -d /config ] && echo OK || exit 1'
docker compose down
```

### HA runtime (non-destructive)

```bash
# Verify shell_command include is discoverable from /config
grep -q 'ha_git_push:' /config/config/includes/shell_command.yaml && echo OK
```

---

## Rollback

* **Scripts/config files**: Restore `*.bak_adr0024` where present or `git checkout -- <path>`.
* **LaunchAgent**:

  ```bash
  launchctl unload ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist || true
  rm -f ~/Library/LaunchAgents/com.hestia.mount.homeassistant.plist
  ```
* **Mount script**:

  ```bash
  rm -f /Users/evertappels/bin/ha-mount.sh
  ```
* **Dev/CI configs**:

  ```bash
  rm -f .devcontainer/devcontainer.json .vscode/tasks.json .vscode/hass-live.code-workspace \
        .github/workflows/ha-canonical-guard.yml .pre-commit-config.yaml docker-compose.yml
  ```
* **HA include**:

  ```bash
  rm -f config/includes/shell_command.yaml
  # Manually remove the include line from configuration.yaml if added.
  ```

---

## Risks & Mitigations

* **SMB password exposure in process list** during mount:

  * *Mitigation:* Use a Keychain item and keep retries minimal. Consider `.nsmbrc` for passwordless mounting in future; current approach confines exposure to brief window.
* **Network unavailable at login**:

  * *Mitigation:* `KeepAlive.NetworkState` with retry interval.
* **Firmlink not materialized** due to existing node at `/config`:

  * *Mitigation:* Ensure clean namespace; `sudo automount -vc` (or reboot once after initial setup).
* **CI missing ripgrep**:

  * *Mitigation:* Workflow bootstraps `ripgrep` or falls back to `grep`.
* **Developer caches causing editor lag**:

  * *Mitigation:* VS Code watcher/search excludes for caches and archives.

---

## Acceptance Criteria (binary)

* `/config` exists on macOS and resolves to `/System/Volumes/Data/homeassistant`.
* `bin/require-config-root` passes in RO and RW modes.
* `tools/lint_paths.sh` reports “OK: path lint passed”.
* VS Code task “ADR-0024: Health” prints realpath and exits 0.
* Devcontainer opens with `/config` as workspaceFolder.
* CI workflow completes both jobs with success.
* Compose service healthcheck passes.
* `configuration.yaml` includes `config/includes/shell_command.yaml` and that file uses `/config` only.
* Deprecated ADRs are isolated under `ADR/deprecated/**` and linter excludes `library/docs/ADR-imports/**`.

END OF DELIVERABLE
