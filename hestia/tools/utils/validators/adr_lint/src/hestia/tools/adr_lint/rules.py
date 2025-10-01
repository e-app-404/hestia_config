"""Core linting rules and file discovery for ADR files."""
from __future__ import annotations

import os
import re
from typing import Any, Dict, Iterable, List, Optional

import frontmatter

from . import config


def collect_targets(paths: Iterable[str], include_playbooks: bool, walker_cfg: config.WalkerConfig) -> List[str]:
    out: List[str] = []
    seen = set()
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p, followlinks=walker_cfg.follow_symlinks):
                # ignore dotdirs and common large dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'venv')]
                if not include_playbooks:
                    # filter operator paths
                    if any(root.startswith(op) for op in config.OPERATOR_PATHS):
                        continue
                for f in files:
                    if f.lower().endswith('.md'):
                        fp = os.path.join(root, f)
                        if fp in seen:
                            continue
                        seen.add(fp)
                        out.append(fp)
        else:
            if os.path.isfile(p):
                out.append(p)
    return out


def _file_read_safe(path: str, max_bytes: int) -> Optional[str]:
    try:
        st = os.stat(path, follow_symlinks=False)
        if st.st_size > max_bytes:
            return None
        with open(path, 'r', encoding='utf-8') as fh:
            return fh.read()
    except Exception:
        return None


def check_file(path: str, walker_cfg: config.WalkerConfig | None = None) -> Dict[str, Any]:
    walker_cfg = walker_cfg or config.WalkerConfig()
    raw = _file_read_safe(path, walker_cfg.max_bytes)
    violations: List[Dict[str, Any]] = []
    if raw is None:
        violations.append({"severity": "warn", "rule": "io.skip", "line": 0, "message": "skipped (binary/too large/unreadable)",})
        return {"file": path, "violations": violations}

    # frontmatter check
    violations.extend(_check_frontmatter(path, raw))

    # fences and path checks
    violations.extend(_check_fences_and_paths(path, raw))

    # token block check
    violations.extend(_check_token_block(path, raw))

    return {"file": path, "violations": violations}


def _check_frontmatter(path: str, content: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    # tolerate leading blank lines before the YAML frontmatter
    # detect frontmatter delimiters (---) using a line-oriented search so
    # that tests which include a leading newline are handled correctly.
    markers = re.findall(r"(?m)^---\s*$", content)
    if len(markers) < 2:
        out.append({"severity": "error", "rule": "frontmatter.missing", "line": 1, "message": "missing frontmatter block"})
        return out
    if len(markers) > 2:
        # multiple '---' delimiting markers usually means duplicated FM blocks
        out.append({"severity": "error", "rule": "frontmatter.duplicate", "line": 1, "message": "multiple frontmatter blocks"})
        # continue to parse the first block for additional errors

    # parse and validate keys/order using frontmatter loader
    try:
        # frontmatter.loads expects the YAML block at the start of the string.
        # Allow files that have leading blank lines by stripping left-side
        # whitespace for the parser while keeping the original content for
        # other checks and line numbers.
        md = frontmatter.loads(content.lstrip())
    except Exception as e:
        return [{"severity": "error", "rule": "frontmatter.parse", "line": 1, "message": f"parse error: {e}"}]

    fm = md.metadata or {}
    required = ["title", "date", "status", "author", "related", "supersedes", "last_updated"]
    for k in required:
        if k not in fm:
            out.append({"severity": "error", "rule": "frontmatter.missing-key", "line": 1, "message": f"missing key '{k}'"})

    # order check for first three keys
    # we do a simple check by re-parsing the start of file
    head = content.splitlines()[:40]
    head_txt = "\n".join(head)
    order_ok = re.search(r"^title:\s.*\n^date:\s.*\n^status:\s.*", head_txt, re.M)
    if not order_ok:
        out.append({"severity": "error", "rule": "frontmatter.order", "line": 1, "message": "first three keys must be: title, date, status"})

    # status alias
    if isinstance(fm.get('status'), str) and fm['status'].strip().lower() == 'approved':
        out.append({"severity": "warn", "rule": "frontmatter.status-alias", "line": 1, "message": "use 'Accepted' instead of 'Approved'"})

    # crossrefs check
    body = md.content
    if re.search(r"ADR-\d{4}", body) is None:
        # not mandatory, but warn if absent
        out.append({"severity": "warn", "rule": "frontmatter.crossref", "line": 1, "message": "no ADR-#### cross-reference found in body"})

    return out


_fence_re = re.compile(r"(?m)^(```+)([^\n]*)$")


def _check_fences_and_paths(path: str, content: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    lines = content.splitlines()
    in_fence = False
    fence_lang = ''
    fence_start = 0
    block_lines: List[str] = []

    for i, line in enumerate(lines, start=1):
        m = _fence_re.match(line)
        if m:
            fence_marker, lang = m.group(1), m.group(2).strip()
            if not in_fence:
                in_fence = True
                fence_lang = lang
                fence_start = i
                block_lines = []
                if fence_lang and fence_lang not in ('bash', 'sh', 'zsh', 'python', 'yaml', 'jinja', ''):
                    out.append({"severity": "warn", "rule": "fence.unknown-lang", "line": i, "lang": fence_lang, "message": f"unknown fence language '{fence_lang}'"})
            else:
                # closing fence
                in_fence = False
                # process block for path checks
                block_text = "\n".join(block_lines)
                out.extend(_check_paths_in_block(path, fence_start, fence_lang, block_text))
                fence_lang = ''
        else:
            if in_fence:
                block_lines.append(line)

    if in_fence:
        out.append({"severity": "error", "rule": "fence.unclosed", "line": fence_start, "message": "unclosed code fence"})

    # also run inline path checks in prose for symlink mentions
    if re.search(r"\b(ln -s|symlink|os\.symlink)\b", content, re.I):
        out.append({"severity": "error", "rule": "symlink.mention", "line": 1, "message": "symlink usage in config root is forbidden per ADR-0015"})

    return out


def _check_paths_in_block(path: str, start_line: int, lang: str, block_text: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    # /Volumes is always ERROR
    for m in re.finditer(r"/Volumes/\S+", block_text):
        ln = start_line + block_text[:m.start()].count('\n')
        out.append({"severity": "error", "rule": "path.volumes", "line": ln, "lang": lang, "message": f"forbidden /Volumes path: {m.group(0)}"})

    # /n/ha is ERROR unless parameterized or operator-only
    for m in re.finditer(r"/n/ha(?:/\S*)?", block_text):
        ln = start_line + block_text[:m.start()].count('\n')
        # allow if block_text contains one of ALLOWED_VARS
        if any(v in block_text for v in config.ALLOWED_VARS):
            continue
        # allow operator-only annotation
        if re.search(r"operator-only\s*\(macOS\)", block_text, re.I):
            continue
        out.append({"severity": "error", "rule": "path.n_ha", "line": ln, "lang": lang, "message": "hard-coded /n/ha in code block; parameterize using allowed vars or mark operator-only"})

    # canonical template checks
    for m in re.finditer(r"/config/[^\s`'\)]+template\.library\.jinja", block_text):
        ln = start_line + block_text[:m.start()].count('\n')
        found = m.group(0)
        if found.strip().startswith(config.CANONICAL_TEMPLATE):
            # allowed
            continue
        # allow parameterized forms like ${EFFECTIVE}/custom_templates/template.library.jinja
        if re.search(r"\$\{[^}]+\}/custom_templates/template\.library\.jinja", found):
            continue
        out.append({"severity": "error", "rule": "template.path", "line": ln, "lang": lang, "message": f"non-canonical template path: {found}"})

    return out


def _check_token_block(path: str, content: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    # find a fenced yaml block at end labeled TOKEN_BLOCK:
    m = re.search(r"```\s*yaml\s*\n(.*?TOKEN_BLOCK:.*)```\s*$", content, re.S)
    if not m:
        out.append({"severity": "error", "rule": "token_block.missing", "line": 1, "message": "missing TOKEN_BLOCK YAML at end"})
        return out

    block = m.group(1)
    # quick checks for accepted/requires/drift keys
    if 'accepted' not in block and 'requires' not in block:
        out.append({"severity": "error", "rule": "token_block.schema", "line": 1, "message": "TOKEN_BLOCK must include 'accepted' or 'requires'"})

    # drift entries should be 'DRIFT: <kebab>'
    for d in re.findall(r"DRIFT:\s*([a-z0-9-]+)", block):
        if not re.match(r"^[a-z0-9-]+$", d):
            out.append({"severity": "error", "rule": "token_block.drift", "line": 1, "message": f"invalid DRIFT token: {d}"})

    return out
