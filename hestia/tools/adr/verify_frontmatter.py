#!/usr/bin/env python3
"""
CI shim: Verify ADR front-matter and TOKEN_BLOCK presence for all ADRs.
This delegates to the existing minimal validator at
  hestia/tools/utils/validators/adr_validator.py

Exit non-zero if any ADR fails validation.
"""
from pathlib import Path
import sys
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[3]
ADR_DIR = REPO_ROOT / 'hestia' / 'library' / 'docs' / 'ADR'
VALIDATOR = REPO_ROOT / 'hestia' / 'tools' / 'utils' / 'validators' / 'adr_validator.py'

def main() -> int:
    if not ADR_DIR.exists():
        print(f"WARNING: ADR directory not found: {ADR_DIR}")
        return 0
    if not VALIDATOR.exists():
        print(f"ERROR: validator missing: {VALIDATOR}")
        return 1
    md_files = sorted([p for p in ADR_DIR.rglob('ADR-*.md') if '/archive/' not in str(p)])
    if not md_files:
        print("No ADR files found; nothing to validate.")
        return 0
    failures = 0
    for p in md_files:
        proc = subprocess.run([sys.executable, str(VALIDATOR), str(p)])
        if proc.returncode != 0:
            failures += 1
    if failures:
        print(f"Front-matter verification failures: {failures}")
        return 2
    print("ADR front-matter verification passed for all files.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
