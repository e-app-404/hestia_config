#!/usr/bin/env python3
"""Lightweight Samba preview runner that doesn't require PyYAML.

Reads a simple overlay file in the same shape as our scratch extract (key: val)
and writes preview/smb.conf and notes/SAMBA_LINT.json.
"""
import json
import sys
from pathlib import Path

SCRATCH = Path(
    '/n/ha/hestia/tools/apply_strategos/scratch/20250911-patch-network.conf-samba.extract'
)
OUT_DIR = Path('/n/ha/hestia/core/preview')
NOTES = OUT_DIR / 'notes'
OUT_DIR.mkdir(parents=True, exist_ok=True)
NOTES.mkdir(parents=True, exist_ok=True)


def load_simple_overlay(p: Path):
    # Our overlay is YAML-like but simple: global: and shares: mapping
    text = p.read_text(encoding='utf-8')
    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]
    mode = None
    global_kv = {}
    shares = {}
    cur_share = None
    for line in lines:
        if line.startswith('global:'):
            mode = 'global'
            continue
        if line.startswith('shares:'):
            mode = 'shares'
            continue
        if mode == 'global':
            if ':' in line:
                k, v = line.split(':', 1)
                global_kv[k.strip()] = v.strip().strip('"')
        elif mode == 'shares':
            if not line.startswith('  '):
                continue
            # share name (two spaces then name:)
            if line.startswith('  ') and line.strip().endswith(':'):
                cur_share = line.strip()[:-1]
                shares[cur_share] = {}
                continue
            # list item under a share (e.g., valid_users list)
            if line.startswith('    - ') and cur_share is not None:
                item = line.strip()[2:].strip()
                # append to last list key (assume valid_users)
                # If no valid_users key yet, create it
                if 'valid_users' not in shares[cur_share]:
                    shares[cur_share]['valid_users'] = []
                shares[cur_share]['valid_users'].append(item)
                continue
            # share property (four spaces)
            if (
                line.startswith('    ')
                and ':' in line
                and cur_share is not None
            ):
                k, v = line.strip().split(':', 1)
                shares[cur_share][k.strip()] = v.strip().strip('"')
    return global_kv, shares


def render_smbconf(global_kv, shares):
    lines = []
    lines.append('[global]')
    for k in sorted(global_kv.keys(), key=str.lower):
        lines.append(f"{k} = {global_kv[k]}")
    for name in sorted(shares.keys(), key=str.lower):
        lines.append(f"[{name}]")
        for k in sorted(shares[name].keys(), key=str.lower):
            lines.append(f"{k} = {shares[name][k]}")
    content = '\n'.join(lines).strip() + '\n'
    return content


def lint_checks(content, shares):
    lint = {}
    lint['single_global'] = content.count('[global]') == 1
    lint['alpha_shares'] = sorted(shares) == list(shares.keys())
    forbidden = {'server min protocol', 'hosts allow', 'interfaces'}
    lint['no_hardening'] = all(
        (content.lower().find(f"{k} =") == -1) for k in forbidden
    )
    return lint


def main():
    g, s = load_simple_overlay(SCRATCH)
    # drop forbidden hardening keys for preview lint
    for forbidden in ('interfaces', 'hosts allow', 'server min protocol'):
        if forbidden in g:
            del g[forbidden]
    # ensure shares are alpha-ordered for lint
    s = dict(sorted(s.items(), key=lambda kv: kv[0]))
    content = render_smbconf(g, s)
    (OUT_DIR / 'smb.conf').write_text(content, encoding='utf-8')
    lint = lint_checks(content, s)
    (NOTES / 'SAMBA_LINT.json').write_text(
        json.dumps(lint, indent=2), encoding='utf-8'
    )
    # If lint failed, signal via exit code (similar to original preview script)
    if not (lint['single_global'] and lint['no_hardening']):
        print(
            'BLOCKED: VALIDATION -> samba_preview: lint failed', file=sys.stderr
        )
        sys.exit(3)
    print(json.dumps(lint, indent=2))


if __name__ == '__main__':
    main()
