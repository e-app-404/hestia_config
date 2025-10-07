#!/bin/bash
# Advanced Entity Registry Cleanup Strategy
# Addresses orphaned entities from deleted mobile app integrations
# Three-pronged approach: Relationship repair, GUI mimicry, and wholesale replacement

set -euo pipefail

ENTITY_REGISTRY="/config/.storage/core.entity_registry"
CONFIG_ENTRIES="/config/.storage/core.config_entries"
DEVICE_REGISTRY="/config/.storage/core.device_registry"
BACKUP_ROOT="/config/hestia/workspace/archive/backups"
TS=$(date -u +%Y%m%dT%H%M%SZ)

log_info() { echo "ℹ️  $(date '+%H:%M:%S') $*" >&2; }
log_warn() { echo "⚠️  $(date '+%H:%M:%S') $*" >&2; }
log_success() { echo "✅ $(date '+%H:%M:%S') $*" >&2; }

show_usage() {
    cat << 'EOF'
Advanced Entity Registry Cleanup Strategy

PROBLEM:
- Orphaned entities reference deleted config entries
- Home Assistant prevents direct registry manipulation
- GUI doesn't allow editing "phantom" entities

SOLUTIONS:
1. relationship-repair  : Update orphaned entities to reference active config entries
2. gui-mimicry         : Replicate exact GUI rename patterns with proper timestamps
3. wholesale-replace   : Offline modification of entire .storage structure

USAGE:
    ./advanced_entity_cleanup.sh [strategy] [options]

STRATEGIES:
    relationship-repair --config-entry NEW_ID --target-entities pattern
    gui-mimicry --rename-plan plan.json
    wholesale-replace --offline-dir /path/to/offline/storage

EXAMPLES:
    # Fix orphaned ePhone UK entities to use active config entry
    ./advanced_entity_cleanup.sh relationship-repair \
        --config-entry 01K6MCMF7CZQQX132VSKW9GP8B \
        --target-entities "sensor.ephone_uk_.*[^_2]$"
    
    # Perform GUI-style renames with proper metadata
    ./advanced_entity_cleanup.sh gui-mimicry \
        --rename-plan mobile_device_renames.json
    
    # Nuclear option: offline wholesale replacement
    ./advanced_entity_cleanup.sh wholesale-replace \
        --offline-dir /tmp/storage_offline

EOF
}

# Strategy 1: Relationship Repair
repair_entity_relationships() {
    local target_config_entry="$1"
    local entity_pattern="$2"
    local device_id="$3"
    
    log_info "Strategy 1: Repairing entity relationships"
    log_info "Target config entry: $target_config_entry"
    log_info "Entity pattern: $entity_pattern"
    
    # Create backup
    local backup_dir="$BACKUP_ROOT/${TS}_relationship_repair"
    mkdir -p "$backup_dir"
    cp -a "/config/.storage" "$backup_dir/storage_complete"
    
    # Find orphaned entities
    local orphaned_entities
    orphaned_entities=$(jq -r --arg pattern "$entity_pattern" \
        '.data.entities[] | select(.entity_id | test($pattern)) | .entity_id' \
        "$ENTITY_REGISTRY")
    
    log_info "Found orphaned entities:"
    echo "$orphaned_entities" | while read -r entity; do
        log_info "  - $entity"
    done
    
    # Update entities to reference active config entry and device
    local temp_registry="/tmp/entity_registry_repair_$TS.json"
    jq --arg target_config "$target_config_entry" \
       --arg target_device "$device_id" \
       --arg pattern "$entity_pattern" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%S.%6N+00:00)" \
       '.data.entities |= map(
         if (.entity_id | test($pattern)) 
         then . + {
           "config_entry_id": $target_config,
           "device_id": $target_device,
           "modified_at": $timestamp
         }
         else . 
         end
       )' "$ENTITY_REGISTRY" > "$temp_registry"
    
    # Validate and apply
    if jq -e '.data.entities | type == "array"' "$temp_registry" &>/dev/null; then
        mv "$temp_registry" "$ENTITY_REGISTRY"
        log_success "Entity relationships repaired successfully"
        log_info "Backup: $backup_dir"
    else
        log_warn "Validation failed, changes not applied"
        rm -f "$temp_registry"
        return 1
    fi
}

# Strategy 2: GUI Mimicry
gui_style_rename() {
    local rename_plan="$1"
    
    log_info "Strategy 2: GUI-style entity renaming"
    
    # Create backup
    local backup_dir="$BACKUP_ROOT/${TS}_gui_mimicry"
    mkdir -p "$backup_dir"
    cp -a "/config/.storage" "$backup_dir/storage_complete"
    
    # Process rename plan
    local temp_registry="/tmp/entity_registry_gui_$TS.json"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%S.%6N+00:00)
    
    # Apply renames with GUI-style metadata updates
    jq --argjson plan "$(cat "$rename_plan")" \
       --arg timestamp "$timestamp" \
       '.data.entities |= map(
         . as $entity |
         ($plan[] | select(.old_id == $entity.entity_id)) as $rename |
         if $rename then
           $entity + {
             "entity_id": $rename.new_id,
             "modified_at": $timestamp,
             "name": ($rename.new_name // null)
           }
         else $entity end
       )' "$ENTITY_REGISTRY" > "$temp_registry"
    
    # Validate and apply
    if jq -e '.data.entities | type == "array"' "$temp_registry" &>/dev/null; then
        mv "$temp_registry" "$ENTITY_REGISTRY"
        log_success "GUI-style renames completed successfully"
        log_info "Backup: $backup_dir"
    else
        log_warn "Validation failed, changes not applied"
        rm -f "$temp_registry"
        return 1
    fi
}

# Strategy 3: Wholesale Replace
wholesale_storage_replace() {
    local offline_dir="$1"
    
    log_info "Strategy 3: Wholesale storage replacement"
    log_warn "NUCLEAR OPTION - Complete .storage replacement"
    
    # Create backup
    local backup_dir="$BACKUP_ROOT/${TS}_wholesale_backup"
    mkdir -p "$backup_dir"
    cp -a "/config/.storage" "$backup_dir/storage_complete"
    
    # Validate offline directory
    if [[ ! -d "$offline_dir" ]]; then
        log_warn "Offline directory not found: $offline_dir"
        return 1
    fi
    
    # Validate critical files exist
    local required_files=(
        "core.entity_registry"
        "core.device_registry"
        "core.config_entries"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$offline_dir/$file" ]]; then
            log_warn "Required file missing: $offline_dir/$file"
            return 1
        fi
    done
    
    # Validate JSON structure of critical files
    for file in "${required_files[@]}"; do
        if ! jq -e . "$offline_dir/$file" &>/dev/null; then
            log_warn "Invalid JSON in: $offline_dir/$file"
            return 1
        fi
    done
    
    log_info "Offline storage validation passed"
    
    # Replace storage atomically
    local temp_storage="/tmp/storage_temp_$TS"
    cp -a "$offline_dir" "$temp_storage"
    rm -rf "/config/.storage"
    mv "$temp_storage" "/config/.storage"
    
    log_success "Wholesale storage replacement completed"
    log_info "Backup: $backup_dir"
}

# Generate relationship repair plan for mobile devices
generate_mobile_repair_plan() {
    log_info "Analyzing mobile device entity relationships..."
    
    # Find active mobile app config entries
    local active_configs
    active_configs=$(jq -r '.data.entries[] | select(.domain == "mobile_app" and .disabled_by == null) | {entry_id, title}' "$CONFIG_ENTRIES")
    
    log_info "Active mobile app config entries:"
    echo "$active_configs" | jq -r '"  - \(.entry_id): \(.title)"'
    
    # Find orphaned mobile entities (those with non-existent config entries)
    local all_config_ids
    all_config_ids=$(jq -r '.data.entries[].entry_id' "$CONFIG_ENTRIES")
    
    jq -r --argjson active_ids "$(echo "$all_config_ids" | jq -R . | jq -s .)" \
        '.data.entities[] | 
         select(.platform == "mobile_app" and (.config_entry_id | IN($active_ids[]) | not)) |
         {entity_id, config_entry_id, device_id, platform}' \
        "$ENTITY_REGISTRY" | \
    jq -s 'group_by(.config_entry_id)[] | {
        orphaned_config_entry: .[0].config_entry_id,
        entity_count: length,
        sample_entities: [.[0:3][].entity_id]
    }'
}

# Main execution
main() {
    local strategy="${1:-}"
    shift || true
    
    case "$strategy" in
        "relationship-repair")
            local config_entry="" target_entities="" device_id=""
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --config-entry) config_entry="$2"; shift 2 ;;
                    --target-entities) target_entities="$2"; shift 2 ;;
                    --device-id) device_id="$2"; shift 2 ;;
                    *) log_warn "Unknown option: $1"; shift ;;
                esac
            done
            
            if [[ -z "$config_entry" || -z "$target_entities" || -z "$device_id" ]]; then
                log_warn "Missing required parameters for relationship-repair"
                show_usage
                return 1
            fi
            
            repair_entity_relationships "$config_entry" "$target_entities" "$device_id"
            ;;
        "gui-mimicry")
            local rename_plan=""
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --rename-plan) rename_plan="$2"; shift 2 ;;
                    *) log_warn "Unknown option: $1"; shift ;;
                esac
            done
            
            if [[ -z "$rename_plan" ]]; then
                log_warn "Missing required parameter: --rename-plan"
                show_usage
                return 1
            fi
            
            gui_style_rename "$rename_plan"
            ;;
        "wholesale-replace")
            local offline_dir=""
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --offline-dir) offline_dir="$2"; shift 2 ;;
                    *) log_warn "Unknown option: $1"; shift ;;
                esac
            done
            
            if [[ -z "$offline_dir" ]]; then
                log_warn "Missing required parameter: --offline-dir"
                show_usage
                return 1
            fi
            
            wholesale_storage_replace "$offline_dir"
            ;;
        "analyze")
            generate_mobile_repair_plan
            ;;
        *)
            show_usage
            return 1
            ;;
    esac
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi