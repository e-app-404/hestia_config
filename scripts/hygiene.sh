#!/bin/sh
set -eu
echo "== untrack banned (index-only)"
git ls-files -z | tr '\0' '\n' | grep -E '^(\.storage/|\.venv|deps/|__pycache__/|\.mypy_cache/|\.trash/|\.quarantine/|artifacts/)' \
  | xargs -I{} git rm --cached -- {} 2>/dev/null || true
echo "== legacy backup renamer (dry-run)"
python3 hestia/tools/utils/legacy_backup_renamer.py --tag adr0018_grace || true
echo "== compact report index"
python3 hestia/tools/utils/reportkit/compact_index.py --keep-days 30 || true
echo "== link latest batch"
python3 hestia/tools/utils/reportkit/link_latest.py || true
echo "== delta"
git status -s