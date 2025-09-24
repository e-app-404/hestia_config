#!/usr/bin/env python3
"""Minimal ADR validator that avoids external dependencies.
This lightweight parser looks for a leading YAML front-matter block and extracts required keys with simple parsing rules.
It is intentionally conservative and intended for CI-style sanity checks only.

Exits:
 0 - success
 1 - usage error
 2 - front-matter missing
 3 - TOKEN_BLOCK missing
 4 - missing required keys / parse error
"""
import re
import sys
from pathlib import Path


def parse_front_matter(raw: str):
    """Return a mapping of top-level YAML keys using naive parsing.
    Supports simple scalars and top-level lists (dash-prefixed).
    """
    mapping = {}
    key = None
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        if not line.strip():
            i += 1
            continue
        if re.match(r"^\s*-\s+", line) and key:
            # list item
            val = line.split('-', 1)[1].strip()
            mapping.setdefault(key, []).append(_unquote(val))
            i += 1
            continue
        m = re.match(r"^(?P<k>[A-Za-z0-9_]+):\s*(?P<v>.*)$", line)
        if m:
            k = m.group('k')
            v = m.group('v').strip()
            if v == '':
                # likely a list or nested block
                key = k
                mapping.setdefault(k, [])
            else:
                mapping[k] = _unquote(v)
                key = k
            i += 1
            continue
        # unknown line — skip
        i += 1
    return mapping


def _unquote(s: str):
    if (s.startswith("\"") and s.endswith("\"")) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def validate_adr(path: Path):
    s = path.read_text(encoding='utf-8')
    m = re.search(r"^---\n(.*?)\n---\n", s, flags=re.S|re.M)
    if not m:
        print(f"ERROR: No YAML front-matter found in {path}")
        return 2
    fm_raw = m.group(1)
    fm = parse_front_matter(fm_raw)
    req = ['title', 'date', 'status', 'author', 'related', 'supersedes', 'last_updated']
    missing = [k for k in req if k not in fm]
    if missing:
        print(f"ERROR: Missing required front-matter keys in {path}: {missing}")
        return 4
    if 'TOKEN_BLOCK' not in s:
        print(f"ERROR: TOKEN_BLOCK not found in {path}")
        return 3
    print(f"OK: {path} front-matter parsed. Keys: {list(fm.keys())}")
    print('Parsed front-matter mapping:')
    for k, v in fm.items():
        print(f"  {k}: {v!r}")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: adr_validator.py /path/to/adr.md")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file does not exist: {path}")
        sys.exit(1)
    rc = validate_adr(path)
    sys.exit(rc)
