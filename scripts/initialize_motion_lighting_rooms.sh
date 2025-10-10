#!/bin/bash
# Database initialization script for motion lighting rooms
# Part of PATCH_PLAN.md Phase 1 implementation

echo "🔧 Initializing room database configurations for motion lighting..."

# Function to add room configuration
add_room_config() {
    local room_id="$1"
    local timeout="$2"
    local illuminance="$3"
    
    echo "Adding configuration for room: $room_id"
    
    # Use Home Assistant REST API to call the service
    curl -X POST \
        -H "Content-Type: application/json" \
        -d "{
            \"entity_id\": \"rest_command.room_db_update_config\",
            \"room_id\": \"$room_id\",
            \"domain\": \"motion_lighting\",
            \"config_data\": \"{\\\"timeout\\\": $timeout, \\\"bypass\\\": false, \\\"illuminance_threshold\\\": $illuminance, \\\"presence_timeout_multiplier\\\": 1.0}\"
        }" \
        "http://localhost:8123/api/services/rest_command/room_db_update_config"
    
    echo "✅ Added $room_id configuration"
    sleep 3  # Rate limiting
}

# Initialize all rooms with appropriate defaults
add_room_config "upstairs" 180 15
add_room_config "downstairs" 180 15  
add_room_config "kitchen" 300 20
add_room_config "living_room" 240 10
add_room_config "ensuite" 120 5

echo "🎉 Database initialization complete!"
echo "Run /config/hestia/library/templates/devtools/diagnostics.jinja to verify all rooms are configured."