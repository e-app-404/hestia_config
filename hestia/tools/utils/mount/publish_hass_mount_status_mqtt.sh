#!/usr/bin/env bash
# MQTT publisher for Home Assistant mount diagnostics
# Usage: ./publish_hass_mount_status_mqtt.sh

set -euo pipefail

# Source centralized environment variables
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/hass")"
source "$WORKSPACE_ROOT/.env"

GEN="$HESTIA_TOOLS/utils/mount/generate_hass_mount_diagnostics.sh"
BROKER="homeassistant.local"
TOPIC="home/macbook/hass_mount/status"
TMP="$(mktemp)"

# Generate JSON diagnostics
"$GEN" --format json > "$TMP"

# Publish to MQTT with retained flag
if command -v mosquitto_pub >/dev/null 2>&1; then
    mosquitto_pub -h "$BROKER" -t "$TOPIC" -r -f "$TMP"
    echo "Published mount status to MQTT topic: $TOPIC"
else
    echo "ERROR: mosquitto_pub not found. Install with: brew install mosquitto" >&2
    exit 1
fi

rm -f "$TMP"