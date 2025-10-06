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
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  scan      - Scan for duplicate entities (default)"
    echo "  analyze   - Detailed analysis of duplicate entities"
    echo "  suggest   - Suggest cleanup actions"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 scan                 # Quick scan for duplicates"
    echo "  $0 analyze             # Detailed analysis"
    echo "  $0 suggest             # Get cleanup suggestions"
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
    echo "2. Disable unused entities:"
    echo "   - If base entity is 'unavailable' and suffixed entity is active:"
    echo "     → Keep the suffixed entity, disable the base entity"
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

main() {
    local command="${1:-scan}"
    
    case "$command" in
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
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi