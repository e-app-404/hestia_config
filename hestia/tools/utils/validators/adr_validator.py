#!/usr/bin/env python3
"""Minimal ADR validator that avoids external dependencies.
This lightweight parser looks for a leading YAML front-matter block and
extracts required keys with simple parsing rules. It is intentionally
conservative and intended for CI-style sanity checks only.

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
    if (
        (s.startswith("\"") and s.endswith("\""))
        or (s.startswith("'") and s.endswith("'"))
    ):
        return s[1:-1]
    return s


def validate_adr(path: Path) -> int:
    s = path.read_text(encoding='utf-8')
    # allow optional leading whitespace before the opening '---' and allow the
    # closing '---' to be followed by EOF or a newline. This tolerates small
    # formatting differences (CRLF, extra blank line, or missing trailing NL).
    m = re.search(r"^\s*---\s*\n(.*?)\n---\s*(?:\n|$)", s, flags=re.S | re.M)
    if not m:
        print(f"ERROR: No YAML front-matter found in {path}")
        return 2
    fm_raw = m.group(1)
    try:
        fm = parse_front_matter(fm_raw)
    except Exception as e:
        print(f"ERROR: Failed parsing front-matter in {path}: {e}")
        return 4

    # author/authors consistency checks
    if 'author' in fm and 'authors' in fm:
        # normalize authors to comparable form
        a = fm['author']
        authors = fm['authors']
        # if authors is a list and a differs from the first element, error
        if isinstance(authors, list) and authors:
            if a != authors[0]:
                print(
                    "ERROR: Conflicting 'author' and 'authors' in {}: "
                    "author={!r} authors[0={!r}]".format(path, a, authors[0])
                )
                return 4
        else:
            # authors present but not a list — warn and continue
            if a != authors:
                print(
                    "ERROR: Conflicting 'author' and 'authors' in {}: "
                    "author={!r} authors={!r}".format(path, a, authors)
                )
                return 4
    elif 'author' not in fm and 'authors' in fm:
        # promote authors[0] to author for downstream consumers
        authors = fm['authors']
        if isinstance(authors, list) and authors:
            promoted = authors[0]
            print(
                "NOTICE: Promoting authors[0] -> author for {}: "
                "author={!r}".format(path, promoted)
            )
            fm['author'] = promoted
        elif isinstance(authors, str) and authors:
            print(
                "NOTICE: Promoting authors -> author for {}: "
                "author={!r}".format(path, authors)
            )
            fm['author'] = authors
        else:
            print(
                "ERROR: 'authors' present but empty in {}; "
                "missing 'author'".format(path)
            )
            return 4

    req = [
        'id', 'title', 'date', 'status', 'author', 'related', 'supersedes',
        'last_updated'
    ]
    missing = [k for k in req if k not in fm]
    if missing:
        print(f"ERROR: Missing required front-matter keys in {path}: {missing}")
        return 3

    if 'TOKEN_BLOCK' not in s:
        # TOKEN_BLOCK is recommended but not fatal; warn only
        print(f"WARN: TOKEN_BLOCK not found in {path}")

    print(f"OK: {path} front-matter parsed. Keys: {list(fm.keys())}")
    print('Parsed front-matter mapping:')
    for k, v in fm.items():
        print(f"  {k}: {v!r}")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: adr_validator.py /path/to/adr.md [dir_or_file ...]")
        sys.exit(1)

    paths = []
    for a in sys.argv[1:]:
        p = Path(a)
        if not p.exists():
            print(f"ERROR: path does not exist: {p}")
            continue
        if p.is_dir():
            # ignore duplicate .md.md files and ADR template placeholders
            md_files = [
                p for p in p.glob('*.md')
                if (
                    not str(p).endswith('.md.md')
                    and not p.name.startswith('ADR-000x')
                )
            ]
            paths.extend(sorted(md_files))
        else:
            paths.append(p)

    if not paths:
        print("No ADR files found to validate.")
        sys.exit(1)

    failures = 0
    for p in paths:
        rc = validate_adr(p)
        if rc != 0:
            failures += 1

    if failures:
        print(f"Validation completed: {failures} file(s) failed.")
        sys.exit(2)
    print("Validation completed: all files OK.")
    sys.exit(0)
