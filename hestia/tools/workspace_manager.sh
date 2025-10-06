#!/usr/bin/env bash
set -euo pipefail

ROOT="${WORKSPACE_ROOT:-$HOME/actions-runner/Projects}"
CONF="${1:-}" ; CMD="${2:-help}"
CONF=${CONF:-"$ROOT/hestia/workspace/workspace_policy.yaml"} 

# defaults
ARCH="$ROOT/hestia/workspace/archive"
TRASH="$ROOT/.trash"
TMP="$ROOT/tmp"

usage(){ cat <<EOF
workspace_manager <policy.yaml> <command> [args]
Commands:
  dry-run                     Show what would be changed
  sweep-trash                 List trash; with --apply empties (requires APPROVE=1)
  sweep-tmp                   Prune tmp files older than N days (default 7); --days N --apply
  relocate-backups            Move *.bak* into $ARCH/backups/<YYYY-Www>/  (respects exclusions)
  relocate-tarballs           Move *.tar.gz into $ARCH/tarballs/<YYYY-Www>/ (respects exclusions)
  audit-bleed                 Detect BB8 bleed-through under /config/**, emit report
  fix-bleed                   Quarantine bleed-through into $ARCH/bleedthrough/<ts>/ and patch includes
Options:
  --apply                     Execute changes (default is dry-run)
  --days N                    Age threshold for tmp prune (default 7)
EOF
}

need_approve(){ : "${APPROVE:=0}"; [ "$APPROVE" = "1" ] || { echo "Approval required: export APPROVE=1"; exit 3; }; }

iso_week(){ date +"%G-W%V"; }

exclude_args(){
  # read recursive exclusions from policy file (yaml list under exclusions:)
  # fall back to none if file missing
  if [ -f "$CONF" ]; then
    python3 - "$CONF" <<'PY'
import sys,yaml,shlex,json,os
conf=yaml.safe_load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}
ex=conf.get("exclusions",[])
# print as -path 'X' -prune -o for find
cla=[]
for p in ex:
  cla+=["-path",p,"-prune","-o"]
print(json.dumps(cla))
PY
  else
    echo '[]'
  fi
}

FIND_EXCLUDES=($(python3 -c "import json;print(' '.join(json.loads('$(exclude_args)')))"))

cmd_dry_run(){ echo "Policy: $CONF"; echo "Root:   $ROOT"; echo "Excl:   ${FIND_EXCLUDES[*]:-(none)}"; }

cmd_sweep_trash(){
  echo "Trash at $TRASH"
  [ -d "$TRASH" ] || { echo "No trash directory"; return 0; }
  du -sh "$TRASH" || true
  if [ "${1:-}" = "--apply" ]; then need_approve; rm -rf "$TRASH"/* || true; echo "Trash emptied."; fi
}

cmd_sweep_tmp(){
  DAYS=7
  while [ $# -gt 0 ]; do case "$1" in --days) DAYS="$2"; shift 2;; --apply) APPLY=1; shift;; *) shift;; esac; done
  [ -d "$TMP" ] || { echo "No tmp directory"; return 0; }
  echo "Would remove files older than $DAYS days in $TMP"
  find "$TMP" -type f -mtime +"$DAYS" -print
  if [ "${APPLY:-0}" = "1" ]; then need_approve; find "$TMP" -type f -mtime +"$DAYS" -delete; echo "Tmp pruned."; fi
}

cmd_relocate_backups(){
  DEST="$ARCH/backups/$(iso_week)"
  mkdir -p "$DEST"
  echo "Relocating *.bak* → $DEST"
  find "$ROOT" \( "${FIND_EXCLUDES[@]}" \) -type f -name "*.bak*" -print |
  while read -r f; do
    echo "→ $f"
    [ "${APPLY:-0}" = "1" ] && install -d "$DEST" && mv "$f" "$DEST"/
  done
}

cmd_relocate_tarballs(){
  DEST="$ARCH/tarballs/$(iso_week)"
  mkdir -p "$DEST"
  echo "Relocating *.tar.gz → $DEST"
  find "$ROOT" \( "${FIND_EXCLUDES[@]}" \) -type f -name "*.tar.gz" -print |
  while read -r f; do
    echo "→ $f"
    [ "${APPLY:-0}" = "1" ] && install -d "$DEST" && mv "$f" "$DEST"/
  done
}

BLEED_LIST="/tmp/bleed_report.txt"
cmd_audit_bleed(){
  : > "$BLEED_LIST"
  echo "Scanning for BB8 bleed-through under /config…"
  # Paths you flagged:
  for p in /config/build.yaml /config/mypy.ini /config/includes/shell_command.yaml; do
    [ -e "$p" ] && echo "$p" | tee -a "$BLEED_LIST"
  done
  # Heuristic scan for hestia/domain/shell_command refs & BB8 components in /config:
  grep -RIl "bb8" /config 2>/dev/null | sed 's/^/bb8-ref: /' | tee -a "$BLEED_LIST" || true
  echo "Report: $BLEED_LIST"
}

cmd_fix_bleed(){
  TS=$(date -u +%Y%m%dT%H%M%SZ)
  DEST="$ARCH/bleedthrough/$TS"
  mkdir -p "$DEST"
  [ -f "$BLEED_LIST" ] || cmd_audit_bleed >/dev/null
  echo "Quarantining listed files to $DEST"
  while read -r p; do
    [[ "$p" == bb8-ref:* ]] && continue
    [ -f "$p" ] || continue
    echo "→ $p"
    if [ "${APPLY:-0}" = "1" ]; then
      install -D "$p" "$DEST/$(basename "$p")"
      : > "$p"  # leave stub if HA expects file
      echo "# moved to $DEST by workspace_manager" > "$p"
    fi
  done < <(grep -v '^$' "$BLEED_LIST")
  echo "Patch includes to canonical hestia/tools and hestia/domain references as needed."
}

case "$CMD" in
  help|"") usage;;
  dry-run) cmd_dry_run;;
  sweep-trash) shift 2 || true; cmd_sweep_trash "$@";;
  sweep-tmp) shift 2 || true; cmd_sweep_tmp "$@";;
  relocate-backups) shift 2 || true; cmd_relocate_backups;;
  relocate-tarballs) shift 2 || true; cmd_relocate_tarballs;;
  audit-bleed) cmd_audit_bleed;;
  fix-bleed) shift 2 || true; cmd_fix_bleed;;
  *) usage; exit 2;;
esac
