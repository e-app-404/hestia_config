#!/usr/bin/env python3
"""Check for duplicate keys in YAML files using ruamel.yaml"""
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError


def check_file(filepath):
    yaml = YAML()
    yaml.allow_duplicate_keys = False
    try:
        with open(filepath, 'r') as f:
            yaml.load(f)
        return True
    except DuplicateKeyError as e:
        print(f"ERROR: Duplicate key in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"WARNING: Could not parse {filepath}: {e}")
        return True  # Don't fail on parse errors

def main():
    success = True
    yaml_files = (
        list(Path('.').glob('**/*.yaml')) +
        list(Path('.').glob('**/*.yml'))
    )
    
    # Skip problematic directories
    skip_dirs = {'.venv', '.storage', 'deps', 'www', '.git', '__pycache__'}
    
    for filepath in yaml_files:
        if any(part in skip_dirs for part in filepath.parts):
            continue
        if not check_file(filepath):
            success = False
    
    if success:
        print("No duplicate keys found in YAML files")
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()