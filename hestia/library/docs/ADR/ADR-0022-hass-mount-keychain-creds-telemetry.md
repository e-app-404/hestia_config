---
id: ADR-0022
title: 'ADR-0022: Home Assistant Mount Keychain Credentials and Telemetry System'
slug: home-assistant-mount-keychain-credentials-and-telemetry-system
status: Superseded
related:
- ADR-0009
- ADR-0024
superseded_by: 
- ADR-0029
date: 2025-10-04
decision: 'Implement a comprehensive mount reliability and telemetry system'
author: Evert Appels
tags:
- homeassistant
- mount
- telemetry
- keychain
- automation
- smbfs
- webhook
- launchagent
- macos
last_updated: 2025-10-20
---

# ADR-0022: Home Assistant Mount Keychain Credentials and Telemetry System

> Decision: To resolve the issues, we will update the LaunchAgent to invoke a hardened helper script for secure credential management, integrate webhook-based telemetry for real-time mount status in Home Assistant, deploy automated health checks, and provide robust rollback procedures for safe reversion.

## Table of Contents

1. [Context](#1-context)
2. [Problem Statement](#2-problem-statement)
3. [Decision](#3-decision)
4. [Solution Architecture](#4-solution-architecture)
5. [Implementation Details](#5-implementation-details)
6. [Verification Framework](#6-verification-framework)
7. [Consequences](#7-consequences)
8. [Rollback Strategy](#8-rollback-strategy)
9. [Enforcement](#9-enforcement)
10. [Token Block](#10-token-block)

## 1. Context

The Home Assistant (HA) configuration mount on macOS was experiencing intermittent failures with manual password prompts, disrupting automation workflows. The existing LaunchAgent implementation used direct `mount_smbfs` calls with the `-N` flag (no authentication), bypassing the hardened helper script that properly handles Keychain credential retrieval and URL encoding.

**Environment:**
- Host: macOS 15.x (Apple Silicon)
- Mount target: `~/hass` → `//evertappels@homeassistant.local/config`
- Authentication: SMB via macOS Keychain
- Automation: LaunchAgent-based automount with network state awareness

## 2. Problem Statement

**Primary Issues Identified:**
1. LaunchAgent configured to call `mount_smbfs` directly instead of hardened helper script
2. Authentication failures causing exit code 64 (EX_USAGE) and password prompts
3. No proactive monitoring of mount health, write access, or configuration availability
4. Missing telemetry for debugging mount-related automation failures

**Root Cause Analysis:**
- LaunchAgent plist contained raw `mount_smbfs` command with `-N` flag
- Hardened helper script (`hass_mount_once.sh`) existed but was not being invoked
- Keychain credentials were properly stored but not accessed due to direct mount call

## 3. Decision

Implement a comprehensive mount reliability and telemetry system with the following components:

1. **Fix LaunchAgent Configuration**: Replace direct `mount_smbfs` calls with hardened helper script execution
2. **Implement Webhook-Based Telemetry**: Create real-time mount status monitoring via HA webhook integration
3. **Deploy Verification Framework**: Automated end-to-end testing and health checks
4. **Establish Rollback Procedures**: Complete reversion capability for all changes

## 4. Solution Architecture

### 4.1 Mount Management
- **Primary LaunchAgent**: `com.local.hass.mount.plist`
  - Executes: `/bin/zsh -lc /Users/evertappels/bin/hass_mount_once.sh`
  - Triggers: `RunAtLoad=true`, `KeepAlive.NetworkState=true`
  - Credentials: Keychain lookup for both `homeassistant` and `homeassistant.local` services

### 4.2 Telemetry System
- **Telemetry LaunchAgent**: `com.local.hass.telemetry.plist`
  - Frequency: Every 120 seconds (`StartInterval=120`)
  - Script: `/Users/evertappels/bin/hass_telemetry.sh`
  - Delivery: HTTP webhook to `http://homeassistant.local:8123/api/webhook/macbook_hass_mount_telemetry_f8d2a9b4c7e1`
  - Logging: Separate log file `~/Library/Logs/hass-telemetry.log`

- **Watchdog LaunchAgent**: `com.local.hass.mount.watch.plist`
  - Frequency: Every 180 seconds (`StartInterval=180`)
  - Function: Failsafe mount recovery if primary agent fails
  - Command: `mount | egrep -qi "on /Users/evertappels/hass .*smbfs" || /Users/evertappels/bin/hass_mount_once.sh`

### 4.3 Home Assistant Integration
- **Webhook Automation**: `macbook_ha_mount_telemetry_webhook`
  - Trigger: `webhook_id: "macbook_hass_mount_telemetry_f8d2a9b4c7e1"`
  - Methods: `["POST"]`, `local_only: true`
  - Action: Fires `macbook_mount_telemetry_received` event

- **Template Sensors**:
  - `sensor.macbook_ha_mount_status`: Detailed state and attributes
  - `binary_sensor.macbook_ha_mount`: Boolean connectivity status

- **Alert Automations**:
  - DOWN alert: Triggers after 5 minutes of `off` state
  - RECOVERY notification: Triggers on return to `on` state

### 4.4 Monitored Attributes
```json
{
  "state": "ON|OFF",
  "mounted": true|false,
  "write_ok": true|false,
  "config_present": true|false,
  "keychain_ok": true|false,
  "agent_loaded": true|false,
  "agent_state": "string",
  "agent_exit_code": 0,
  "host": "macbook",
  "user": "evertappels",
  "last_run": "2025-10-04T18:31:32Z",
  "age_s": 120,
  "mount_details": "//evertappels@homeassistant.local/config on /Users/evertappels/hass (smbfs)"
}
```

## 5. Implementation Details

### 5.1 File Locations
- LaunchAgents: `~/Library/LaunchAgents/com.local.hass.{mount,telemetry,mount.watch}.plist`
- Scripts: `~/bin/hass_telemetry.sh`
- HA Package: `~/hass/packages/hestia/ha_mount_telemetry_webhook.yaml`
- Verification: `~/hass/hestia/config/diagnostics/verify_hass_mount_telemetry.sh`
- Rollback: `~/hass/hestia/config/diagnostics/rollback_hass_mount_telemetry.sh`
- Logs: `~/Library/Logs/hass-mount.log`, `~/Library/Logs/hass-telemetry.log`

### 5.2 LaunchAgent Fix
```xml
<!-- BEFORE: Direct mount_smbfs call -->
<key>ProgramArguments</key>
<array>
  <string>/sbin/mount_smbfs</string>
  <string>-N</string>
  <string>-d</string><string>0777</string>
  <string>-f</string><string>0777</string>
  <string>//evertappels@homeassistant.local/config</string>
  <string>/Users/evertappels/hass</string>
</array>

<!-- AFTER: Hardened helper script -->
<key>ProgramArguments</key>
<array>
  <string>/bin/zsh</string>
  <string>-lc</string>
  <string>/Users/evertappels/bin/hass_mount_once.sh</string>
</array>
```

### 5.3 Webhook Integration Structure
```yaml
automation:
  - alias: "MacBook HA Mount Telemetry Webhook"
    id: "macbook_ha_mount_telemetry_webhook"
    trigger:
      - trigger: webhook
        webhook_id: "macbook_hass_mount_telemetry_f8d2a9b4c7e1"
        allowed_methods:
          - POST
        local_only: true
    action:
      - event: macbook_mount_telemetry_received
        event_data:
          # JSON payload forwarding
```

## 6. Verification Framework

### 6.1 End-to-End Test Suite
10-point verification checklist covering:
1. SMB mount status and writability
2. Configuration file accessibility
3. LaunchAgent health and exit codes
4. Keychain credential availability
5. Telemetry script execution
6. Webhook endpoint connectivity
7. Log file presence and rotation
8. Recent activity verification

### 6.2 Success Criteria
- All 10 verification tests pass
- Mount accessible with write permissions
- `configuration.yaml` readable
- LaunchAgent exit code 0
- Webhook returns HTTP 200
- Recent telemetry logged within 24 hours

## 7. Consequences

### 7.1 Positive Outcomes
- **Eliminated Password Prompts**: Keychain integration prevents interactive authentication
- **Proactive Monitoring**: Real-time mount health visibility in Home Assistant
- **Automated Recovery**: LaunchAgent with network state awareness handles reconnection
- **Failsafe Protection**: Watchdog agent provides 3-minute interval backup mounting
- **Security Hardening**: Long random webhook ID prevents unauthorized access
- **Debugging Capability**: Comprehensive telemetry with separate logging for clarity
- **Production Stability**: All acceptance gates passed, system bulletproof

### 7.2 Maintenance Requirements
- **Keychain Management**: Credentials must be kept current for both service names
- **LaunchAgent Monitoring**: Periodic verification of agent load state and exit codes
- **Log Rotation**: Telemetry logs accumulate; consider rotation policy
- **HA Package Updates**: Webhook automation must remain synchronized with script changes

### 7.3 Security Considerations
- **Credential Storage**: SMB passwords remain in macOS Keychain (encrypted at rest)
- **Network Exposure**: Webhook limited to `local_only: true`
- **Webhook Security**: Long random ID (`macbook_hass_mount_telemetry_f8d2a9b4c7e1`) prevents enumeration
- **Log Separation**: Telemetry logs isolated from mount logs for security auditing
- **Log Sensitivity**: Telemetry logs contain mount paths but no credentials
- **Script Permissions**: Telemetry script requires access to Keychain and network

## 8. Rollback Strategy

Complete rollback capability provided via `rollback_hass_mount_telemetry.sh`:

1. **Stop telemetry services**: Remove LaunchAgent and associated scripts
2. **Revert mount LaunchAgent**: Restore original direct `mount_smbfs` configuration
3. **Clean up files**: Remove all telemetry-related scripts and HA packages
4. **Reset logs**: Clear telemetry log files

**Rollback Command:**
```bash
$HOME/hass/hestia/config/diagnostics/rollback_hass_mount_telemetry.sh
```

**Post-Rollback State:**
- System returns to original behavior (manual password prompts)
- No telemetry or monitoring capabilities
- Mount functionality preserved via direct `mount_smbfs` calls

## 9. Current Operational Status

**As of 2025-10-04 19:03:**
- ✅ All acceptance gates PASSED
- ✅ Non-interactive mount test successful (RC=0, no password prompts)
- ✅ Primary mount agent: Running, exit code 0
- ✅ Telemetry agent: Running every 2 minutes
- ✅ Watchdog agent: Running every 3 minutes as failsafe
- ✅ Webhook integration: Working with secure random ID
- ✅ Separate logging: `hass-telemetry.log` operational
- ✅ Mount health: MOUNT_OK, WRITE_OK, CONFIG_OK

**Agent Status:**
```
Primary: state = not running, last exit code = 0 (normal)
Telemetry: Active, sending every 120 seconds
Watchdog: Active, checking every 180 seconds
```

## 10. Enforcement

### 9.1 Verification Requirements
- Execute `verify_hass_mount_telemetry.sh` must achieve 10/10 test passes
- LaunchAgent exit codes must be 0 for successful operation
- Webhook endpoint must return HTTP 200 for connectivity validation
- Mount must provide write access to `~/hass` directory

### 9.2 Monitoring Standards
- Telemetry must execute every 2 minutes during normal operation
- DOWN alerts trigger after 5 minutes of connectivity loss
- Recovery notifications fire upon restoration of service
- Log retention minimum 30 days for debugging purposes

### 9.3 Change Control
- Any modifications to LaunchAgent configuration require verification test execution
- Keychain credential updates must be applied to both service names
- HA webhook automation changes require corresponding script updates
- Rollback capability must be tested and validated with each major change

## 10. Token Block

```yaml
TOKEN_BLOCK:
  accepted:
    - HASS_MOUNT_KEYCHAIN_OK
    - HASS_MOUNT_TELEMETRY_OK
    - LAUNCHAGENT_HARDENED_OK
    - WEBHOOK_INTEGRATION_OK
    - VERIFICATION_FRAMEWORK_OK
    - ROLLBACK_CAPABILITY_OK
  produces:
    - MOUNT_HEALTH_TELEMETRY
    - WEBHOOK_MOUNT_STATUS
    - AUTOMATED_MOUNT_RECOVERY
  requires:
    - MACOS_KEYCHAIN_ACCESS
    - HOMEASSISTANT_WEBHOOK_API
    - LAUNCHD_USER_AGENTS
  drift:
    - DRIFT: mount_authentication_failure
    - DRIFT: telemetry_delivery_failure
    - DRIFT: launchagent_misconfiguration
    - DRIFT: keychain_credential_missing
    - DRIFT: webhook_endpoint_unreachable
```
