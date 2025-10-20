
The checklist of touchpoints that usually slip through the cracks, plus ready-to-paste snippets/instructions for each. 

Everything assumes **`/config` is the canonical path** and anything else is implementation detail.

---

## 1) macOS synthetic `/config` (root-level symlink)

**Why:** Make `/config` exist at the filesystem root and point at the real storage path. One-time, zero-maintenance.

**Do this (pick one target):**

**A. Target a root path** `/homeassistant` (good for autofs/NFS):

```bash
# One-time setup (requires sudo)
sudo mkdir -p /homeassistant
printf "config\thomeassistant\n" | sudo tee -a /etc/synthetic.conf >/dev/null
# Rebuild synthetic entries (or reboot to be safe)
sudo /System/Library/Filesystems/apfs.fs/Contents/Resources/apfs.util -B
# Verify
ls -ld /config && readlink /config
```

**B. Target a user path** `/Users/evertappels/homeassistant` (good for user-space SMB mounts, no sudo at runtime):

```bash
mkdir -p /Users/evertappels/homeassistant
printf "config\tUsers/evertappels/homeassistant\n" | sudo tee -a /etc/synthetic.conf >/dev/null
sudo /System/Library/Filesystems/apfs.fs/Contents/Resources/apfs.util -B
ls -ld /config && readlink /config
```

---

## 2) Autofs: zero-touch network mount to the realpath

**Why:** Auto-mount the HA share on demand so `/config` always works; no login scripts, no clicking.

**NFS (recommended for reliability):**

```bash
# /etc/auto_master (add a direct map)
echo "/- auto_homeassistant" | sudo tee -a /etc/auto_master

# /etc/auto_homeassistant (create/overwrite)
sudo tee /etc/auto_homeassistant >/dev/null <<'EOF'
/homeassistant  -fstype=nfs,nfc,tcp,resvport,rw  nfs.example.lan:/export/homeassistant
EOF

sudo automount -cv
# Verify triggers:
ls /homeassistant
```

**SMB (works; credentials handled via Keychain or guest share):**

```bash
echo "/- auto_homeassistant" | sudo tee -a /etc/auto_master

sudo tee /etc/auto_homeassistant >/dev/null <<'EOF'
/homeassistant  -fstype=smbfs  ://username@fileserver.lan/homeassistant
EOF

sudo automount -cv
ls /homeassistant
```

> Tip: Store SMB creds once:

```bash
security add-internet-password -a "username" -s "fileserver.lan" -r "smb " -w "YOUR_PASSWORD" -U
```

---

## 3) LaunchAgent: health-check + gentle self-healing

**Why:** Detect drift early (after sleep/network changes) and log actionable hints. No root needed if autofs already manages the mount.

**File:** `~/Library/LaunchAgents/com.hestia.ensure-config-root.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.hestia.ensure-config-root</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/ensure-config-root.sh</string>
  </array>
  <key>StartInterval</key><integer>120</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>/tmp/ensure-config-root.out</string>
  <key>StandardErrorPath</key><string>/tmp/ensure-config-root.err</string>
  <key>KeepAlive</key>
  <dict>
    <key>NetworkState</key><true/>
  </dict>
</dict></plist>
```

**File:** `/usr/local/bin/ensure-config-root.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
CONFIG_ROOT="/config"
REAL_ROOT="/homeassistant"   # or /Users/evertappels/homeassistant
SENTINEL=".ha_config_root"

# 1) Ensure synthetic link exists and points correctly (read-only check)
if [[ ! -L "$CONFIG_ROOT" ]]; then
  echo "[ensure-config-root] ERROR: $CONFIG_ROOT missing (synthetic.conf not applied?)"
  exit 1
fi

# 2) Touch path to trigger autofs
ls -ld "$REAL_ROOT" >/dev/null 2>&1 || true

# 3) Mount health
if ! df "$REAL_ROOT" >/dev/null 2>&1; then
  echo "[ensure-config-root] WARN: $REAL_ROOT not mounted. autofs should mount on access."
  # Trigger once more:
  (ls -la "$REAL_ROOT" >/dev/null 2>&1) || true
fi

# 4) Sentinel
if [[ ! -e "$REAL_ROOT/$SENTINEL" ]]; then
  echo "[ensure-config-root] Creating sentinel: $REAL_ROOT/$SENTINEL"
  ( : > "$REAL_ROOT/$SENTINEL" ) || echo "[ensure-config-root] WARN: cannot write sentinel"
fi

# 5) Final check that /config resolves and is readable
test -r "$CONFIG_ROOT" || { echo "[ensure-config-root] ERROR: $CONFIG_ROOT not readable"; exit 1; }
echo "[ensure-config-root] OK: $(readlink $CONFIG_ROOT) -> $(df -h $REAL_ROOT | tail -1)"
```

```bash
# Install
chmod +x /usr/local/bin/ensure-config-root.sh
launchctl unload ~/Library/LaunchAgents/com.hestia.ensure-config-root.plist 2>/dev/null || true
launchctl load -w ~/Library/LaunchAgents/com.hestia.ensure-config-root.plist
```

---

## 4) “Require config root” library (sourced by any script)

**Why:** Hard fail if a tool tries to use anything but `/config`.

**File:** `tools/lib/require-config-root.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${CONFIG_ROOT:=/config}"
if [[ "$CONFIG_ROOT" != "/config" ]]; then
  echo "[guard] CONFIG_ROOT must be /config (got: $CONFIG_ROOT)"; exit 64
fi
if [[ ! -d "$CONFIG_ROOT" ]]; then
  echo "[guard] /config not present; mount or synthetic.conf missing"; exit 65
fi
```

**Use in any script:**

```bash
source "$(dirname "$0")/../lib/require-config-root.sh"
```

---

## 5) Home Assistant `configuration.yaml` sanity (shell_command)

**Why:** Eliminate path drift inside HA automations.

```yaml
# configuration.yaml
shell_command:
  ha_git_push: "/config/tools/ha_git_push.sh /config"
```

**File:** `/config/tools/ha_git_push.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
source /config/tools/lib/require-config-root.sh
ROOT="${1:-/config}"
git -C "$ROOT" add -A
git -C "$ROOT" commit -m "HA: automated commit $(date +%FT%T%z)" || true
git -C "$ROOT" push origin HEAD:main
```

```bash
chmod +x /config/tools/ha_git_push.sh
```

---

## 6) GitHub Actions (self-hosted or cloud) preflight

**Why:** CI should see `/config` even if runners are ephemeral.

```yaml
# .github/workflows/ci.yml (top of jobs.* steps)
- name: Ensure /config (Linux host-runner)
  if: runner.os == 'Linux' && !startsWith(matrix.container, 'ghcr.io/home-assistant')
  run: |
    set -euo pipefail
    sudo mkdir -p /config
    sudo mount --bind "$GITHUB_WORKSPACE" /config
    [[ -d /config ]] && ls -ld /config
```

> If your runner is macOS: replace the bind mount with `ln -sfn "$GITHUB_WORKSPACE" /homeassistant` (no bind mounts on macOS), and ensure synthetic `/config` was pre-provisioned on that runner image.

---

## 7) Devcontainer (VS Code)

**Why:** Dev tooling must agree on `/config`.

**File:** `.devcontainer/devcontainer.json`

```json
{
  "name": "HA Config",
  "image": "ghcr.io/home-assistant/devcontainer:stable",
  "mounts": [
    "source=${localWorkspaceFolder},target=/config,type=bind,consistency=cached"
  ]
}
```

---

## 8) VS Code tasks for config validation

**Why:** One tap to validate HA config against `/config`.

**File:** `.vscode/tasks.json`

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "HA: check_config",
      "type": "shell",
      "command": "hass --script check_config -c /config",
      "problemMatcher": []
    }
  ]
}
```

---

## 9) Pre-commit path linter (blocks drift in PRs)

**Why:** Prevent re-introducing `$HOME/hass`, `/Volumes/...`, `~/hass`, etc.

**File:** `tools/lint_paths.py`

```python
#!/usr/bin/env python3
import re, sys, pathlib
BAD = [
    r"\$HOME/[^ ]", r"~/hass", r"/Volumes/HA/Config", r"/Volumes/Config",
    r"/n/ha", r"/Users/.+/Projects/actions-runner/hass"
]
pat = re.compile("|".join(BAD))
fail = []
for p in sys.argv[1:]:
    text = pathlib.Path(p).read_text(errors="ignore")
    if pat.search(text):
        fail.append(p)
if fail:
    print("Path drift detected in:", *fail, sep="\n - ")
    sys.exit(1)
```

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: ha-path-lint
        name: HA Path Lint
        entry: tools/lint_paths.py
        language: python
        files: '^(?!ADR/).*'   # lint all but ADRs
```

```bash
pipx install pre-commit || pip install pre-commit
pre-commit install
```

---

## 10) Zsh prompt guard (developer UX)

**Why:** Scream if working outside `/config`.

**Add to `~/.zshrc`:**

```bash
export PROMPT='%F{%(?::red)}%n@%m%f %1~ %# '
function chpwd() {
  if [[ "$PWD" != /config* ]]; then
    print -P "%F{yellow}[warn]%f Not in /config (here: $PWD)"
  fi
}
```

---

## 11) Template/heredoc policy (Copilot-friendly)

**Why:** Generated scripts must use `/config` too.

**Rule:** Replace any `$HOME/...` or templated `${HOME}/...` in heredocs with `/config/...`. For literal (single-quoted) heredocs, update the literal.

**One-shot fixer (safe backup):**

```bash
git ls-files | xargs gsed -i.bak -E "s#(~|\$HOME)/hass#\/config#g; s#/Volumes/(HA/Config|Config)#/config#g; s#/n/ha#/config#g"
```

---

## 12) ADR index refresh + deprecations (mechanical)

**Why:** Keep machine-parsing sane.

**File:** `tools/adr_refresh.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
ADR_DIR="ADR"
DEPR="$ADR_DIR/deprecated"
mkdir -p "$DEPR"
# Ensure statuses
gsed -i -E 's/^Status: (Proposed|Accepted|Superseded).*/Status: Superseded by ADR-0024/' \
  "$ADR_DIR"/ADR-0010*.md "$ADR_DIR"/ADR-0012*.md "$ADR_DIR"/ADR-0016*.md || true
git mv -f "$ADR_DIR"/ADR-0010*.md "$DEPR"/ 2>/dev/null || true
git mv -f "$ADR_DIR"/ADR-0012*.md "$DEPR"/ 2>/dev/null || true
git mv -f "$ADR_DIR"/ADR-0016*.md "$DEPR"/ 2>/dev/null || true
# Rebuild index (simple)
printf "# ADR Index\n\n" > "$ADR_DIR/README.md"
for f in $(ls -1 "$ADR_DIR" | sort); do echo "- $f" >> "$ADR_DIR/README.md"; done
```

---

## 13) HA add-ons & Supervisor expectations

**Why:** Add-ons expect `/config` inside their containers; bind it from the host if you’re on supervised/docker installs.

**Docker-Compose example (if you run Core in Docker):**

```yaml
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    volumes:
      - /System/Volumes/Data/homeassistant:/config
    network_mode: host
    restart: unless-stopped
```

---

## 14) Time Machine / Spotlight exclusions (optional, avoids churn)

**Why:** Don’t back up fast-changing HA states.

```bash
# Spotlight ignore
sudo mdutil -i off /homeassistant
# Time Machine ignore
sudo tmutil addexclusion /homeassistant
```

---

## 15) Minimal “smoke test” for all environments

**Why:** One command to confirm alignment.

**File:** `tools/smoke_config_root.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
[[ -d /config ]] || { echo "FAIL: /config not a directory"; exit 1; }
python3 - <<'PY'
import os; p="/config"
assert os.path.isdir(p), "/config not a directory"
print("OK:", os.path.realpath(p))
PY
echo "OK: directory check passed"
```

---

## 16) Copilot prompt to auto-fix path drift (drop in `.github/COPILOT.md`)

**Why:** Guide Copilot to suggest the right paths in PRs.

```markdown
# Copilot Ground Rules: Home Assistant Paths
- Canonical path is **/config**. Never propose `$HOME/...`, `~/hass`, `/Volumes/...`, or `/n/ha`.
- For shell_command and scripts, assume `/config/tools/...`.
- For Docker/devcontainer, bind host realpath to container `/config`.
- If a path variable is needed, name it `CONFIG_ROOT` and set it to `/config` by default.
```

---

## 17) Optional Windows/WSL parity (if ever needed)

**Why:** Keep cross-platform contributors from re-introducing drift.

```powershell
# PowerShell (WSL): create /config symlink to /mnt/w/homeassistant
wsl.exe -d Ubuntu -- bash -lc 'sudo mkdir -p /mnt/w/homeassistant && sudo ln -sfn /mnt/w/homeassistant /config'
```

---

### What this covers

* Concrete **LaunchAgent** and **ensure-config** script (installable today).
* **Autofs** recipes for NFS/SMB (true zero-touch).
* **CI/GA, devcontainer, VS Code** wiring with `/config`.
* **Pre-commit linter**, **Copilot guardrails**, **docs/index refresh**, and **smoke tests**.
