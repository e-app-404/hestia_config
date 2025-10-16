# DEPRECATED: AppDaemon Configuration Directory

⚠️ **DEPRECATION NOTICE** ⚠️

This directory `/config/appdaemon/` is **DEPRECATED** as of October 16, 2025.

## New Canonical Location

**All AppDaemon configurations have moved to:**
```
/Volumes/addon_configs/a0d7b954_appdaemon/
```

**From within the AppDaemon container, this is accessible as:**
```
/config/
```

**In workspace documentation, reference as:**
```
/addon_configs/a0d7b954_appdaemon/
```

## Migration Timeline

- **Deprecation Date**: October 16, 2025
- **Removal Date**: November 1, 2025 (2 weeks)
- **Current Status**: Legacy directory maintained for compatibility only

## What Changed

1. **apps.yaml**: Now located at `/addon_configs/a0d7b954_appdaemon/apps/apps.yaml`
2. **room_db_updater.py**: Now located at `/addon_configs/a0d7b954_appdaemon/apps/room_db_updater.py`
3. **All configurations**: Moved to canonical add-on configuration directory

## For Machine Operators

**DO NOT** modify files in this directory. All changes should be made to the canonical location:

```bash
# Navigate to canonical AppDaemon configuration
cd /Volumes/addon_configs/a0d7b954_appdaemon/

# Edit configurations
vim apps/apps.yaml
vim apps/room_db_updater.py

# Restart AppDaemon add-on to apply changes
```

## References Updated

The following files have been updated to reference the canonical location:
- `/config/hestia/config/index/appdaemon_index.yaml`
- ADR-0028 (AppDaemon & Room-DB canonicalization)
- All workspace documentation and scripts

## Questions?

See the migration documentation in ADR-0028 or consult the maintenance log session `session_2025_10_16_appdaemon_canonical_migration`.