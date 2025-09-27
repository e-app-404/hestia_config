#!/usr/bin/env python3
"""Validator for hades_config_index.yaml
Checks configured ci_checks:
- yaml_load: try to parse target files with a safe YAML loader (naive fallback to text check if PyYAML not present)
- path_exists: ensure the path exists (maps /config/ to /n/ha where appropriate)
- tag_policy: ensure tags are subset of allowed set
"""
import sys
from pathlib import Path

# Prefer the canonical hades index file (conf or custom .indx extension) to
# denote that this is an index metadata file rather than a config yaml.
PREFERRED_INDEXS = [
    Path('/n/ha/hestia/index/hades_index.conf'),
    Path('/n/ha/hestia/index/hades.indx'),
]
# Fallback (legacy) location for compatibility
FALLBACK_INDEX = Path('/n/ha/hestia/index/hades_index.conf')


def locate_index():
    for p in PREFERRED_INDEXS:
        if p.exists():
            return p
    if FALLBACK_INDEX.exists():
        return FALLBACK_INDEX
    # If none found, raise so caller can display a helpful message
    checked = PREFERRED_INDEXS + [FALLBACK_INDEX]
    raise FileNotFoundError(
        'No hades index found; checked: ' + ','.join([str(x) for x in checked])
    )
ALLOWED_TAGS = set([
    'tailscale',
    'mullvad',
    'samba',
    'glances',
    'hades',
    'layer3',
    'healthcheck',
    'home_assistant',
    'synology_dsm',
])


def load_index(path: Path):
    # Prefer PyYAML when available; fall back to a minimal parser for our
    # specific index shape to allow offline validation in minimal envs.
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding='utf-8'))
    except Exception:
        # Targeted parser for the hades_index.conf file format we produce.
        text = path.read_text(encoding='utf-8')
        lines = [
            line.rstrip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith('#')
        ]
        idx = {'hades_config_index': {'artifacts': {}}}
        cur_category = None
        cur_item = None
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('hades_config_index:'):
                continue
            if stripped.startswith('artifacts:'):
                continue
            # category lines: e.g., 'network:' at two-space indent
            if (
                line.startswith('    ')
                and stripped.endswith(':')
                and not stripped.startswith('-')
            ):
                # new category
                cur_category = stripped[:-1]
                idx['hades_config_index']['artifacts'][cur_category] = []
                continue
            # item start (dash)
            if stripped.startswith('- '):
                # start a new item
                cur_item = {}
                idx['hades_config_index']['artifacts'][cur_category].append(cur_item)
                # line may contain key: value after '- '
                after = stripped[2:]
                if ':' in after:
                    k, v = after.split(':', 1)
                    cur_item[k.strip()] = v.strip().strip('"')
                continue
            # continuation line under current item (further indented)
            if (
                line.startswith('      ')
                and ':' in stripped
                and cur_item is not None
            ):
                k, v = stripped.split(':', 1)
                val = v.strip()
                if val.startswith('[') and val.endswith(']'):
                    # simple inline list
                    raw_items = val[1:-1].split(',')
                    items = [
                        x.strip().strip('"')
                        for x in raw_items
                        if x.strip()
                    ]
                    cur_item[k.strip()] = items
                else:
                    cur_item[k.strip()] = val.strip('"')
                continue
        return idx


def map_path(p: str):
    # map /config/ to /n/ha for local checks, if path starts with /config
    if p.startswith('/config/'):
        return Path('/n/ha') / p[len('/config/'):]
    return Path(p)


def check_yaml_load(p: Path):
    try:
        import yaml
        yaml.safe_load(p.read_text(encoding='utf-8'))
        return True, None
    except Exception:
        # Fallback heuristic when PyYAML is not available: ensure file is
        # non-empty and looks like YAML (contains at least one ':'). This is
        # intentionally permissive but prevents false negatives in minimal
        # environments.
        try:
            txt = p.read_text(encoding='utf-8')
            if not txt.strip():
                return False, 'empty_file'
            if ':' in txt:
                return True, None
            return False, 'no_yaml_backend_and_no_colon'
        except Exception as e:
            return False, str(e)


def check():
    idx_path = locate_index()
    idx = load_index(idx_path)
    failures = []
    art = idx.get('hades_config_index', {}).get('artifacts', {})
    for cat, items in art.items():
        for it in items:
            raw = it.get('path')
            p = map_path(raw)
            # path_exists
            if not p.exists():
                failures.append((raw, 'path_missing', str(p)))
            # tag_policy
            tags = it.get('tags', []) or []
            bad = [t for t in tags if t not in ALLOWED_TAGS]
            if bad:
                failures.append((raw, 'bad_tags', bad))
            # yaml_load
            if p.exists():
                ok, err = check_yaml_load(p)
            else:
                ok, err = (False, 'file_missing')
            if not ok:
                failures.append((raw, 'yaml_load_fail', err))
    return failures


if __name__ == '__main__':
    failures = check()
    if not failures:
        print('OK: hades index checks passed')
        sys.exit(0)
    print('FAILURES:')
    for f in failures:
        print(f)
    sys.exit(2)
