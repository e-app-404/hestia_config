```bash
#!/usr/bin/env bash
# Copilot Diagnostic Collector — root-cause evidence pack
# Paste into your VS Code / code-server integrated terminal at the WORKSPACE ROOT (e.g., /config)
# It gathers agent/IDE/FS/VCS/HA/automation data into a single tarball you can share.

set -Eeuo pipefail

TS="$(date -u +%Y%m%d_%H%M%SZ)"
OUT="copilot_diag_${TS}"

mkdir -p "$OUT"/{env,ide,workspace,fs,git,ha,automations,repro,logs,policy}

log() { printf '\n==== %s ====\n' "$*" | tee -a "$OUT/collector.log" ; }
exists() { command -v "$1" >/dev/null 2>&1 ; }
save() {
  # save <relative_output_path> <command...>
  local dest="$1"; shift
  log "$*"
  (eval "$@" || true) | tee "$OUT/$dest" >/dev/null || true
}

log "Start collector at $(pwd)"

# ---------- 1) Agent / Copilot layer ----------
save "ide/code_version.txt" 'code --version || true; code-server --version || true'
save "ide/copilot_extensions.txt" '
  if exists code; then code --list-extensions --show-versions || code --list-extensions; fi
  if exists code-server; then code-server --list-extensions --show-versions || code-server --list-extensions; fi
'
# Grep user/workspace settings for copilot-related knobs
save "ide/copilot_settings_grep.txt" '
  grep -RInE "copilot|github\.copilot" \
    ~/.config/Code/User \
    ~/.vscode-server/data/Machine \
    ~/.local/share/code-server/User \
    .vscode 2>/dev/null || true
'

# Capture complete settings/workspace config if present
log "Archiving VS Code / code-server user and workspace settings (if present)"
tar -czf "$OUT/ide/vscode_user_config.tgz" \
  -C "$HOME" .config/Code/User 2>/dev/null || true
tar -czf "$OUT/ide/code_server_user_config.tgz" \
  -C "$HOME" .local/share/code-server/User 2>/dev/null || true
[ -d .vscode ] && tar -czf "$OUT/ide/workspace_vscode_dir.tgz" .vscode || true

# Try to capture Copilot-related logs from typical locations
save "logs/copilot_files_found.txt" '
  find \
    ~/.config/Code/logs \
    ~/.vscode-server/data/logs \
    ~/.local/share/code-server/logs \
    -type f -iname "*copilot*" 2>/dev/null || true
'
if [ -s "$OUT/logs/copilot_files_found.txt" ]; then
  log "Archiving Copilot log files"
  # shellcheck disable=SC2046
  tar -czf "$OUT/logs/copilot_logs.tgz" $(cat "$OUT/logs/copilot_files_found.txt" | tr "\n" " ") 2>/dev/null || true
fi

# ---------- 2) IDE / Host environment ----------
save "env/uname.txt" 'uname -a'
save "env/os_release.txt" 'cat /etc/os-release 2>/dev/null || true'
save "env/extensions_full.txt" '
  if exists code; then code --list-extensions --show-versions || code --list-extensions; fi
  if exists code-server; then code-server --list-extensions --show-versions || code-server --list-extensions; fi
'
save "ide/workspace_trust_grep.txt" '
  grep -RInE "security\.workspace\.trust|workspace\.trust" \
    ~/.config/Code/User \
    ~/.local/share/code-server/User \
    .vscode 2>/dev/null || true
'

# ---------- 3) Workspace topology & path mapping ----------
save "workspace/pwd.txt" 'pwd'
save "workspace/realpath.txt" 'readlink -f . 2>/dev/null || realpath . 2>/dev/null || pwd'
save "workspace/ls_root.txt" 'ls -la'
save "workspace/mounts_filter.txt" 'mount | grep -E "/config|overlay|nfs|smb" || true'

# ---------- 4) Filesystem health & permissions ----------
save "fs/fsinfo.txt" '
  { stat -f -c "FS Type: %T  BlockSize: %s" . 2>/dev/null \
    || df -T . 2>/dev/null \
    || true; }
'
save "fs/permissions_sample.txt" 'find . -maxdepth 2 -printf "%M %U:%G %p\n" 2>/dev/null | head -n 400'
save "fs/immutable_attrs.txt" 'if exists lsattr; then lsattr -R . 2>/dev/null; else echo "lsattr not available"; fi'
save "env/watchers_ps.txt" "ps aux | egrep -i 'inotify|syncthing|unison|watcher|rsync' || true"

# ---------- 5) VCS (Git) ----------
save "git/root.txt" 'git rev-parse --show-toplevel 2>/dev/null || echo "Not a git repo?"'
save "git/status.txt" 'git status --porcelain -uall 2>/dev/null || true'
save "git/config_keys.txt" 'git config --list --show-origin 2>/dev/null | egrep "worktree|autocrlf|safe\.directory" || true'
save "git/hooks_listing.txt" 'ls -la .git/hooks 2>/dev/null || true'
save "git/hooks_contents.txt" '
  for f in .git/hooks/*; do
    [ -f "$f" ] || continue
    echo -e "\n### $f\n"
    sed -n "1,200p" "$f"
  done 2>/dev/null || true
'
save "git/ignore.txt" 'sed -n "1,400p" .gitignore 2>/dev/null || true'
save "git/attributes.txt" 'sed -n "1,400p" .gitattributes 2>/dev/null || true'

# ---------- 6) Home Assistant specifics ----------
save "ha/ha_cli_info.txt" 'ha info 2>/dev/null || echo "ha CLI not available"'
save "ha/supervisor_info.txt" 'ha supervisor info 2>/dev/null || true'
save "ha/supervisor_logs.txt" 'ha supervisor logs 2>/dev/null || true'
save "ha/core_logs.txt" 'ha core logs --lines 300 2>/dev/null || ha core logs 2>/dev/null || true'

# ---------- 7) Containers / Docker mounts (if available) ----------
save "env/docker_ps.txt" 'docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Mounts}}\t{{.Image}}" 2>/dev/null || echo "docker not available"'
for C in homeassistant addon_core_studio-code-server addon_core_ssh addon_core_configurator; do
  save "env/docker_inspect_${C}.json" "docker inspect $C 2>/dev/null || true"
done

# ---------- 8) Other automations that might overwrite files ----------
save "automations/crontab_user.txt" 'crontab -l 2>/dev/null || echo "no user crontab"'
save "automations/etc_cron_dirs.txt" '
  for d in /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly /etc/cron.monthly; do
    [ -d "$d" ] && { echo "## $d"; ls -la "$d"; }
  done 2>/dev/null || true
'
save "automations/systemd_timers.txt" 'systemctl list-timers --all 2>/dev/null || echo "systemd not available"'

# ---------- 9) Repro snapshot (ground truth on likely files, if they exist) ----------
# Adjust/extend this list if your targets differ
TARGETS=(
  "custom_components/localtuya/humidifier.py"
  "packages/motion_lighting_v2/motion_light_automations.yaml"
  "hestia/library/error_patterns.yml"
)
{
  for f in "${TARGETS[@]}"; do
    if [ -f "$f" ]; then
      echo "## $f"
      sha256sum "$f" 2>/dev/null || true
      echo "-- grep isinstance.*modes (if applicable) --"
      grep -n -E "isinstance.*modes" "$f" 2>/dev/null || true
      echo
    fi
  done
} | tee "$OUT/repro/file_checks.txt" >/dev/null

# ---------- 10) Final packaging ----------
log "Creating tarball"
tar -czf "$OUT.tar.gz" "$OUT" 2>/dev/null || {
  echo "Tar creation failed — attempting zip fallback"
  if exists zip; then (cd "$OUT" && zip -r "../$OUT.zip" .); fi
}

if [ -f "$OUT.tar.gz" ]; then
  sha256sum "$OUT.tar.gz" | tee "$OUT/manifest.sha256" >/dev/null
  echo
  echo "== Evidence package ready =="
  ls -lh "$OUT.tar.gz"
  echo "SHA256: $(cut -d' ' -f1 "$OUT/manifest.sha256")"
elif [ -f "$OUT.zip" ]; then
  echo
  echo "== Evidence package ready (zip fallback) =="
  ls -lh "$OUT.zip"
else
  echo "Packaging failed; see $OUT/collector.log for details."
fi
```
