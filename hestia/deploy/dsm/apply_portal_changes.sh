#!/usr/bin/env bash
set -euo pipefail
LC_ALL=C

# Hardened, idempotent deploy script for DSM portal assets
# Dry-run by default. Use --apply to actually write files.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$REPO_DIR/dsm"
# Allow overriding TARGET_BASE via environment variable for local mounts (e.g. /Volumes/web on macOS)
# Default to the Synology path if not provided
TARGET_BASE="${TARGET_BASE:-/volume1/web}"
DRY_RUN=1
WRITE_HTACCESS=0
BACKUP_DIR=""

usage(){
  cat <<'USAGE' >&2
Usage: apply_portal_changes.sh [--apply] [--write-htaccess] [--backup-dir <path>]

--apply            Actually copy files to the NAS (requires permissions). Without --apply the script prints actions only.
--write-htaccess   Install .htaccess.template as /volume1/web/.htaccess when applying.
--backup-dir PATH  Override default backup location (default: ./backup-<ts> under repo)
USAGE
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --apply) DRY_RUN=0; shift ;;
    --write-htaccess) WRITE_HTACCESS=1; shift ;;
    --backup-dir) BACKUP_DIR="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "BLOCKED: unknown argument $1" >&2; usage ;;
  esac
done

# portable sha256 helper
sha256(){
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v openssl >/dev/null 2>&1; then
    openssl dgst -sha256 "$1" | awk '{print $2}'
  else
    echo ""
  fi
}

# Prechecks
if [ ! -d "$TARGET_BASE" ]; then
  echo "BLOCKED: target $TARGET_BASE does not exist on this host" >&2
  exit 3
fi
for d in public portal _assets; do
  if [ ! -d "$TARGET_BASE/$d" ]; then
    echo "EVIDENCE: missing_dir=$TARGET_BASE/$d"
    if [ $DRY_RUN -eq 1 ]; then
      echo "DRY-RUN: would create $TARGET_BASE/$d"
    else
      mkdir -p "$TARGET_BASE/$d"
    fi
  fi
done

# Files to copy (source relative to this script's parent dsm/)
COPY_LIST=(
  public/index.html
  portal/index.html
  _assets/app.js
  _assets/portal.config.json
  portal/ping.html
)

# Optionally include htaccess as a special-case when requested
if [ "$WRITE_HTACCESS" -eq 1 ]; then
  COPY_LIST+=(.htaccess.template)
fi

# Determine backup dir when applying
if [ $DRY_RUN -eq 0 ]; then
  if [ -z "$BACKUP_DIR" ]; then
    TS=$(date -u +%Y%m%dT%H%M%SZ)
    BACKUP_DIR="$REPO_DIR/backup-$TS"
  fi
  echo "EVIDENCE: backup_dir=$BACKUP_DIR"
  mkdir -p "$BACKUP_DIR"
fi

# Perform copy or dry-run with idempotency (sha256 compare)
for f in "${COPY_LIST[@]}"; do
  src="$SRC_DIR/$f"
  if [ "$f" = ".htaccess.template" ]; then
    tgt="$TARGET_BASE/.htaccess"
  else
    tgt="$TARGET_BASE/$f"
  fi

  if [ ! -f "$src" ]; then
    echo "EVIDENCE: source_missing=$src"
    continue
  fi

  if [ -f "$tgt" ]; then
    srcsum=$(sha256 "$src" || true)
    tgtsum=$(sha256 "$tgt" || true)
    if [ -n "$srcsum" ] && [ "$srcsum" = "$tgtsum" ]; then
      echo "SKIP: identical $tgt"
      continue
    fi
  fi

  if [ $DRY_RUN -eq 1 ]; then
    echo "DRY-RUN: would copy $src -> $tgt"
    if [ -f "$tgt" ] && command -v diff >/dev/null 2>&1; then
      echo "DRY-RUN: diff summary for $f:"
      diff -u --label a/$src --label b/$tgt "$src" "$tgt" 2>/dev/null | sed -n '1,6p' || true
    fi
  else
    mkdir -p "$(dirname "$tgt")"
    if [ -f "$tgt" ]; then
      bname="$(basename "$tgt")"
      cp -a "$tgt" "$BACKUP_DIR/${bname}.bak" || true
    fi
    cp -a "$src" "$tgt"
    echo "EVIDENCE: wrote=$tgt"
  fi
done

if [ $DRY_RUN -eq 1 ]; then
  echo "OK: DRY_RUN_COMPLETE"
else
  echo "OK: APPLIED"
fi

exit 0
