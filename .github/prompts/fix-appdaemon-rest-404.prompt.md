---
mode: "agent"
model: "Claude Sonnet 4"
description: "Diagnose and fix AppDaemon REST endpoint 404 errors for room_db integration"
tools: ["edit", "search", "runCommands", "runTasks", "problems"]
---

# Fix AppDaemon REST Endpoint 404 Errors

Diagnose and resolve 404 "App Not Found" errors in Home Assistant + AppDaemon room_db SQL integration where REST commands fail to reach registered endpoints.

## Problem Context

- **Symptoms**: REST commands `room_db_health` and `room_db_update_config` return 404
- **Integration**: AppDaemon app `room_db_updater.py` with HTTP API endpoints
- **Current URLs**: `http://a0d7b954-appdaemon:5050/api/app/room_db_updater/*`
- **Root Cause**: Mismatch between endpoint registration names and expected URL paths

## Investigation Points

### 1. Endpoint Registration Analysis

Examine `room_db_updater.py` endpoint registration:

```python
# Current registration (likely incorrect)
self.register_endpoint(self.update_config, "room_db/update_config")
self.register_endpoint(self.health_check, "room_db/health")
```

### 2. URL Pattern Validation

AppDaemon URL structure: `/api/app/<app_name>/<endpoint_name>`

- **App name**: `room_db_updater` (from apps.yaml)
- **Expected endpoints**: Simple names without prefixes/slashes
- **Current URLs**: May include incorrect prefixes

### 3. Configuration Files to Check

- `room_db_updater.py` - Endpoint registration methods
- `package_room_database.yaml` - REST command URL definitions
- `apps.yaml` - AppDaemon app configuration
- `appdaemon.yaml` - Global AppDaemon settings

## Required Fixes

### Fix 1: Standardize Endpoint Names

Update `room_db_updater.py` to use simple endpoint names:

```python
# Change from:
self.register_endpoint(self.update_config, "room_db/update_config")
self.register_endpoint(self.health_check, "room_db/health")

# To:
self.register_endpoint(self.health_check, "health")
self.register_endpoint(self.update_config, "update_config")
```

### Fix 2: Update REST Command URLs

Update `package_room_database.yaml` REST command URLs to match:

```yaml
# Change from:
url: "http://a0d7b954-appdaemon:5050/api/app/room_db_updater/room_db_health"
url: "http://a0d7b954-appdaemon:5050/api/app/room_db_updater/room_db_update_config"

# To:
url: "http://a0d7b954-appdaemon:5050/api/app/room_db_updater/health"
url: "http://a0d7b954-appdaemon:5050/api/app/room_db_updater/update_config"
```

### Fix 3: Add Diagnostic Logging

Enhance endpoint registration with verbose logging:

```python
self.log("Registering health endpoint")
self.register_endpoint(self.health_check, "health")
self.log("Health endpoint registered at /api/app/room_db_updater/health")

self.log("Registering update_config endpoint")
self.register_endpoint(self.update_config, "update_config")
self.log("Update endpoint registered at /api/app/room_db_updater/update_config")
```

## Validation Steps

### 1. AppDaemon Restart

```bash
ha addons restart a0d7b954_appdaemon
```

### 2. Log Verification

Check AppDaemon logs for successful registration:

```
INFO room_db_updater: Registering health endpoint
INFO room_db_updater: Health endpoint registered at /api/app/room_db_updater/health
INFO room_db_updater: Registering update_config endpoint
INFO room_db_updater: Update endpoint registered at /api/app/room_db_updater/update_config
INFO room_db_updater: RoomDbUpdater initialized
```

### 3. Health Check Test

```yaml
service: rest_command.room_db_health
data: {}
```

**Expected**: Status 200, JSON response with `"status": "healthy"`

### 4. Update Config Test

```yaml
service: rest_command.room_db_update_config
data:
  room_id: bedroom
  domain: motion_lighting
  config_data:
    timeout: 999
    bypass: false
  schema_expected: 1
```

**Expected**: Status 200, successful database update

### 5. Template Verification

```jinja2
{% set payload = state_attr('sensor.room_configs_motion_lighting_dict', 'payload') %}
Bedroom timeout: {{ payload.bedroom.timeout }}
```

**Expected**: `Bedroom timeout: 999`

## Troubleshooting

### Direct HTTP Test

Bypass Home Assistant and test AppDaemon directly:

```bash
curl -v http://a0d7b954-appdaemon:5050/api/app/room_db_updater/health
```

**Expected**: JSON response with status and database info

### Common Patterns

- **AppDaemon endpoint registration**: Use simple names without slashes
- **URL construction**: `/api/app/<app_name>/<simple_endpoint_name>`
- **Home Assistant integration**: REST command URLs must match exactly

### Error Indicators

- **404 errors**: Endpoint name mismatch between registration and URL
- **No startup logs**: App initialization failure
- **Connection refused**: AppDaemon service not running

## Success Criteria

- [ ] AppDaemon logs show successful endpoint registration
- [ ] Health check REST command returns 200 status
- [ ] Update config REST command returns 200 status
- [ ] Database updates reflect in SQL sensor templates
- [ ] No 404 errors in Home Assistant logs
- [ ] Room configuration changes propagate to motion lighting automations

## Root Cause Summary

AppDaemon `register_endpoint()` expects simple endpoint names without prefixes. The URL path is automatically constructed as `/api/app/<app_name>/<endpoint_name>`. Using names like `"room_db/health"` or `"room_db_update_config"` creates mismatched paths that result in 404 errors.

**Solution**: Use simple names (`"health"`, `"update_config"`) and update corresponding REST command URLs to match the auto-generated paths.
