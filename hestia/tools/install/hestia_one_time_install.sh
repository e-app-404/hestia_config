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
