# === COPILOT MISSION: Hestia Env Bootstrap & Verification (idempotent) ===
# Role: Strategos-Orchestrator (GPT-4.1)
# Goal: Validate config environment, wire neutral mount, confirm locator/doctor, record receipt.
# Emits: OK:, BLOCKED:, EVIDENCE:

set -Eeuo pipefail
IFS=$'\n\t'

emit() { printf '%s %s\n' "$1" "${2//\'/}"; }  # usage: emit "OK:" "message"

now_utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }
JID="${JID_OVERRIDE:-$(date -u +%Y%m%dT%H%M%SZ)}"

# --- 0) Validate required commands ---
for cmd in grep stat sudo tee python3 bash mkdir ls; do
  command -v "$cmd" >/dev/null 2>&1 || { emit "BLOCKED:" "Required command '$cmd' not found"; exit 127; }
done

# --- 1) Locate config root (case-tolerant, idempotent) ---
CANDIDATES=(
  "/n/ha"
  "/Volumes/ha/config"
  "/Volumes/HA/config"
)
CONFIG_ROOT=""
for p in "${CANDIDATES[@]}"; do
  [ -d "$p" ] && CONFIG_ROOT="$p" && break
done
if [ -z "$CONFIG_ROOT" ]; then
  emit "BLOCKED:" "No config root found at /n/ha or /Volumes/*/config"; exit 2
fi
emit "EVIDENCE:" "CONFIG_ROOT=$CONFIG_ROOT"

# --- 2) Source locator (ha_path.sh) and validate ---
if [ -f "$HOME/ha_path.sh" ]; then
  # shellcheck disable=SC1090
  source "$HOME/ha_path.sh" || { emit "BLOCKED:" "Failed sourcing ~/ha_path.sh"; exit 2; }
elif [ -f "$CONFIG_ROOT/hestia/tools/ha_path.sh" ]; then
  # shellcheck disable=SC1090
  source "$CONFIG_ROOT/hestia/tools/ha_path.sh" || { emit "BLOCKED:" "Failed sourcing repo ha_path.sh"; exit 2; }
else
  emit "BLOCKED:" "ha_path.sh not found (home or repo)"; exit 2
fi

if [ -z "${HESTIA_CONFIG:-}" ] || [ ! -d "$HESTIA_CONFIG" ]; then
  emit "BLOCKED:" "HESTIA_CONFIG not exported or path missing"; exit 2
fi
CFG_FILE="${HESTIA_CONFIG_FILE:-configuration.yaml}"
if [ -z "$CFG_FILE" ]; then
  emit "BLOCKED:" "HESTIA_CONFIG_FILE not set and no default found"; exit 2
fi
if [ ! -f "$HESTIA_CONFIG/$CFG_FILE" ]; then
  emit "BLOCKED:" "configuration file not found at $HESTIA_CONFIG/$CFG_FILE"; exit 2
fi
emit "OK:" "Locator resolved HESTIA_CONFIG=$HESTIA_CONFIG (file=$CFG_FILE)"

# --- 3) Wire neutral mount (/n/ha) if not present ---
NEED_AUTOMOUNT="no"
if ! /usr/bin/stat -f '%N' /n/ha >/dev/null 2>&1; then NEED_AUTOMOUNT="yes"; fi
if [ "$NEED_AUTOMOUNT" = "yes" ]; then
  T_AUTO_MASTER="$HESTIA_CONFIG/hestia/templates/autofs/auto_master.hestia.snippet"
  T_AUTO_SMB="$HESTIA_CONFIG/hestia/templates/autofs/auto_ha.smb"
  if [ ! -f "$T_AUTO_MASTER" ] || [ ! -f "$T_AUTO_SMB" ]; then
    emit "BLOCKED:" "autofs templates missing ($T_AUTO_MASTER / $T_AUTO_SMB)"; exit 2
  fi

  # Ensure /- auto_smb line in /etc/auto_master
  if ! grep -qE '^\s*/-\s+auto_smb' /etc/auto_master; then
    sudo tee -a /etc/auto_master >/dev/null < "$T_AUTO_MASTER"
    emit "OK:" "auto_master updated with /- auto_smb"
  else
    emit "OK:" "/etc/auto_master already contains /- auto_smb"
  fi

  # Install /etc/auto_smb from template
  sudo tee /etc/auto_smb >/dev/null < "$T_AUTO_SMB"
  sudo mkdir -p /n
  sudo automount -cv >/dev/null || true

  # Trigger mount
  ls -ld /n/ha >/dev/null 2>&1 && emit "OK:" "neutral path /n/ha available" || emit "EVIDENCE:" "autofs will mount on access"
else
  emit "OK:" "/n/ha already present"
fi

# --- 4) Confirm VS Code config helper ---
VSC="$HESTIA_CONFIG/.vscode/settings.json"
if [ -f "$VSC" ]; then
  if ! grep -q 'home-assistant.configFile' "$VSC"; then
    emit "EVIDENCE:" "VS Code settings present but no HA configFile key; consider adding: \"home-assistant.configFile\": \"\${workspaceFolder}/\${env:HESTIA_CONFIG_FILE}\""
  else
    emit "OK:" "VS Code settings detected"
  fi
else
  emit "EVIDENCE:" "No .vscode/settings.json at repo; skipping VS Code checks"
fi

# --- 5) Run doctor script for diagnostics ---
if [ -x "$HOME/hestia_doctor.sh" ]; then
  bash "$HOME/hestia_doctor.sh" || true
elif [ -x "$HESTIA_CONFIG/hestia/tools/doctor/hestia_doctor.sh" ]; then
  bash "$HESTIA_CONFIG/hestia/tools/doctor/hestia_doctor.sh" || true
else
  emit "EVIDENCE:" "Doctor script not executable or not found; continuing"
fi

# --- 6) Record receipt (append-only, stable JSON) ---
RECEIPTS_DIR="$HESTIA_CONFIG/hestia/vault/receipts"
RECEIPT_JSON="$RECEIPTS_DIR/hestia_setup.json"
mkdir -p "$RECEIPTS_DIR"
[ -s "$RECEIPT_JSON" ] || printf '{}\n' > "$RECEIPT_JSON"

exec python3 - "$RECEIPT_JSON" "$JID" "$HESTIA_CONFIG" "$CFG_FILE" <<'PY'
import json, sys, time, os, hashlib
path, jid, root, cfg = sys.argv[1:5]
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception:
    data = {}
data.setdefault("runs", [])
stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
finger = hashlib.sha256((root + "/" + cfg).encode()).hexdigest()
data["last_run"] = {"jid": jid, "utc": stamp, "config_root": root, "config_file": cfg, "fingerprint": finger}
data["runs"].append(data["last_run"])
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print(json.dumps(data["last_run"], indent=2))
PY

emit "OK:" "Receipt updated at $RECEIPT_JSON"
emit "COMPLETED:" "Hestia Env Bootstrap (JID=$JID)"