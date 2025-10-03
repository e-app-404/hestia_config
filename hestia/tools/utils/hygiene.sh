#!/bin/sh
set -eu
echo "== untrack banned (index-only)"
git ls-files -z | tr '\0' '\n' | grep -E '^(\.storage/|\.venv|deps/|__pycache__/|\.mypy_cache/|\.trash/|\.quarantine/|artifacts/)' \
  | xargs -I{} git rm --cached -- {} 2>/dev/null || true
echo "== legacy backup renamer (dry-run)"
if [ -x .venv_ha_governance/bin/python ]; then
  .venv_ha_governance/bin/python hestia/tools/utils/legacy_backup_renamer.py --tag adr0018_grace || true
else
  python3 hestia/tools/utils/legacy_backup_renamer.py --tag adr0018_grace || true
fi
echo "== compact report index"
if [ -x .venv_ha_governance/bin/python ]; then
  .venv_ha_governance/bin/python hestia/tools/utils/reportkit/compact_index.py --keep-days 30 || true
else
  python3 hestia/tools/utils/reportkit/compact_index.py --keep-days 30 || true
fi
echo "== link latest batch"
if [ -x .venv_ha_governance/bin/python ]; then
  .venv_ha_governance/bin/python hestia/tools/utils/reportkit/link_latest.py || true
else
  python3 hestia/tools/utils/reportkit/link_latest.py || true
fi
echo "== delta"
git status -s