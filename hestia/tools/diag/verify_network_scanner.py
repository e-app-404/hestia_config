#!/usr/bin/env python3

import requests
import json
import sys
from typing import Dict, List, Optional
import yaml
from pathlib import Path

"""
Verify and generate network_scanner MAC mappings from Home Assistant
Run this script on your Home Assistant instance or any machine with API access
"""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION - Update these values
# ═══════════════════════════════════════════════════════════════

# Load token from secrets.yaml
secrets_path = Path("/config/secrets.yaml")
with open(secrets_path) as f:
    secrets = yaml.safe_load(f)

HA_URL = "http://homeassistant.local:8123"
HA_TOKEN = secrets["HA_TOKEN"]

# Known entities from your YAML files
KNOWN_ENTITIES = [
    # Bedroom
    "binary_sensor.bedroom_tplink_powerstrip_omega",
    "media_player.bedroom_apple_tv_alpha",
    "sensor.bedroom_ambient_climate_alpha_temperature",
    "sensor.bedroom_ambient_climate_alpha_humidity",
    "sensor.bedroom_dehumidifier_alpha_humidity",
    "binary_sensor.bedroom_wardrobe_motion_alpha_motion",
    "climate.bedroom_climate_trv_left_alpha",
    "climate.bedroom_climate_trv_right_alpha",

    # Ensuite
    "light.ensuite_lightstrip_alpha_matter",
    "sensor.ensuite_climate_alpha_matter_humidity",
    "sensor.ensuite_climate_alpha_humidity",
    "binary_sensor.ensuite_motion_alpha",

    # Living Room
    "sensor.living_room_broadlink_rm4_alpha_humidity",
    "sensor.living_room_broadlink_rm4_alpha_temperature",
    "binary_sensor.living_room_multipurpose_alpha_motion",
    "sensor.living_room_multipurpose_alpha_illuminance",
    "climate.living_room_climate_trv_alpha",

    # Kitchen
    "sensor.kitchen_ambient_climate_alpha_temperature",
    "sensor.kitchen_ambient_climate_alpha_humidity",
    "binary_sensor.kitchen_motion_alpha_motion",
    "climate.kitchen_climate_trv_alpha",

    # Personal
    "device_tracker.macbook",
]

# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

def make_request(endpoint: str) -> dict | None:
    """Make authenticated request to Home Assistant API"""
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{HA_URL}/api/{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return None

def get_entity_registry() -> list[dict]:
    """Get all entities from registry"""
    return make_request("config/entity_registry/list") or []

def get_device_registry() -> list[dict]:
    """Get all devices from registry"""
    return make_request("config/device_registry/list") or []

def get_network_scanner_state() -> dict | None:
    """Get current network_scanner sensor state"""
    return make_request("states/sensor.network_scanner")

def extract_mac_from_device(device: dict) -> str | None:
            return conn_value.lower()
    return None

# ═══════════════════════════════════════════════════════════════
# Main Verification Logic
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Home Assistant network_scanner MAC Mapping Verifier        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Test connection
    print("🔍 Testing connection to Home Assistant...")
    test = make_request("config")
    if not test:
        print("❌ Failed to connect to Home Assistant")
        print(f"   URL: {HA_URL}")
        print("   Please check your URL and token")
        sys.exit(1)
    print(f"✓ Connected to: {test.get('location_name', 'Home Assistant')}")
    print()

    # Fetch registries
    print("📥 Fetching entity registry...")
    entities = get_entity_registry()
    print(f"   Found {len(entities)} entities")

    print("📥 Fetching device registry...")
    devices = get_device_registry()
    print(f"   Found {len(devices)} devices")
    print()

    # Build mappings
    entity_to_device = {e["entity_id"]: e["device_id"] for e in entities if e.get("device_id")}
    device_by_id = {d["id"]: d for d in devices if "id" in d}

    # Verify known entities
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  VERIFIED MAC MAPPINGS FROM YOUR YAML                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    verified_mappings = []
    missing_entities = []
    entities_without_mac = []

    for entity_id in KNOWN_ENTITIES:
        if entity_id not in entity_to_device:
            missing_entities.append(entity_id)
            continue

        device_id = entity_to_device[entity_id]
        if device_id not in device_by_id:
            entities_without_mac.append(entity_id)
            continue

        device = device_by_id[device_id]
        mac = extract_mac_from_device(device)

        if not mac:
            entities_without_mac.append(entity_id)
            continue

        name = device.get("name_by_user") or device.get("name", "Unknown")
        manufacturer = device.get("manufacturer", "Unknown")
        model = device.get("model", "")
        area_id = device.get("area_id", "")

        verified_mappings.append({
            "mac": mac,
            "entity_id": entity_id,
            "name": name,
            "manufacturer": manufacturer,
            "model": model,
            "area_id": area_id
        })

        print(f"✓ {entity_id}")
        print(f"  MAC: {mac}")
        print(f"  Name: {name}")
        print(f"  Manufacturer: {manufacturer}")
        if model:
            print(f"  Model: {model}")
        if area_id:
            print(f"  Area: {area_id}")
        print()

    # Get current network_scanner devices
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  CURRENT NETWORK SCANNER DISCOVERIES                         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    scanner_state = get_network_scanner_state()
    if scanner_state and "attributes" in scanner_state:
        discovered_devices = scanner_state["attributes"].get("devices", [])
        print(f"Network scanner currently sees {len(discovered_devices)} devices")
        print()

        # Find unmapped devices
        verified_macs = {m["mac"] for m in verified_mappings}
        unmapped_devices = [d for d in discovered_devices if d.get("mac", "").lower() not in verified_macs]

        if unmapped_devices:
            print("⚠ Unmapped devices found on network:")
            print()
            for device in unmapped_devices[:10]:  # Show first 10
                print(f"  MAC: {device.get('mac', 'unknown')}")
                print(f"  IP: {device.get('ip', 'unknown')}")
                print(f"  Hostname: {device.get('hostname', 'unknown')}")
                print(f"  Vendor: {device.get('vendor', 'unknown')}")
                print()

            if len(unmapped_devices) > 10:
                print(f"  ... and {len(unmapped_devices) - 10} more")
                print()

    # Generate YAML output
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  GENERATED YAML CONFIGURATION                                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print("network_scanner:")
    print("  scan_interval: 1800  # 30 minutes")
    print('  ip_range: "192.168.0.0/24"')
    print()

    # Group by area
    by_area = {}
    for mapping in verified_mappings:
        area = mapping["area_id"] or "uncategorized"
        if area not in by_area:
            by_area[area] = []
        by_area[area].append(mapping)

    mapping_num = 1
    for area, mappings in sorted(by_area.items()):
        area_name = area.replace("_", " ").title()
        print(f"  # ═══ {area_name} ═══")
        for mapping in mappings:
            entity_comment = f"  # {mapping['name']} - {mapping['model']}" if mapping['model'] else f"  # {mapping['name']}"
            print(entity_comment)
            print(f'  mac_mapping_{mapping_num}: "{mapping["mac"]};{mapping["entity_id"]};{mapping["manufacturer"]}"')
            mapping_num += 1
        print()

    # Summary
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  SUMMARY                                                     ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"✓ Verified mappings: {len(verified_mappings)}")
    if missing_entities:
        print(f"⚠ Missing entities: {len(missing_entities)}")
        for entity in missing_entities:
            print(f"    - {entity}")
    if entities_without_mac:
        print(f"⚠ Entities without MAC: {len(entities_without_mac)}")
        for entity in entities_without_mac:
            print(f"    - {entity}")
    print()

    # Save to file
    output_file = "verified_network_scanner.yaml"
    with open(output_file, "w") as f:
        f.write("network_scanner:\n")
        f.write("  scan_interval: 1800  # 30 minutes\n")
        f.write('  ip_range: "192.168.0.0/24"\n')
        f.write("\n")

        mapping_num = 1
        for area, mappings in sorted(by_area.items()):
            area_name = area.replace("_", " ").title()
            f.write(f"  # ═══ {area_name} ═══\n")
            for mapping in mappings:
                entity_comment = f"  # {mapping['name']} - {mapping['model']}" if mapping['model'] else f"  # {mapping['name']}"
                f.write(f"{entity_comment}\n")
                f.write(f'  mac_mapping_{mapping_num}: "{mapping["mac"]};{mapping["entity_id"]};{mapping["manufacturer"]}"\n')
                mapping_num += 1
            f.write("\n")

    print(f"✓ Configuration saved to: {output_file}")
    print()

if __name__ == "__main__":
    main()
