#!/bin/bash

# Enhanced Entity Duplicate Validator
# Demonstrates the improved filtering logic for entity elimination

# Configuration
ENTITY_REGISTRY="/config/.storage/core.entity_registry"
HA_URL="http://localhost:8123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Enhanced entity evaluation
evaluate_entity_safety() {
    local entity_id="$1"
    local state="$2"
    local restored="$3"
    local disabled_by="$4"
    
    local safety_score=0
    local flags=()
    
    # Positive indicators (safer to keep)
    if [[ "$disabled_by" == "null" ]]; then
        ((safety_score += 10))
        flags+=("ENABLED")
    else
        flags+=("DISABLED:$disabled_by")
    fi
    
    if [[ "$state" != "unavailable" && "$state" != "unknown" ]]; then
        ((safety_score += 5))
        flags+=("AVAILABLE")
    else
        flags+=("UNAVAILABLE")
    fi
    
    if [[ "$restored" != "true" ]]; then
        ((safety_score += 3))
        flags+=("ACTIVE")
    else
        ((safety_score -= 5))
        flags+=("RESTORED")
    fi
    
    # Base name bonus
    if [[ ! "$entity_id" =~ _[0-9]+$ ]]; then
        ((safety_score += 8))
        flags+=("BASE_NAME")
    else
        flags+=("SUFFIXED")
    fi
    
    echo "$safety_score|$(IFS=','; echo "${flags[*]}")"
}

# Demonstrate enhanced filtering on Matter device group
demo_matter_device_filtering() {
    log_info "=== ENHANCED FILTERING DEMO: Matter Device Group ==="
    
    local entities=(
        "select.bedroom_wallpanel_alpha_matter_power_on_behaviour_on_startup"
        "select.bedroom_wallpanel_alpha_matter_power_on_behaviour_on_startup_2"
    )
    
    echo
    echo "ENTITY SAFETY EVALUATION:"
    echo "========================="
    
    # Get current states (simulated for demo)
    local entity_states=(
        "on|false|null"      # Entity 1: available, not restored, enabled
        "unavailable|true|null"  # Entity 2: unavailable, restored, enabled
    )
    
    for i in "${!entities[@]}"; do
        local entity="${entities[$i]}"
        IFS='|' read -r state restored disabled_by <<< "${entity_states[$i]}"
        
        local result
        result=$(evaluate_entity_safety "$entity" "$state" "$restored" "$disabled_by")
        
        IFS='|' read -r score flags <<< "$result"
        
        printf "%-60s Score: %2d  [%s]\n" "$entity" "$score" "$flags"
    done
    
    echo
    log_success "RECOMMENDATION: Keep entity with higher safety score"
    log_warn "ELIMINATED: Entities with 'RESTORED' or 'UNAVAILABLE' flags should be eliminated"
    echo
}

# Demonstrate the correct elimination logic
demo_elimination_logic() {
    log_info "=== CORRECTED ELIMINATION LOGIC ==="
    
    echo "NEW PRIORITIZATION ORDER:"
    echo "1. enabled + available + not_restored + base_name      (Score: 26+)"
    echo "2. enabled + available + base_name                     (Score: 23+)"  
    echo "3. enabled + available + not_restored                  (Score: 18+)"
    echo "4. enabled + available                                 (Score: 15+)"
    echo "5. ALL OTHERS                                          (Score: <15)"
    echo
    
    echo "SAFETY FILTERS:"
    echo "❌ restored: true     → AUTOMATIC LOSER"
    echo "❌ state: unavailable → AUTOMATIC LOSER" 
    echo "❌ disabled_by: user  → AUTOMATIC LOSER"
    echo "✅ enabled + available + not_restored → PREFERRED WINNER"
    echo
}

# Main demonstration
main() {
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    ENHANCED ENTITY SAFETY LOGIC                 ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo
    
    demo_elimination_logic
    demo_matter_device_filtering
    
    log_info "Enhanced filtering prevents elimination of valid active entities"
    log_info "Only restored/unavailable/disabled entities are eliminated"
}

main "$@"