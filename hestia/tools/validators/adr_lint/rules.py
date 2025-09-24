"""Minimal ADR linting rules."""
import re
from typing import Any, Dict, List

import frontmatter


def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as fh:
        return fh.read()


def check_frontmatter(content: str) -> List[str]:
    errors = []
    try:
        md = frontmatter.loads(content)
    except Exception as e:
        return [f"frontmatter: parse error: {e}"]

    fm = md.metadata or {}
    required = ['title', 'date', 'status', 'author']
    for k in required:
        if k not in fm:
            errors.append(f"frontmatter: missing '{k}'")

    return errors


_banned = [r"/Volumes/", r"/n/ha"]


def check_banned_paths(content: str) -> List[str]:
    errors = []
    for pat in _banned:
        if re.search(re.escape(pat), content):
            errors.append(f"banned-path: contains '{pat}'")
    return errors


def check_file(path: str) -> Dict[str, Any]:
    content = read_file(path)
    violations = []
    violations.extend(check_frontmatter(content))
    violations.extend(check_banned_paths(content))
    return {"file": path, "violations": violations}
