#!/usr/bin/env bash
set -euo pipefail

# Simple guardrails checker for rest_command docs and configs
# Usage: ./check_rest_command_guardrails.sh

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
guardrails_dir="$root_dir/guardrails"

if [ ! -d "$guardrails_dir" ]; then
  echo "guardrails dir not found: $guardrails_dir" >&2
  exit 2
fi

# use python for robust regex and globbing
python3 - <<'PY'
import re, sys, yaml
from pathlib import Path

root = Path('')
rules = {'rules': []}
for y in Path('hestia/guardrails').glob('*_guardrails.yaml'):
    try:
        loaded = yaml.safe_load(y.read_text())
        if loaded and 'rules' in loaded:
            rules['rules'].extend(loaded['rules'])
    except Exception:
        print(f"warning: failed to load {y}", file=sys.stderr)

violations = []
for rule in rules.get('rules', []):
    try:
        pat = re.compile(rule['pattern'])
    except Exception as e:
        print(f"invalid regex for rule {rule.get('id')}: {e}", file=sys.stderr)
        continue
    files_glob = rule.get('files', ['**/*.md','**/*.yaml','**/*.yml'])
    for g in files_glob:
        for p in Path('.').glob(g):
            try:
                text = p.read_text()
            except Exception:
                continue
            for m in pat.finditer(text):
                excerpt = m.group(0)
                violations.append((rule['id'], rule['title'], str(p), excerpt.strip()))

if violations:
    print('Guardrail violations found:')
    for v in violations:
        print(f"- {v[0]} {v[1]}: {v[2]} -> {v[3]}")
    sys.exit(1)
else:
    print('No guardrail violations found.')
    sys.exit(0)
PY
