#!/usr/bin/env python3
"""Vault indexer and daily janitor
- Indexes files in hestia/workspace/archive/vault and assigns them to categories
- Enforces deletion windows for tarballs and deprecated
- Emits a small log entry and writes a 'deletion_receipt' file when items are removed
- Optionally integrates with Home Assistant notifier via a webhook or an MQTT publish (placeholder)

This is a tiny, local script intended to be run by cron/daily scheduler.
"""
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

VAULT_ROOT = Path('~/hass/hestia/workspace/archive/vault').expanduser()
INDEX_FILE = VAULT_ROOT / 'vault_index.json'
LOG_FILE = VAULT_ROOT / 'vault_index.log'

# Deletion policy (days)
POLICY = {
    'backups': None,     # no deletion
    'bundles': None,     # no deletion
    'tarballs': 60,      # days
    'deprecated': 60,    # days
    'receipts': 14,      # days
    'storage': None,
}


def categorize(p: Path):
    # category is the first-level directory under vault
    try:
        rel = p.relative_to(VAULT_ROOT)
    except Exception:
        return None
    parts = rel.parts
    if len(parts) == 0:
        return None
    return parts[0]


def scan_and_index():
    idx = {'generated_at': datetime.now(timezone.utc).isoformat(), 'items': []}
    now = time.time()
    for p in VAULT_ROOT.rglob('*'):
        if p.is_dir():
            continue
        cat = categorize(p)
        st = p.stat()
        item = {
            'path': str(p),
            'category': cat,
            'size': st.st_size,
            'mtime': datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
        }
        idx['items'].append(item)
    INDEX_FILE.write_text(json.dumps(idx, indent=2), encoding='utf-8')
    LOG_FILE.write_text(
        f"{datetime.now(timezone.utc).isoformat()} - indexed {len(idx['items'])} items\n",
        encoding='utf-8'
    )
    return idx


def enforce_policy(idx=None, dry_run=True):
    if idx is None:
        idx_path = INDEX_FILE
        if not idx_path.exists():
            idx = scan_and_index()
        else:
            idx = json.loads(idx_path.read_text(encoding='utf-8'))
    now = datetime.now(timezone.utc)
    removed = []
    for item in idx['items']:
        cat = item.get('category')
        if cat not in POLICY:
            continue
        days = POLICY[cat]
        if days is None:
            continue
        mtime = datetime.fromisoformat(item['mtime'])
        if now - mtime > timedelta(days=days):
            p = Path(item['path'])
            if dry_run:
                removed.append({'path': str(p), 'action': 'would_remove'})
            else:
                # move to a tombstone area (just remove here)
                receipt = p.parent / (p.name + '.deleted.json')
                p.unlink()
                receipt.write_text(
                    json.dumps({'deleted_at': now.isoformat(), 'path': str(p)}),
                    encoding='utf-8'
                )
                removed.append({'path': str(p), 'action': 'removed'})
                # TODO: emit HA notification / logbook event (placeholder)
    return removed


if __name__ == '__main__':
    dry = '--no-dry' not in sys.argv
    idx = scan_and_index()
    removed = enforce_policy(idx, dry_run=dry)
    print('indexed', len(idx['items']), 'items; policy removals:', len(removed))
    if removed:
        print('sample:', removed[:5])
