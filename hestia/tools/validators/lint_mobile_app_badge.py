#!/usr/bin/env python3
"""Lint notify.mobile_app_* badge usage in YAML files.

Scans YAML files for service/action entries that call notify.mobile_app_* and
flags any `badge:` keys that are not nested under `data: -> data: -> push:`
or under `data: push:` depending on style.

This script writes a TSV report to hestia/ops/audit/mobile_app_badge_lint.tsv
with columns: file	line	service	description
"""
from __future__ import annotations

import os
import re
from typing import List, Optional, Tuple

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIT_DIR = os.path.join(ROOT, 'ops', 'audit')
AUDIT_FILE = os.path.join(AUDIT_DIR, 'mobile_app_badge_lint.tsv')

MOBILE_RE = re.compile(r"notify\.mobile_app_[A-Za-z0-9_]+")


def find_yaml_files(root: str) -> List[str]:
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # skip .git and deps and venvs
        if '.git' in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.endswith(('.yaml', '.yml')):
                out.append(os.path.join(dirpath, fn))
    return out


def load_yaml_safe(path: str) -> Optional[object]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def node_contains_badge(node) -> bool:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == 'badge':
                return True
            if node_contains_badge(v):
                return True
    elif isinstance(node, list):
        for item in node:
            if node_contains_badge(item):
                return True
    return False


def is_badge_nested_correctly(data_node) -> bool:
    """Return True if any badge found is nested under
    data->data->push or data->push.

    We consider these valid forms:
    - data:
        message: "..."
        data:
          push:
            badge: 0

    - data:
        message: "..."
        push:
          badge: 0

    Also allow templates as badge value.
    """
    if not isinstance(data_node, dict):
        return False
    # direct data.push
    if (
        'push' in data_node
        and isinstance(data_node['push'], dict)
        and 'badge' in data_node['push']
    ):
        return True
    # nested data.data.push
    if 'data' in data_node and isinstance(data_node['data'], dict):
        nested = data_node['data']
        if (
            'push' in nested
            and isinstance(nested['push'], dict)
            and 'badge' in nested['push']
        ):
            return True
    return False


def scan_file(path: str) -> List[Tuple[int, str, str]]:
    """Return list of (line, service, description) findings for the file."""
    content = None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return []

    findings: List[Tuple[int, str, str]] = []

    # Quick heuristic: search for notify.mobile_app_ occurrences in text
    for m in MOBILE_RE.finditer(content):
        # find line number
        start = m.start()
        line = content.count('\n', 0, start) + 1
        service = m.group(0)

    # Try to parse surrounding YAML block to examine related data/badge keys.
    # We load the whole file and traverse for dicts containing the service.
        parsed = load_yaml_safe(path)
        if parsed is None:
            findings.append((line, service, 'failed-to-parse-yaml'))
            continue

    # Walk parsed structure to find nodes where service value equals our
    # service
        stack: List[Tuple[object, List[str]]] = [(parsed, [])]
        while stack:
            node, path_keys = stack.pop()
            if isinstance(node, dict):
                for k, v in node.items():
                    # service may be under 'service' key or action
                    # items may be scalar strings
                    if (
                        k == 'service'
                        and isinstance(v, str)
                        and MOBILE_RE.search(v)
                    ):
                        svc = v
                        # find sibling 'data' node
                        parent = node
                        data_node = (
                            parent.get('data')
                            if isinstance(parent, dict)
                            else None
                        )
                        if data_node is None:
                            # Another allowed style uses
                            # 'service: notify.mobile_app'
                            # then 'data:' elsewhere
                            desc = 'missing-data-block'
                            findings.append((line, svc, desc))
                        else:
                            if (
                                not is_badge_nested_correctly(data_node)
                                and node_contains_badge(data_node)
                            ):
                                findings.append(
                                    (line, svc, 'badge-not-under-data.push')
                                )
                    else:
                        stack.append((v, path_keys + [str(k)]))
            elif isinstance(node, list):
                for item in node:
                    stack.append((item, path_keys + ['[]']))

    return findings


def main() -> int:
    files = find_yaml_files(ROOT)
    os.makedirs(AUDIT_DIR, exist_ok=True)
    rows: List[str] = []
    rows.append('file\tline\tservice\tdescription')
    total = 0
    for f in files:
        findings = scan_file(f)
        for line, svc, desc in findings:
            rel = os.path.relpath(f, ROOT)
            rows.append(f"{rel}\t{line}\t{svc}\t{desc}")
            total += 1

    with open(AUDIT_FILE, 'w', encoding='utf-8') as out:
        out.write('\n'.join(rows) + '\n')

    print(f'Wrote {AUDIT_FILE} with {total} findings')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
