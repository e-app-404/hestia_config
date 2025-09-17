# Home Assistant Config Environment: Implementation & Automation Contract

## Environment State & Confirmations

- **autofs neutral path `/n/ha`:** Enabled. SMB shares available:
  - `smb://homeassistant.local/`
  - `smb://homeassistant.reverse-beta.ts.net` (Tailscale)
- **SMB credentials:**
  - Present in macOS Keychain (generic SMB credentials added)
  - Also available in `~/.nsmbrc`
- **Python venv:**
  - Exists at `$HESTIA_CONFIG/.venv`
  - `python3` available at `/opt/homebrew/bin/python3`
- **Git root:**
  - `<config>` (`$HESTIA_CONFIG`) is the git root for your repo
  - All git operations use `<config>` as both repository root and work tree

---

## 1. Environment Variables & Path Resolution

- **Authoritative Variable:**  
  `$HESTIA_CONFIG` is the single source of truth for your Home Assistant config root.  
  Always resolve this using a robust locator script (`ha_path.sh`).

- **Path Candidates (priority order):**  
  - `$HESTIA_CONFIG_OVERRIDE` (manual override)
  - `$HOME/hestia-config` (symlink, optional)
  - `/n/ha` (autofs mount, optional)
  - `/Volumes/HA/config`
  - `/Volumes/HA/config`

- **Validation:**  
  The chosen path must be a directory containing `configuration.yaml`.

- **Portable Realpath:**  
  Use Python or shell to resolve real paths, avoiding brittle absolute paths.

## 2. Hardened Locator Script (`ha_path.sh`)

- **Purpose:**  
  - Exports `$HESTIA_CONFIG` after validating presence of configuration.yaml.
  - Optionally exports `$HESTIA_VENV` if a Python venv exists.
  - Emits clear `BLOCKED:` diagnostics if resolution fails.
  - Idempotent and case-agnostic.

- **Usage:**  
  - Source in every shell/Copilot session:  
    `source ~/ha_path.sh`  
  - All scripts/tools reference `$HESTIA_CONFIG` for paths.

- **Code**

```bash
#!/bin/bash
# ~/ha_path.sh — resilient locator for Home Assistant config
# Idempotent; emits BLOCKED: diagnostics on failure

set -Eeuo pipefail
IFS=$'\n\t'

: "${HESTIA_CONFIG_OVERRIDE:=}"

_candidates=(
  "$HESTIA_CONFIG_OVERRIDE"
  "$HOME/hestia-config"        # symlink (optional)
  "/n/ha"                      # autofs neutral path (optional)
  "/Volumes/HA/config"
  "/Volumes/HA/config"
)

_realpath() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$1" <<'PY'
import os,sys
print(os.path.realpath(sys.argv[1]))
PY
  else
    (cd "$1" 2>/dev/null && pwd) || return 1
  fi
}

# case-insensitive config filename resolution (returns path to the file if present)
_cfg_file() {
  local d="$1"
  for n in configuration.yaml Configuration.yaml CONFIGURATION.YAML; do
    [ -f "$d/$n" ] && { echo "$n"; return 0; }
  done
  return 1
}

_resolve_first() {
  local p f
  for p in "${_candidates[@]}"; do
    [ -n "$p" ] || continue
    if [ -d "$p" ] && f="$(_cfg_file "$p")"; then
      printf "%s\n" "$(_realpath "$p")"
      return 0
    fi
  done
  return 1
}

_die() {
  echo "BLOCKED: unable to locate Home Assistant config root (configuration.yaml)" >&2
  echo "Checked:" >&2
  local p
  for p in "${_candidates[@]}"; do
    [ -n "$p" ] || continue
    printf ' - %s : ' "$p" >&2
    if [ -e "$p" ]; then
      if [ -d "$p" ]; then
        if f="$(_cfg_file "$p")"; then
          echo "OK (has $f)" >&2
        else
          echo "MISSING configuration.yaml (any case)" >&2
        fi
      else
        echo "NOT A DIRECTORY" >&2
      fi
    else
      echo "NOT FOUND" >&2
    fi
  done
  echo "Fix: mount the HA 'config' share or set HESTIA_CONFIG_OVERRIDE to the correct path." >&2
  exit 2
}

if ! HESTIA_CONFIG="$(_resolve_first)"; then _die; fi
export HESTIA_CONFIG

# expose the resolved config filename for tools (e.g., VS Code helpers)
if f="$(_cfg_file "$HESTIA_CONFIG")"; then
  export HESTIA_CONFIG_FILE="$f"
fi

# Optional venv convenience
if [ -x "$HESTIA_CONFIG/.venv/bin/python" ]; then
  export HESTIA_VENV="$HESTIA_CONFIG/.venv/bin/python"
  export PATH="$HESTIA_CONFIG/.venv/bin:$PATH"
fi

# Guard common footguns
[ -w "$HESTIA_CONFIG" ] || echo "WARN: $HESTIA_CONFIG is not writable; some tasks may fail." >&2
```

## 3. One-Time Installer Script

- **Creates:**  
  - Symlink `$HOME/hestia-config` to the resolved config path.
  - Installs `ha_path.sh` in `$HOME`.
  - Optionally auto-sources in `.zshrc`/`.bashrc`.
  - Smoke-tests resolution.

- **Run:**  
  ```bash
  bash ~/install_hestia_locator.sh
  source ~/ha_path.sh
  ```
- **Code**

```bash
#!/bin/bash
set -Eeuo pipefail
IFS=$'\n\t'

# Prefer lowercase mount, then uppercase; if neither present, skip symlink (autofs may be used)
if [ -d /Volumes/HA/config ]; then target=/Volumes/HA/config
elif [ -d /Volumes/HA/config ]; then target=/Volumes/HA/config
else target=""
fi

# Create/refresh a convenient symlink if a target is known
if [ -n "$target" ]; then
  rm -f "$HOME/hestia-config"
  ln -s "$target" "$HOME/hestia-config"
fi

# Write resolver (idempotent overwrite)
cat > "$HOME/ha_path.sh" <<'EOF'
# BEGIN ha_path.sh
#!/bin/bash
set -Eeuo pipefail
IFS=$'\n\t'
: "${HESTIA_CONFIG_OVERRIDE:=}"
_candidates=("$HESTIA_CONFIG_OVERRIDE" "$HOME/hestia-config" "/n/ha" "/Volumes/HA/config" "/Volumes/HA/config")
_realpath(){ if command -v python3 >/dev/null 2>&1; then python3 - "$1" <<'PY'
import os,sys;print(os.path.realpath(sys.argv[1]))
PY
else (cd "$1" 2>/dev/null && pwd)||return 1; fi; }
_cfg_file(){ local d="$1"; for n in configuration.yaml Configuration.yaml CONFIGURATION.YAML; do [ -f "$d/$n" ] && { echo "$n"; return 0; }; done; return 1; }
_resolve_first(){ local p f; for p in "${_candidates[@]}"; do [ -n "$p" ] || continue; if [ -d "$p" ] && f="$(_cfg_file "$p")"; then printf "%s\n" "$(_realpath "$p")"; return 0; fi; done; return 1; }
_die(){ echo "BLOCKED: unable to locate Home Assistant config root (configuration.yaml)"; echo "Fix: mount the HA 'config' share or set HESTIA_CONFIG_OVERRIDE."; exit 2; }
if ! HESTIA_CONFIG="$(_resolve_first)"; then _die; fi; export HESTIA_CONFIG
if f="$(_cfg_file "$HESTIA_CONFIG")"; then export HESTIA_CONFIG_FILE="$f"; fi
if [ -x "$HESTIA_CONFIG/.venv/bin/python" ]; then export HESTIA_VENV="$HESTIA_CONFIG/.venv/bin/python"; export PATH="$HESTIA_CONFIG/.venv/bin:$PATH"; fi
# END ha_path.sh
EOF
chmod +x "$HOME/ha_path.sh"

# Auto-source in interactive shells (guarded)
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
  [ -f "$rc" ] || continue
  grep -q 'ha_path.sh' "$rc" || echo '[[ -f "$HOME/ha_path.sh" ]] && source "$HOME/ha_path.sh"' >> "$rc"
done

# Smoke test (non-fatal)
if source "$HOME/ha_path.sh" 2>/dev/null; then
  echo "Installer complete. HESTIA_CONFIG -> $HESTIA_CONFIG (file: ${HESTIA_CONFIG_FILE:-configuration.yaml})"
else
  echo "Installer complete. Resolver installed; mount not found yet."
fi
```

## 4. autofs Neutral Mount (`/n/ha`)

- **Purpose:**  
  - Provides a reboot-proof, case-proof mount point for the HA config share.
  - Uses `/etc/auto_master` and `/etc/auto_smb` for mapping.
  - Credentials are managed via Keychain or `~/.nsmbrc`.

- **Setup Steps:**  
  - Append autofs mapping to `/etc/auto_master` (guarded).
  - Write `/etc/auto_smb` with the SMB share mapping.
  - Run `sudo automount -cv` to apply.
  - Access `/n/ha` to trigger mount.

- **Code**
```bash
# Create mount base (once)
sudo mkdir -p /n

# Guarded append to auto_master
grep -qE '^\s*/-\s+auto_smb' /etc/auto_master || echo "/-    auto_smb   -nosuid" | sudo tee -a /etc/auto_master >/dev/null

# Define share mapping (safe overwrite)
sudo tee /etc/auto_smb >/dev/null <<'EOF'
# Direct map for Home Assistant config share
# Default to Bonjour (mDNS); switch to Tailscale FQDN if preferred.
#/n/ha  -fstype=smbfs ://homeassistant.reverse-beta.ts.net/config   # Tailscale option
/n/ha   -fstype=smbfs ://homeassistant.local/config
EOF

# Apply (no reboot)
sudo automount -cv

# Touch the path to trigger mount
ls -ld /n/ha || true
```


## 5. VS Code Workspace Settings

- **Config File:**  
  `$HESTIA_CONFIG/.vscode/settings.json`

- **Key Settings:**  
  - `"home-assistant.configFile": "configuration.yaml"`
  - `"python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"`
  - `"yaml.customTags": [...]` (include all HA YAML tags)
  - `"git.enabled": false` (if desired for mono-repo)

- **Open Folder:**  
  Always open via the resolved path or symlink:  
  `code "$HESTIA_CONFIG"` or `code "$HOME/hestia-config"`

**Code**

```json
{
  "home-assistant.configFile": "${workspaceFolder}/${env:HESTIA_CONFIG_FILE}",
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "yaml.customTags": [
    "!include",
    "!include_dir_merge_named",
    "!include_dir_merge_list",
    "!include_dir_list",
    "!include_dir_named",
    "!secret",
    "!env_var"
  ],
  "yaml.schemaStore.enable": true,
  "yaml.schemaStore.url": "https://www.schemastore.org/api/json/catalog.json",
  "yaml.validate": true
}
```

## 6. Doctor Script (`ha_doctor.sh`)

- **Purpose:**  
  - Diagnostics for config path, mount status, git root, ports, and case presence.
  - Non-destructive, emits clear status and evidence.

- **Usage:**  
  ```bash
  bash ~/ha_doctor.sh
  ```

- **Code**
```bash
#!/bin/bash
set -Eeuo pipefail
IFS=$'\n\t'
source "$HOME/ha_path.sh" || exit 2

echo "== HESTIA DOCTOR =="
echo "HESTIA_CONFIG: $HESTIA_CONFIG"
echo "Config file    : ${HESTIA_CONFIG_FILE:-configuration.yaml}"
echo "Exists         : $([ -d "$HESTIA_CONFIG" ] && echo YES || echo NO)"
echo "Writable       : $([ -w "$HESTIA_CONFIG" ] && echo YES || echo NO)"
echo "Git root       : $(git -C "$HESTIA_CONFIG" rev-parse --show-toplevel 2>/dev/null || echo "not a git work tree")"
echo "Mount info     :"
df -h "$HESTIA_CONFIG" | sed -n '1,2p' || true

probe() {
  local h=$1 p=$2
  if command -v nc >/dev/null 2>&1; then
    nc -z -G 1 "$h" "$p" >/dev/null 2>&1 && echo "open" || echo "closed/filtered"
  else
    (echo > /dev/tcp/$h/$p) >/dev/null 2>&1 && echo "open" || echo "closed/filtered"
  fi
}
HA_IP_LAN="192.168.0.129"
echo "Port 8123 (LAN $HA_IP_LAN): $(probe $HA_IP_LAN 8123)"
echo "Port 22222 (HA CLI,  $HA_IP_LAN): $(probe $HA_IP_LAN 22222)"

[ -d /Volumes/HA/config ] && echo "/Volumes/ha present" || echo "/Volumes/ha not present"
[ -d /Volumes/HA/config ] && echo "/Volumes/HA present" || echo "/Volumes/HA not present"
[ -d /n/ha ] && echo "/n/ha mount point present" || echo "/n/ha missing (run autofs setup)"
```

## 7. Automation Contract for Copilot/Tasks

- **Prelude for Every Task:**  

Always begin with: `source ~/ha_path.sh || echo "BLOCKED: locator" && exit 2`
Use `$HESTIA_CONFIG` and `${HESTIA_CONFIG_FILE}` for all paths.
On every action, emit:
  ```
  OK: <what succeeded>
  BLOCKED: <why>
  EVIDENCE: <path|json>
  ```
On failure, propose a one-liner fix.

- **Examples:**  
  ```bash
  source ~/ha_path.sh || exit 2
  git -C "$HESTIA_CONFIG" rev-parse --show-toplevel || echo "EVIDENCE: not a git work tree"
  [ -f "$HESTIA_CONFIG/configuration.yaml" ] || echo "BLOCKED: missing configuration.yaml at $HESTIA_CONFIG"
  ```

## 8. Directory & File Scaffold (Idempotent)

- **Create Directories:**  
  ```bash
  mkdir -p \
    $HESTIA_CONFIG/hestia/tools/install \
    $HESTIA_CONFIG/hestia/tools/system \
    $HESTIA_CONFIG/hestia/tools/doctor \
    $HESTIA_CONFIG/hestia/diagnostics/logs \
    $HESTIA_CONFIG/hestia/templates/autofs \
    $HESTIA_CONFIG/hestia/vault/receipts \
    $HESTIA_CONFIG/hestia/core/governance/output_contracts \
    $HESTIA_CONFIG/hestia/work/out
  ```

- **Create Placeholders:**  
  For each key script/template, create a stub if missing.

## 9. Guardrails & Output Contracts

- All automations/scripts must:
  - Use `$HESTIA_CONFIG` for all repo paths.
  - Never mutate system files without explicit user confirmation.
  - Emit status tokens for success, failure, and evidence.
  - Propose corrective actions on failure.

---

## Manifest of Files
```
/Volumes/HA/config/hestia/tools/ha_path.sh
/Volumes/HA/config/hestia/tools/install/hestia_one_time_install.sh
/Volumes/HA/config/hestia/templates/autofs/auto_master.hestia.snippet
/Volumes/HA/config/hestia/templates/autofs/auto_ha.smb
/Volumes/HA/config/hestia/tools/doctor/hestia_doctor.sh
/Volumes/HA/config/hestia/core/governance/output_contracts/copilot_automation_contract.md
/Volumes/HA/config/hestia/tools/system/hestia_autofs_uninstall.sh
/Volumes/HA/config/hestia/vault/receipts/hestia_setup.json
/Volumes/HA/config/hestia/vault/receipts/hestia_setup.log
```