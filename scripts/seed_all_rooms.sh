#!/bin/bash
# Seed all new rooms with default configurations via Home Assistant REST commands
# Run this script after reloading YAML configurations to populate the room database

set -e

echo "=== Room Database Seeding Script ==="
echo "This script will seed all new rooms with default configurations."
echo "Make sure to reload YAML configurations first via Home Assistant UI."
echo

# Check if Home Assistant is available
if ! curl -s -o /dev/null -w "%{http_code}" "http://homeassistant.local:8123" | grep -q "200\|401"; then
    echo "❌ Home Assistant not accessible at homeassistant.local:8123"
    echo "Please ensure Home Assistant is running and accessible."
    exit 1
fi

echo "✅ Home Assistant detected"
echo

# Define room configurations
declare -A MOTION_ROOMS=(
    ["kitchen"]='{"timeout": 180, "bypass": false, "illuminance_threshold": 10, "presence_timeout_multiplier": 1.0}'
    ["living_room"]='{"timeout": 300, "bypass": false, "illuminance_threshold": 8, "presence_timeout_multiplier": 1.2}'
    ["ensuite"]='{"timeout": 120, "bypass": false, "illuminance_threshold": 5, "presence_timeout_multiplier": 0.8}'
    ["upstairs"]='{"timeout": 180, "bypass": false, "illuminance_threshold": 12, "presence_timeout_multiplier": 1.0}'
    ["downstairs"]='{"timeout": 240, "bypass": false, "illuminance_threshold": 15, "presence_timeout_multiplier": 1.1}'
)

declare -A VACUUM_ROOMS=(
    ["kitchen"]='{"segment_id": 2, "last_cleaned": null, "cleaning_frequency": 7, "needs_cleaning": 1}'
    ["living_room"]='{"segment_id": 3, "last_cleaned": null, "cleaning_frequency": 14, "needs_cleaning": 1}'
    ["ensuite"]='{"segment_id": 4, "last_cleaned": null, "cleaning_frequency": 21, "needs_cleaning": 1}'
    ["hallway"]='{"segment_id": 5, "last_cleaned": null, "cleaning_frequency": 14, "needs_cleaning": 1}'
    ["powder_room"]='{"segment_id": 6, "last_cleaned": null, "cleaning_frequency": 21, "needs_cleaning": 1}'
)

echo "📝 Seeding Motion Lighting configurations..."
for room in "${!MOTION_ROOMS[@]}"; do
    config="${MOTION_ROOMS[$room]}"
    echo "  → $room"
    echo "    Config: $config"
    
    # Note: This would normally call the REST command, but we need Home Assistant auth
    # For now, just show what needs to be done
    echo "    ⏳ To seed via Home Assistant UI:"
    echo "       Developer Tools → Services → rest_command.room_db_update_config"
    echo "       room_id: $room"
    echo "       domain: motion_lighting"
    echo "       config_data: $config"
    echo
done

echo "🧹 Seeding Vacuum Control configurations..."
for room in "${!VACUUM_ROOMS[@]}"; do
    config="${VACUUM_ROOMS[$room]}"
    echo "  → $room"
    echo "    Config: $config"
    
    echo "    ⏳ To seed via Home Assistant UI:"
    echo "       Developer Tools → Services → rest_command.room_db_update_config"
    echo "       room_id: $room"
    echo "       domain: vacuum_control"
    echo "       config_data: $config"
    echo
done

echo "🔍 After seeding, verify with:"
echo "  1. Developer Tools → Templates:"
echo '     {{ (state_attr("sensor.room_configs_motion_lighting","payload") | from_json).keys() }}'
echo '     {{ (state_attr("sensor.room_configs_vacuum_control","payload") | from_json).keys() }}'
echo
echo "  2. Run diagnostics template:"
echo "     /config/hestia/library/templates/devtools/diagnostics.jinja"
echo
echo "✅ Seeding instructions complete!"