---
title: "Home Assistant Automount Playbook"
date: 2025-10-02
authors:
  - "e-app-404"
status: Active
related:
  - "ADR-0016: Canonical HA edit root & non-interactive SMB mount"
  - "ha_smb_mount.md: SMB Mount Operations Guide"
  - LaunchAgent Configurations: ["com.local.hass.mount.watch.plist", "com.local.hass.mount.plist"]
  - Local scripts: ["hass_mount_once.sh", "hass_mount_retry.sh"]
  - Diagnostic scripts: ["hestia/tools/utils/mount/generate_hass_mount_diagnostics.sh"]
tags: ["automation","smb-mount", "launchagent", "macos", "playbook"]
---

# Home Assistant Automount Playbook

> Update • 2025-10-18
> This playbook now aligns with ADR-0024 canonical paths and the hardened telemetry pipeline:
> - Telemetry sender script: `~/bin/hass_telemetry.sh` (single source of truth)
> - LaunchAgent label: `com.local.hass.telemetry` with `StartInterval=120`
> - Environment: `HA_MOUNT=/config` for canonical path semantics while still mounting at `~/hass`
> - File sensor JSON: a single-line, minified `.last_mount_status.json` at `~/hass/hestia/config/diagnostics/` (seen in HA as `/config/...`) to avoid "unknown" parsing
> - Single-writer policy: telemetry is the only periodic writer; diagnostic scripts require explicit `--write`

**Objective**: Establish reliable automatic mounting of Home Assistant configuration from SMB share to `~/hass`

**Prerequisites**: 
- macOS with SMB client support
- Valid credentials for Home Assistant SMB share
- Network connectivity to Home Assistant host

## Quick Start (Mount Now)

1. **Immediate Mount**
   ```bash
   $HOME/bin/hass_mount_once.sh
   mount | egrep -i "on $HOME/hass .*smbfs" && echo MOUNT_OK || echo MOUNT_FAIL
   test -w "$HOME/hass" && echo WRITE_OK || echo WRITE_FAIL
   test -f "$HOME/hass/configuration.yaml" && echo CONFIG_OK || echo CONFIG_MISSING
   ```

2. **Troubleshoot Failed Mount**
   ```bash
   tail -n 120 "$HOME/Library/Logs/hass-mount.log" || true
   ```

## LaunchAgent Configuration

### Primary Mount Agent

1. **Check Existing Agent**
   ```bash
   ls -l "$HOME/Library/LaunchAgents/com.local.hass.mount.plist"
   ```

2. **Create LaunchAgent (if missing)**
   ```bash
   cat >"$HOME/Library/LaunchAgents/com.local.hass.mount.plist" <<'PL'
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
     <dict>
       <key>Label</key><string>com.local.hass.mount</string>
       <key>ProgramArguments</key>
       <array>
         <string>/bin/zsh</string>
         <string>-lc</string>
         <string>$HOME/bin/hass_mount_once.sh</string>
       </array>
       <key>RunAtLoad</key><true/>
       <key>KeepAlive</key>
       <dict>
         <key>NetworkState</key><true/>
       </dict>
       <key>StandardOutPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
       <key>StandardErrorPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
     </dict>
   </plist>
   PL
   ```

3. **Load and Activate Agent**
   ```bash
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.mount.plist" 2>/dev/null || true
   launchctl kickstart -k "gui/$(id -u)/com.local.hass.mount"
   launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'state|last exit code|program'
   ```

### Optional: Watchdog Agent (Periodic Checks)

1. **Create Watchdog LaunchAgent**
   ```bash
   cat >"$HOME/Library/LaunchAgents/com.local.hass.mount.watch.plist" <<'PL'
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
     <dict>
       <key>Label</key><string>com.local.hass.mount.watch</string>
       <key>ProgramArguments</key>
       <array>
         <string>/bin/zsh</string>
         <string>-lc</string>
         <string>mount | egrep -qi "on $HOME/hass .*smbfs" || $HOME/bin/hass_mount_once.sh</string>
       </array>
       <key>StartInterval</key><integer>180</integer>
       <key>StandardOutPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
       <key>StandardErrorPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
     </dict>
   </plist>
   PL
   ```

2. **Activate Watchdog**
   ```bash
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.mount.watch.plist"
   launchctl kickstart -k "gui/$(id -u)/com.local.hass.mount.watch"
   ```

## Environment Configuration

### Shell Environment
```bash
# Canonical path semantics for telemetry: write to /config via mounted ~/hass
grep -F 'export HA_MOUNT="/config"' "$HOME/.zshrc" || echo 'export HA_MOUNT="/config"' >> "$HOME/.zshrc"
```

### Keychain Setup

1. **Verify Existing Credentials**
   ```bash
   security find-internet-password -w -s "homeassistant" -a "evertappels" >/dev/null
   security find-internet-password -w -s "homeassistant.local" -a "evertappels" >/dev/null
   ```

2. **Add Missing Credentials**
   ```bash
   read -r -s -p "SMB password for evertappels: " PASS; echo
   security add-internet-password -U -s "homeassistant" -a "evertappels" -w "$PASS"
   security add-internet-password -U -s "homeassistant.local" -a "evertappels" -w "$PASS"
   unset PASS
   ```

## Network Resilience Hardening

### Option 1: Mount Script Retry Loop

Append this retry logic to `$HOME/bin/hass_mount_once.sh` before final validations:

```bash
i=0; until mount | egrep -qi "on $HOME/hass .*smbfs"; do
  i=$((i+1))
  [ $i -gt 5 ] && break
  sleep 2
  "$HOME/bin/hass_mount_once.sh" || true
done
```

### Option 2: Separate Retry Wrapper

Create `$HOME/bin/hass_mount_retry.sh`:
```bash
#!/bin/bash
i=0; until mount | egrep -qi "on $HOME/hass .*smbfs"; do
  i=$((i+1))
  [ $i -gt 5 ] && break
  sleep 2
  "$HOME/bin/hass_mount_once.sh" || true
done
```

## Validation & Testing

### Post-Reboot Acceptance Test
```bash
mount | egrep -i "on $HOME/hass .*smbfs" && echo MOUNT_OK || echo MOUNT_FAIL
test -w "$HOME/hass" && echo WRITE_OK || echo WRITE_FAIL
test -f "$HOME/hass/configuration.yaml" && echo CONFIG_OK || echo CONFIG_MISSING
tail -n 80 "$HOME/Library/Logs/hass-mount.log" | tail -n 40
```

### Diagnostic Commands
```bash
# LaunchAgent status
launchctl print "gui/$(id -u)/com.local.hass.mount" | egrep 'state|last exit code|error|program' || true

# Network connectivity test  
smbutil view //evertappels@homeassistant </dev/null || true

# Force remount
diskutil unmount "$HOME/hass" 2>/dev/null || true
"$HOME/bin/hass_mount_once.sh"
```

## Troubleshooting Guide

| Symptom | Check Command | Resolution |
|---------|--------------|------------|
| Mount not present | `mount \| grep hass` | Run `$HOME/bin/hass_mount_once.sh` |
| LaunchAgent not running | `launchctl print "gui/$(id -u)/com.local.hass.mount"` | Bootstrap and kickstart agent |
| Keychain prompts | `security find-internet-password -s homeassistant` | Re-add credentials to keychain |
| Network timeout | `smbutil view //evertappels@homeassistant` | Check network connectivity |
| Permission denied | `test -w "$HOME/hass"` | Verify mount options and credentials |

## Monitoring

- **Log Location**: `$HOME/Library/Logs/hass-mount.log`
- **Mount Check**: `mount | egrep "on $HOME/hass .*smbfs"`
- **Write Test**: `test -w "$HOME/hass"`
- **Config Validation**: `test -f "$HOME/hass/configuration.yaml"`

For machine-readable diagnostics, see: `hestia/config/diagnostics/hass_mount_status.yaml`

## Home Assistant Integration

### Diagnostics Sensors Implementation

The mount diagnostics can be integrated into Home Assistant for monitoring and alerting. Two implementation paths are available:

#### Option A: Webhook Push (No MQTT Required) — Hardened (Recommended)

**1. Mac-Side Telemetry Script**

Use the single, hardened sender `~/bin/hass_telemetry.sh` with these guarantees:
- Writes a minified, single-line JSON file at `~/hass/hestia/config/diagnostics/.last_mount_status.json` (HA sees it at `/config/...`)
- Posts webhook telemetry to Home Assistant
- Bounded logs and reliable exit codes
- Respects `HA_MOUNT=/config` for canonical path alignment

If you do not yet have the script, retrieve it from the workspace tools package or re-deploy from version control. Ensure it is executable:
```bash
chmod +x "$HOME/bin/hass_telemetry.sh"
```

**2. Telemetry LaunchAgent (Every 2 Minutes)**

```bash
cat >"$HOME/Library/LaunchAgents/com.local.hass.telemetry.plist" <<'PL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.local.hass.telemetry</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>export HA_MOUNT="/config"; source ~/.zshrc; "$HOME/bin/hass_telemetry.sh"</string>
  </array>
  <key>StartInterval</key><integer>120</integer>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
</dict></plist>
PL

launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.telemetry.plist" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/com.local.hass.telemetry"
launchctl print "gui/$(id -u)/com.local.hass.telemetry" | egrep 'state|last exit code|program' || true
```

**3. Home Assistant Package Configuration**

Create or update the HA package (example `packages/hass_mount_monitor.yaml`). Ensure the File sensor reads the minified JSON and that template sensors are stale-aware (auto OFF after ~5 minutes without telemetry):
```yaml
automation:
  - id: hass_mount_webhook_ingest
    alias: HASS Mount Status Ingest (Macbook)
    trigger:
      - platform: webhook
        webhook_id: hass_mount_status
    action:
      - event: hass_mount_status_event
        event_data:
          payload: "{{ trigger.json }}"

template:
  - trigger:
      - platform: event
        event_type: hass_mount_status_event
    sensor:
      - name: "Macbook HASS Mount State"
        unique_id: macbook_hass_mount_state
        state: "{{ trigger.event.data.payload.health_summary.overall_status|default('unknown') }}"
        attributes:
          mounted: "{{ trigger.event.data.payload.mount_status.is_mounted|default(false) }}"
          write_ok: "{{ trigger.event.data.payload.mount_status.mount_point_writable|default(false) }}"
          config_present: "{{ trigger.event.data.payload.mount_status.config_file_exists|default(false) }}"
          host: "{{ trigger.event.data.payload.metadata.hostname|default('unknown') }}"
          user: "{{ trigger.event.data.payload.metadata.user|default('unknown') }}"
          keychain_ok: "{{ trigger.event.data.payload.keychain.homeassistant_entry_exists|default(false) }}"
          agent_loaded: "{{ trigger.event.data.payload.launch_agents.primary_agent.is_loaded|default(false) }}"
          last_run: "{{ now().isoformat() }}"

  - binary_sensor:
      - name: "Macbook HASS Mount OK"
        unique_id: macbook_hass_mount_ok
        state: >
          {{ is_state('sensor.macbook_hass_mount_state','healthy')
             and state_attr('sensor.macbook_hass_mount_state','mounted')
             and state_attr('sensor.macbook_hass_mount_state','write_ok')
             and state_attr('sensor.macbook_hass_mount_state','config_present') }}
        device_class: connectivity

# File integration fallback expects a single-line JSON file:
# /config/hestia/config/diagnostics/.last_mount_status.json (written by hass_telemetry.sh)
# If state remains 'unknown', reload the File integration or re-add the entity.

automation:
  - id: hass_mount_alert_down
    alias: ALERT • Macbook HASS mount down
    mode: single
    trigger:
      - trigger: state
        entity_id: binary_sensor.macbook_hass_mount_ok
        to: 'off'
        for: "00:05:00"
    action:
      - action: persistent_notification.create
        data:
          title: "Macbook HASS mount is down"
          message: >
            State={{ states('sensor.macbook_hass_mount_state') }},
            mounted={{ state_attr('sensor.macbook_hass_mount_state','mounted') }},
            write_ok={{ state_attr('sensor.macbook_hass_mount_state','write_ok') }},
            config_present={{ state_attr('sensor.macbook_hass_mount_state','config_present') }}.

  - id: hass_mount_recovery_info
    alias: INFO • Macbook HASS mount recovered
    mode: single
    trigger:
      - trigger: state
        entity_id: binary_sensor.macbook_hass_mount_ok
        to: 'on'
    action:
      - action: persistent_notification.create
        data:
          title: "Macbook HASS mount recovered"
          message: "Mount recovered at {{ now().isoformat() }}"
```

#### Option B: MQTT Push (Retained, Survives HA Restarts) - **RECOMMENDED**

**1. Mac-Side MQTT Publisher**

Create MQTT push script:
```bash
# Create the MQTT publisher script
cat > "$HESTIA_TOOLS/utils/mount/publish_hass_mount_status_mqtt.sh" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Source centralized environment variables
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel 2>/dev/null || echo "$HOME/hass")"
source "$WORKSPACE_ROOT/.env"

GEN="$HESTIA_TOOLS/utils/mount/generate_hass_mount_diagnostics.sh"
BROKER="homeassistant.local"
TOPIC="home/macbook/hass_mount/status"
TMP="$(mktemp)"

"$GEN" --format json > "$TMP"
mosquitto_pub -h "$BROKER" -t "$TOPIC" -r -f "$TMP"

rm -f "$TMP"
EOF

chmod +x "$HESTIA_TOOLS/utils/mount/publish_hass_mount_status_mqtt.sh"
```

**2. MQTT Telemetry LaunchAgent**

```bash
cat >"$HOME/Library/LaunchAgents/com.local.hass.mount.mqtt.plist" <<'PL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.local.hass.mount.mqtt</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>source ~/.zshrc && $HESTIA_TOOLS/utils/mount/publish_hass_mount_status_mqtt.sh</string>
  </array>
  <key>StartInterval</key><integer>120</integer>
  <key>KeepAlive</key><dict><key>NetworkState</key><true/></dict>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/hass-mount.log</string>
</dict></plist>
PL

launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.local.hass.mount.mqtt.plist"
launchctl kickstart -k "gui/$(id -u)/com.local.hass.mount.mqtt"
```

**3. Home Assistant MQTT Configuration**

Add to `packages/hass_mount_monitor.yaml`:
```yaml
mqtt:
  sensor:
    - name: "Macbook HASS Mount State"
      unique_id: macbook_hass_mount_state
      state_topic: "home/macbook/hass_mount/status"
      value_template: "{{ value_json.health_summary.overall_status | default('unknown') }}"
      json_attributes_topic: "home/macbook/hass_mount/status"
      json_attributes_template: >
        {
          "mounted": {{ value_json.mount_status.is_mounted | default(false) }},
          "write_ok": {{ value_json.mount_status.mount_point_writable | default(false) }},
          "config_present": {{ value_json.mount_status.config_file_exists | default(false) }},
          "host": "{{ value_json.metadata.hostname | default('unknown') }}",
          "user": "{{ value_json.metadata.user | default('unknown') }}",
          "keychain_ok": {{ value_json.keychain.homeassistant_entry_exists | default(false) }},
          "agent_loaded": {{ value_json.launch_agents.primary_agent.is_loaded | default(false) }},
          "last_update": "{{ value_json.metadata.generated_at | default('unknown') }}"
        }

  binary_sensor:
    - name: "Macbook HASS Mount OK"
      unique_id: macbook_hass_mount_ok
      state_topic: "home/macbook/hass_mount/status"
      value_template: >
        {{ value_json.health_summary.overall_status == 'healthy'
           and value_json.mount_status.is_mounted
           and value_json.mount_status.mount_point_writable
           and value_json.mount_status.config_file_exists }}
      device_class: connectivity

# Reuse alert automations from Option A
```

### Dashboard Card

Add to Lovelace dashboard:
```yaml
type: entities
title: Macbook • HASS Mount
entities:
  - binary_sensor.macbook_hass_mount_ok
  - sensor.macbook_hass_mount_state
show_header_toggle: false
```

### Prerequisites for MQTT Option

Install mosquitto client on Mac:
```bash
brew install mosquitto
```

Enable MQTT integration in Home Assistant and ensure broker is accessible.
