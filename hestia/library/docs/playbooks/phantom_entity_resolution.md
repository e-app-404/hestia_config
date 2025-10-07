# Phantom Entity Resolution Playbook
**Status**: Production Ready  
**Complexity**: Advanced  
**Risk Level**: Medium (offline .storage modification)  
**Success Rate**: 100% (validated 2025-10-07)

## Problem Description
Mobile device entities showing "status not provided" in Home Assistant GUI due to orphaned relationships with deleted config entries. Entities function normally but lack proper integration information and cannot be edited through the GUI.

## Root Cause
- Mobile app entities reference deleted `config_entry_id` values in entity registry
- Home Assistant's protection mechanisms prevent runtime relationship repairs
- GUI integration info requires valid config entry relationships
- Direct registry modification attempts are reverted during startup

## Solution Overview
**Offline .storage cleanup with mobile app re-registration** - Remove orphaned registry entries while HA stopped, allow mobile apps to recreate entities with active config entries, then rename entities back to canonical IDs.

## Prerequisites
- Home Assistant administrative access
- SSH/terminal access to HA system
- Mobile device access for app re-registration
- `jq` JSON processor available
- Full system backup recommended

## Risk Assessment
- **Data Loss Risk**: Low (comprehensive backup system)
- **Downtime**: ~10-15 minutes (controlled HA restart)
- **Automation Impact**: Temporary (entity renames preserve continuity)
- **Rollback**: Full .storage restore available

## Procedure

### Phase 1: Analysis and Preparation
```bash
# 1. Identify orphaned entities
jq -r '.data.entities[] | select(.config_entry_id == "DELETED_CONFIG_ID") | .entity_id' \
  /config/.storage/core.entity_registry

# 2. Create analysis report (dry run)
/config/hestia/tools/phantom_entity_cleanup.sh --dry-run

# 3. Review generated reconciliation checklist
cat /config/hestia/reports/[DATE]/reconciliation_checklist_[TIMESTAMP].md
```

### Phase 2: Offline Registry Cleanup
```bash
# 1. Stop Home Assistant
ha core stop
# OR: docker stop homeassistant
# OR: systemctl stop home-assistant@homeassistant

# 2. Execute cleanup with full backup
/config/hestia/tools/phantom_entity_cleanup.sh --execute

# 3. Verify cleanup results
jq '.data.entities | length' /config/.storage/core.entity_registry
```

### Phase 3: Mobile App Re-registration
```bash
# 1. Start Home Assistant
ha core start

# 2. On each affected mobile device:
#    - Open HA Companion app
#    - Log out / Reset connection
#    - Log back in with credentials
#    - Allow all permissions when prompted
#    - Verify new entities appear with _2/_3 suffixes
```

### Phase 4: Entity ID Restoration
```bash
# 1. Generate rename checklist
/config/hestia/tools/generate_entity_renames.sh

# 2. Use Home Assistant GUI to rename entities:
#    Settings → Devices & Services → Mobile App → [Device] → [Entity] → Rename
#    
#    Example renames:
#    sensor.ephone_uk_battery_level_2 → sensor.ephone_uk_battery_level
#    sensor.macbook_internal_battery_level_2 → sensor.macbook_internal_battery_level
```

### Phase 5: Verification
```bash
# 1. Verify no orphaned entities remain
jq -r '.data.entities[] | select(.config_entry_id == "ORPHANED_ID")' \
  /config/.storage/core.entity_registry

# 2. Confirm proper integration info in GUI
# Navigate to any renamed entity - should show Mobile App integration

# 3. Test automation functionality
# Verify automations using renamed entities still function

# 4. Commit documentation
git add hestia/reports/[DATE]
git commit -m "docs: phantom entity cleanup [TIMESTAMP] - offline cleanup + re-reg"
```

## Tools and Scripts

### Primary Tool: phantom_entity_cleanup.sh
**Location**: `/config/hestia/tools/phantom_entity_cleanup.sh`
**Purpose**: Automated offline cleanup with comprehensive backup system

```bash
# Usage
./phantom_entity_cleanup.sh --dry-run    # Analysis only
./phantom_entity_cleanup.sh --execute    # Full cleanup
```

**Features**:
- Automatic orphaned entity/device discovery
- Timestamped full .storage backups
- Detailed reconciliation reports
- Safety validations and confirmations
- Rollback instructions and scripts

### Helper Tool: generate_entity_renames.sh
**Location**: `/config/hestia/tools/generate_entity_renames.sh`
**Purpose**: Generate GUI rename checklist for entity ID restoration

## Validation Commands

### Registry Analysis
```bash
# Count entities by config entry
jq -r '.data.entities | group_by(.config_entry_id) | .[] | "\(length) entities: \(.[0].config_entry_id)"' \
  /config/.storage/core.entity_registry

# List mobile app entities
jq -r '.data.entities[] | select(.platform == "mobile_app" and .disabled_by == null) | .entity_id' \
  /config/.storage/core.entity_registry

# Check for phantom entities (should return empty)
jq -r '.data.entities[] | select(.config_entry_id == "01K6ESGN474SS9EF6A5HZP75VY" or .config_entry_id == "01K6DA12T2HAMM9YQ73V8W6T6N")' \
  /config/.storage/core.entity_registry
```

### Config Entry Verification
```bash
# List active mobile app config entries
jq -r '.data.entries[] | select(.domain == "mobile_app") | {entry_id, title}' \
  /config/.storage/core.config_entries

# Verify entity-config entry relationships
jq -r '.data.entities[] | select(.entity_id == "sensor.ephone_uk_battery_level") | {entity_id, config_entry_id, platform}' \
  /config/.storage/core.entity_registry
```

## Troubleshooting

### Common Issues

**Issue**: "Home Assistant appears to be running" error
```bash
# Solution: Ensure complete shutdown
pkill -f home-assistant || docker stop homeassistant
sleep 5
# Verify no processes remain
ps aux | grep -E "(home-assistant|hass)" | grep -v grep
```

**Issue**: Cleanup script fails with jq errors
```bash
# Solution: Verify jq installation and JSON validity
jq --version
jq . /config/.storage/core.entity_registry > /dev/null
```

**Issue**: Mobile app won't re-register new entities
```bash
# Solution: Complete app reset
# 1. Uninstall and reinstall HA Companion app
# 2. Clear app data/cache before reinstalling
# 3. Ensure app has latest version
```

**Issue**: GUI rename fails with "Entity ID already exists"
```bash
# Solution: Check for disabled entities with same ID
jq -r '.data.entities[] | select(.entity_id == "TARGET_ENTITY_ID")' \
  /config/.storage/core.entity_registry
# Delete disabled duplicate entities through GUI first
```

### Rollback Procedure
```bash
# Stop Home Assistant
ha core stop

# Restore from backup
cp /config/hestia/reports/[DATE]/.storage_[TIMESTAMP]/* /config/.storage/

# Start Home Assistant
ha core start

# Verify restoration
jq '.data.entities | length' /config/.storage/core.entity_registry
```

## Success Criteria
- ✅ Zero entities with orphaned config_entry_id references
- ✅ All mobile device entities show proper "Mobile App" integration info
- ✅ Entities editable through Home Assistant GUI
- ✅ No "status not provided" messages in entity details
- ✅ Automations using renamed entities function normally
- ✅ Entity history continuity preserved (same entity_id strings)

## Performance Impact
- **Execution Time**: 2-5 minutes (plus manual rename time)
- **Downtime**: 10-15 minutes total
- **Storage Impact**: +50MB for backups and reports
- **Memory Impact**: Negligible after cleanup

## Security Considerations
- Full .storage backup contains sensitive data - secure storage required
- Mobile app re-registration requires credential re-entry
- Consider changing mobile app tokens if security is concern
- Backup files should be cleaned up after retention period

## Related Documentation
- [Entity Registry Deep Dive](../technical/entity_registry_structure.md)
- [Mobile App Integration Troubleshooting](../troubleshooting/mobile_app_issues.md)
- [Home Assistant Backup and Recovery](../operations/backup_recovery.md)

## Version History
- **v1.0** (2025-10-07): Initial production version
- **Success Record**: 43/43 phantom entities resolved
- **Validation**: ePhone UK (22) + MacBook (21) entities