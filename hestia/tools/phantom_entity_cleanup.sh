#!/usr/bin/env bash
# phantom_entity_cleanup.sh
# Comprehensive offline cleanup of orphaned mobile device entities
# Usage: ./phantom_entity_cleanup.sh [--dry-run] [--execute]
# Author: Advanced Entity Registry Cleanup Strategy
# Date: 2025-10-07

set -euo pipefail
[ "${DEBUG:-}" = "" ] || set -x

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_CONFIG="${ROOT_CONFIG:-/config}"
STORAGE_DIR="$ROOT_CONFIG/.storage"
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
DAY=$(date -u +%Y%m%d)
REPORTS_DIR="$ROOT_CONFIG/hestia/reports/$DAY"

# Orphaned config entry IDs to remove
ORPHANED_CONFIG_ENTRIES=(
    "01K6ESGN474SS9EF6A5HZP75VY"  # ePhone UK - deleted
    "01K6DA12T2HAMM9YQ73V8W6T6N"  # MacBook - deleted
)

# Known orphaned device IDs (will be discovered automatically too)
KNOWN_ORPHANED_DEVICES=(
    "1bbcd24d26b98d2ee55e5ddf84e38e09"  # From previous analysis
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }

# Check if we should proceed
DRY_RUN=false
EXECUTE=false

for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --execute) EXECUTE=true ;;
        --help)
            cat << EOF
Phantom Entity Cleanup - Offline .storage cleanup for orphaned mobile entities

USAGE:
    $0 [--dry-run] [--execute]

OPTIONS:
    --dry-run    Show what would be done without making changes
    --execute    Actually perform the cleanup (requires confirmation)
    --help       Show this help message

DESCRIPTION:
    This script safely removes orphaned mobile device entities and devices
    from Home Assistant's entity and device registries. It operates offline
    (HA must be stopped) and creates comprehensive backups.

PROCESS:
    1. Create timestamped backups of all .storage files
    2. Analyze and report orphaned entities/devices
    3. Generate cleaned registry files (removes orphaned relationships)
    4. Create reconciliation checklist for post-restart entity renaming
    5. Provide clear restart and re-registration instructions

SAFETY:
    - Full .storage backup before any changes
    - Timestamped receipts for audit trail
    - Rollback instructions provided
    - Preserves all non-orphaned entities and relationships

EOF
            exit 0
            ;;
    esac
done

if [[ "$DRY_RUN" == false && "$EXECUTE" == false ]]; then
    log_error "Must specify either --dry-run or --execute"
    echo "Use --help for usage information"
    exit 1
fi

# Verify dependencies
command -v jq >/dev/null || { log_error "jq is required but not installed"; exit 1; }

# Verify we're in the right location
if [[ ! -f "$STORAGE_DIR/core.entity_registry" ]]; then
    log_error "Cannot find $STORAGE_DIR/core.entity_registry"
    log_error "Please run this script from the Home Assistant config directory"
    exit 1
fi

log_info "Starting phantom entity cleanup - Timestamp: $TIMESTAMP"
log_info "Mode: $([ "$DRY_RUN" == true ] && echo "DRY RUN" || echo "EXECUTE")"

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Phase 0: Preflight checks and backups
log_info "Phase 0: Preflight checks and backups"

if [[ "$EXECUTE" == true ]]; then
    # Check if Home Assistant is running
    if pgrep -f "home-assistant" >/dev/null; then
        log_error "Home Assistant appears to be running!"
        log_error "Please stop Home Assistant before running this cleanup:"
        log_error "  ha core stop"
        log_error "  # or docker stop homeassistant"
        log_error "  # or systemctl stop home-assistant@homeassistant"
        exit 1
    fi
    
    log_success "Home Assistant appears to be stopped"
    
    # Create full storage backup
    log_info "Creating full .storage backup..."
    cp -a "$STORAGE_DIR" "$REPORTS_DIR/.storage_$TIMESTAMP"
    log_success "Backup created: $REPORTS_DIR/.storage_$TIMESTAMP"
fi

# Phase 1: Analysis - discover all orphaned entities and devices
log_info "Phase 1: Analyzing orphaned entities and devices"

ORPHANED_ENTITIES_FILE="$REPORTS_DIR/orphaned_entities_$TIMESTAMP.json"
ORPHANED_DEVICES_FILE="$REPORTS_DIR/orphaned_devices_$TIMESTAMP.json"
RECONCILIATION_FILE="$REPORTS_DIR/reconciliation_checklist_$TIMESTAMP.md"

# Find all entities with orphaned config entries
log_info "Discovering orphaned entities..."
ORPHANED_FILTER=""
for entry_id in "${ORPHANED_CONFIG_ENTRIES[@]}"; do
    ORPHANED_FILTER="$ORPHANED_FILTER.config_entry_id == \"$entry_id\" or "
done
ORPHANED_FILTER="${ORPHANED_FILTER% or }"

jq --argjson orphaned_entries "$(printf '%s\n' "${ORPHANED_CONFIG_ENTRIES[@]}" | jq -R . | jq -s .)" '
[.data.entities[] | select(
    .config_entry_id as $entry | 
    $orphaned_entries | index($entry) != null
)]
' "$STORAGE_DIR/core.entity_registry" > "$ORPHANED_ENTITIES_FILE"

ORPHANED_ENTITY_COUNT=$(jq length "$ORPHANED_ENTITIES_FILE")
log_info "Found $ORPHANED_ENTITY_COUNT orphaned entities"

# Find all devices that only have orphaned config entries
log_info "Discovering orphaned devices..."
jq --argjson orphaned_entries "$(printf '%s\n' "${ORPHANED_CONFIG_ENTRIES[@]}" | jq -R . | jq -s .)" '
[.data.devices[] | select(
    # Device is orphaned if ALL its config_entries are in the orphaned list
    ([.config_entries[] | . as $entry | $orphaned_entries | index($entry)] | all) and
    (.config_entries | length > 0)
)]
' "$STORAGE_DIR/core.device_registry" > "$ORPHANED_DEVICES_FILE"

ORPHANED_DEVICE_COUNT=$(jq length "$ORPHANED_DEVICES_FILE")
log_info "Found $ORPHANED_DEVICE_COUNT orphaned devices"

# Generate detailed report
cat > "$RECONCILIATION_FILE" << EOF
# Phantom Entity Cleanup Reconciliation Report
**Generated:** $TIMESTAMP  
**Orphaned Entities:** $ORPHANED_ENTITY_COUNT  
**Orphaned Devices:** $ORPHANED_DEVICE_COUNT  

## Orphaned Config Entries Being Removed
$(printf '- `%s`\n' "${ORPHANED_CONFIG_ENTRIES[@]}")

## Entities to be Removed (will need re-registration)
EOF

if [[ "$ORPHANED_ENTITY_COUNT" -gt 0 ]]; then
    echo "" >> "$RECONCILIATION_FILE"
    jq -r '.[] | "- `\(.entity_id)` (\(.platform)) - Device: `\(.device_id // "none")`"' "$ORPHANED_ENTITIES_FILE" >> "$RECONCILIATION_FILE"
fi

cat >> "$RECONCILIATION_FILE" << EOF

## Devices to be Removed
EOF

if [[ "$ORPHANED_DEVICE_COUNT" -gt 0 ]]; then
    echo "" >> "$RECONCILIATION_FILE"
    jq -r '.[] | "- `\(.id)` - \(.name // "Unknown") (\(.manufacturer // "Unknown"))"' "$ORPHANED_DEVICES_FILE" >> "$RECONCILIATION_FILE"
fi

cat >> "$RECONCILIATION_FILE" << EOF

## Post-Cleanup Steps

### 1. Start Home Assistant
\`\`\`bash
ha core start
# Wait for full startup, then check logs for any errors
\`\`\`

### 2. Re-register Mobile Apps
**On each device (ePhone UK, MacBook):**
1. Open Home Assistant Companion app
2. Log out or reset app connection
3. Log back in with your Home Assistant credentials
4. Allow all permissions when prompted
5. Verify new entities appear in **Settings → Devices & Services → Mobile App**

### 3. Rename New Entities to Canonical Names
The mobile apps will create new entities with likely different names (often with _2 suffix).
Use the Home Assistant UI to rename them back to the original entity_ids:

**Settings → Devices & Services → Mobile App → [Device] → [Entity] → Rename**

#### Expected Renames (update as needed after re-registration):
EOF

if [[ "$ORPHANED_ENTITY_COUNT" -gt 0 ]]; then
    echo "" >> "$RECONCILIATION_FILE"
    jq -r '.[] | "- New: `\(.entity_id)_new` → Rename to: `\(.entity_id)`"' "$ORPHANED_ENTITIES_FILE" >> "$RECONCILIATION_FILE"
fi

cat >> "$RECONCILIATION_FILE" << EOF

### 4. Verification Checklist
- [ ] All mobile device entities show proper integration info (not "status not provided")
- [ ] Entities are editable in the GUI
- [ ] Automations using these entities still work
- [ ] History graphs show continuity (if entity_ids match exactly)
- [ ] No phantom entities remain in entity registry

### 5. Rollback (if needed)
\`\`\`bash
ha core stop
cd $ROOT_CONFIG/.storage
cp $REPORTS_DIR/.storage_$TIMESTAMP/* .
ha core start
\`\`\`

## Files Modified
- \`core.entity_registry\` - Removed $ORPHANED_ENTITY_COUNT orphaned entities
- \`core.device_registry\` - Removed $ORPHANED_DEVICE_COUNT orphaned devices
- \`mobile_app\` - No changes (will be repopulated on re-registration)

## Backup Location
\`$REPORTS_DIR/.storage_$TIMESTAMP/\`
EOF

log_success "Analysis complete. Report: $RECONCILIATION_FILE"

# Display summary
log_info "=== CLEANUP SUMMARY ==="
log_info "Orphaned entities to remove: $ORPHANED_ENTITY_COUNT"
log_info "Orphaned devices to remove: $ORPHANED_DEVICE_COUNT"
log_info "Backup location: $REPORTS_DIR/.storage_$TIMESTAMP"

if [[ "$DRY_RUN" == true ]]; then
    log_info "=== DRY RUN COMPLETE ==="
    log_info "No changes made. Review the reconciliation report:"
    log_info "  $RECONCILIATION_FILE"
    log_info ""
    log_info "To execute the cleanup:"
    log_info "  ha core stop"
    log_info "  $0 --execute"
    exit 0
fi

# Phase 2: Execute cleanup
log_warn "=== EXECUTING CLEANUP ==="
log_warn "This will modify .storage files and remove orphaned entities/devices"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    log_info "Cleanup cancelled"
    exit 0
fi

log_info "Phase 2: Executing .storage cleanup"

# Create individual file backups
cp "$STORAGE_DIR/core.entity_registry" "$STORAGE_DIR/core.entity_registry.$TIMESTAMP.bak"
cp "$STORAGE_DIR/core.device_registry" "$STORAGE_DIR/core.device_registry.$TIMESTAMP.bak"

# Clean entity registry - remove entities with orphaned config entries
log_info "Cleaning entity registry..."
jq --argjson orphaned_entries "$(printf '%s\n' "${ORPHANED_CONFIG_ENTRIES[@]}" | jq -R . | jq -s .)" '
.data.entities |= map(
    select(
        .config_entry_id as $entry | 
        $orphaned_entries | index($entry) == null
    )
)
' "$STORAGE_DIR/core.entity_registry.$TIMESTAMP.bak" > "$STORAGE_DIR/core.entity_registry"

log_success "Entity registry cleaned - removed $ORPHANED_ENTITY_COUNT entities"

# Clean device registry - remove devices with only orphaned config entries
log_info "Cleaning device registry..."
jq --argjson orphaned_entries "$(printf '%s\n' "${ORPHANED_CONFIG_ENTRIES[@]}" | jq -R . | jq -s .)" '
.data.devices |= map(
    select(
        # Keep device if it has at least one non-orphaned config entry
        ([.config_entries[] | . as $entry | $orphaned_entries | index($entry) == null] | any) or
        (.config_entries | length == 0)
    )
)
' "$STORAGE_DIR/core.device_registry.$TIMESTAMP.bak" > "$STORAGE_DIR/core.device_registry"

log_success "Device registry cleaned - removed $ORPHANED_DEVICE_COUNT devices"

# Verify the cleanup worked
NEW_ENTITY_COUNT=$(jq '.data.entities | length' "$STORAGE_DIR/core.entity_registry")
NEW_DEVICE_COUNT=$(jq '.data.devices | length' "$STORAGE_DIR/core.device_registry")
OLD_ENTITY_COUNT=$(jq '.data.entities | length' "$STORAGE_DIR/core.entity_registry.$TIMESTAMP.bak")
OLD_DEVICE_COUNT=$(jq '.data.devices | length' "$STORAGE_DIR/core.device_registry.$TIMESTAMP.bak")

ENTITIES_REMOVED=$((OLD_ENTITY_COUNT - NEW_ENTITY_COUNT))
DEVICES_REMOVED=$((OLD_DEVICE_COUNT - NEW_DEVICE_COUNT))

log_success "=== CLEANUP COMPLETE ==="
log_success "Entities: $OLD_ENTITY_COUNT → $NEW_ENTITY_COUNT (removed $ENTITIES_REMOVED)"
log_success "Devices: $OLD_DEVICE_COUNT → $NEW_DEVICE_COUNT (removed $DEVICES_REMOVED)"

# Final instructions
log_info "=== NEXT STEPS ==="
log_info "1. Start Home Assistant: ha core start"
log_info "2. Re-register mobile apps (log out/in on each device)"
log_info "3. Follow reconciliation checklist: $RECONCILIATION_FILE"
log_info ""
log_info "Rollback if needed: cp $REPORTS_DIR/.storage_$TIMESTAMP/* $STORAGE_DIR/"

# Create a quick commit helper
cat > "$REPORTS_DIR/commit_cleanup_$TIMESTAMP.sh" << EOF
#!/bin/bash
cd "$ROOT_CONFIG"
git add hestia/reports/$DAY
git commit -m "docs(receipt): phantom entity cleanup $TIMESTAMP — offline .storage prune + mobile app re-reg

- Removed $ENTITIES_REMOVED orphaned entities
- Removed $DEVICES_REMOVED orphaned devices  
- Backup: hestia/reports/$DAY/.storage_$TIMESTAMP
- Next: mobile app re-registration required"
EOF
chmod +x "$REPORTS_DIR/commit_cleanup_$TIMESTAMP.sh"

log_info "Commit script created: $REPORTS_DIR/commit_cleanup_$TIMESTAMP.sh"
log_success "Phantom entity cleanup complete!"