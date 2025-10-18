#!/usr/bin/env python3
"""
Test script for the room_db_updater AppDaemon API endpoints.
This script will test both the health endpoint and configuration update endpoint.
"""

import json
import requests
import time
from urllib.parse import urljoin

# Configuration
APPDAEMON_BASE_URL = "http://localhost:5050"  # Default AppDaemon port (inside HA network)
# App-scoped endpoints registered by AppDaemon for the 'room_db_updater' app
HEALTH_ENDPOINT = "/api/app/room_db_updater/health"
UPDATE_ENDPOINT = "/api/app/room_db_updater/update_config"

def test_health_endpoint():
    """Test the health endpoint to verify the service is running."""
    print("🔍 Testing AppDaemon room_db health endpoint...")
    
    try:
        url = urljoin(APPDAEMON_BASE_URL, HEALTH_ENDPOINT)
        response = requests.get(url, timeout=10)
        
        print(f"   URL: {url}")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - AppDaemon may not be running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_update_endpoint():
    """Test the configuration update endpoint."""
    print("\n🔍 Testing AppDaemon room_db update endpoint...")
    
    test_config = {
        "room_id": "bedroom",
        "domain": "motion_lighting",
        "config_data": {
            "enabled": True,
            "brightness": 80,
            "test_mode": True
        }
    }
    
    try:
        url = urljoin(APPDAEMON_BASE_URL, UPDATE_ENDPOINT)
        response = requests.post(
            url, 
            json=test_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   URL: {url}")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Update endpoint test passed!")
            return True
        else:
            print("❌ Update endpoint test failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - AppDaemon may not be running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing AppDaemon room_db_updater API endpoints")
    print("=" * 60)
    
    # Wait a moment for AppDaemon to fully start
    print("⏳ Waiting 5 seconds for AppDaemon to be ready...")
    time.sleep(5)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    # Test update endpoint only if health check passes
    if health_ok:
        update_ok = test_update_endpoint()
        
        if health_ok and update_ok:
            print("\n🎉 All tests passed! AppDaemon room_db_updater is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the logs for more details.")
    else:
        print("\n⚠️  Health check failed. AppDaemon may not be running or room_db_updater may have issues.")
    
    print("\n📋 Next steps:")
    print("   1. Check AppDaemon add-on logs for any error messages")
    print("   2. Verify the room_database.db file was created: ls -la /config/room_database.db")
    print("   3. Check AppDaemon app logs for room_db_updater initialization")

if __name__ == "__main__":
    main()