#!/bin/bash
# AppDaemon Startup Monitor
# This script monitors the Home Assistant logs for AppDaemon-related entries

echo "🔍 Monitoring Home Assistant logs for AppDaemon startup..."
echo "=================================="
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to check if AppDaemon is accessible
check_appdaemon_health() {
    if curl -s http://localhost:5050/api/app/room_db_updater/health >/dev/null 2>&1; then
        echo "✅ AppDaemon API is accessible at http://localhost:5050"
        return 0
    else
        echo "⏳ AppDaemon API not yet accessible..."
        return 1
    fi
}

# Monitor for AppDaemon entries in logs
tail -f /config/home-assistant.log | while read line; do
    # Check for AppDaemon-related log entries
    if echo "$line" | grep -qi "appdaemon\|ad_\|room_db"; then
        timestamp=$(echo "$line" | cut -d' ' -f1-2)
        echo "[$timestamp] $line"
        
        # Check if this indicates AppDaemon is starting
        if echo "$line" | grep -qi "appdaemon.*start\|ad.*start"; then
            echo "🚀 AppDaemon appears to be starting..."
            sleep 5
            check_appdaemon_health
        fi
    fi
done