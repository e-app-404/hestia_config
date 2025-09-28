#!/usr/bin/env python3
"""Check for unique automation IDs"""
import sys
import yaml
from pathlib import Path

def main():
    automation_ids = set()
    duplicates = []
    
    # Check automations.yaml and automation files
    yaml_files = [Path('automations.yaml')] + list(Path('.').glob('**/automations/*.yaml'))
    
    for filepath in yaml_files:
        if not filepath.exists():
            continue
            
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                
            if not data:
                continue
                
            # Handle both list format and single automation
            automations = data if isinstance(data, list) else [data]
            
            for automation in automations:
                if isinstance(automation, dict) and 'id' in automation:
                    auto_id = automation['id']
                    if auto_id in automation_ids:
                        duplicates.append((auto_id, filepath))
                    else:
                        automation_ids.add(auto_id)
                        
        except Exception as e:
            print(f"WARNING: Could not parse {filepath}: {e}")
            continue
    
    if duplicates:
        print("ERROR: Duplicate automation IDs found:")
        for auto_id, filepath in duplicates:
            print(f"  {auto_id} in {filepath}")
        sys.exit(1)
    else:
        print(f"OK: {len(automation_ids)} unique automation IDs found")
        sys.exit(0)

if __name__ == '__main__':
    main()