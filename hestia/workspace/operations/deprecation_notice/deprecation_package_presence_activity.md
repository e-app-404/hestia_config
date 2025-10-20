## 🗑️ Deprecated Components

### package_presence_activity.yaml (Deprecated 2025-10-18)

**Status:** REPLACED by Room-DB Activity Tracking AppDaemon app

**Reason:** Eliminated 22 helper entities (input_datetime) by moving activity 
timestamps to SQLite database with richer metadata and cross-domain intelligence.

**Migration Path:**
1. ✅ New system operational (8 rooms tracked via AppDaemon)
2. ⏳ Old package marked DEPRECATED (safe to ignore)
3. ⏳ After 7 days: Remove input_datetime entities
4. ⏳ After 30 days: Delete deprecated package file

**Replacement Sensors:**
- Old: `input_datetime.bedroom_last_activity`
- New: `state_attr('sensor.room_configs_activity_tracking_dict', 'payload').bedroom.last_activity`

**Decay Sensors:**
- Old: `sensor.bedroom_minutes_since_activity`
- New: `sensor.bedroom_minutes_since_activity_v2`

**Files:**
- Deprecated: `/config/packages/package_presence_activity.yaml.DEPRECATED`
- Replacement: `/config/hestia/workspace/patches/appdaemon/activity_tracker.py`
- Templates: `/config/packages/room_database/activity_tracker_templates.yaml`
