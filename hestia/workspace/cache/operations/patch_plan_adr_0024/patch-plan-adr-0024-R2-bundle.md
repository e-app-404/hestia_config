# Patch bundle R2 (drop-in)

## 1) Guard: no symlink assumption, optional RO

**File:** `tools/lib/require-config-root.sh` (replace)

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${CONFIG_ROOT:=/config}"

# Directory check (covers APFS firmlink)
if [[ ! -d "$CONFIG_ROOT" ]]; then
  echo "[guard] ERROR: $CONFIG_ROOT missing or not a directory" >&2
  exit 2
fi

# Allow read-only contexts when explicitly requested
: "${REQUIRE_CONFIG_WRITABLE:=1}"
if [[ "${REQUIRE_CONFIG_WRITABLE}" = "1" && ! -w "$CONFIG_ROOT" ]]; then
  echo "[guard] ERROR: $CONFIG_ROOT not writable; set REQUIRE_CONFIG_WRITABLE=0 for RO contexts" >&2
  exit 3
fi

# Helpful resolution log
if command -v realpath >/dev/null 2>&1; then
  echo "[guard] OK: $(realpath "$CONFIG_ROOT")"
else
  python3 - <<'PY' 2>/dev/null || echo "[guard] OK: $CONFIG_ROOT"
import os; print("[guard] OK:", os.path.realpath("/config"))
PY
fi
```

## 2) Smoke test: binary, RO-tolerant

**File:** `tools/smoke_config_root.sh` (replace)

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

## 3) macOS synthetic `/config` (firmlink), single target

> Pick **one** realpath; example uses `/System/Volumes/Data/homeassistant`. Do **not** also mount or symlink onto `/config`.

**/etc/synthetic.conf** (append or edit):

```
config	homeassistant
```

Then:

```bash
sudo mkdir -p /System/Volumes/Data/homeassistant
sudo chown "$USER":staff /System/Volumes/Data/homeassistant
# Rebuild synthetic entries (Ventura/Sonoma)
sudo /System/Library/Filesystems/apfs.fs/Contents/Resources/apfs.util -B
# Sanity (no symlink assumption)
[[ -d /config ]] && python3 -c 'import os; print(os.path.realpath("/config"))'
```

**Clean up old drift (run once):**

```bash
# If an old symlink or mount onto /config exists, remove it
[[ -L /config ]] && sudo rm /config || true
mount | grep -qE ' /config ' && { echo "ERROR: /config is a mountpoint; unmount it"; exit 1; } || true
```

## 4) Autofs: mount the **Data** path, not `/config`

> If you use autofs, target the real directory. Let synthetic expose `/config`.

**/etc/auto_master** (add once):

```
/-	auto_homeassistant
```

**/etc/auto_homeassistant** (create/replace):

```
/System/Volumes/Data/homeassistant  -fstype=smbfs  ://user@fileserver/homeassistant
# or for NFS:
#/System/Volumes/Data/homeassistant  -fstype=nfs,nfc,tcp,resvport,rw  nfs.example:/export/homeassistant
```

Then:

```bash
sudo automount -cv
ls -ld /System/Volumes/Data/homeassistant >/dev/null
[[ -d /config ]] || { echo "No /config firmlink"; exit 1; }
```

## 5) LaunchAgent: absolute log paths, no `${HOME}`

**File:** `~/Library/LaunchAgents/com.hestia.ensure-config-root.plist` (replace `USERNAME`)

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
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>120</integer>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StandardOutPath</key><string>/Users/USERNAME/Library/Logs/ensure-config-root.out</string>
  <key>StandardErrorPath</key><string>/Users/USERNAME/Library/Logs/ensure-config-root.err</string>
</dict></plist>
```

**File:** `/usr/local/bin/ensure-config-root.sh` (replace)

```bash
#!/usr/bin/env bash
set -euo pipefail
CONFIG_ROOT="/config"
REAL_ROOT="/System/Volumes/Data/homeassistant"
SENTINEL=".ha_config_root"

# Trigger autofs if present
ls -ld "$REAL_ROOT" >/dev/null 2>&1 || true

# Directory health
if [[ ! -d "$CONFIG_ROOT" ]]; then
  echo "[ensure-config-root] ERROR: /config missing (synthetic not applied?)"; exit 1
fi

# Optional sentinel (best-effort; ignore if RO)
: >"$REAL_ROOT/$SENTINEL" 2>/dev/null || true

# Final log without symlink assumptions
python3 - <<PY || true
import os,sys
p="/config"
print("[ensure-config-root] OK:", os.path.realpath(p) if os.path.isdir(p) else "MISSING")
PY
```

```bash
mkdir -p ~/Library/Logs
chmod +x /usr/local/bin/ensure-config-root.sh
launchctl unload ~/Library/LaunchAgents/com.hestia.ensure-config-root.plist 2>/dev/null || true
launchctl load -w ~/Library/LaunchAgents/com.hestia.ensure-config-root.plist
```

## 6) GitHub Actions: split Linux/macOS semantics

**Snippet for Linux jobs:**

```yaml
- name: Ensure /config (Linux host-runner)
  if: runner.os == 'Linux' && !startsWith(matrix.container, 'ghcr.io/home-assistant')
  run: |
    set -euo pipefail
    sudo mkdir -p /config
    sudo mount --bind "$GITHUB_WORKSPACE" /config
    [[ -d /config ]] && ls -ld /config
```

**Snippet for macOS jobs:**

```yaml
- name: macOS: workspace-local alias for tools
  if: runner.os == 'macOS'
  run: |
    set -euo pipefail
    mkdir -p "$PWD/.ci-config"
    ln -sfn "$PWD" "$PWD/.ci-config/config"
    echo "LOCAL_CONFIG=$PWD/.ci-config/config" >> $GITHUB_ENV
```

> Use `${LOCAL_CONFIG}` for host-side steps. Inside containers, still mount to `/config` as usual.

## 7) Linter: safer scope + `rg` fallback

**File:** `tools/lint_paths.sh` (replace)

```bash
#!/usr/bin/env bash
set -euo pipefail

PATTERN='\$HOME/|~/hass|/Volumes/(HA/Config|Config)|/n/ha|actions-runner/.+?/hass'
INCLUDE='(config|tools|scripts|packages|custom_components|.github|.devcontainer|.vscode)/'

if command -v rg >/dev/null 2>&1; then
  rg -nE "$PATTERN" --hidden -g '!ADR/**' -g '!ADR/deprecated/**' -g '!**/*.md' -g '!**/*.png' -g '!**/*.jpg' -g '!**/*.svg' -g '!**/.git/**' -g '!**/node_modules/**' -g '!**/.venv/**' -g "$INCLUDE" .
else
  grep -RInE "$PATTERN" --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=ADR/deprecated --exclude=ADR/** --exclude='*.md' -- . | grep -E "$INCLUDE"
fi

if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
  echo 'ERROR: Disallowed path alias detected. Use /config only.' >&2
  exit 1
else
  echo 'OK: path lint passed'
fi
```

**.pre-commit hook (update if you use pre-commit):**

```yaml
repos:
  - repo: local
    hooks:
      - id: ha-path-lint
        name: HA Path Lint
        entry: tools/lint_paths.sh
        language: system
        files: '^(config|tools|scripts|packages|custom_components|\.github|\.devcontainer|\.vscode)/'
```

## 8) Bulk replace: narrowed, idempotent

**File:** `tools/fix_path_drift.sh` (new)

```bash
#!/usr/bin/env bash
set -euo pipefail
FILES=$(git ls-files ':config/**' ':tools/**' ':scripts/**' ':packages/**' ':custom_components/**' ':**/*.yaml' ':**/*.yml')
for f in $FILES; do
  cp -n "$f" "$f.bak_driftfix" 2>/dev/null || true
  gsed -i -E 's#(~|\$HOME)/hass#/config#g; s#/Volumes/HA/Config#/config#g; s#/Volumes/Config#/config#g; s#/n/ha#/config#g' "$f" || true
done
echo "Done. Backups: *.bak_driftfix"
```

## 9) HA `shell_command` (affirm change)

**File:** `config/configuration.yaml` (confirm present)

```yaml
shell_command:
  ha_git_push: "/config/tools/ha_git_push.sh /config"
```

**File:** `config/tools/ha_git_push.sh` (ensure guard + RO toggle)

```bash
#!/usr/bin/env bash
set -euo pipefail
export REQUIRE_CONFIG_WRITABLE=1
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

# Binary validation (copy/paste)

**Operator host (macOS):**

```bash
# 1) /config is a directory (firmlink OK)
[[ -d /config ]] || exit 1
python3 - <<'PY'
import os; p="/config"; assert os.path.isdir(p); print(os.path.realpath(p))
PY

# 2) If autofs is used, it targets Data path (not /config)
df -h /System/Volumes/Data/homeassistant || true

# 3) No mountpoint/symlink onto /config
mount | grep -qE ' /config ' && { echo "FAIL: /config is a mount point"; exit 1; } || echo OK
```

**Repo guard:**

```bash
tools/lint_paths.sh
```

**HA runtime:**

```bash
ha core check
/config/tools/ha_git_push.sh /config; echo EXIT:$?
```

**CI (Linux container):**

```bash
[[ -d /config ]] && hass --script check_config -c /config
```

---

# Copilot ground rules (snippets to drop in `.github/COPILOT.md`)

```markdown
- Canonical path is **/config**. Never propose `$HOME/...`, `~/hass`, `/Volumes/...`, or `/n/ha`.
- If a path variable is needed, name it `CONFIG_ROOT` with default `/config`.
- On macOS, **/config is a firmlink** (synthetic); do not rely on `readlink`.
- Host steps on macOS may use a workspace-local alias `${LOCAL_CONFIG}`; container steps still mount to `/config`.
- Do not mount or symlink directly onto `/config`. Autofs should target the Data path; synthetic exposes `/config`.
- Prefer read-only checks where appropriate; set `REQUIRE_CONFIG_WRITABLE=0` for CI.
```

---

# What’s left / finite next steps

1. Apply this bundle (file replaces + host config snippets).
2. Run the **Binary validation** section.
3. (Optional) Wire `tools/fix_path_drift.sh` into a one-time migration PR; keep `tools/lint_paths.sh` in pre-commit thereafter.
4. If any environment still assumes `readlink /config`, switch it to `python os.path.realpath('/config')`.
