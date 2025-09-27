#!/bin/bash
# Hardened rehydrate_v2_1.sh with stricter legacy auto-detect, fail-fast overlays, and audit echo
set -euo pipefail

# --- 0) Resolve a WRITABLE Git workdir ----------------------------------------
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERR: Not inside a git repository. cd into your repo and retry." >&2
  exit 2
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Quick write test in repo
if ! ( tfile="$(mktemp -p "$REPO_ROOT" .kyb_write_test.XXXX)" 2>/dev/null && rm -f "$tfile" ); then
  echo "NOTICE: Repo root appears read-only. Creating a writable git worktree…" >&2
  WT_BASE="${HOME}/.kyb_worktrees"; mkdir -p "$WT_BASE"
  WT_DIR="${WT_BASE}/rehydrate_v2_1_$(date -u +%Y%m%dT%H%M%SZ)"
  BR_REHY="governance/system-instruction-v2.1-rehydrate"
  if git show-ref --verify --quiet "refs/heads/${BR_REHY}"; then
    git worktree add --detach "$WT_DIR" HEAD
  else
    git worktree add -b "$BR_REHY" "$WT_DIR" HEAD
  fi
  cd "$WT_DIR"
  echo "WORKDIR: $WT_DIR"
fi

tfile="$(mktemp -p "." .kyb_write_test.XXXX)"; rm -f "$tfile" || { echo "ERR: Selected workdir still not writable."; exit 3; }

# --- 1) Rehydration EXEC script (re-entrant) ----------------------------------
LEGACY_PATH="${LEGACY_PATH:-path/to/ACTIVE/system_instruction.yaml}"
CORE_PATH="${CORE_PATH:-hestia/core/governance/system_instruction/v2.1/system_instruction.yaml}"
REHYDRATE_KEYS=("personas" "prompt_registry" "templates" "prompt_tests" "architectures" "profiles")
BRANCH="${BRANCH:-governance/system-instruction-v2.1-rehydrate}"

mkdir -p .kyb_overlay_merge/overlays .kyb_overlay_merge/norm .kyb_overlay_merge/bin

# Stricter legacy auto-detect (exclude v2.x and CORE_PATH filename)
if [[ "$LEGACY_PATH" == "path/to/ACTIVE/system_instruction.yaml" ]]; then
  core_file="$(basename "$CORE_PATH")"
  LEGACY_PATH="$(
    git ls-files '**/system_instruction.yaml' 2>/dev/null \
      | grep -Ev '/v2\.0[^/]*/|/v2\.1/' \
      | grep -v "/${core_file}$" \
      | while read -r p; do
          sz="$(stat -c %s "$p" 2>/dev/null || stat -f %z "$p" 2>/dev/null || echo 0)"
          printf '%012d %s\n' "$sz" "$p"
        done \
      | sort -nr \
      | awk 'NR==1 {sub(/^[0-9]+ /,"\"); print; exit}' \
      || true
  )"
fi

[[ -n "${LEGACY_PATH:-}" && -f "$LEGACY_PATH" ]] || { echo "ERR: LEGACY_PATH not found: $LEGACY_PATH"; exit 4; }
[[ -f "$CORE_PATH" ]] || { echo "ERR: CORE_PATH not found: $CORE_PATH"; exit 4; }
echo "LEGACY_SOURCE => $LEGACY_PATH"
echo "CORE_TARGET   => $CORE_PATH"

REHYDRATE_KEYS_STR="${REHYDRATE_KEYS[*]-}"
export LEGACY_PATH CORE_PATH REHYDRATE_KEYS_STR

source /Volumes/HA/config/.venv/bin/activate 2>/dev/null || true

python3 - <<'PY'
import yaml, os, json, sys
legacy=os.environ["LEGACY_PATH"]; keys=(os.environ.get("REHYDRATE_KEYS_STR","").split() or [])
L=yaml.safe_load(open(legacy)) or {}
os.makedirs(".kyb_overlay_merge/overlays", exist_ok=True)
written=[]
for k in keys:
    if k in L:
        path=f".kyb_overlay_merge/overlays/zzz_rehydrate__{k}.yaml"
        with open(path,"w") as f: yaml.safe_dump({k:L[k]}, f, sort_keys=False)
        written.append(path)
manifest={"source":legacy,"overlays":written}
open(".kyb_overlay_merge/norm/rehydrate_manifest.json","w").write(json.dumps(manifest,indent=2))
print(json.dumps({"overlays_written":written},indent=2))
# Hard gate: require at least one overlay written to proceed
if not written:
    sys.stderr.write("ERROR: No overlays were extracted (check LEGACY_PATH and REHYDRATE_KEYS).\n")
    sys.exit(6)
PY

# ...existing code...
