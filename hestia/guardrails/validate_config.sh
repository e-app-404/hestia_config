#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-}"
# Syntax-only: fast parse with Python (no HA runtime)
if [[ "$MODE" == "--syntax-only" ]]; then
  python - <<'PY'
import sys,glob
import yaml
for p in glob.glob("**/*.yaml", recursive=True):
    try:
        yaml.safe_load(open(p, 'r', encoding='utf-8'))
    except Exception as e:
        print(f"[YAML] {p}: {e}", file=sys.stderr); sys.exit(1)
print("YAML parse OK")
PY
  exit $?
fi
# Evidence mode is repo-only (no host assumptions)
if [[ "$MODE" == "--evidence" ]]; then
  mkdir -p evidence/recorder
  # counts
  grep -R --include="*.yaml" -nE "^[[:space:]]*recorder:" packages configuration.yaml > evidence/recorder/recorder_occurrences.txt || true
  # placeholder for CSVs produced from your prior SQL scripts
  touch evidence/recorder/top_entities.csv evidence/recorder/domain_counts.csv
  echo "Evidence scaffolding created."
  exit 0
fi
