#!/bin/sh
# BusyBox-safe promoter & rollback helper
# Usage:
#   promote_registry.sh <candidate_path> <ha_config_dir>
# Example:
#   promote_registry.sh ./final_candidate.json /config

set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: $0 <candidate_path> <ha_config_dir>" 1>&2
    exit 2
fi

CAND=$1
HACONF=$2
STORAGE_DIR="$HACONF/.storage"
TARGET="$STORAGE_DIR/core.entity_registry"

if [ ! -f "$CAND" ]; then
    echo "candidate not found: $CAND" 1>&2
    exit 3
fi

if [ ! -d "$STORAGE_DIR" ]; then
    echo "ha storage dir not found: $STORAGE_DIR" 1>&2
    exit 4
fi

# backup existing registry
TS=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP="$STORAGE_DIR/core.entity_registry.$TS.bak"
if [ -f "$TARGET" ]; then
    cp "$TARGET" "$BACKUP" || { echo "backup failed" 1>&2; exit 5; }
    echo "backup: $BACKUP"
else
    echo "no existing registry to backup";
fi

# copy candidate to target
cp "$CAND" "$TARGET" || { echo "copy failed" 1>&2; exit 6; }
chmod 600 "$TARGET" || true
sync || true

# print size and first byte check
echo "WROTE $TARGET: size=$(wc -c < \"$TARGET\") bytes"
echo "first line:" 
head -n 1 "$TARGET" | sed -n '1p'

echo "promote complete"

exit 0
