#!/bin/sh
set -eu
OUT="${1:-bundle.tar.gz}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# manifest (stable ordering)
git ls-files | LC_ALL=C sort > "$TMP/MANIFEST.txt"
sha256sum $(cat "$TMP/MANIFEST.txt") > "$TMP/SHA256SUMS.txt" 2>/dev/null || true

# reproducible tar (mtime pinned)
tar --sort=name --owner=0 --group=0 --mtime='UTC 2020-01-01' -czf "$OUT" \
  --files-from="$TMP/MANIFEST.txt" \
  "$TMP/MANIFEST.txt" "$TMP/SHA256SUMS.txt"
echo "WROTE $OUT"