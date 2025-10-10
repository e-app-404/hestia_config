#!/bin/bash
# Database initialization script for vacuum control rooms
# Part of PATCH_PLAN.md Phase 2 implementation

echo "🧹 Initializing room database configurations for vacuum control..."

# Function to add vacuum room configuration
add_vacuum_config() {
    local room_id="$1"
    local segment_id="$2"
    
    echo "Adding vacuum configuration for room: $room_id (segment: $segment_id)"
    
    # Use Home Assistant REST API to call the service
    curl -X POST \
        -H "Content-Type: application/json" \
        -d "{
            \"entity_id\": \"rest_command.room_db_update_config\",
            \"room_id\": \"$room_id\",
            \"domain\": \"vacuum_control\",
            \"config_data\": \"{\\\"segment_id\\\": $segment_id, \\\"last_cleaned\\\": null, \\\"needs_cleaning\\\": true}\"
        }" \
        "http://localhost:8123/api/services/rest_command/room_db_update_config"
    
    echo "✅ Added $room_id vacuum configuration (segment $segment_id)"
    sleep 3  # Rate limiting
}

# Initialize vacuum-eligible rooms with segment IDs
# Note: These segment IDs are examples and need to be verified against actual Valetudo map
add_vacuum_config "kitchen" 1
add_vacuum_config "laundry_room" 2
add_vacuum_config "hallway" 3
add_vacuum_config "powder_room" 4
add_vacuum_config "living_room" 5

echo "🎉 Vacuum control database initialization complete!"
echo "⚠️  Note: Verify segment IDs match your actual Valetudo robot map"
echo "Test with: script.clean_room_with_sql_tracking"