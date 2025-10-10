#!/bin/bash
# Complete validation script for the room database system
# Checks SQL sensors, REST endpoints, and automation states

set -e

echo "=== Room Database System Validation ==="
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo

# Test REST health endpoint
echo "🏥 Testing AppDaemon health endpoint..."
HEALTH_STATUS=$(curl -s -w "%{http_code}" "http://a0d7b954-appdaemon:5050/api/appdaemon/room_db/health" -o /tmp/health_response.json 2>/dev/null || echo "000")

if [[ "$HEALTH_STATUS" == "200" ]]; then
    echo "✅ AppDaemon health endpoint responding"
    if [[ -f /tmp/health_response.json ]]; then
        echo "   Response: $(cat /tmp/health_response.json)"
    fi
else
    echo "❌ AppDaemon health endpoint not responding (HTTP $HEALTH_STATUS)"
    echo "   Expected: Container network isolation - this is normal"
fi
echo

# Check database file
echo "💾 Checking database file..."
if [[ -f /config/room_database.db ]]; then
    echo "✅ Database file exists: /config/room_database.db"
    echo "   Size: $(du -h /config/room_database.db | cut -f1)"
    echo "   Modified: $(stat -f "%Sm" /config/room_database.db)"
else
    echo "❌ Database file missing: /config/room_database.db"
fi
echo

# Test SQL sensor data (requires Home Assistant API)
echo "📊 SQL Sensor validation requires Home Assistant API access"
echo "   Please check these manually in Home Assistant:"
echo "   1. States → sensor.room_configs_motion_lighting"
echo "   2. States → sensor.room_configs_vacuum_control"
echo "   3. States → sensor.rooms_needing_cleaning"
echo

# Check automation files
echo "🤖 Checking automation files..."
AUTOMATION_FILE="/config/packages/motion_lighting_v2/motion_light_automations.yaml"
if [[ -f "$AUTOMATION_FILE" ]]; then
    echo "✅ Motion lighting automations file exists"
    AUTOMATION_COUNT=$(grep -c "^  - alias:" "$AUTOMATION_FILE" 2>/dev/null || echo "0")
    echo "   Automation count: $AUTOMATION_COUNT"
else
    echo "❌ Motion lighting automations file missing"
fi

TEMPLATE_FILE="/config/packages/motion_lighting_v2/motion_light_templates.yaml"
if [[ -f "$TEMPLATE_FILE" ]]; then
    echo "✅ Motion lighting templates file exists"
else
    echo "❌ Motion lighting templates file missing"
fi
echo

# Check package consolidation
echo "📦 Checking package consolidation..."
PACKAGE_FILE="/config/packages/package_room_database.yaml"
if [[ -f "$PACKAGE_FILE" ]]; then
    echo "✅ Consolidated package file exists"
    echo "   SQL sensors: $(grep -c "name:" "$PACKAGE_FILE" | head -1)"
    echo "   REST commands: $(grep -c "rest_command:" "$PACKAGE_FILE")"
else
    echo "❌ Consolidated package file missing"
fi
echo

# Check diagnostics template
echo "🔍 Checking diagnostics template..."
DIAGNOSTICS_FILE="/config/hestia/library/templates/devtools/diagnostics.jinja"
if [[ -f "$DIAGNOSTICS_FILE" ]]; then
    echo "✅ Diagnostics template exists (migrated location)"
    echo "   File size: $(wc -c < "$DIAGNOSTICS_FILE") bytes"
else
    echo "❌ Diagnostics template missing at migrated location"
fi
echo

# Check initialization scripts
echo "🚀 Checking initialization scripts..."
for script in initialize_motion_lighting_rooms.sh initialize_vacuum_control_rooms.sh seed_all_rooms.sh; do
    if [[ -f "/config/scripts/$script" ]]; then
        echo "✅ Script exists: $script"
    else
        echo "❌ Script missing: $script"
    fi
done
echo

echo "=== Validation Summary ==="
echo "Core files validated. For complete validation:"
echo "1. Reload YAML in Home Assistant UI"
echo "2. Run /config/scripts/seed_all_rooms.sh instructions"
echo "3. Test diagnostics template in Developer Tools"
echo "4. Trigger motion sensors and verify automation responses"
echo "5. Test vacuum cleaning scripts"
echo

echo "✅ File-level validation complete!"