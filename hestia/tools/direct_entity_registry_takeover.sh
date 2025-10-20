#!/bin/bash
# Direct Entity Registry Takeover Tool
# Solves the problem where base entities block name slots for canonical entities
# by directly manipulating the .storage/core.entity_registry JSON file

set -euo pipefail

# Configuration
ENTITY_REGISTRY="${ENTITY_REGISTRY:-/config/.storage/core.entity_registry}"
REPORT_ROOT="${REPORT_ROOT:-/config/hestia/workspace/operations/logs}"
TS=$(date -u +%Y%m%dT%H%M%SZ)

# Safety and logging
log_info() { echo "ℹ️  $(date '+%H:%M:%S') $*" >&2; }
log_warn() { echo "⚠️  $(date '+%H:%M:%S') $*" >&2; }
log_error() { echo "❌ $(date '+%H:%M:%S') $*" >&2; }

show_usage() {
    cat << 'EOF'
Direct Entity Registry Takeover Tool

PROBLEM SOLVED:
- Base entities (e.g., sensor.ephone_uk_battery_level) are blocking name slots
- Newer _2 entities (e.g., sensor.ephone_uk_battery_level_2) should take over the canonical names
- Home Assistant UI doesn't allow modifying stale base entities
- API doesn't support entity renaming operations

SOLUTION:
- Direct manipulation of .storage/core.entity_registry JSON file
- Atomic swapping of entity_id values between base and _2 entities
- Production-safe with mandatory backup and validation

USAGE:
    ./direct_entity_registry_takeover.sh [command] [options]

COMMANDS:
    analyze [--plan plan.json]    - Analyze entities for takeover operations
    execute --plan plan.json      - Execute takeover operations (requires --apply for actual changes)
    validate                      - Validate entity registry structure

OPTIONS:
    --plan FILE                   - JSON plan file with entity groups
    --apply                       - Actually perform changes (default is dry-run)
    --force                       - Skip safety prompts
    --backup-dir DIR              - Custom backup directory

EXAMPLES:
    # Analyze mobile device duplicates
    ./direct_entity_registry_takeover.sh analyze --plan mobile_devices_cleanup_plan_final.json
    
    # Execute takeover operations (dry-run first)
    ./direct_entity_registry_takeover.sh execute --plan mobile_devices_cleanup_plan_final.json
    
    # Execute with actual changes
    ./direct_entity_registry_takeover.sh execute --plan mobile_devices_cleanup_plan_final.json --apply

SAFETY:
- Automatic .storage backup before any changes
- Atomic JSON operations with validation
- Emergency restore script generation
- Dry-run mode by default
- Structure validation before and after

EOF
}

# Backup and safety functions
backup_storage() {
    local backup_root="/config/hestia/workspace/archive/backups"
    local bdir="$backup_root/${TS}"
    
    mkdir -p "$bdir"
    
    log_info "Creating complete .storage backup at $bdir"
    
    # Complete .storage backup
    cp -a "/config/.storage" "$bdir/storage_complete"
    
    # Individual registry files for quick access
    cp -a "$ENTITY_REGISTRY" "$bdir/core.entity_registry.json"
    [[ -f "/config/.storage/core.device_registry" ]] && cp -a "/config/.storage/core.device_registry" "$bdir/core.device_registry.json"
    
    # Create emergency restore script
    cat > "$bdir/restore.sh" << 'EOF'
#!/bin/bash
# Emergency restore script for entity takeover operations
# Usage: ./restore.sh

BACKUP_DIR="$(dirname "$0")"
STORAGE_DIR="/config/.storage"

echo "🚨 EMERGENCY RESTORE: Restoring .storage from backup"
echo "Backup location: $BACKUP_DIR"
echo "Target location: $STORAGE_DIR"

read -p "Are you sure you want to restore? This will overwrite current .storage (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping Home Assistant..."
    # Note: Add your HA stop command here if needed
    
    echo "Restoring .storage directory..."
    rm -rf "$STORAGE_DIR"
    cp -a "$BACKUP_DIR/storage_complete" "$STORAGE_DIR"
    
    echo "✅ Restore complete. Restart Home Assistant to apply changes."
    echo "💡 All entity takeover operations have been reverted."
else
    echo "Restore cancelled."
fi
EOF
    chmod +x "$bdir/restore.sh"
    
    echo "$bdir"
}

# Validate entity registry structure
validate_registry() {
    local registry_file="$1"
    
    if ! jq -e '.data.entities | type == "array"' "$registry_file" &>/dev/null; then
        log_error "Invalid entity registry structure: missing .data.entities array"
        return 1
    fi
    
    local entity_count
    entity_count=$(jq -r '.data.entities | length' "$registry_file")
    log_info "Entity registry validation: $entity_count entities found"
    
    # Check for duplicate entity_ids (should not happen)
    local unique_count
    unique_count=$(jq -r '.data.entities | map(.entity_id) | unique | length' "$registry_file")
    
    if [[ "$entity_count" != "$unique_count" ]]; then
        log_error "Registry corruption detected: duplicate entity_ids found"
        return 1
    fi
    
    return 0
}

# Analyze entities for takeover operations
analyze_entities() {
    local plan_file="$1"
    
    log_info "Analyzing entities for takeover operations..."
    
    if [[ ! -f "$plan_file" ]]; then
        log_error "Plan file not found: $plan_file"
        return 1
    fi
    
    # Validate registry first
    if ! validate_registry "$ENTITY_REGISTRY"; then
        return 1
    fi
    
    # Read plan and analyze each group
    local report_file="$REPORT_ROOT/direct_takeover_analysis_$TS.json"
    mkdir -p "$(dirname "$report_file")"
    
    echo '{"analysis_timestamp": "'$TS'", "groups": []}' > "$report_file"
    
    local group_count
    group_count=$(jq -r '. | length' "$plan_file")
    log_info "Processing $group_count entity groups from plan"
    
    for ((i=0; i<group_count; i++)); do
        local group
        group=$(jq -r ".[$i]" "$plan_file")
        
        local base_entity newer_entity group_name
        base_entity=$(echo "$group" | jq -r '.base_entity')
        newer_entity=$(echo "$group" | jq -r '.newer_entity')  
        group_name=$(echo "$group" | jq -r '.group_name // .device_name')
        
        log_info "Analyzing group: $group_name ($base_entity → $newer_entity)"
        
        # Check if both entities exist in registry
        local base_exists newer_exists
        base_exists=$(jq -r --arg entity "$base_entity" '.data.entities[] | select(.entity_id == $entity) | .entity_id' "$ENTITY_REGISTRY" 2>/dev/null || echo "")
        newer_exists=$(jq -r --arg entity "$newer_entity" '.data.entities[] | select(.entity_id == $entity) | .entity_id' "$ENTITY_REGISTRY" 2>/dev/null || echo "")
        
        local status="ready"
        local notes=""
        
        if [[ -z "$base_exists" ]]; then
            status="base_missing"
            notes="Base entity $base_entity not found in registry"
        elif [[ -z "$newer_exists" ]]; then
            status="newer_missing"  
            notes="Newer entity $newer_entity not found in registry"
        fi
        
        # Add to analysis report
        local group_analysis
        group_analysis=$(jq -n \
            --arg group_name "$group_name" \
            --arg base_entity "$base_entity" \
            --arg newer_entity "$newer_entity" \
            --arg status "$status" \
            --arg notes "$notes" \
            --argjson base_exists "$(if [[ -n "$base_exists" ]]; then echo true; else echo false; fi)" \
            --argjson newer_exists "$(if [[ -n "$newer_exists" ]]; then echo true; else echo false; fi)" \
            '{
                group_name: $group_name,
                base_entity: $base_entity,
                newer_entity: $newer_entity,
                base_exists: $base_exists,
                newer_exists: $newer_exists,
                status: $status,
                notes: $notes
            }')
        
        # Append to report
        jq --argjson group "$group_analysis" '.groups += [$group]' "$report_file" > "$report_file.tmp"
        mv "$report_file.tmp" "$report_file"
    done
    
    # Summary
    local ready_count missing_count
    ready_count=$(jq -r '[.groups[] | select(.status == "ready")] | length' "$report_file")
    missing_count=$(jq -r '[.groups[] | select(.status != "ready")] | length' "$report_file")
    
    log_info "Analysis complete:"
    log_info "  Ready for takeover: $ready_count groups"
    log_info "  Issues found: $missing_count groups"
    log_info "  Report saved: $report_file"
    
    if [[ "$missing_count" -gt 0 ]]; then
        log_warn "Some groups have issues - check report for details"
        jq -r '.groups[] | select(.status != "ready") | "  ⚠️  \(.group_name): \(.notes)"' "$report_file"
    fi
}

# Execute takeover operations
execute_takeover() {
    local plan_file="$1"
    local apply_changes="${2:-false}"
    
    log_info "Executing entity takeover operations (apply=$apply_changes)..."
    
    if [[ ! -f "$plan_file" ]]; then
        log_error "Plan file not found: $plan_file"
        return 1
    fi
    
    # Validate registry first
    if ! validate_registry "$ENTITY_REGISTRY"; then
        return 1
    fi
    
    # Create backup before any changes
    local backup_dir
    backup_dir=$(backup_storage)
    log_info "Backup created: $backup_dir"
    
    # Create working copy for modifications
    local working_registry="/tmp/entity_registry_work_$TS.json"
    cp "$ENTITY_REGISTRY" "$working_registry"
    
    local report_file="$REPORT_ROOT/direct_takeover_execution_$TS.json"
    mkdir -p "$(dirname "$report_file")"
    
    echo '{"execution_timestamp": "'$TS'", "apply_changes": '$apply_changes', "operations": []}' > "$report_file"
    
    local group_count
    group_count=$(jq -r '. | length' "$plan_file")
    log_info "Processing $group_count entity groups from plan"
    
    local success_count=0
    local error_count=0
    
    for ((i=0; i<group_count; i++)); do
        local group
        group=$(jq -r ".[$i]" "$plan_file")
        
        local base_entity newer_entity group_name
        base_entity=$(echo "$group" | jq -r '.base_entity')
        newer_entity=$(echo "$group" | jq -r '.newer_entity')
        group_name=$(echo "$group" | jq -r '.group_name // .device_name')
        
        log_info "Processing group $((i+1))/$group_count: $group_name"
        
        # Perform the entity ID swap
        local swap_result
        if swap_result=$(perform_entity_swap "$working_registry" "$base_entity" "$newer_entity" "$group_name"); then
            ((success_count++))
            log_info "✅ Swapped: $base_entity ↔ $newer_entity"
        else
            ((error_count++))
            log_error "❌ Failed: $group_name - $swap_result"
        fi
        
        # Record operation result
        local operation_result
        operation_result=$(jq -n \
            --arg group_name "$group_name" \
            --arg base_entity "$base_entity" \
            --arg newer_entity "$newer_entity" \
            --arg result "$swap_result" \
            --argjson success "$(if [[ "$swap_result" == "success" ]]; then echo true; else echo false; fi)" \
            '{
                group_name: $group_name,
                base_entity: $base_entity,
                newer_entity: $newer_entity,
                success: $success,
                result: $result
            }')
        
        jq --argjson op "$operation_result" '.operations += [$op]' "$report_file" > "$report_file.tmp"
        mv "$report_file.tmp" "$report_file"
    done
    
    # Validate modified registry
    if ! validate_registry "$working_registry"; then
        log_error "Modified registry failed validation - aborting"
        rm -f "$working_registry"
        return 1
    fi
    
    # Apply changes if requested
    if [[ "$apply_changes" == "true" ]]; then
        log_info "Applying changes to entity registry..."
        cp "$working_registry" "$ENTITY_REGISTRY"
        log_info "✅ Entity registry updated successfully"
        log_info "🔄 Restart Home Assistant to apply changes"
    else
        log_info "Dry-run complete - no changes applied"
        log_info "Use --apply to perform actual changes"
    fi
    
    rm -f "$working_registry"
    
    log_info "Execution summary:"
    log_info "  Successful operations: $success_count"
    log_info "  Failed operations: $error_count"
    log_info "  Report saved: $report_file"
    log_info "  Backup location: $backup_dir"
}

# Perform atomic entity ID swap
perform_entity_swap() {
    local registry_file="$1"
    local base_entity="$2"
    local newer_entity="$3"
    local group_name="$4"
    
    # Check both entities exist
    local base_index newer_index
    base_index=$(jq -r --arg entity "$base_entity" '.data.entities | to_entries[] | select(.value.entity_id == $entity) | .key' "$registry_file")
    newer_index=$(jq -r --arg entity "$newer_entity" '.data.entities | to_entries[] | select(.value.entity_id == $entity) | .key' "$registry_file")
    
    if [[ -z "$base_index" ]]; then
        echo "base_entity_not_found"
        return 1
    fi
    
    if [[ -z "$newer_index" ]]; then
        echo "newer_entity_not_found"
        return 1
    fi
    
    # Create temporary unique ID to avoid collision during swap
    local temp_id="temp_swap_$(echo "$base_entity" | tr '.' '_')_$$"
    
    # Step 1: Rename base_entity to temp_id
    jq --arg idx "$base_index" --arg temp_id "$temp_id" \
        '.data.entities[($idx | tonumber)].entity_id = $temp_id' \
        "$registry_file" > "$registry_file.tmp1"
    
    # Step 2: Rename newer_entity to base_entity name
    jq --arg idx "$newer_index" --arg base_id "$base_entity" \
        '.data.entities[($idx | tonumber)].entity_id = $base_id' \
        "$registry_file.tmp1" > "$registry_file.tmp2"
    
    # Step 3: Rename temp_id to newer_entity name  
    jq --arg idx "$base_index" --arg newer_id "$newer_entity" \
        '.data.entities[($idx | tonumber)].entity_id = $newer_id' \
        "$registry_file.tmp2" > "$registry_file.tmp3"
    
    # Final validation and commit
    if validate_registry "$registry_file.tmp3"; then
        mv "$registry_file.tmp3" "$registry_file"
        rm -f "$registry_file.tmp1" "$registry_file.tmp2"
        echo "success"
        return 0
    else
        rm -f "$registry_file.tmp1" "$registry_file.tmp2" "$registry_file.tmp3"
        echo "validation_failed"
        return 1
    fi
}

# Main script logic
main() {
    local command="${1:-}"
    shift || true
    
    local plan_file=""
    local apply_changes="false"
    local force="false"
    local backup_dir=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --plan)
                plan_file="$2"
                shift 2
                ;;
            --apply)
                apply_changes="true"
                shift
                ;;
            --force)
                force="true"
                shift
                ;;
            --backup-dir)
                backup_dir="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                return 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                return 1
                ;;
        esac
    done
    
    # Validate prerequisites
    if [[ ! -f "$ENTITY_REGISTRY" ]]; then
        log_error "Entity registry not found: $ENTITY_REGISTRY"
        return 1
    fi
    
    if ! command -v jq &>/dev/null; then
        log_error "jq is required but not installed"
        return 1
    fi
    
    case "$command" in
        analyze)
            if [[ -z "$plan_file" ]]; then
                log_error "Plan file required for analyze command"
                show_usage
                return 1
            fi
            analyze_entities "$plan_file"
            ;;
        execute)
            if [[ -z "$plan_file" ]]; then
                log_error "Plan file required for execute command"
                show_usage
                return 1
            fi
            
            if [[ "$apply_changes" == "true" && "$force" != "true" ]]; then
                echo "⚠️  DIRECT ENTITY REGISTRY MANIPULATION"
                echo "This will modify /config/.storage/core.entity_registry directly"
                echo "Home Assistant restart will be required after changes"
                echo ""
                read -p "Continue with entity takeover operations? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    log_info "Operation cancelled by user"
                    return 0
                fi
            fi
            
            execute_takeover "$plan_file" "$apply_changes"
            ;;
        validate)
            validate_registry "$ENTITY_REGISTRY"
            log_info "Entity registry validation complete"
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi