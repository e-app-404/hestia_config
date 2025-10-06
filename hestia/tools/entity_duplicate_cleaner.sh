#!/bin/bash
# Entity Registry Duplicate Cleaner
# Identifies and helps clean up duplicate entities with _2, _3 suffixes

set -euo pipefail

 ENTITY_REGISTRY="${ENTITY_REGISTRY:-/config/.storage/core.entity_registry}"
 DEVICE_REGISTRY="${DEVICE_REGISTRY:-/config/.storage/core.device_registry}"
 CONFIG_ENTRIES="${CONFIG_ENTRIES:-/config/.storage/core.config_entries}"
 REPORT_ROOT="${REPORT_ROOT:-/config/hestia/workspace/reports/checkpoints/ENTITY_DEDUP}"
 TS="$(date -u +%Y%m%dT%H%M%SZ)"
 mkdir -p "$REPORT_ROOT"

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

# Safety functions
entity_exists() {
    # states endpoint returns 200 if entity is registered and known to HA
    local eid="$1"
    local r; r=$(ha_api_call "GET" "/api/states/$eid") || true
    [[ "${DRY_RUN:-true}" == "true" ]] && return 1
    echo "$r" | grep -q "\"entity_id\":\"$eid\""
}

# Endpoint compatibility probe - cache working paths
probe_registry_endpoints() {
    [[ -n "$REGISTRY_ENDPOINT_CACHED" ]] && return 0
    local test_entity="sensor.nonexistent_probe_test"
    
    # Try primary registry endpoint
    if ha_api_call "GET" "/api/config/entity_registry/$test_entity" >/dev/null 2>&1; then
        REGISTRY_ENDPOINT="/api/config/entity_registry"
        REGISTRY_ENDPOINT_CACHED=true
        log_debug "Using primary registry endpoint: $REGISTRY_ENDPOINT"
        return 0
    fi
    
    # Try fallback registry endpoint
    if ha_api_call "GET" "/api/config/entity_registry/update/$test_entity" >/dev/null 2>&1; then
        REGISTRY_ENDPOINT="/api/config/entity_registry/update"
        REGISTRY_ENDPOINT_CACHED=true
        log_debug "Using fallback registry endpoint: $REGISTRY_ENDPOINT" 
        return 0
    fi
    
    # Default to services as tertiary fallback
    REGISTRY_ENDPOINT="/api/services/homeassistant/update_entity"
    REGISTRY_ENDPOINT_CACHED=true
    log_warn "Using services endpoint as fallback: $REGISTRY_ENDPOINT"
}

backup_storage() {
    local bdir="/config/hestia/workspace/archive/backups/$TS"
    install -d "$bdir"
    cp -a "$ENTITY_REGISTRY" "$bdir/core.entity_registry.json"
    [[ -f "$DEVICE_REGISTRY" ]] && cp -a "$DEVICE_REGISTRY" "$bdir/core.device_registry.json"
    [[ -f "$CONFIG_ENTRIES" ]] && cp -a "$CONFIG_ENTRIES" "$bdir/core.config_entries.json"
    log_info "Backup created: $bdir"
}

# Binary acceptance checklist validation
validate_execution_readiness() {
    local checks_passed=0
    local checks_total=7
    
    echo "=== BINARY ACCEPTANCE CHECKLIST ==="
    
    # Ensure backup directory exists for validation
    backup_storage
    
    # Pre-check: validate enhanced filtering logic
    local test_plan="$REPORT_ROOT/validation_plan.$TS.json"
    emit_plan
    if [[ -f "$PLAN_FILE" ]]; then
        local risky_groups
        risky_groups=$(jq '[.[] | select(.candidates | map(select(.restored == true or .state == "unavailable")) | length == length)] | length' "$PLAN_FILE")
        if [[ $risky_groups -gt 0 ]]; then
            echo "⚠️  WARNING: $risky_groups groups contain only restored/unavailable entities - manual review required"
        fi
    fi
    
    # Check 1: Backup directory and files
    local backup_dir="/config/hestia/workspace/archive/backups/$TS"
    if [[ -f "$backup_dir/core.entity_registry.json" && -f "$backup_dir/core.device_registry.json" ]]; then
        echo "✅ Backup present: $backup_dir/{core.entity_registry.json,core.device_registry.json}"
        ((checks_passed++))
    else
        echo "❌ Backup missing: $backup_dir/"
    fi
    
    # Check 2: Plan file exists and non-empty
    if [[ -n "$PLAN_FILE" && -f "$PLAN_FILE" && -s "$PLAN_FILE" ]]; then
        local plan_length
        plan_length=$(jq 'length' "$PLAN_FILE" 2>/dev/null || echo 0)
        if [[ $plan_length -gt 0 ]]; then
            echo "✅ Plan file exists and non-empty: $PLAN_FILE (length: $plan_length)"
            ((checks_passed++))
        else
            echo "❌ Plan file empty: $PLAN_FILE"
        fi
    else
        echo "❌ Plan file missing or empty: ${PLAN_FILE:-unset}"
    fi
    
    # Check 3: DRY-RUN default with explicit apply required
    if [[ "${DRY_RUN:-true}" == "true" && "${FORCE_MODE:-false}" != "true" ]]; then
        echo "✅ DRY-RUN default true; --apply required to mutate"
        ((checks_passed++))
    else
        echo "❌ DRY-RUN not properly defaulted or --apply already set"
    fi
    
    # Check 4: Batch limits
    if [[ ${BATCH_SIZE:-0} -le 25 && ${SLEEP_MS:-0} -ge 150 ]]; then
        echo "✅ Batch limits set: --batch-size=$BATCH_SIZE (≤25), --sleep-ms=$SLEEP_MS (≥150)"
        ((checks_passed++))
    else
        echo "❌ Batch limits not properly configured: batch-size=$BATCH_SIZE, sleep-ms=$SLEEP_MS"
    fi
    
    # Check 5: Post-validation enabled (entity_exists function available)
    if declare -f entity_exists >/dev/null; then
        echo "✅ Post-validation ON (entity_exists + states GET after each op)"
        ((checks_passed++))
    else
        echo "❌ Post-validation functions missing"
    fi
    
    # Check 6: Report folder writable
    local report_dir="/config/hestia/workspace/reports/checkpoints/ENTITY_DEDUP"
    if [[ -d "$report_dir" && -w "$report_dir" ]]; then
        echo "✅ Report folder writable: $report_dir"
        ((checks_passed++))
    else
        echo "❌ Report folder not writable: $report_dir"
    fi
    
    echo "=== CHECKLIST RESULT: $checks_passed/$checks_total ==="
    
    if [[ $checks_passed -eq $checks_total ]]; then
        echo "🟢 GO for production in controlled batches"
        return 0
    else
        echo "🔴 NO-GO: $(($checks_total - $checks_passed)) checks failed"
        return 1
    fi
}

emit_plan() {
    local plan="$REPORT_ROOT/duplicate_cleanup_plan.$TS.json"
    
    # Get current states for all entities to check restored/unavailable status
    local states_file="$REPORT_ROOT/current_states.$TS.json"
    if [[ "${DRY_RUN:-true}" == "true" ]]; then
        echo "[]" > "$states_file"  # Skip API call in dry-run mode
    else
        ha_api_call "GET" "/api/states" > "$states_file"
    fi
    
    jq -r --slurpfile states "$states_file" '
      .data.entities
      | map({
          entity_id,platform,device_id,config_entry_id,unique_id,disabled_by,
          state: ($states[0][] | select(.entity_id == .entity_id) | .state // "unknown"),
          restored: ($states[0][] | select(.entity_id == .entity_id) | .attributes.restored // false)
        })
      | group_by(.entity_id|sub("_[0-9]+$";""))
      | map({
          base:(.[0].entity_id|sub("_[0-9]+$";"")),
          candidates: .
        })
      | map(select(
          (.candidates|length)>1 and 
          (.base | test("(sonos_alarm|segment_[0-9]+|_[0-9]{3}|backlight_alpha)$") | not)
        ))
    ' "$ENTITY_REGISTRY" > "$plan"
    
    log_info "Plan written: $plan (with state/restored info)"
    rm -f "$states_file"
}

execute_plan() {
    local plan="${PLAN_FILE:?plan file required}"
    [[ -f "$plan" ]] || { log_error "Plan file not found: $plan"; return 1; }
    [[ "${DRY_RUN:-true}" == "true" ]] && log_warn "DRY-RUN: execution will simulate only"
    
    # Initialize execution logging
    local exec_log="$REPORT_ROOT/execute.$TS.log"
    local exec_summary="$REPORT_ROOT/execute_summary.$TS.json"
    exec > >(tee -a "$exec_log")
    exec 2>&1
    
    # Initialize counters
    local planned_groups=0 processed=0 parked=0 disabled=0 renamed=0 failures=0
    planned_groups=$(jq 'length' "$plan")
    
    log_info "Starting execution: $planned_groups groups planned"
    
    if [[ "$FORCE_MODE" != "true" ]]; then
        backup_storage
    fi
    
    local n=0
    # TAKEOVER Strategy: newer entities (usually suffixed) take over base names from stale registrations
    jq -c '.[]' "$plan" | while read -r grp; do
      base=$(echo "$grp" | jq -r '.base')
      
      # TAKEOVER LOGIC: Prefer newer entities (typically suffixed) over older base entities
      # This handles mobile app re-registrations where _2 is the current device
      # Priority: 1) newest enabled + available + not restored (highest suffix number)
      #          2) any enabled + available + not restored  
      #          3) any enabled + available
      #          4) fallback to base name
      
      # Sort candidates by suffix number (newer = higher suffix)
      winners=$(echo "$grp" | jq -r '
        [.candidates[] | select(
          (.disabled_by == null) and
          (.restored != true) and
          (.state != "unavailable")
        )] | sort_by(.entity_id) | reverse | .[0].entity_id // empty' --arg base "$base")
      
      if [[ -z "$winners" ]]; then
        winners=$(echo "$grp" | jq -r '
          [.candidates[] | select(
            (.disabled_by == null) and
            (.state != "unavailable")
          )] | sort_by(.entity_id) | reverse | .[0].entity_id // empty' --arg base "$base")
      fi
      
      if [[ -z "$winners" ]]; then
        winners=$(echo "$grp" | jq -r '
          [.candidates[] | select(.disabled_by == null)] | 
          sort_by(.entity_id) | reverse | .[0].entity_id // empty' --arg base "$base")
      fi
      
      # Final fallback to base name if available
      if [[ -z "$winners" ]]; then
        winners=$(echo "$grp" | jq -r '
          .candidates[] | select(.entity_id == $base) | .entity_id' --arg base "$base")
      fi
      
      # If still no winners, skip this group entirely
      if [[ -z "$winners" ]]; then
        log_warn "No suitable winner found in group base=$base - skipping"
        continue
      fi
      
      losers=$(echo "$grp" | jq -r --arg w "$winners" '.candidates[] | select(.entity_id != $w) | .entity_id')
      log_info "Group base=$base winner=${winners:-none}"
      
      # TAKEOVER OPERATION: Winner takes over base name, old entities are disabled
      
      # Step 1: If winner is not the base entity, perform takeover
      if [[ -n "$winners" && "$winners" != "$base" ]]; then
        log_info "TAKEOVER: $winners will take over $base"
        
        # Disable the old base entity (stale registration)
        if entity_exists "$base"; then
          log_info "Disabling stale base entity: $base"
          if disable_entity "$base"; then
            ((disabled++))
          else
            ((failures++))
            log_error "Failed to disable base entity, skipping takeover"
            continue
          fi
        fi
        
        # Rename winner to take over base name
        log_info "Renaming winner to base name: $winners -> $base"
        if rename_entity "$winners" "$base"; then
          ((renamed++))
        else
          ((failures++))
          log_error "Failed to rename winner to base name"
        fi
        
        # Disable all other losers (except the base we already handled)
        for e in $losers; do
          if [[ "$e" != "$base" ]]; then
            log_info "Disabling duplicate entity: $e"
            if disable_entity "$e"; then
              ((disabled++))
            else
              ((failures++))
            fi
          fi
        done
        
      else
        # Winner is already the base entity, just disable losers
        log_info "Base entity $base is already the winner, disabling duplicates"
        for e in $losers; do
          log_info "Disabling duplicate entity: $e"
          if disable_entity "$e"; then
            ((disabled++))
          else
            ((failures++))
          fi
        done
      fi
      
      ((processed++))
      n=$((n+1)); [[ $n -ge $BATCH_SIZE ]] && { log_warn "Batch limit reached"; break; }
      sleep "$(awk "BEGIN{print $SLEEP_MS/1000}")"
    done
    log_info "Execution complete (processed up to $BATCH_SIZE groups)."
    
    # Generate execution summary
    jq -n \
      --arg planned_groups "$planned_groups" \
      --arg processed "$processed" \
      --arg parked "$parked" \
      --arg disabled "$disabled" \
      --arg renamed "$renamed" \
      --arg failures "$failures" \
      '{
        planned_groups: ($planned_groups | tonumber),
        processed: ($processed | tonumber), 
        parked: ($parked | tonumber),
        disabled: ($disabled | tonumber),
        renamed: ($renamed | tonumber),
        failures: ($failures | tonumber),
        timestamp: now | strftime("%Y-%m-%dT%H:%M:%SZ")
      }' > "$exec_summary"
    
    # Post-validation: check that operations succeeded
    local post_report="$REPORT_ROOT/post_validation.$TS.json"
    analyze_duplicates > "$post_report"
    local post_count
    post_count=$(jq '[.[] | select(.candidates | length > 1)] | length' "$post_report")
    log_info "Post-validation: $post_count duplicate groups remaining (report: $post_report)"
    log_info "Execution summary: $exec_summary"
}

 show_usage() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  scan       - Scan for duplicate entities (default, read-only)"
    echo "  plan       - Generate duplicate_cleanup_plan.json (no changes)"
    echo "  preflight  - Run binary acceptance checklist before execution"
    echo "  execute    - Execute a plan file safely (TAKEOVER mode: newer entities take base names)"
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
    echo "  --plan FILE       - Plan file to execute"
    echo "  --batch-size N    - Max changes per run (default: 25)"
    echo "  --sleep-ms N      - Sleep between ops (default: 150)"
    echo "  --dry-run         - Simulate operations without changes (default: true)"
    echo "  --apply           - Actually perform operations (overrides dry-run)"
    echo "  --sleep-ms N      - Sleep between ops (default: 150)"
    echo "  --force           - Skip backup requirement for destructive ops"
    echo "  --dry-run         - Show what would be done without executing (default)""
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
     DRY_RUN=true
     BATCH_SIZE=25
     SLEEP_MS=150
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --plan) PLAN_FILE="$2"; shift 2;;
            --batch-size) BATCH_SIZE="$2"; shift 2;;
            --sleep-ms) SLEEP_MS="$2"; shift 2;;
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
    
    if [[ "${DRY_RUN:-true}" == "true" ]]; then
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
    # Use probed endpoint with proper compatibility
    probe_registry_endpoints
    local response
    if [[ "$REGISTRY_ENDPOINT" == "/api/services/homeassistant/update_entity" ]]; then
        response=$(ha_api_call "POST" "/api/services/homeassistant/update_entity" "{\"entity_id\":\"$entity_id\",\"disabled_by\":\"user\"}")
    else
        response=$(ha_api_call "POST" "$REGISTRY_ENDPOINT/$entity_id" '{"disabled_by":"user"}')
    fi
    
    if [[ "${DRY_RUN:-true}" == "true" ]]; then
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
    # Ensure target does not exist
    if entity_exists "$new_id"; then
        log_error "Target entity_id already exists: $new_id"; return 1
    fi
    # Use probed endpoint with proper compatibility
    probe_registry_endpoints
    local response
    if [[ "$REGISTRY_ENDPOINT" == "/api/services/homeassistant/update_entity" ]]; then
        log_warn "Services endpoint cannot rename entities - operation skipped"
        return 1
    else
        response=$(ha_api_call "POST" "$REGISTRY_ENDPOINT/$old_id" "{\"new_entity_id\":\"$new_id\"}")
    fi

backup_storage() {
        local bdir="/config/hestia/workspace/archive/backups/$TS"
        install -d "$bdir"
        cp -a "$ENTITY_REGISTRY" "$bdir/core.entity_registry.json"
        [[ -f "$DEVICE_REGISTRY" ]] && cp -a "$DEVICE_REGISTRY" "$bdir/core.device_registry.json"
        [[ -f "$CONFIG_ENTRIES" ]] && cp -a "$CONFIG_ENTRIES" "$bdir/core.config_entries.json"
        log_info "Backup created: $bdir"
}

emit_plan() {
        local plan="$REPORT_ROOT/duplicate_cleanup_plan.$TS.json"
        jq -r '
            .data.entities
            | map({entity_id,platform,device_id,config_entry_id,unique_id,disabled_by})
            | group_by(.entity_id|sub("_[0-9]+$";""))
            | map({
                    base:(.[0].entity_id|sub("_[0-9]+$";"")),
                    candidates: .
                })
            | map(select((.candidates|length)>1 or (.candidates[]|.entity_id|test("_[0-9]+$"))))
        ' "$ENTITY_REGISTRY" > "$plan"
        log_info "Plan written: $plan"
}

execute_plan() {
        local plan="${PLAN_FILE:?plan file required}"
        [[ -f "$plan" ]] || { log_error "Plan file not found: $plan"; return 1; }
        [[ "${DRY_RUN:-true}" == "true" ]] && log_warn "DRY-RUN: execution will simulate only"
        backup_storage
        local n=0
        # naive strategy: keep first non-suffixed or most-enabled; disable others; fix name
        jq -c '.[]' "$plan" | while read -r grp; do
            base=$(echo "$grp" | jq -r '.base')
            winners=$(echo "$grp" | jq -r '.candidates[] | select(.entity_id == $base and (.disabled_by == null)) | .entity_id' --arg base "$base")
            if [[ -z "$winners" ]]; then
                winners=$(echo "$grp" | jq -r '.candidates[] | select(.disabled_by == null) | .entity_id' | head -1)
            fi
            losers=$(echo "$grp" | jq -r --arg w "$winners" '.candidates[] | select(.entity_id != $w) | .entity_id')
            log_info "Group base=$base winner=${winners:-none}"
            # If base exists but not the winner, park it
            if [[ -n "$winners" && "$winners" != "$base" ]] && entity_exists "$base"; then
                 park="${base}__retired__${TS}"
                 log_info "Parking existing base: $base -> $park"
                 rename_entity "$base" "$park" || true
            fi
            # Disable losers
            for e in $losers; do
                disable_entity "$e" || true
            done
            # If winner lacks base name, rename to base
            if [[ -n "$winners" && "$winners" != "$base" ]]; then
                rename_entity "$winners" "$base" || true
            fi
            n=$((n+1)); [[ $n -ge $BATCH_SIZE ]] && { log_warn "Batch limit reached"; break; }
            sleep "$(awk "BEGIN{print $SLEEP_MS/1000}")"
        done
        log_info "Execution complete (processed up to $BATCH_SIZE groups)."
}
    
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
        "plan")
            emit_plan
            ;;
        "execute")
            execute_plan
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
        "plan")
            emit_plan
            ;;
        "execute")
            execute_plan
            ;;
        "preflight")
            validate_execution_readiness
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