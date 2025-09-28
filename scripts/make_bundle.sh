#!/bin/sh
set -eu
OUT="${1:-bundle.tar.gz}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# manifest (stable ordering)
git ls-files | LC_ALL=C sort > "$TMP/MANIFEST.txt"
sha256sum $(cat "$TMP/MANIFEST.txt") > "$TMP/SHA256SUMS.txt" 2>/dev/null || true

# reproducible tar (macOS compatible - basic reproducibility)
# Note: macOS tar has limited options, so we use basic tar with sorted manifest
tar -czf "$OUT" -T "$TMP/MANIFEST.txt" "$TMP/MANIFEST.txt" "$TMP/SHA256SUMS.txt"
echo "WROTE $OUT"