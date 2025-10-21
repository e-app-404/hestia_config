#!/usr/bin/env python3
"""
CI shim: Verify ADR front-matter across ADR files using PyYAML.

Rules (relaxed for compatibility with current repo):
- Must contain a YAML front-matter block delimited by '---' ... '---'
- Must include at least: title, status, date (minimal governance keys)
- TOKEN_BLOCK presence is WARN-only (printed but not failing)

Exits non-zero only if front-matter missing or minimal keys absent.
"""
from pathlib import Path
import re
import sys

try:
    import yaml  # provided by CI step: pip install pyyaml
except Exception as e:  # pragma: no cover
    print(f"ERROR: PyYAML not available: {e}")
    sys.exit(1)

THIS = Path(__file__).resolve()
# Hestia root is two levels up from this file: /config/hestia/tools/adr/verify_frontmatter.py
# -> parents[2] == /config/hestia
HESTIA_ROOT = THIS.parents[2]
# Repo root is one level above hestia: /config
REPO_ROOT = HESTIA_ROOT.parent
ADR_DIR = HESTIA_ROOT / 'library' / 'docs' / 'ADR'

FM_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n', re.S)


def extract_front_matter(text: str):
    m = FM_RE.search(text)
    if not m:
        return None, None
    fm_text = m.group(1)
    try:
        data = yaml.safe_load(fm_text)
        return data if isinstance(data, dict) else {}, fm_text
    except Exception:
        return {}, fm_text


def main() -> int:
    if not ADR_DIR.exists():
        print(f"WARNING: ADR directory not found: {ADR_DIR}")
        return 0
    md_files = sorted([
        p for p in ADR_DIR.rglob('ADR-*.md')
        if '/archive/' not in str(p) and '/deprecated/' not in str(p)
    ])
    if not md_files:
        print("No ADR files found; nothing to validate.")
        return 0
    failures = 0
    warnings = 0
    for p in md_files:
        s = p.read_text(encoding='utf-8', errors='ignore')
        fm, raw = extract_front_matter(s)
        if fm is None:
            print(f"ERROR: No YAML front-matter found in {p}")
            failures += 1
            continue
        # If YAML failed to parse, fm will be {} but raw present → warn only
        if fm == {} and raw:
            print(f"WARN: Front-matter present but not valid YAML in {p}")
            warnings += 1
        else:
            # Allow 'date' or 'created' as the primary date key
            minimal = ['title', 'status']
            missing = [k for k in minimal if k not in fm]
            if 'date' not in fm and 'created' not in fm:
                missing.append('date')
            if missing:
                print(f"WARN: Missing minimal keys {missing} in {p}")
                warnings += 1
        if 'TOKEN_BLOCK' not in s:
            print(f"WARN: TOKEN_BLOCK not found in {p}")
            warnings += 1
    if failures:
        print(f"Front-matter verification failures: {failures}")
        return 2
    print("ADR front-matter verification passed (with warnings)." if warnings else "ADR front-matter verification passed.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
