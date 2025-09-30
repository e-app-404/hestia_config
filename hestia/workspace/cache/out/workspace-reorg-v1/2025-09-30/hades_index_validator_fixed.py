#!/usr/bin/env python3
"""Validator for hades_config_index.yaml - FIXED VERSION
Checks configured ci_checks:
- yaml_load: try to parse target files with a safe YAML loader (naive fallback 
to text check if PyYAML not present)
- path_exists: ensure the path exists (maps /config/ to ~/hass where appropriate)
- tag_policy: ensure tags are subset of allowed set

FIXES APPLIED:
- Updated paths for four-pillar architecture
- Fixed ADR-0016 violations (no hardcoded /Volumes paths)
- Added proper path expansion with .expanduser()
- Support for actual manifest.yaml format
- Path normalization for old -> new structure transition
"""
import sys
import os
from pathlib import Path

# FIXED: Updated paths for four-pillar architecture with proper expansion
PREFERRED_INDEXS = [
    Path('~/hass/hestia/config/index/manifest.yaml').expanduser(),
    Path('~/hass/hestia/config/index/hades_config_index.yaml').expanduser(),
]

def get_fallback_paths():
    """Get fallback index paths respecting ADR-0016"""
    ha_mount = os.getenv('HA_MOUNT', os.path.expanduser('~/hass'))
    return [
        Path(ha_mount) / 'config/hestia/config/index/manifest.yaml',
        Path(ha_mount) / 'config/hestia/config/index/hades_config_index.yaml',
    ]

def locate_index():
    """Locate the hades config index file"""
    # Try preferred locations first
    for p in PREFERRED_INDEXS:
        if p.exists():
            return p
    
    # Try fallback locations (ADR-0016 compliant)
    for p in get_fallback_paths():
        if p.exists():
            return p
    
    # If none found, raise with helpful message
    all_checked = PREFERRED_INDEXS + get_fallback_paths()
    raise FileNotFoundError(
        'No hades index found; checked: ' + ', '.join([str(x) for x in all_checked])
    )

# ENHANCED: Updated tag policy for four-pillar architecture
ALLOWED_TAGS = set([
    'tailscale', 'mullvad', 'samba', 'glances', 'hades',
    'layer3', 'healthcheck', 'home_assistant', 'synology_dsm',
    # New tags for four-pillar architecture
    'config', 'library', 'tools', 'workspace',
    'devices', 'network', 'storage', 'diagnostics', 'preferences',
])

def normalize_artifact_path(path_str: str):
    """Normalize artifact paths from old to new structure"""
    if not path_str:
        return path_str
        
    # Convert old structure to new structure during transition
    if '/hestia/core/config/' in path_str:
        return path_str.replace('/hestia/core/config/', '/hestia/config/')
    
    return path_str

def load_index(path: Path):
    """Load index file supporting both YAML and legacy conf formats"""
    try:
        import yaml
        content = yaml.safe_load(path.read_text(encoding='utf-8'))
        
        # Handle current manifest.yaml structure
        if 'hades_config_index' in content:
            return content
            
        # Handle legacy structure (if needed for compatibility)
        if isinstance(content, dict) and 'artifacts' in content and 'hades_config_index' not in content:
            return {'hades_config_index': content}
            
        return content
        
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parsing error in {path}: {e}")
    except ImportError:
        # Fallback parser for environments without PyYAML
        return _parse_legacy_format(path)

def _parse_legacy_format(path: Path):
    """Targeted parser for the hades_index.conf file format (legacy support)"""
    try:
        text = path.read_text(encoding='utf-8')
        lines = [
            line.rstrip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith('#')
        ]
        idx = {'hades_config_index': {'artifacts': {}}}
        cur_category = None
        cur_item = None
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.lstrip()
            
            if stripped.startswith('hades_config_index:'):
                continue
            if stripped.startswith('artifacts:'):
                continue
                
            # category lines: e.g., 'network:' at two-space indent
            if (line.startswith('    ') and stripped.endswith(':') and not stripped.startswith('-')):
                cur_category = stripped[:-1]
                idx['hades_config_index']['artifacts'][cur_category] = []
                continue
                
            # item start (dash)
            if stripped.startswith('- '):
                if cur_category is None:
                    raise ValueError(f"Item found without category context at line {line_num}: {line}")
                cur_item = {}
                idx['hades_config_index']['artifacts'][cur_category].append(cur_item)
                # line may contain key: value after '- '
                after = stripped[2:]
                if ':' in after:
                    k, v = after.split(':', 1)
                    cur_item[k.strip()] = v.strip().strip('"')
                continue
                
            # continuation line under current item (further indented)
            if (line.startswith('      ') and ':' in stripped and cur_item is not None):
                k, v = stripped.split(':', 1)
                val = v.strip()
                if val.startswith('[') and val.endswith(']'):
                    # simple inline list
                    raw_items = val[1:-1].split(',')
                    items = [x.strip().strip('"') for x in raw_items if x.strip()]
                    cur_item[k.strip()] = items
                else:
                    cur_item[k.strip()] = val.strip('"')
                continue
                
        return idx
        
    except Exception as e:
        raise ValueError(f"Failed to parse legacy format {path}: {e}")

def map_path(p: str):
    """Map /config/ paths to local filesystem with proper expansion and ADR-0016 compliance"""
    if not p:
        return None
        
    if p.startswith('/config/'):
        # Use environment variable per ADR-0016
        ha_mount = os.getenv('HA_MOUNT', os.path.expanduser('~/hass'))
        return Path(ha_mount) / p[len('/config/'):]
    
    return Path(p).expanduser()

def check_yaml_load(p: Path):
    """Check if file can be loaded as valid YAML with enhanced error reporting"""
    try:
        import yaml
        yaml.safe_load(p.read_text(encoding='utf-8'))
        return True, None
    except yaml.YAMLError as e:
        return False, f'yaml_error: {e}'
    except FileNotFoundError:
        return False, 'file_not_found'
    except PermissionError:
        return False, 'permission_denied'
    except ImportError:
        # Fallback heuristic when PyYAML is not available
        try:
            txt = p.read_text(encoding='utf-8')
            if not txt.strip():
                return False, 'empty_file'
            if ':' in txt:
                return True, None
            return False, 'no_yaml_backend_and_no_colon'
        except Exception as e:
            return False, f'fallback_check_failed: {e}'
    except Exception as e:
        return False, f'unexpected_error: {e}'

def check():
    """Main validation function with enhanced error reporting"""
    try:
        idx_path = locate_index()
        idx = load_index(idx_path)
    except Exception as e:
        return [('INDEX_FILE', 'locate_or_load_failed', str(e))]
    
    failures = []
    art = idx.get('hades_config_index', {}).get('artifacts', {})
    
    if not art:
        return [('INDEX_STRUCTURE', 'no_artifacts_found', 'Index contains no artifacts to validate')]
    
    for cat, items in art.items():
        if not isinstance(items, list):
            failures.append((f'CATEGORY_{cat}', 'invalid_structure', 'Category items must be a list'))
            continue
            
        for item_idx, it in enumerate(items):
            if not isinstance(it, dict):
                failures.append((f'{cat}[{item_idx}]', 'invalid_item', 'Item must be a dictionary'))
                continue
                
            raw = it.get('path')
            if not raw:
                failures.append((f'{cat}[{item_idx}]', 'missing_path', 'Item missing path field'))
                continue
                
            # Normalize path for transition period
            normalized_path = normalize_artifact_path(raw)
            p = map_path(normalized_path)
            
            if p is None:
                failures.append((raw, 'path_mapping_failed', 'Could not map path'))
                continue
            
            # path_exists check
            if not p.exists():
                failures.append((raw, 'path_missing', f'Resolved to: {p}'))
            
            # tag_policy check
            tags = it.get('tags', []) or []
            if not isinstance(tags, list):
                failures.append((raw, 'invalid_tags', 'Tags must be a list'))
            else:
                bad_tags = [t for t in tags if t not in ALLOWED_TAGS]
                if bad_tags:
                    failures.append((raw, 'bad_tags', bad_tags))
            
            # yaml_load check (only if file exists)
            if p.exists():
                ok, err = check_yaml_load(p)
                if not ok:
                    failures.append((raw, 'yaml_load_fail', err))
    
    return failures

if __name__ == '__main__':
    try:
        failures = check()
        if not failures:
            print('✅ OK: hades index checks passed')
            sys.exit(0)
        
        print('❌ FAILURES:')
        for f in failures:
            print(f'  {f[0]} | {f[1]} | {f[2]}')
        sys.exit(1)
        
    except Exception as e:
        print(f'💥 CRITICAL ERROR: {e}')
        sys.exit(2)