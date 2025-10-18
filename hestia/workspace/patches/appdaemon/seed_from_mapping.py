#!/usr/bin/env python3
"""
Seed Room-DB from Area Mapping v3.1
Posts only allowed domain/room pairs to Room-DB
"""

import json
import sys
import yaml
import argparse
import requests

def load_mapping(path="/config/www/area_mapping.yaml"):
    """Load and parse the area mapping"""
    with open(path) as f:
        data = yaml.safe_load(f)
    
    allowed = {}
    nodes = data.get("nodes", [])
    
    for node in nodes:
        room_id = node.get("id")
        if not room_id:
            continue
        
        capabilities = node.get("capabilities", {})
        room_data = {}
        
        if "motion_lighting" in capabilities:
            ml_config = capabilities["motion_lighting"]
            room_data["motion_lighting"] = {
                "timeout": ml_config.get("timeout", 120),
                "illuminance_threshold": ml_config.get("illuminance_threshold", 10)
            }
        
        if "vacuum_control" in capabilities:
            vc_config = capabilities["vacuum_control"]
            room_data["vacuum_control"] = {
                "segment_id": vc_config.get("segment_id"),
                "default_mode": vc_config.get("default_mode", "standard"),
                "needs_cleaning": 0
            }
        
        if room_data:
            allowed[room_id] = room_data
    
    return allowed

def main():
    parser = argparse.ArgumentParser(description="Seed Room-DB from mapping")
    parser.add_argument("--domain", help="Filter by domain (motion_lighting, vacuum_control)")
    parser.add_argument("--rooms", help="Comma-separated list of rooms to seed")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be posted")
    parser.add_argument("--url", default="http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_bulk_update")
    
    args = parser.parse_args()
    
    try:
        mapping_data = load_mapping()
    except Exception as e:
        print(f"✗ Failed to load mapping: {e}")
        sys.exit(1)
    
    # Prepare bulk update items
    items = []
    
    for room_id, domains in mapping_data.items():
        # Filter by rooms if specified
        if args.rooms:
            room_filter = [r.strip() for r in args.rooms.split(",")]
            if room_id not in room_filter:
                continue
        
        for domain, config_data in domains.items():
            # Filter by domain if specified
            if args.domain and domain != args.domain:
                continue
            
            items.append({
                "domain": domain,
                "room_id": room_id,
                "config_data": config_data
            })
    
    if not items:
        print("✗ No items to seed")
        sys.exit(1)
    
    print(f"✓ Prepared {len(items)} items for seeding")
    
    if args.dry_run:
        print("\nDry run - would post:")
        for item in items[:5]:  # Show first 5
            print(f"  {item['domain']}:{item['room_id']} -> {item['config_data']}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more items")
        return
    
    # Post bulk update
    try:
        print(f"Posting to {args.url}")
        response = requests.post(args.url, json=items, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Bulk update successful: {result.get('status')}")
            
            results = result.get('results', [])
            success_count = sum(1 for r in results if r.get('status') == 200)
            print(f"✓ {success_count}/{len(results)} items processed successfully")
            
            # Show any failures
            failures = [r for r in results if r.get('status') != 200]
            if failures:
                print(f"✗ {len(failures)} failures:")
                for failure in failures[:3]:  # Show first 3 failures
                    item = failure.get('item', {})
                    print(f"  {item.get('domain')}:{item.get('room_id')} -> {failure.get('result', {}).get('error', 'unknown error')}")
        else:
            print(f"✗ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")

if __name__ == "__main__":
    main()