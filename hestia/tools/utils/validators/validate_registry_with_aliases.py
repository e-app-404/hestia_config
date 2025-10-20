#!/usr/bin/env python3
"""
validate_registry_with_aliases.py

Validate `room_registry.yaml` against `area_mapping.yaml` and `presence_mapping.yaml` while
supporting simple alias mappings and person.<id> ↔ node id equivalence.

Usage:
  python validate_registry_with_aliases.py
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
REG_PATH = ROOT / 'hestia' / 'config' / 'registry' / 'room_registry.yaml'
AREA_PATH = (
    ROOT
    / 'hestia'
    / 'library'
    / 'docs'
    / 'architecture'
    / 'area_mapping.yaml'
)

PRES_PATH = (
    ROOT
    / 'hestia'
    / 'library'
    / 'docs'
    / 'architecture'
    / 'presence_mapping.yaml'
)


# === Configurable alias mappings: canonical -> alias
CANONICAL_TO_AREA_ALIAS = {
    'downstairs': 'hallway_downstairs',
    'upstairs': 'hallway_upstairs',
}

CANONICAL_TO_FLOOR_ALIAS = {
    'downstairs': 'ground_floor',
    'upstairs': 'top_floor',
}

# invert maps for lookup alias -> canonical
AREA_ALIAS_TO_CANONICAL = {v: k for k, v in CANONICAL_TO_AREA_ALIAS.items()}
FLOOR_ALIAS_TO_CANONICAL = {v: k for k, v in CANONICAL_TO_FLOOR_ALIAS.items()}


def load_yaml(p: Path):
    if not p.exists():
        print('Missing file', p)
        sys.exit(1)
    return yaml.safe_load(p.read_text(encoding='utf-8'))


def extract_registry_areas(reg):
    reg_entities = set()
    rooms = reg.get('_rooms', {})
    for topk, topv in rooms.items():
        if isinstance(topv, dict):
            for group, groupval in topv.items():
                if isinstance(groupval, dict):
                    for k in groupval.keys():
                        if k.startswith('__'):
                            continue
                        reg_entities.add(k)

                    def walk(o):
                        if isinstance(o, dict):
                            for kk, vv in o.items():
                                if kk == 'area_id' and isinstance(vv, str):
                                    reg_entities.add(vv)
                                else:
                                    walk(vv)
                        elif isinstance(o, list):
                            for it in o:
                                walk(it)

                    walk(groupval)
    return reg_entities


def extract_area_nodes(area):
    nodes = area.get('nodes', [])
    node_ids = set()
    for n in nodes:
        if isinstance(n, dict) and 'id' in n:
            node_ids.add(n['id'])
    containment_keys = set(area.get('containment_graph', {}).keys())
    return node_ids, containment_keys


def run():
    reg = load_yaml(REG_PATH)
    area = load_yaml(AREA_PATH)
    pres = load_yaml(PRES_PATH)

    reg_areas = extract_registry_areas(reg)
    node_ids, containment_keys = extract_area_nodes(area)

    presence_map = pres.get('area_presence_map', {})
    presence_areas = set(presence_map.keys())
    persons_in_presence = set()
    for v in presence_map.values():
        if isinstance(v, list):
            for p in v:
                persons_in_presence.add(p)

    # person nodes in area mapping
    person_nodes = set()
    for n in area.get('nodes', []):
        if isinstance(n, dict) and n.get('type') == 'person' and 'id' in n:
            person_nodes.add(n['id'])

    # raw registry text search for person.<id>
    reg_text = REG_PATH.read_text(encoding='utf-8')
    reg_persons = set(re.findall(r'person\.[A-Za-z0-9_\-]+', reg_text))

    # Validate presence areas using alias mapping
    missing = []
    resolved_aliases = {}
    for a in sorted(presence_areas):
        ok = False
        reasons = []
        if a in reg_areas or a in node_ids or a in containment_keys:
            ok = True
            reasons.append('direct')
        else:
            # try alias -> canonical mapping (alias -> canonical)
            if a in AREA_ALIAS_TO_CANONICAL:
                canonical = AREA_ALIAS_TO_CANONICAL[a]
                if (
                    canonical in reg_areas
                    or canonical in node_ids
                    or canonical in containment_keys
                ):
                    ok = True
                    reasons.append(f'alias->canonical({canonical})')
                    resolved_aliases[a] = canonical
            # also try mapping with floor alias mapping (if presence area looks
            # like hallway_downstairs etc.)
            if not ok and a in AREA_ALIAS_TO_CANONICAL:
                canonical = AREA_ALIAS_TO_CANONICAL[a]
                if canonical in reg_areas:
                    ok = True
                    reasons.append('alias fallback')

        if not ok:
            missing.append(a)

    # check persons: treat person.<id> equivalent to node id '<id>'
    persons_missing = []
    for p in sorted(persons_in_presence):
        if not isinstance(p, str):
            continue
        if p.startswith('person.'):
            pid = p.split('.', 1)[1]
            if pid in person_nodes or p in reg_persons:
                continue
            # also accept node id equal to pid
            if pid in node_ids:
                continue
            persons_missing.append(p)
        else:
            # non-person literal — check node presence
            if p not in person_nodes and p not in reg_persons:
                persons_missing.append(p)

    # Report
    print('Validation with aliases:')
    print(' - registry areas discovered:', len(reg_areas))
    print(' - area_mapping nodes:', len(node_ids))
    print('   containment keys:', len(containment_keys))
    print(' - presence areas declared:', len(presence_areas))
    print(' - persons referenced in presence mapping:', persons_in_presence)
    print('\nResolved aliases (presence area -> canonical):')
    for k, v in resolved_aliases.items():
        print(' ', k, '->', v)

    if missing:
        print('\nPresence areas still missing from registry/area mapping:')
        for m in missing:
            print(' ', m)
    else:
        print('\nAll presence areas resolved (direct or via aliases).')

    if persons_missing:
        print('\nPersons referenced but not defined as person node '
              'or present in registry text:')
        for p in persons_missing:
            print(' ', p)
    else:
        print('\nAll persons referenced in presence mapping are accounted for '
              '(person.<id> ↔ node id equivalence supported).')


if __name__ == '__main__':
    run()
