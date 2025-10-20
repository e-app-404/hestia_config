# AppDaemon Workspace Patches

> ⚠️ **IMPORTANT**: This is NOT the AppDaemon runtime directory!

## Purpose

This directory contains development patches and working files for AppDaemon applications. These files are **not** automatically loaded by AppDaemon and must be manually deployed to their final destinations.

## File Deployment

### Active AppDaemon Files
The following files need to be copied to the AppDaemon addon configuration directory:

- `room_db_updater.py` → `/addon_configs/a0d7b954_appdaemon/apps/`
- `valetudo_default_activity.py` → `/addon_configs/a0d7b954_appdaemon/apps/`

### Configuration Files
- `area_mapping.yaml` → `/config/www/area_mapping.yaml` (web-accessible)

### Missing Files
If any required files are missing from this directory, they may need to be recreated from their `-copy.py` backups or from the patch plan documentation.

## Deployment Process

1. **Test locally** - Validate syntax and logic in this workspace
2. **Deploy to addon** - Copy files to `/addon_configs/a0d7b954_appdaemon/apps/`
3. **Restart AppDaemon** - Reload the addon to pick up changes
4. **Monitor logs** - Check AppDaemon logs for successful loading

## File Structure

```
/config/hestia/workspace/patches/appdaemon/  ← YOU ARE HERE (workspace)
├── room_db_updater.py                      ← Active development file
├── valetudo_default_activity.py            ← Active development file
├── area_mapping.yaml                       ← Area configuration
├── *-copy.py                               ← Backup files
└── v3.1_patch_plan.md                      ← Development documentation

/addon_configs/a0d7b954_appdaemon/          ← RUNTIME DESTINATION
├── appdaemon.yaml                          ← AppDaemon configuration
└── apps/                                   ← Where .py files go
    ├── apps.yaml                           ← App registration
    ├── room_db_updater.py                  ← Deploy here
    └── valetudo_default_activity.py        ← Deploy here
```

## Safety Notes

- Always backup existing files before deployment
- Test changes in this workspace before deploying
- The AppDaemon addon must be restarted after file changes
- Monitor AppDaemon logs for errors after deployment

## Related Documentation

- See `v3.1_patch_plan.md` for development context and implementation details
- Check `/config/packages/room_database/` for related Home Assistant integrations
- Review `/config/www/area_mapping.yaml` for area configuration dependencies
