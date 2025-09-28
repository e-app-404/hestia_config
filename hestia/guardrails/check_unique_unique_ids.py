#!/usr/bin/env python3
"""Check for unique 'unique_id' values across the repository"""
import sys
from pathlib import Path

import yaml


def main():
    unique_ids = {}
    duplicates = []
    
    # Check all YAML files for unique_id entries
    yaml_files = (
        list(Path('.').glob('**/*.yaml')) +
        list(Path('.').glob('**/*.yml'))
    )
    
    # Skip problematic directories
    skip_dirs = {'.venv', '.storage', 'deps', 'www', '.git', '__pycache__'}
    
    for filepath in yaml_files:
        if any(part in skip_dirs for part in filepath.parts):
            continue
            
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Simple search for unique_id patterns
            if 'unique_id:' in content:
                data = yaml.safe_load(content)
                if data:
                    _check_unique_ids_recursive(
                        data,
                        filepath,
                        unique_ids,
                        duplicates
                    )
                        
        except Exception as e:
            print(f"WARNING: Could not parse {filepath}: {e}")
            continue
    
    if duplicates:
        print("ERROR: Duplicate unique_id values found:")
        for uid, filepaths in duplicates:
            print(f"  '{uid}' in: {', '.join(str(f) for f in filepaths)}")
        sys.exit(1)
    else:
        print(f"OK: {len(unique_ids)} unique 'unique_id' values found")
        sys.exit(0)

def _check_unique_ids_recursive(obj, filepath, unique_ids, duplicates):
    """Recursively check for unique_id in nested structures"""
    if isinstance(obj, dict):
        if 'unique_id' in obj:
            uid = obj['unique_id']
            if uid in unique_ids:
                duplicates.append((uid, [unique_ids[uid], filepath]))
            else:
                unique_ids[uid] = filepath
        for value in obj.values():
            _check_unique_ids_recursive(value, filepath, unique_ids, duplicates)
    elif isinstance(obj, list):
        for item in obj:
            _check_unique_ids_recursive(item, filepath, unique_ids, duplicates)

if __name__ == '__main__':
    main()