#!/bin/bash
# Final Room Database Seeding - Step by Step Instructions
# Execute these steps manually in Home Assistant Developer Tools

echo "=== Room Database Seeding - Manual Steps ==="
echo "Since AppDaemon holds the database in WAL mode, manual seeding via Home Assistant UI is required."
echo
echo "📋 STEP 1: Reload YAML Configuration"
echo "  Go to: Settings → System → Reload all YAML configurations"
echo "  Wait: 30 seconds for reload to complete"
echo
echo "📋 STEP 2: Execute REST Commands via Developer Tools"
echo "  Go to: Developer Tools → Services"
echo "  Service: rest_command.room_db_update_config"
echo
echo "🏠 Motion Lighting Configurations:"
echo "Execute each of these in Developer Tools → Services:"
echo

echo "📝 Kitchen Motion Lighting:"
echo "room_id: kitchen"
echo "domain: motion_lighting"
echo 'config_data: {"timeout": 180, "bypass": false, "illuminance_threshold": 10, "presence_timeout_multiplier": 1.0}'
echo "---"

echo "📝 Living Room Motion Lighting:"
echo "room_id: living_room" 
echo "domain: motion_lighting"
echo 'config_data: {"timeout": 300, "bypass": false, "illuminance_threshold": 8, "presence_timeout_multiplier": 1.2}'
echo "---"

echo "📝 Ensuite Motion Lighting:"
echo "room_id: ensuite"
echo "domain: motion_lighting"
echo 'config_data: {"timeout": 120, "bypass": false, "illuminance_threshold": 5, "presence_timeout_multiplier": 0.8}'
echo "---"

echo "📝 Upstairs Motion Lighting:"
echo "room_id: upstairs"
echo "domain: motion_lighting"
echo 'config_data: {"timeout": 180, "bypass": false, "illuminance_threshold": 12, "presence_timeout_multiplier": 1.0}'
echo "---"

echo "📝 Downstairs Motion Lighting:"
echo "room_id: downstairs"
echo "domain: motion_lighting"
echo 'config_data: {"timeout": 240, "bypass": false, "illuminance_threshold": 15, "presence_timeout_multiplier": 1.1}'
echo "---"

echo
echo "🧹 Vacuum Control Configurations:"
echo "Execute each of these in Developer Tools → Services:"
echo

echo "📝 Kitchen Vacuum Control:"
echo "room_id: kitchen"
echo "domain: vacuum_control"
echo 'config_data: {"segment_id": 2, "last_cleaned": null, "cleaning_frequency": 7, "needs_cleaning": 1}'
echo "---"

echo "📝 Living Room Vacuum Control:"
echo "room_id: living_room"
echo "domain: vacuum_control"
echo 'config_data: {"segment_id": 3, "last_cleaned": null, "cleaning_frequency": 14, "needs_cleaning": 1}'
echo "---"

echo "📝 Ensuite Vacuum Control:"
echo "room_id: ensuite"
echo "domain: vacuum_control"
echo 'config_data: {"segment_id": 4, "last_cleaned": null, "cleaning_frequency": 21, "needs_cleaning": 1}'
echo "---"

echo "📝 Hallway Vacuum Control:"
echo "room_id: hallway"
echo "domain: vacuum_control"
echo 'config_data: {"segment_id": 5, "last_cleaned": null, "cleaning_frequency": 14, "needs_cleaning": 1}'
echo "---"

echo "📝 Powder Room Vacuum Control:"
echo "room_id: powder_room"  
echo "domain: vacuum_control"
echo 'config_data: {"segment_id": 6, "last_cleaned": null, "cleaning_frequency": 21, "needs_cleaning": 1}'
echo "---"

echo
echo "📋 STEP 3: Verification"
echo "  Go to: Developer Tools → Templates"
echo "  Test 1: {{ (state_attr('sensor.room_configs_motion_lighting','payload') | from_json).keys() | list }}"
echo "  Expected: ['bedroom', 'kitchen', 'living_room', 'ensuite', 'upstairs', 'downstairs']"
echo
echo "  Test 2: {{ (state_attr('sensor.room_configs_vacuum_control','payload') | from_json).keys() | list }}"
echo "  Expected: ['bedroom', 'kitchen', 'living_room', 'ensuite', 'hallway', 'powder_room']"
echo
echo "  Test 3: Run diagnostics template:"
echo "  Paste content from: /config/hestia/library/templates/devtools/diagnostics.jinja"
echo "  Expected: status: 'ok', room counts > 1, no escaped JSON strings"
echo
echo "📋 STEP 4: Final System Test"
echo "  1. Trigger motion sensor in any room with automation"
echo "  2. Verify lights turn on/off with configured timeout"
echo "  3. Check room database for trigger_count increment"
echo "  4. Test vacuum cleaning script for any configured room"
echo
echo "✅ Manual seeding instructions complete!"
echo "   After completing these steps, the system will be fully operational."