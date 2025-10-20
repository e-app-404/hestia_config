#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

# ADR-0024: Use canonical /config path resolution
: "${CONFIG_ROOT:=/config}"
REPO=$(git -C "$CONFIG_ROOT" rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "${REPO:-}" ] || [ ! -d "$REPO" ]; then 
  echo "BLOCKED: unable to resolve repo root via git from $CONFIG_ROOT"; 
  exit 2
fi
mkdir -p "$REPO/tmp" "$REPO/hestia/tools/system"
LOG="$REPO/tmp/hestia_neutralize.log"
: > "$LOG"
ENF="$REPO/hestia/tools/system/hestia_workspace_enforcer.sh"
cat > "$ENF" <<'EOSH'
#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO"
ALLOW_RE='^(hestia/library/|hestia/workspace/archive/vault/|hestia/workspace/|\.git/|\.venv/)'
HITS_FILE="$REPO/tmp/hestia_path_hits.txt"
: > "$HITS_FILE"
hits=0
while IFS= read -r -d '' f; do
  [[ "$f" =~ $ALLOW_RE ]] && continue
  [[ -f "$f" ]] || continue
  # ADR-0024: Check for legacy mount paths and non-canonical references
  if grep -EnH --binary-files=without-match -E "(/Volumes/(HA|ha)|/n/ha|/Users/[^/]+/hass|~/hass)" "$f" >/dev/null; then
    grep -EnH --binary-files=without-match -E "(/Volumes/(HA|ha)|/n/ha|/Users/[^/]+/hass|~/hass)" "$f" >> "$HITS_FILE" || true
    hits=$((hits+1))
  fi
done < <(git ls-files -z || printf "")
if (( hits > 0 )); then
  echo "BLOCKED: non-canonical paths found in tracked config/code (ADR-0024 violation)."
  echo "EVIDENCE: hits_file=$HITS_FILE"
  exit 3
fi
# success
echo "OK: workspace paths are ADR-0024 compliant"
EOSH
chmod +x "$ENF"
# redirect stdout/stderr to log except final tokens
{
  # branch - ADR-0024 compliance branch
  if ! git -C "$REPO" rev-parse --verify adr-0024/canonical-paths >/dev/null 2>&1; then
    git -C "$REPO" checkout -b adr-0024/canonical-paths >/dev/null 2>&1 || true
  fi
  if ! git -C "$REPO" checkout adr-0024/canonical-paths >/dev/null 2>&1; then echo "BLOCKED: unable to checkout branch adr-0024/canonical-paths" >> "$LOG"; exit 2; fi
  echo "BRANCH_OK" >> "$LOG"
  # scan - ADR-0024: Check for all non-canonical path patterns
  PRE_HITS=$(git -C "$REPO" grep -nI -E "(/Volumes/(HA|ha)|/n/ha|/Users/[^/]+/hass|~/hass)" -- . ':(exclude)hestia/library/**' ':(exclude)hestia/workspace/archive/vault/**' ':(exclude)hestia/workspace/**' ':(exclude).git/**' ':(exclude).venv/**' | wc -l | tr -d '[:space:]' || true)
  PRE_HITS=${PRE_HITS:-0}
  echo "PRE_HITS=$PRE_HITS" >> "$LOG"
  # candidates
  git -C "$REPO" ls-files -z -- . ':(exclude)hestia/library/**' ':(exclude)hestia/workspace/archive/vault/**' ':(exclude)hestia/workspace/**' ':(exclude).git/**' ':(exclude).venv/**' > "$REPO/tmp/hestia_candidates.z"
  CHANGED=0
  while IFS= read -r -d '' rel; do
    f="$REPO/$rel"
    [ -f "$f" ] || continue
    if file -I "$f" 2>/dev/null | grep -qE 'charset=binary|application/octet-stream'; then continue; fi
    case "$f" in
      *.md|*.markdown|*.txt|*.yml|*.yaml|*.json|*.conf|*.ini|*.sh|*.bash|*.zsh|*.py|*.service|*.plist|*.code-workspace) ;;
      *) continue ;;
    esac
    tmp=$(mktemp "$REPO/tmp/hst.rew.XXXXXX")
    # ADR-0024: Normalize all legacy paths to canonical /config
    LC_ALL=C sed -E \
      -e 's#/Volumes/HA/config#/config#g' \
      -e 's#/Volumes/ha/config#/config#g' \
      -e 's#/Volumes/HA#/config#g' \
      -e 's#/Volumes/ha#/config#g' \
      -e 's#/n/ha#/config#g' \
      -e 's#~/hass#/config#g' \
      -e 's#/Users/[^/]+/hass#/config#g' \
      "$f" > "$tmp"
    if ! cmp -s "$tmp" "$f"; then mv "$tmp" "$f"; git -C "$REPO" add "$rel" >/dev/null 2>&1 || true; CHANGED=$((CHANGED+1)); else rm -f "$tmp"; fi
  done < "$REPO/tmp/hestia_candidates.z"
  echo "CHANGED=$CHANGED" >> "$LOG"
  # run enforcer
  if ! "$ENF" > "$REPO/tmp/enforcer.out" 2>&1; then
    # extract hits_file if present
    HITS_FILE=$(sed -n "s/^EVIDENCE: hits_file=\(.*\)$/\1/p" "$REPO/tmp/enforcer.out" || true)
    HITS_FILE=${HITS_FILE:-$REPO/tmp/hestia_path_hits.txt}
    # mask path - ADR-0024: Use canonical /config
    HITS_MASKED=${HITS_FILE/#$REPO/\/config}
    echo "EVIDENCE: hits_file=$HITS_MASKED"
    echo "BLOCKED: ENFORCER -> remediation: neutralize remaining non-canonical paths and re-run"
    exit 4
  fi
  echo "ENFORCER_OK" >> "$LOG"
  # pre-commit
  HOOKS_DIR=$(git -C "$REPO" rev-parse --git-path hooks)
  mkdir -p "$HOOKS_DIR"
  cat > "$HOOKS_DIR/pre-commit" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO="$(git rev-parse --show-toplevel)"
bash "$REPO/hestia/tools/system/hestia_workspace_enforcer.sh"
EOF
  chmod +x "$HOOKS_DIR/pre-commit"
  HOOKS_MASKED=${HOOKS_DIR/#$REPO/\/config}
  echo "HOOKS=$HOOKS_MASKED" >> "$LOG"
  # commit
  if git -C "$REPO" diff --quiet && git -C "$REPO" diff --cached --quiet; then :; else git -C "$REPO" commit -m "workspace: normalize paths to ADR-0024 canonical /config; enforce compliance" >/dev/null 2>&1 || true; fi
  HEAD=$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo NONE)
  echo "HEAD=$HEAD" >> "$LOG"
  # attempt push
  if git -C "$REPO" remote get-url origin >/dev/null 2>&1; then if git -C "$REPO" push -u origin adr-0024/canonical-paths >/dev/null 2>&1; then echo "PUSHED_OK" >> "$LOG"; else echo "PUSH_FAILED" >> "$LOG"; fi; else echo "NO_REMOTE" >> "$LOG"; fi
} >> "$LOG" 2>&1 || true
# print final tokens based on log
# if enforcer produced hits file, the script already exited; otherwise proceed
# read values
PRE_HITS=$(sed -n 's/^PRE_HITS=\(.*\)$/\1/p' "$LOG" || echo 0)
CHANGED=$(sed -n 's/^CHANGED=\(.*\)$/\1/p' "$LOG" || echo 0)
HEAD=$(sed -n 's/^HEAD=\(.*\)$/\1/p' "$LOG" || echo NONE)
HOOKS_DIR=$(sed -n 's/^HOOKS=\(.*\)$/\1/p' "$LOG" || echo /hooks)
# emit tokens
echo "DONE: ADR-0024_PATHS_NORMALIZED"
echo "SUMMARY: repo=$CONFIG_ROOT branch=$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo UNKNOWN) head=$HEAD pre_hits=${PRE_HITS:-0} changed=${CHANGED:-0} hooks=$HOOKS_DIR"
exit 0
