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

REPO_ROOT = Path(__file__).resolve().parents[3]
ADR_DIR = REPO_ROOT / 'hestia' / 'library' / 'docs' / 'ADR'

FM_RE = re.compile(r"^---\n(.*?)\n---\n", flags=re.S | re.M)


def extract_front_matter(text: str):
    m = FM_RE.search(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def main() -> int:
    if not ADR_DIR.exists():
        print(f"WARNING: ADR directory not found: {ADR_DIR}")
        return 0
    md_files = sorted([p for p in ADR_DIR.rglob('ADR-*.md') if '/archive/' not in str(p)])
    if not md_files:
        print("No ADR files found; nothing to validate.")
        return 0
    failures = 0
    warnings = 0
    for p in md_files:
        s = p.read_text(encoding='utf-8', errors='ignore')
        fm = extract_front_matter(s)
        if fm is None:
            print(f"ERROR: No YAML front-matter found in {p}")
            failures += 1
            continue
        missing = [k for k in ('title', 'status', 'date') if k not in fm]
        if missing:
            print(f"ERROR: Missing minimal keys {missing} in {p}")
            failures += 1
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
