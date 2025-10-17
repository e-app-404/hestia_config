---
description: "Systematic debugging and validation of AppDaemon room_db endpoint configuration with binary validation gates"
mode: "agent"
tools: ["file_system", "terminal", "search"]
model: "gpt-4o"
---

# Debug AppDaemon Room Database Endpoints - Systematic Validation

## Mission

Execute systematic debugging of AppDaemon room_db_updater endpoint configuration failures using binary validation gates and automated correction. Identify root cause of 404 errors and non-appearing REST sensors through comprehensive validation protocol.

## Scope & Preconditions

**Target Components:**
- AppDaemon room_db_updater app endpoint registration
- Home Assistant REST sensor configuration  
- REST command configuration
- Network connectivity validation
- Configuration syntax validation

**Required Files:**
- `/config/packages/room_database/room_db_src.yaml`
- `/config/packages/room_database/room_db_diag.yaml`
- `/config/appdaemon/apps/room_db_updater.py`
- `/Volumes/addon_configs/a0d7b954_appdaemon/apps/room_db_updater.py`

## Validation Gates Protocol

Execute each validation gate and provide binary ACK status: `PASS` or `FAIL`

### Gate 1: AppDaemon App Status Validation
**Command:** Check AppDaemon logs for room_db_updater initialization
**Validation Token:** `APPDAEMON_APP_INIT`
**Expected Output:**
```
INFO room_db_updater: RoomDbUpdater initialized
INFO room_db_updater: Test endpoint registered: /api/app/room_db_updater/test
```
**ACK Required:** `APPDAEMON_APP_INIT: [PASS|FAIL]`

### Gate 2: Endpoint Registration Validation  
**Command:** Verify endpoint registration logs
**Validation Token:** `ENDPOINT_REGISTRATION`
**Expected Output:**
```
INFO room_db_updater: Health endpoint registered with name: health
INFO room_db_updater: Update_config endpoint registered with name: update_config
```
**ACK Required:** `ENDPOINT_REGISTRATION: [PASS|FAIL]`

### Gate 3: Network Connectivity Validation
**Command:** Execute shell_command.test_appdaemon_endpoints
**Validation Token:** `NETWORK_CONNECTIVITY`
**Expected Output:** At least one successful HTTP response (not "FAILED")
**ACK Required:** `NETWORK_CONNECTIVITY: [PASS|FAIL]`

### Gate 4: REST Sensor Configuration Validation
**Command:** Check Home Assistant configuration validation
**Validation Token:** `REST_SENSOR_CONFIG`
**Expected Output:** No configuration errors for REST sensors
**ACK Required:** `REST_SENSOR_CONFIG: [PASS|FAIL]`

### Gate 5: Entity Discovery Validation
**Command:** Verify REST sensor entities exist in Home Assistant
**Validation Token:** `ENTITY_DISCOVERY`
**Expected Entities:**
- `sensor.appdaemon_health_raw`
- `sensor.appdaemon_test_raw`
- `sensor.appdaemon_health_direct_test`
**ACK Required:** `ENTITY_DISCOVERY: [PASS|FAIL]`

### Gate 6: Endpoint Response Validation
**Command:** Test direct endpoint access via REST commands
**Validation Token:** `ENDPOINT_RESPONSE`
**Expected Output:** HTTP 200 responses with JSON data
**ACK Required:** `ENDPOINT_RESPONSE: [PASS|FAIL]`

## Workflow

### Phase 1: Baseline Validation
1. **Execute all validation gates** in sequence
2. **Document ACK status** for each gate  
3. **Identify failure point** - first FAIL gate indicates root cause area
4. **Generate failure analysis** with specific remediation steps

### Phase 2: Configuration Correction
Based on failure pattern, execute systematic corrections:

**If APPDAEMON_APP_INIT: FAIL**
- Check AppDaemon addon status
- Validate apps.yaml configuration  
- Verify Python code syntax
- Restart AppDaemon addon

**If ENDPOINT_REGISTRATION: FAIL**
- Review register_endpoint() calls in room_db_updater.py
- Validate endpoint naming conventions
- Check for registration errors in logs
- Update canonical and workspace copies

**If NETWORK_CONNECTIVITY: FAIL**
- Test different hostname patterns (localhost, 127.0.0.1)
- Validate port accessibility  
- Check AppDaemon HTTP server status
- Test internal vs external network access

**If REST_SENSOR_CONFIG: FAIL**
- Validate YAML syntax in room_db_diag.yaml
- Check REST integration documentation compliance
- Fix sensor configuration structure
- Validate template syntax

**If ENTITY_DISCOVERY: FAIL**
- Reload Home Assistant configuration
- Check integration logs for REST sensor creation
- Validate unique sensor names
- Force entity refresh

**If ENDPOINT_RESPONSE: FAIL**
- Test individual endpoint URLs manually
- Check AppDaemon API authentication
- Validate JSON response format
- Test different HTTP methods

### Phase 3: Automated Validation
After corrections:
1. **Re-execute all validation gates**
2. **Confirm all ACKs are PASS**
3. **Execute comprehensive endpoint test**
4. **Generate validation report**

## Output Expectations

### Validation Gate Summary
```
VALIDATION GATE RESULTS:
APPDAEMON_APP_INIT: [PASS|FAIL]
ENDPOINT_REGISTRATION: [PASS|FAIL]  
NETWORK_CONNECTIVITY: [PASS|FAIL]
REST_SENSOR_CONFIG: [PASS|FAIL]
ENTITY_DISCOVERY: [PASS|FAIL]
ENDPOINT_RESPONSE: [PASS|FAIL]

OVERALL STATUS: [PASS|FAIL]
FAILURE POINT: [Gate X] (if applicable)
```

### Remediation Report
- **Root cause analysis** based on failure pattern
- **Specific configuration fixes** applied
- **File modifications** with before/after comparisons
- **Verification commands** to confirm resolution

### Success Criteria
- All validation gates return `PASS`
- REST sensors appear in Home Assistant
- Endpoint responses return HTTP 200 with valid JSON
- REST commands execute successfully
- No configuration errors in logs

## Quality Assurance

### Pre-Execution Checklist
- [ ] AppDaemon addon is running
- [ ] Home Assistant is accessible
- [ ] Configuration files exist and are readable
- [ ] Shell commands are executable
- [ ] Network connectivity to localhost:5050 is available

### Post-Execution Validation
- [ ] Execute `rest_command.room_db_health` returns HTTP 200
- [ ] Execute `rest_command.room_db_test` returns HTTP 200  
- [ ] Sensors show valid states (not "unavailable" or "unknown")
- [ ] Configuration validation shows no errors
- [ ] AppDaemon logs show no endpoint-related errors

### Rollback Procedures
- Backup all configuration files before modifications
- Document original configurations for restoration
- Provide rollback commands if validation fails
- Ensure system remains stable during debugging process

## Security & Compliance

- Use localhost/127.0.0.1 for internal network testing only
- No external network exposure of debug endpoints
- Validate all configuration changes before applying
- Follow ADR-0027 file writing governance with atomic operations
- Document all changes for audit trail

## Testing Instructions

After successful validation, execute comprehensive testing:

1. **REST Command Test:**
```yaml
action: rest_command.room_db_health
data: {}
```

2. **Endpoint Discovery Test:**
```yaml  
action: shell_command.test_appdaemon_endpoints
data: {}
```

3. **Sensor State Verification:**
Check states of diagnostic sensors for valid responses

4. **Integration Validation:**
Verify room database functionality end-to-end

Execute this prompt systematically to achieve complete resolution of room_db endpoint configuration issues with binary validation confirmation at each step.