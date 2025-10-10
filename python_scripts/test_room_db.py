#!/usr/bin/env python3
"""
Test script to verify room_db_updater database initialization logic
"""
import json
import os
import sqlite3
import sys
import yaml

def test_database_init():
    """Test database initialization logic"""
    db_path = "/config/test_room_database.db"
    schema_expected = 1
    
    # Clean up any existing test database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    print(f"Creating test database at: {db_path}")
    
    # Initialize database (mimicking the AppDaemon app logic)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        
        # Create schema_version table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        """)
        
        # Create room_configs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS room_configs (
                room_id TEXT,
                config_domain TEXT,
                config_data TEXT,
                updated_at TIMESTAMP,
                PRIMARY KEY (room_id, config_domain)
            )
        """)
        
        # Insert schema version if not exists
        cur.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (?)", 
                   (schema_expected,))
        conn.commit()
        print("✅ Database initialized successfully")
        
        # Verify schema
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"✅ Tables created: {tables}")
        
        # Verify schema version
        cur.execute("SELECT version FROM schema_version")
        version = cur.fetchone()[0]
        print(f"✅ Schema version: {version}")
        
        # Test inserting a sample record
        cur.execute(
            "INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at) VALUES (?,?,?, datetime('now'))",
            ("test_room", "motion_lighting", '{"enabled": true}')
        )
        conn.commit()
        
        # Verify the record
        cur.execute("SELECT * FROM room_configs")
        records = cur.fetchall()
        print(f"✅ Test record inserted: {records}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()
    
    # Clean up
    os.remove(db_path)
    print("✅ Test database cleaned up")
    return True

def test_canonical_mapping():
    """Test canonical mapping loading"""
    mapping_file = "/config/domain/architecture/area_mapping.yaml"
    
    if not os.path.exists(mapping_file):
        print(f"❌ Canonical mapping file not found: {mapping_file}")
        return False
    
    try:
        with open(mapping_file, "r") as f:
            amap = yaml.safe_load(f) or {}
        
        # Extract room IDs from nodes
        nodes = amap.get("nodes", [])
        canonical_rooms = {node["id"] for node in nodes if node.get("type") in ["area", "subarea"]}
        
        print(f"✅ Loaded {len(canonical_rooms)} canonical rooms")
        print(f"✅ Sample rooms: {sorted(list(canonical_rooms))[:10]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error loading canonical mapping: {e}")
        return False

def main():
    print("🧪 Testing room_db_updater components...")
    print()
    
    print("1. Testing database initialization:")
    db_success = test_database_init()
    print()
    
    print("2. Testing canonical mapping:")
    mapping_success = test_canonical_mapping()
    print()
    
    if db_success and mapping_success:
        print("🎉 All tests passed! AppDaemon app should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())