#!/usr/bin/env python3

import sys
from datetime import UTC, datetime
from pathlib import Path

import requests
import yaml

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
    result = make_request("config/entity_registry/list")
    if isinstance(result, list):
        return result
    return []

def get_device_registry() -> list[dict]:
    """Get all devices from registry"""
    result = make_request("config/device_registry/list")
    if isinstance(result, list):
        return result
    return []

def get_area_registry() -> list[dict]:
    """Get all areas from registry"""
    result = make_request("config/area_registry/list")
    if isinstance(result, list):
        return result
    return []

def get_network_scanner_state() -> dict | None:
    """Get current network_scanner sensor state"""
    return make_request("states/sensor.network_scanner")

def extract_mac_from_device(device: dict) -> str | None:
    """Extract MAC address from device connections"""
    # Home Assistant device registry stores connections as a list of [type, value] pairs
    # Look for a connection of type 'mac'
    connections = device.get("connections", [])
    for conn_type, conn_value in connections:
        if conn_type == "mac":
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

    # Fetch areas for friendly names
    print("📥 Fetching area registry...")
    areas = get_area_registry()
    area_name_by_id: dict[str, str] = {}
    for a in areas:
        # HA areas have fields: id, name, aliases, etc.
        a_id = a.get("id")
        a_name = a.get("name")
        if a_id and a_name:
            area_name_by_id[a_id] = a_name
    print(f"   Found {len(area_name_by_id)} areas")
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

    for entity_id in sorted(KNOWN_ENTITIES):  # deterministic order
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
        # Map to friendly display name when possible
        area_display = area_name_by_id.get(area_id) if area_id else None
        if not area_display:
            area_display = "Uncategorized"

        verified_mappings.append({
            "mac": mac,
            "entity_id": entity_id,
            "name": name,
            "manufacturer": manufacturer,
            "model": model,
            "area_id": area_id,
            "area_display": area_display
        })

        print(f"✓ {entity_id}")
        print(f"  MAC: {mac}")
        print(f"  Name: {name}")
        print(f"  Manufacturer: {manufacturer}")
        if model:
            print(f"  Model: {model}")
        print(f"  Area: {area_display}")
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
        unmapped_devices = [
            d for d in discovered_devices if d.get("mac", "").lower() not in verified_macs
        ]

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
    by_area: dict[str, list[dict]] = {}
    for mapping in verified_mappings:
        area_display = mapping.get("area_display") or "Uncategorized"
        if area_display not in by_area:
            by_area[area_display] = []
        by_area[area_display].append(mapping)

    # Deterministic sorting: areas by display name, mappings by entity_id
    for area_key in by_area:
        by_area[area_key] = sorted(by_area[area_key], key=lambda m: m["entity_id"]) 

    mapping_num = 1
    for area_display, mappings in sorted(by_area.items(), key=lambda kv: kv[0].lower()):
        print(f"  # ═══ {area_display} ═══")
        for mapping in mappings:
            entity_comment = (
                f"  # {mapping['name']} - {mapping['model']}"
                if mapping["model"]
                else f"  # {mapping['name']}"
            )
            print(entity_comment)
            print(
                f'  mac_mapping_{mapping_num}: "'
                f'{mapping["mac"]};{mapping["entity_id"]};{mapping["manufacturer"]}"'
            )
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
    # Build YAML content once for reuse
    yaml_lines: list[str] = []
    yaml_lines.append("network_scanner:\n")
    yaml_lines.append("  scan_interval: 1800  # 30 minutes\n")
    yaml_lines.append('  ip_range: "192.168.0.0/24"\n')
    yaml_lines.append("\n")

    mapping_num = 1
    for area_display, mappings in sorted(by_area.items(), key=lambda kv: kv[0].lower()):
        yaml_lines.append(f"  # ═══ {area_display} ═══\n")
        for mapping in mappings:
            entity_comment = (
                f"  # {mapping['name']} - {mapping['model']}"
                if mapping["model"]
                else f"  # {mapping['name']}"
            )
            yaml_lines.append(f"{entity_comment}\n")
            yaml_lines.append(
                f'  mac_mapping_{mapping_num}: "{mapping["mac"]};'
                f'{mapping["entity_id"]};{mapping["manufacturer"]}"\n'
            )
            mapping_num += 1
        yaml_lines.append("\n")

    # Save to repo-local file
    output_file = "verified_network_scanner.yaml"
    with open(output_file, "w") as f:
        f.writelines(yaml_lines)

    print(f"✓ Configuration saved to: {output_file}")
    print()

    # Save timestamped copy under operations logs per ADR-0018
    utc_ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    logs_dir = Path("/config/hestia/workspace/operations/logs/network_scanner")
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        logs_file = logs_dir / f"{utc_ts}__verify_network_scanner__config.yaml"
        with open(logs_file, "w") as f:
            f.writelines(yaml_lines)
        print(f"✓ Timestamped copy saved to: {logs_file}")
    except Exception as e:
        print(f"⚠ Could not write logs copy to {logs_dir}: {e}")

if __name__ == "__main__":
    main()
