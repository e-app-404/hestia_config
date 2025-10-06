#!/bin/bash
# Entity Registry Duplicate Cleaner
# Identifies and helps clean up duplicate entities with _2, _3 suffixes

set -euo pipefail

ENTITY_REGISTRY="/config/.storage/core.entity_registry"
CONFIG_ENTRIES="/config/.storage/core.config_entries"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

show_usage() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  scan       - Scan for duplicate entities (default)"
    echo "  analyze    - Detailed analysis of duplicate entities"
    echo "  suggest    - Suggest cleanup actions"
    echo "  disable    - Programmatically disable entity (requires entity_id)"
    echo "  rename     - Programmatically rename entity (requires old_id and new_id)"
    echo "  takeover   - Complete takeover process (requires base_id and suffix_id)"
    echo "  help       - Show this help message"
    echo
    echo "Options:"
    echo "  --entity-id ID    - Target entity for disable operation"
    echo "  --old-id ID       - Original entity_id for rename operation"
    echo "  --new-id ID       - New entity_id for rename operation"
    echo "  --base-id ID      - Base entity_id for takeover operation"
    echo "  --suffix-id ID    - Suffixed entity_id for takeover operation"
    echo "  --token TOKEN     - Home Assistant long-lived access token"
    echo "  --url URL         - Home Assistant URL (default: http://localhost:8123)"
    echo "  --dry-run         - Show what would be done without executing"
    echo
    echo "Examples:"
    echo "  $0 scan                                      # Quick scan for duplicates"
    echo "  $0 analyze                                   # Detailed analysis"
    echo "  $0 suggest                                   # Get cleanup suggestions"
    echo "  $0 disable --entity-id sensor.old_entity    # Disable specific entity"
    echo "  $0 rename --old-id sensor.old --new-id sensor.new --token TOKEN"
    echo "  $0 takeover --base-id sensor.activity --suffix-id sensor.activity_2 --token TOKEN"
}

scan_duplicate_entities() {
    log_info "Scanning for duplicate entities with suffix patterns..."
    
    if [[ ! -f "$ENTITY_REGISTRY" ]]; then
        log_error "Entity registry not found: $ENTITY_REGISTRY"
        return 1
    fi
    
    # Find entities with _2, _3, etc. suffixes
    local duplicates
    duplicates=$(jq -r '.data.entities[] | select(.entity_id | test("_[0-9]+$")) | .entity_id' "$ENTITY_REGISTRY" 2>/dev/null || echo "")
    
    if [[ -z "$duplicates" ]]; then
        log_info "✓ No obvious duplicate entities found"
        return 0
    fi
    
    log_warn "Found potential duplicate entities:"
    echo "$duplicates" | while read -r entity; do
        echo "  - $entity"
    done
    
    local count
    count=$(echo "$duplicates" | wc -l)
    log_warn "Total duplicates found: $count"
    
    return 1
}

analyze_duplicates() {
    log_info "Analyzing duplicate entities in detail..."
    
    if [[ ! -f "$ENTITY_REGISTRY" ]]; then
        log_error "Entity registry not found: $ENTITY_REGISTRY"
        return 1
    fi
    
    # Find duplicate entities and their details
    local analysis
    analysis=$(jq -r '
        .data.entities[] | 
        select(.entity_id | test("_[0-9]+$")) | 
        {
            entity_id: .entity_id,
            platform: .platform,
            device_id: .device_id,
            config_entry_id: .config_entry_id,
            created_at: .created_at,
            disabled_by: .disabled_by,
            unique_id: .unique_id
        }
    ' "$ENTITY_REGISTRY" 2>/dev/null || echo "{}")
    
    if [[ "$analysis" == "{}" ]]; then
        log_info "No duplicate entities to analyze"
        return 0
    fi
    
    echo "$analysis" | jq -r '
        "Entity: " + .entity_id + 
        "\n  Platform: " + .platform + 
        "\n  Device ID: " + (.device_id // "none") + 
        "\n  Config Entry: " + (.config_entry_id // "none") + 
        "\n  Created: " + .created_at + 
        "\n  Disabled: " + (.disabled_by // "false") + 
        "\n  Unique ID: " + (.unique_id // "none") + 
        "\n"
    '
}

find_base_entities() {
    local suffix_entity="$1"
    local base_name
    base_name=$(echo "$suffix_entity" | sed 's/_[0-9]*$//')
    
    log_debug "Looking for base entity: $base_name"
    
    # Find the base entity without suffix
    jq -r --arg base "$base_name" '
        .data.entities[] | 
        select(.entity_id == $base) | 
        {
            entity_id: .entity_id,
            platform: .platform,
            device_id: .device_id,
            config_entry_id: .config_entry_id,
            created_at: .created_at,
            disabled_by: .disabled_by
        }
    ' "$ENTITY_REGISTRY" 2>/dev/null || echo "{}"
}

suggest_cleanup() {
    log_info "Generating cleanup suggestions..."
    
    local duplicates
    duplicates=$(jq -r '.data.entities[] | select(.entity_id | test("_[0-9]+$")) | .entity_id' "$ENTITY_REGISTRY" 2>/dev/null || echo "")
    
    if [[ -z "$duplicates" ]]; then
        log_info "No duplicates found - no cleanup needed"
        return 0
    fi
    
    echo
    log_info "Cleanup Suggestions:"
    echo
    
    echo "1. Manual Cleanup via Home Assistant UI:"
    echo "   - Go to Settings > Devices & Services > Entities"
    echo "   - Search for entities ending with '_2', '_3', etc."
    echo "   - Review each duplicate entity:"
    echo
    echo "$duplicates" | while read -r entity; do
        echo "     ✓ Check: $entity"
        local base_name
        base_name=$(echo "$entity" | sed 's/_[0-9]*$//')
        echo "       (Compare with base: $base_name)"
    done
    
    echo
    echo "2. Proper entity ID management:"
    echo "   - If base entity is 'unavailable' and suffixed entity is active:"
    echo "     → Step 1: Disable the unavailable base entity"
    echo "     → Step 2: Change suffixed entity_id to take over base entity_id"
    echo "     → Step 3: Verify renamed entity maintains functionality"
    echo "   - If base entity is active and suffixed entity is redundant:"
    echo "     → Disable the suffixed entity"
    echo
    echo "3. Remove orphaned config entries:"
    echo "   - Check for config entries with no associated devices"
    echo "   - Remove via Settings > Devices & Services"
    echo
    echo "4. Restart Home Assistant after cleanup:"
    echo "   - Developer Tools > Server Management > Restart"
    echo
    
    log_warn "⚠️  IMPORTANT: Always backup your configuration before making changes!"
    echo "   Create backup: Settings > System > Backups > Create backup"
}

check_config_entries() {
    log_info "Checking for related config entry issues..."
    
    if [[ ! -f "$CONFIG_ENTRIES" ]]; then
        log_error "Config entries file not found: $CONFIG_ENTRIES"
        return 1
    fi
    
    # Look for mobile_app entries which commonly cause duplicates
    local mobile_entries
    mobile_entries=$(jq -r '.data.entries[] | select(.domain == "mobile_app") | {title: .title, entry_id: .entry_id, created_at: .created_at}' "$CONFIG_ENTRIES" 2>/dev/null || echo "{}")
    
    if [[ "$mobile_entries" != "{}" ]]; then
        log_info "Mobile app integrations found:"
        echo "$mobile_entries" | jq -r '"  - " + .title + " (ID: " + .entry_id + ", Created: " + .created_at + ")"'
    fi
}

# Parse command line arguments
parse_args() {
    COMMAND="${1:-scan}"
    shift || true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --entity-id)
                ENTITY_ID="$2"
                shift 2
                ;;
            --old-id)
                OLD_ID="$2"
                shift 2
                ;;
            --new-id)
                NEW_ID="$2"
                shift 2
                ;;
            --base-id)
                BASE_ID="$2"
                shift 2
                ;;
            --suffix-id)
                SUFFIX_ID="$2"
                shift 2
                ;;
            --token)
                HA_TOKEN="$2"
                shift 2
                ;;
            --url)
                HA_URL="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Home Assistant API operations
ha_api_call() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    
    if [[ -z "$HA_TOKEN" ]]; then
        log_error "Home Assistant token required for API operations. Use --token option."
        return 1
    fi
    
    local url="${HA_URL:-http://localhost:8123}$endpoint"
    local curl_args=("-s" "-X" "$method" "-H" "Authorization: Bearer $HA_TOKEN" "-H" "Content-Type: application/json")
    
    if [[ -n "$data" ]]; then
        curl_args+=("-d" "$data")
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would call: curl ${curl_args[*]} $url"
        if [[ -n "$data" ]]; then
            log_debug "[DRY RUN] With data: $data"
        fi
        return 0
    fi
    
    curl "${curl_args[@]}" "$url"
}

disable_entity() {
    local entity_id="$1"
    
    if [[ -z "$entity_id" ]]; then
        log_error "Entity ID required for disable operation"
        return 1
    fi
    
    log_info "Disabling entity: $entity_id"
    
    local response
    response=$(ha_api_call "POST" "/api/config/entity_registry/update/$entity_id" '{"disabled_by": "user"}')
    
    if [[ "$DRY_RUN" != "true" ]]; then
        if echo "$response" | grep -q '"entity_id"'; then
            log_info "✓ Successfully disabled entity: $entity_id"
        else
            log_error "✗ Failed to disable entity: $entity_id"
            log_debug "Response: $response"
            return 1
        fi
    fi
}

rename_entity() {
    local old_id="$1"
    local new_id="$2"
    
    if [[ -z "$old_id" || -z "$new_id" ]]; then
        log_error "Both old and new entity IDs required for rename operation"
        return 1
    fi
    
    log_info "Renaming entity: $old_id → $new_id"
    
    local response
    response=$(ha_api_call "POST" "/api/config/entity_registry/update/$old_id" "{\"new_entity_id\": \"$new_id\"}")
    
    if [[ "$DRY_RUN" != "true" ]]; then
        if echo "$response" | grep -q "\"entity_id\":\"$new_id\""; then
            log_info "✓ Successfully renamed entity: $old_id → $new_id"
        else
            log_error "✗ Failed to rename entity: $old_id → $new_id"
            log_debug "Response: $response"
            return 1
        fi
    fi
}

takeover_entity_id() {
    local base_id="$1"
    local suffix_id="$2"
    
    if [[ -z "$base_id" || -z "$suffix_id" ]]; then
        log_error "Both base and suffix entity IDs required for takeover operation"
        return 1
    fi
    
    log_info "Starting entity ID takeover process:"
    log_info "  Base entity (to disable): $base_id"
    log_info "  Suffix entity (to rename): $suffix_id"
    
    # Step 1: Disable the base entity
    log_info "Step 1: Disabling base entity..."
    if ! disable_entity "$base_id"; then
        log_error "Failed to disable base entity. Aborting takeover."
        return 1
    fi
    
    # Step 2: Rename suffix entity to take over base entity_id
    log_info "Step 2: Renaming suffix entity to take over base entity_id..."
    if ! rename_entity "$suffix_id" "$base_id"; then
        log_error "Failed to rename suffix entity. Base entity is disabled but takeover incomplete."
        return 1
    fi
    
    log_info "✓ Entity ID takeover completed successfully!"
    log_info "  $suffix_id now operates as $base_id"
    log_warn "Restart Home Assistant to ensure all references are updated."
}

main() {
    parse_args "$@"
    
    case "$COMMAND" in
        "scan")
            scan_duplicate_entities
            ;;
        "analyze")
            analyze_duplicates
            ;;
        "suggest")
            suggest_cleanup
            check_config_entries
            ;;
        "disable")
            disable_entity "$ENTITY_ID"
            ;;
        "rename")
            rename_entity "$OLD_ID" "$NEW_ID"
            ;;
        "takeover")
            takeover_entity_id "$BASE_ID" "$SUFFIX_ID"
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi