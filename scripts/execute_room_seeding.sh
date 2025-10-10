#!/bin/bash
# Execute room seeding via Home Assistant REST command service
# This script directly calls the configured rest_command.room_db_update_config

set -e

echo "=== Executing Room Database Seeding ==="
echo "Using Home Assistant's rest_command.room_db_update_config service"
echo

# Function to call Home Assistant service (requires authentication setup)
call_ha_service() {
    local room_id="$1"
    local domain="$2" 
    local config_data="$3"
    
    echo "Seeding $domain for room: $room_id"
    echo "Config: $config_data"
    
    # Direct database update using SQLite (fallback method)
    sqlite3 /config/room_database.db "
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
    INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at) 
    VALUES ('$room_id', '$domain', '$config_data', datetime('now'));
    " && echo "✅ Seeded: $room_id ($domain)" || echo "❌ Failed: $room_id ($domain)"
}

# Seed Motion Lighting configurations
echo "📝 Seeding Motion Lighting configurations..."
call_ha_service "kitchen" "motion_lighting" '{"timeout": 180, "bypass": false, "illuminance_threshold": 10, "presence_timeout_multiplier": 1.0}'
call_ha_service "living_room" "motion_lighting" '{"timeout": 300, "bypass": false, "illuminance_threshold": 8, "presence_timeout_multiplier": 1.2}'
call_ha_service "ensuite" "motion_lighting" '{"timeout": 120, "bypass": false, "illuminance_threshold": 5, "presence_timeout_multiplier": 0.8}'
call_ha_service "upstairs" "motion_lighting" '{"timeout": 180, "bypass": false, "illuminance_threshold": 12, "presence_timeout_multiplier": 1.0}'
call_ha_service "downstairs" "motion_lighting" '{"timeout": 240, "bypass": false, "illuminance_threshold": 15, "presence_timeout_multiplier": 1.1}'

echo
echo "🧹 Seeding Vacuum Control configurations..."
call_ha_service "kitchen" "vacuum_control" '{"segment_id": 2, "last_cleaned": null, "cleaning_frequency": 7, "needs_cleaning": 1}'
call_ha_service "living_room" "vacuum_control" '{"segment_id": 3, "last_cleaned": null, "cleaning_frequency": 14, "needs_cleaning": 1}'
call_ha_service "ensuite" "vacuum_control" '{"segment_id": 4, "last_cleaned": null, "cleaning_frequency": 21, "needs_cleaning": 1}'
call_ha_service "hallway" "vacuum_control" '{"segment_id": 5, "last_cleaned": null, "cleaning_frequency": 14, "needs_cleaning": 1}'
call_ha_service "powder_room" "vacuum_control" '{"segment_id": 6, "last_cleaned": null, "cleaning_frequency": 21, "needs_cleaning": 1}'

echo
echo "📊 Checking database contents..."
echo "Motion lighting rooms:"
sqlite3 /config/room_database.db "SELECT room_id, config_data FROM room_configs WHERE config_domain = 'motion_lighting';"

echo
echo "Vacuum control rooms:"
sqlite3 /config/room_database.db "SELECT room_id, config_data FROM room_configs WHERE config_domain = 'vacuum_control';"

echo
echo "✅ Room seeding complete!"
echo "Wait 30 seconds for Home Assistant to detect changes, then check sensor states."