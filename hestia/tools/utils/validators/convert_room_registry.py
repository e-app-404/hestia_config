#!/usr/bin/env python3
"""
convert_room_registry.py
Utility to convert `hestia/config/registry/room_registry.yaml` from list-of-single-key
mappings into mappings keyed by area id. Supports --dry-run (show preview) and --apply
(write changes). Creates timestamped backups when applying.

Usage:
  python convert_room_registry.py --dry-run
  python convert_room_registry.py --apply
"""
import argparse
import datetime
import shutil
import sys
from pathlib import Path

import yaml

P = (
    Path(__file__).resolve().parents[3]
    / 'config'
    / 'registry'
    / 'room_registry.yaml'
)

BACKUP_DIR = (
    Path(__file__).resolve().parents[3]
    / 'vault'
    / 'backups'
)


def extract_single_key(item):
    if isinstance(item, dict) and len(item) == 1:
        k = next(iter(item.keys()))
        return k, item[k]
    if (
        isinstance(item, list)
        and len(item) == 1
        and isinstance(item[0], dict)
        and len(item[0]) == 1
    ):
        k = next(iter(item[0].keys()))
        return k, item[0][k]
    return None, None


def unwrap_single_list_item(x):
    if isinstance(x, list) and len(x)==1:
        return x[0]
    return x


def convert_list_of_single_key_mappings(lst):
    newmap = {}
    order = []
    unconverted = []
    for item in lst:
        k, v = extract_single_key(item)
        if k is None:
            unconverted.append(item)
            continue
        order.append(k)
        v = unwrap_single_list_item(v)
        if isinstance(v, dict):
            sub = v.get('subareas')
            if isinstance(sub, list):
                sub_order = []
                submap = {}
                sub_unconverted = []
                for s in sub:
                    sk, sv = extract_single_key(s)
                    if sk is None:
                        sub_unconverted.append(s)
                        continue
                    sub_order.append(sk)
                    sv = unwrap_single_list_item(sv)
                    submap[sk] = sv
                new_sub = {'__order': sub_order}
                new_sub.update(submap)
                if sub_unconverted:
                    new_sub['__unconverted_items'] = sub_unconverted
                v['subareas'] = new_sub
        newmap[k] = v
    out = {'__order': order}
    out.update(newmap)
    if unconverted:
        out['__unconverted_items'] = unconverted
    return out


def convert(data):
    rooms = data.get('_rooms', {})
    changed = False
    for topk, topv in list(rooms.items()):
        if not isinstance(topv, dict):
            continue
        for group_name, group_val in list(topv.items()):
            if isinstance(group_val, list):
                conv = convert_list_of_single_key_mappings(group_val)
                rooms[topk][group_name] = conv
                changed = True
    return data, changed


def finalize_unconverted(data):
    # Move items from __unconverted_items into mapping where area_id
    # or key can be inferred
    rooms = data.get('_rooms', {})
    changed = False
    for topk, topv in rooms.items():
        if not isinstance(topv, dict):
            continue
        for group, val in list(topv.items()):
            if isinstance(val, dict) and '__unconverted_items' in val:
                items = val.pop('__unconverted_items')
                for item in items:
                    if isinstance(item, dict) and len(item) == 1:
                        k = next(iter(item.keys()))
                        v = item[k]
                        topv[group][k] = v
                        changed = True
                    elif isinstance(item, dict) and 'area_id' in item:
                        k = item.get('area_id')
                        if k in topv[group]:
                            k = f"unconverted_{k}"
                        topv[group][k] = item
                        changed = True
                    else:
                        val.setdefault('__still_unconverted', []).append(item)
                        changed = True
    return data, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    if not (args.dry_run or args.apply):
        ap.error('One of --dry-run or --apply is required')

    if not P.exists():
        print('room_registry.yaml not found at', P)
        sys.exit(1)

    text = P.read_text(encoding='utf-8')
    data = yaml.safe_load(text)

    converted, changed = convert(data)
    converted, more_changed = finalize_unconverted(converted)
    changed = changed or more_changed

    out = yaml.safe_dump(converted, sort_keys=False, allow_unicode=True)

    if args.dry_run:
        print('DRY RUN - changes preview:\n')
        print('\n'.join(out.splitlines()[:300]))
        if changed:
            print('\n-- Would make changes --')
        else:
            print('\n-- No changes needed --')
        return

    if args.apply:
        # ensure backup dir exists
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_name = 'room_registry.yaml.bk.' + ts
        backup = BACKUP_DIR / backup_name
        shutil.copy2(P, backup)
        print('Backup created at', backup)
        P.write_text(out, encoding='utf-8')
        print('Applied conversion to', P)

if __name__ == '__main__':
    main()
