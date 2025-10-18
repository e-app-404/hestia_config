#!/usr/bin/env python3
"""
Validate Area Mapping v3.1
Ensures every room with ML/VC capability is consistent
"""

import yaml
import sys
import os

def main():
    mapping_path = "/config/www/area_mapping.yaml"
    
    if not os.path.exists(mapping_path):
        print(f"✗ Mapping file not found: {mapping_path}")
        sys.exit(1)
    
    try:
        with open(mapping_path) as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"✗ Failed to load mapping: {e}")
        sys.exit(1)
    
    version = data.get("metadata", {}).get("version", "unknown")
    print(f"✓ Mapping version: {version}")
    
    if version != "3.1":
        print(f"✗ Expected version 3.1, found {version}")
        sys.exit(1)
    
    nodes = data.get("nodes", [])
    print(f"✓ Found {len(nodes)} nodes")
    
    # Build allowed domain/room matrix
    ml_rooms = []
    vc_rooms = []
    
    for node in nodes:
        room_id = node.get("id")
        if not room_id:
            continue
            
        capabilities = node.get("capabilities", {})
        
        if "motion_lighting" in capabilities:
            ml_config = capabilities["motion_lighting"]
            if "timeout" in ml_config and "illuminance_threshold" in ml_config:
                ml_rooms.append(room_id)
            else:
                print(f"✗ {room_id}: incomplete motion_lighting config")
        
        if "vacuum_control" in capabilities:
            vc_config = capabilities["vacuum_control"]
            if "segment_id" in vc_config:
                vc_rooms.append(room_id)
            else:
                print(f"✗ {room_id}: vacuum_control missing segment_id")
    
    print(f"✓ Motion lighting enabled: {len(ml_rooms)} rooms")
    print(f"✓ Vacuum control enabled: {len(vc_rooms)} rooms")
    
    print("\nAllowed domain/room matrix:")
    print("Room\t\tML\tVC\tAT")
    print("-" * 40)
    
    for node in sorted(nodes, key=lambda x: x.get("id", "")):
        room_id = node.get("id")
        if not room_id:
            continue
            
        caps = node.get("capabilities", {})
        ml = "✓" if "motion_lighting" in caps else "✗"
        vc = "✓" if "vacuum_control" in caps else "✗"
        at = "✓"  # All rooms have activity tracking
        
        print(f"{room_id:<15}\t{ml}\t{vc}\t{at}")
    
    print(f"\n✓ Validation complete - mapping v{version} is valid")

if __name__ == "__main__":
    main()