#!/usr/bin/env python3
"""Auto-fix ADR front-matter author/authors inconsistencies.

Rules:
 - If `author` is missing and `authors` exists (list or string), promote
     `authors[0]` -> `author`.
 - If both exist and `author != authors[0]`, overwrite `author` with
     `authors[0]` and emit a notice.

This tool is conservative and only edits the YAML front-matter block; the
body content is left untouched.
"""
import re
from pathlib import Path
from typing import Optional


def parse_front_matter(raw: str):
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
            val = line.split('-', 1)[1].strip()
            mapping.setdefault(key, []).append(_unquote(val))
            i += 1
            continue
        m = re.match(r"^(?P<k>[A-Za-z0-9_]+):\s*(?P<v>.*)$", line)
        if m:
            k = m.group('k')
            v = m.group('v').strip()
            if v == '':
                key = k
                mapping.setdefault(k, [])
            else:
                mapping[k] = _unquote(v)
                key = k
            i += 1
            continue
        i += 1
    return mapping


def _unquote(s: str):
    if (
        (s.startswith('"') and s.endswith('"'))
        or (s.startswith("'") and s.endswith("'"))
    ):
        return s[1:-1]
    return s


def read_front_matter_and_body(path: Path) -> Optional[tuple]:
    s = path.read_text(encoding='utf-8')
    m = re.search(r"^---\n(.*?)\n---\n", s, flags=re.S | re.M)
    if not m:
        return None
    fm_raw = m.group(1)
    body = s[m.end():]
    return fm_raw, body, s[:m.start()]


def render_front_matter(mapping: dict) -> str:
    lines = ['---']
    for k, v in mapping.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for it in v:
                lines.append(f"  - {it}")
        else:
            lines.append(f"{k}: {v}")
    lines.append('---')
    return '\n'.join(lines) + '\n'


def fix_file(path: Path) -> bool:
    rv = read_front_matter_and_body(path)
    if rv is None:
        return False
    fm_raw, body, prefix = rv
    fm = parse_front_matter(fm_raw)
    changed = False

    if 'author' in fm and 'authors' in fm:
        authors = fm['authors']
        primary = (
            authors[0]
            if isinstance(authors, list) and authors
            else (authors if isinstance(authors, str) else None)
        )
        if primary and fm['author'] != primary:
            print(
                f"Fix: aligning author -> authors[0] in {path}: "
                f"{fm['author']} -> {primary}"
            )
            fm['author'] = primary
            changed = True
    elif 'author' not in fm and 'authors' in fm:
        authors = fm['authors']
        primary = (
            authors[0]
            if isinstance(authors, list) and authors
            else (authors if isinstance(authors, str) else None)
        )
        if primary:
            print(
                f"Fix: promoting authors[0] -> author in {path}: "
                f"author={primary}"
            )
            fm['author'] = primary
            changed = True

    if changed:
        new_fm = render_front_matter(fm)
        new_content = prefix + new_fm + '\n' + body
        path.write_text(new_content, encoding='utf-8')
    return changed


def main():
    root = Path('hestia/docs/ADR')
    files = sorted(root.glob('*.md'))
    total_changed = 0
    for p in files:
        if fix_file(p):
            total_changed += 1
    print(f"Auto-fix completed: {total_changed} files modified.")


if __name__ == '__main__':
    main()
