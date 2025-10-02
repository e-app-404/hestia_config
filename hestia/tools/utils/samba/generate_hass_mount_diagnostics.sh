#!/usr/bin/env bash
# Generate populated hass_mount_status.yaml diagnostics file
# Usage: ./generate_hass_mount_diagnostics.sh [output_file] [--format json|yaml]

set -euo pipefail

# Get the workspace root directory by finding the .git directory
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/hass")"

# Source centralized environment variables - .env is gospel truth
if [ -f "$WORKSPACE_ROOT/.env" ]; then
    source "$WORKSPACE_ROOT/.env"
else
    echo "ERROR: .env file not found at $WORKSPACE_ROOT/.env" >&2
    exit 1
fi

# Use .env variables as gospel truth
MOUNT_POINT="$HA_MOUNT"
LOG_FILE="$HESTIA_WORKSPACE/operations/logs/hass-mount/diagnostics.log"

# Parse arguments
FORMAT="yaml"
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --format=*)
            FORMAT="${1#*=}"
            shift
            ;;
        *)
            if [ -z "$OUTPUT_FILE" ]; then
                OUTPUT_FILE="$1"
            fi
            shift
            ;;
    esac
done

# Set default output file if not specified - use .env variables as gospel
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="$HESTIA_CONFIG/diagnostics/hass_mount_status_current.${FORMAT}"
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")" "$(dirname "$LOG_FILE")"

# Helper functions for YAML-safe output
yaml_bool() { [ "$1" = "0" ] && echo "true" || echo "false"; }
yaml_string() { [ -n "$1" ] && printf '"%s"' "$1" || echo "null"; }
yaml_int() { [ -n "$1" ] && echo "$1" || echo "0"; }

# Gather system information
TIMESTAMP=$(date -Iseconds)
CURRENT_USER=$(whoami)
USER_ID=$(id -u)
HOME_DIR="$HOME"
HOSTNAME=$(hostname -s)
CURRENT_SHELL="$SHELL"

# Mount status checks
IS_MOUNTED=1; mount | egrep -qi "on $MOUNT_POINT .*smbfs" && IS_MOUNTED=0 || true
MOUNT_SOURCE=""
MOUNT_TYPE=""
if [ "$IS_MOUNTED" = "0" ]; then
    MOUNT_INFO=$(mount | egrep "on $MOUNT_POINT " | head -n1)
    MOUNT_SOURCE=$(echo "$MOUNT_INFO" | awk '{print $1}')
    MOUNT_TYPE=$(echo "$MOUNT_INFO" | sed -n 's/.*(\([^,]*\).*/\1/p')
fi

# Accessibility checks
MOUNT_POINT_EXISTS=1; test -d "$MOUNT_POINT" && MOUNT_POINT_EXISTS=0 || true
MOUNT_POINT_WRITABLE=1; test -w "$MOUNT_POINT" && MOUNT_POINT_WRITABLE=0 || true
CONFIG_FILE_EXISTS=1; test -f "$MOUNT_POINT/configuration.yaml" && CONFIG_FILE_EXISTS=0 || true

# Environment checks
HA_MOUNT_ENV_SET=1; env | grep -q "HA_MOUNT=" && HA_MOUNT_ENV_SET=0 || true
HA_MOUNT_ENV_VALUE=$(env | grep "HA_MOUNT=" | cut -d= -f2- || echo "")
ZSHRC_HAS_EXPORT=1; grep -q 'export HA_MOUNT=' "$HOME/.zshrc" 2>/dev/null && ZSHRC_HAS_EXPORT=0 || true

# Keychain checks
HOMEASSISTANT_EXISTS=1; security find-internet-password -s "homeassistant" -a "evertappels" >/dev/null 2>&1 && HOMEASSISTANT_EXISTS=0 || true
HOMEASSISTANT_LOCAL_EXISTS=1; security find-internet-password -s "homeassistant.local" -a "evertappels" >/dev/null 2>&1 && HOMEASSISTANT_LOCAL_EXISTS=0 || true

# LaunchAgent checks  
PRIMARY_PLIST="$HOME/Library/LaunchAgents/com.local.hass.mount.plist"
PRIMARY_PLIST_EXISTS=1; test -f "$PRIMARY_PLIST" && PRIMARY_PLIST_EXISTS=0 || true
PRIMARY_IS_LOADED=1; launchctl print "gui/$USER_ID/com.local.hass.mount" >/dev/null 2>&1 && PRIMARY_IS_LOADED=0 || true

WATCHDOG_PLIST="$HOME/Library/LaunchAgents/com.local.hass.mount.watch.plist"
WATCHDOG_PLIST_EXISTS=1; test -f "$WATCHDOG_PLIST" && WATCHDOG_PLIST_EXISTS=0 || true  
WATCHDOG_IS_LOADED=1; launchctl print "gui/$USER_ID/com.local.hass.mount.watch" >/dev/null 2>&1 && WATCHDOG_IS_LOADED=0 || true

# Network checks
SMB_SERVER_REACHABLE=1; ping -c 1 homeassistant.local >/dev/null 2>&1 && SMB_SERVER_REACHABLE=0 || true
SMB_SHARE_VISIBLE=1; smbutil view //evertappels@homeassistant </dev/null >/dev/null 2>&1 && SMB_SHARE_VISIBLE=0 || true

# DNS resolution
HOMEASSISTANT_LOCAL_IP=$(dig +short homeassistant.local 2>/dev/null | head -n1 || echo "failed")
HOMEASSISTANT_IP=$(dig +short homeassistant 2>/dev/null | head -n1 || echo "failed")

# Log file checks
LOG_FILE_EXISTS=1; test -f "$LOG_FILE" && LOG_FILE_EXISTS=0 || true
LOG_FILE_SIZE=0; [ -f "$LOG_FILE" ] && LOG_FILE_SIZE=$(wc -c < "$LOG_FILE" 2>/dev/null || echo 0)
LOG_LAST_MODIFIED=""
[ -f "$LOG_FILE" ] && LOG_LAST_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%S%z" "$LOG_FILE" 2>/dev/null || echo "")

# File system checks
MOUNT_SCRIPT_EXISTS=1; test -x "$HOME/bin/hass_mount_once.sh" && MOUNT_SCRIPT_EXISTS=0 || true
MOUNT_SMBFS_AVAILABLE=1; which mount_smbfs >/dev/null 2>&1 && MOUNT_SMBFS_AVAILABLE=0 || true
SMBUTIL_AVAILABLE=1; which smbutil >/dev/null 2>&1 && SMBUTIL_AVAILABLE=0 || true
BIN_DIRECTORY_EXISTS=1; test -d "$HOME/bin" && BIN_DIRECTORY_EXISTS=0 || true

# Overall health assessment
CRITICAL_ISSUES=()
WARNINGS=()
SUGGESTED_ACTIONS=()

if [ "$IS_MOUNTED" != "0" ]; then
    CRITICAL_ISSUES+=("Mount not present at $MOUNT_POINT")
    SUGGESTED_ACTIONS+=("Run \$HOME/bin/hass_mount_once.sh to attempt mount")
fi

if [ "$MOUNT_SCRIPT_EXISTS" != "0" ]; then
    CRITICAL_ISSUES+=("Mount script missing at \$HOME/bin/hass_mount_once.sh")
fi

if [ "$PRIMARY_PLIST_EXISTS" != "0" ]; then
    WARNINGS+=("Primary LaunchAgent plist missing")
    SUGGESTED_ACTIONS+=("Create LaunchAgent with provided configuration")
fi

if [ "$HOMEASSISTANT_EXISTS" != "0" ] || [ "$HOMEASSISTANT_LOCAL_EXISTS" != "0" ]; then
    WARNINGS+=("Keychain entries missing or inaccessible")
    SUGGESTED_ACTIONS+=("Re-add SMB credentials to keychain")
fi

# Determine overall status
OVERALL_STATUS="healthy"
[ ${#CRITICAL_ISSUES[@]} -gt 0 ] && OVERALL_STATUS="unhealthy"
[ ${#WARNINGS[@]} -gt 0 ] && [ "$OVERALL_STATUS" = "healthy" ] && OVERALL_STATUS="degraded"

# Helper function for JSON array formatting
json_array_critical() {
    if [ ${#CRITICAL_ISSUES[@]} -eq 0 ]; then
        echo "[]"
    else
        printf '["%s"]' "$(IFS='", "'; echo "${CRITICAL_ISSUES[*]}")"
    fi
}

json_array_warnings() {
    if [ ${#WARNINGS[@]} -eq 0 ]; then
        echo "[]"
    else
        printf '["%s"]' "$(IFS='", "'; echo "${WARNINGS[*]}")"
    fi
}

json_array_actions() {
    if [ ${#SUGGESTED_ACTIONS[@]} -eq 0 ]; then
        echo "[]"
    else
        printf '["%s"]' "$(IFS='", "'; echo "${SUGGESTED_ACTIONS[*]}")"
    fi
}

# Generate output based on format
if [ "$FORMAT" = "json" ]; then
# Generate JSON output
cat > "$OUTPUT_FILE" << EOF
{
  "metadata": {
    "generated_at": $(yaml_string "$TIMESTAMP"),
    "format_version": "1.0",
    "diagnostic_type": "hass_mount_status",
    "user": $(yaml_string "$CURRENT_USER"),
    "hostname": $(yaml_string "$HOSTNAME")
  },
  "mount_status": {
    "is_mounted": $(yaml_bool $IS_MOUNTED),
    "mount_point": $(yaml_string "$MOUNT_POINT"),
    "mount_source": $(yaml_string "$MOUNT_SOURCE"),
    "mount_type": $(yaml_string "$MOUNT_TYPE"),
    "mount_point_exists": $(yaml_bool $MOUNT_POINT_EXISTS),
    "mount_point_writable": $(yaml_bool $MOUNT_POINT_WRITABLE),
    "config_file_exists": $(yaml_bool $CONFIG_FILE_EXISTS),
    "mount_options": [],
    "mounted_since": null
  },
  "environment": {
    "ha_mount_env_set": $(yaml_bool $HA_MOUNT_ENV_SET),
    "ha_mount_env_value": $(yaml_string "$HA_MOUNT_ENV_VALUE"),
    "zshrc_has_export": $(yaml_bool $ZSHRC_HAS_EXPORT),
    "current_user": $(yaml_string "$CURRENT_USER"),
    "user_id": $(yaml_int "$USER_ID"),
    "home_directory": $(yaml_string "$HOME_DIR"),
    "shell": $(yaml_string "$CURRENT_SHELL")
  },
  "keychain": {
    "homeassistant_entry_exists": $(yaml_bool $HOMEASSISTANT_EXISTS),
    "homeassistant_local_entry_exists": $(yaml_bool $HOMEASSISTANT_LOCAL_EXISTS),
    "entries": [
      {
        "server": "homeassistant",
        "account": "evertappels",
        "exists": $(yaml_bool $HOMEASSISTANT_EXISTS),
        "last_modified": null
      },
      {
        "server": "homeassistant.local",
        "account": "evertappels",
        "exists": $(yaml_bool $HOMEASSISTANT_LOCAL_EXISTS),
        "last_modified": null
      }
    ]
  },
  "launch_agents": {
    "primary_agent": {
      "plist_path": $(yaml_string "$PRIMARY_PLIST"),
      "plist_exists": $(yaml_bool $PRIMARY_PLIST_EXISTS),
      "is_loaded": $(yaml_bool $PRIMARY_IS_LOADED),
      "is_running": false,
      "last_exit_code": null,
      "state": "unknown",
      "program_arguments": []
    },
    "watchdog_agent": {
      "plist_path": $(yaml_string "$WATCHDOG_PLIST"),
      "plist_exists": $(yaml_bool $WATCHDOG_PLIST_EXISTS),
      "is_loaded": $(yaml_bool $WATCHDOG_IS_LOADED),
      "is_running": false,
      "start_interval": null
    }
  },
  "network": {
    "smb_server_reachable": $(yaml_bool $SMB_SERVER_REACHABLE),
    "smb_share_visible": $(yaml_bool $SMB_SHARE_VISIBLE),
    "dns_resolution": {
      "homeassistant_local": $(yaml_string "$HOMEASSISTANT_LOCAL_IP"),
      "homeassistant": $(yaml_string "$HOMEASSISTANT_IP")
    },
    "active_interfaces": [],
    "wifi_connected": false,
    "current_network": null
  },
  "logging": {
    "log_file_path": $(yaml_string "$LOG_FILE"),
    "log_file_exists": $(yaml_bool $LOG_FILE_EXISTS),
    "log_file_size": $(yaml_int $LOG_FILE_SIZE),
    "log_last_modified": $(yaml_string "$LOG_LAST_MODIFIED"),
    "recent_entries": [],
    "recent_errors": {
      "mount_failures": 0,
      "network_errors": 0,
      "keychain_errors": 0
    }
  },
  "file_system": {
    "mount_script_exists": $(yaml_bool $MOUNT_SCRIPT_EXISTS),
    "mount_script_path": $(yaml_string "$HOME/bin/hass_mount_once.sh"),
    "mount_smbfs_available": $(yaml_bool $MOUNT_SMBFS_AVAILABLE),
    "smbutil_available": $(yaml_bool $SMBUTIL_AVAILABLE),
    "mount_point_permissions": null,
    "mount_point_owner": null,
    "bin_directory_exists": $(yaml_bool $BIN_DIRECTORY_EXISTS)
  },
  "health_summary": {
    "overall_status": $(yaml_string "$OVERALL_STATUS"),
    "critical_issues": $(json_array_critical),
    "warnings": $(json_array_warnings),
    "suggested_actions": $(json_array_actions),
    "mount_uptime_seconds": 0,
    "last_successful_mount": null,
    "failure_count_24h": 0
  }
}
EOF
else
# Generate YAML output
cat > "$OUTPUT_FILE" << EOF
# Home Assistant Mount Status Diagnostics  
# Machine-readable status and troubleshooting information for ~/hass SMB mount
# Generated at: $TIMESTAMP

metadata:
  generated_at: $(yaml_string "$TIMESTAMP")
  format_version: "1.0"
  diagnostic_type: "hass_mount_status"
  user: $(yaml_string "$CURRENT_USER")
  hostname: $(yaml_string "$HOSTNAME")

mount_status:
  is_mounted: $(yaml_bool $IS_MOUNTED)
  mount_point: $(yaml_string "$MOUNT_POINT")
  mount_source: $(yaml_string "$MOUNT_SOURCE")
  mount_type: $(yaml_string "$MOUNT_TYPE")
  
  mount_point_exists: $(yaml_bool $MOUNT_POINT_EXISTS)
  mount_point_writable: $(yaml_bool $MOUNT_POINT_WRITABLE) 
  config_file_exists: $(yaml_bool $CONFIG_FILE_EXISTS)
  
  mount_options: []
  mounted_since: null

environment:
  ha_mount_env_set: $(yaml_bool $HA_MOUNT_ENV_SET)
  ha_mount_env_value: $(yaml_string "$HA_MOUNT_ENV_VALUE")
  zshrc_has_export: $(yaml_bool $ZSHRC_HAS_EXPORT)
  
  current_user: $(yaml_string "$CURRENT_USER")
  user_id: $(yaml_int "$USER_ID")
  home_directory: $(yaml_string "$HOME_DIR")
  shell: $(yaml_string "$CURRENT_SHELL")

keychain:
  homeassistant_entry_exists: $(yaml_bool $HOMEASSISTANT_EXISTS)
  homeassistant_local_entry_exists: $(yaml_bool $HOMEASSISTANT_LOCAL_EXISTS)
  
  entries:
    - server: "homeassistant"
      account: "evertappels"
      exists: $(yaml_bool $HOMEASSISTANT_EXISTS)
      last_modified: null
    - server: "homeassistant.local"
      account: "evertappels"  
      exists: $(yaml_bool $HOMEASSISTANT_LOCAL_EXISTS)
      last_modified: null

launch_agents:
  primary_agent:
    plist_path: $(yaml_string "$PRIMARY_PLIST")
    plist_exists: $(yaml_bool $PRIMARY_PLIST_EXISTS)
    is_loaded: $(yaml_bool $PRIMARY_IS_LOADED)
    is_running: false
    last_exit_code: null
    state: "unknown"
    program_arguments: []
    
  watchdog_agent:
    plist_path: $(yaml_string "$WATCHDOG_PLIST")
    plist_exists: $(yaml_bool $WATCHDOG_PLIST_EXISTS)
    is_loaded: $(yaml_bool $WATCHDOG_IS_LOADED)
    is_running: false
    start_interval: null

network:
  smb_server_reachable: $(yaml_bool $SMB_SERVER_REACHABLE)
  smb_share_visible: $(yaml_bool $SMB_SHARE_VISIBLE)
  dns_resolution:
    homeassistant_local: $(yaml_string "$HOMEASSISTANT_LOCAL_IP")
    homeassistant: $(yaml_string "$HOMEASSISTANT_IP")
  
  active_interfaces: []
  wifi_connected: false
  current_network: null

logging:
  log_file_path: $(yaml_string "$LOG_FILE")
  log_file_exists: $(yaml_bool $LOG_FILE_EXISTS)
  log_file_size: $(yaml_int $LOG_FILE_SIZE)
  log_last_modified: $(yaml_string "$LOG_LAST_MODIFIED")
  
  recent_entries: []
  recent_errors:
    mount_failures: 0
    network_errors: 0
    keychain_errors: 0

file_system:
  mount_script_exists: $(yaml_bool $MOUNT_SCRIPT_EXISTS)
  mount_script_path: $(yaml_string "$HOME/bin/hass_mount_once.sh")
  mount_smbfs_available: $(yaml_bool $MOUNT_SMBFS_AVAILABLE)
  smbutil_available: $(yaml_bool $SMBUTIL_AVAILABLE)
  
  mount_point_permissions: null
  mount_point_owner: null
  bin_directory_exists: $(yaml_bool $BIN_DIRECTORY_EXISTS)

health_summary:
  overall_status: $(yaml_string "$OVERALL_STATUS")
  critical_issues: [$(IFS=','; echo "${CRITICAL_ISSUES[*]/#/\"}" | sed 's/,/", "/g')]
  warnings: [$(IFS=','; echo "${WARNINGS[*]/#/\"}" | sed 's/,/", "/g')]
  suggested_actions: [$(IFS=','; echo "${SUGGESTED_ACTIONS[*]/#/\"}" | sed 's/,/", "/g')]
  
  mount_uptime_seconds: 0
  last_successful_mount: null
  failure_count_24h: 0
EOF
fi

echo "Diagnostics written to: $OUTPUT_FILE"
echo "Format: $FORMAT"
echo "Overall status: $OVERALL_STATUS"
[ ${#CRITICAL_ISSUES[@]} -gt 0 ] && echo "Critical issues: ${#CRITICAL_ISSUES[@]}"
[ ${#WARNINGS[@]} -gt 0 ] && echo "Warnings: ${#WARNINGS[@]}"