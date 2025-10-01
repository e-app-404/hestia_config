---
title: "TinyTuya User Manual - Comprehensive Guide"
date: 2025-09-30
author: "GitHub Copilot (from TinyTuya Documentation)"
version: "Latest"
tags: ["tuya", "iot", "python", "smart-devices", "manual", "reference"]
status: "Complete Reference"
source: "https://pypi.org/project/tinytuya/"
---

# 🏠 TinyTuya - Comprehensive User Manual

## 📋 **Table of Contents**

1. [Overview & Features](#overview--features)
2. [Installation](#installation)
3. [Device Preparation](#device-preparation)
4. [Setup Wizard](#setup-wizard)
5. [Programming Guide](#programming-guide)
6. [Command Line Interface](#command-line-interface)
7. [Device Types & Functions](#device-types--functions)
8. [Tuya Cloud Integration](#tuya-cloud-integration)
9. [Data Points (DPS) Reference](#data-points-dps-reference)
10. [Error Codes](#error-codes)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Features](#advanced-features)

---

## 🎯 **Overview & Features**

### **What is TinyTuya?**
Python module to control and read state of Tuya compatible WiFi Smart Devices (Plugs, Switches, Lights, Window Covers, etc.) using local area network (LAN) or cloud (TuyaCloud API).

### **Key Features**
- **Local Control:** Direct device control without cloud dependency
- **Cloud Integration:** Full Tuya Cloud API support
- **Protocol Support:** Tuya Protocols 3.1, 3.2, 3.3, 3.4, and 3.5
- **Device Types:** Outlets, Lights, Covers, Sensors, Thermostats, and more
- **Network Scanner:** Built-in device discovery
- **Setup Wizard:** Automated device key extraction

### **Compatibility**
- **Replacement for:** pytuya PyPI module
- **Dependencies:** cryptography, requests, colorama (optional)
- **Python Versions:** 3.6+

---

## 💾 **Installation**

### **Standard Installation**
```bash
# Install TinyTuya Library
python -m pip install tinytuya

# Optional: Install Command Line Tool
pipx install tinytuya
```

### **Space-Limited Systems Installation**
```bash
# 1. Install cryptography library (choose one)
python -m pip install cryptography          # Recommended
python -m pip install pycryptodome          # Alternative
python -m pip install pyaes                 # Pure Python (legacy)

# 2. Optional: Terminal colors
python -m pip install colorama

# 3. Optional: Cloud functionality
python -m pip install requests

# 4. Install TinyTuya without dependencies
python -m pip install --no-deps tinytuya
```

### **Cryptography Options**
| Library | Status | Features |
|---------|--------|----------|
| `cryptography` | ✅ **Recommended** | Full support, requires OpenSSL |
| `pycryptodome` | ✅ **Good Alternative** | No OpenSSL, actively developed |
| `pyaes` | ⚠️ **Legacy** | Pure Python, no v3.5+ support |
| `pycrypto` | ❌ **Abandoned** | Predecessor, no v3.5+ support |

---

## 🔧 **Device Preparation**

### **Required Information**
To control Tuya devices, you need:

| Parameter | Description | Example |
|-----------|-------------|---------|
| **Address** | Network IPv4 address | `192.168.1.100` |
| **Device ID** | Unique Tuya identifier | `01234567891234567890` |
| **Version** | Tuya protocol version | `3.3` |
| **Local Key** | Security encryption key | `1234567890123abc` |

### **Network Requirements**
Your firewall must allow:
- **UDP:** Ports 6666, 6667, 7000
- **TCP:** Port 6668

### **Device Pairing Prerequisite**
- Devices must be activated via **Smart Life App** or **Tuya Smart App**
- Cannot use 'guest' accounts (will be deleted during setup)

---

## 🧙 **Setup Wizard**

### **Step 1: Pair Devices**
1. Download **Smart Life App** (iPhone/Android)
2. Create account and pair all Tuya devices
3. **Important:** Use regular account, not guest

### **Step 2: Network Scan (Optional)**
```bash
python -m tinytuya scan
```
**Output:** Device Address, ID, Version for local network devices

### **Step 3: Tuya Developer Account**
1. **Create Account:** [iot.tuya.com](https://iot.tuya.com)
   - Account Type: Select "Skip this step..."

2. **Create Cloud Project:**
   - Click "Cloud" → "Create Cloud Project"
   - Select correct **Data Center Region** ([find here](https://developer.tuya.com/en/docs/iot/oem-app-data-center-distributed?id=Kafi0ku9l07qb))
   - Note: **Authorization Key (API ID)** and **Secret**

3. **Link App Account:**
   - Cloud → Select Project → Devices → "Link Tuya App Account"
   - Choose "Automatic" and "Read Only Status"
   - **Scan QR Code** with Smart Life app (Me tab → QR button)

4. **Service API Setup:**
   - Subscribe to: **IoT Core** and **Authorization**
   - Click "Service API" → "Go to Authorize" → Subscribe to API Groups
   - **Important:** Disable popup blockers

5. **API Renewal:**
   - IoT Core subscription expires monthly
   - Renew via form (1, 3, or 6 month options)

### **Step 4: Run Setup Wizard**
```bash
python -m tinytuya wizard
```

**Wizard Process:**
1. **Input API Credentials:**
   - API ID/Client ID (from project overview)
   - API Secret/Client Secret
   - API Region: `cn`, `us`, `us-e`, `eu`, `eu-w`, `sg`, `in`

2. **Sample Device ID:**
   - Enter `scan` for auto-discovery
   - Use ID from Step 2 scan
   - Get from Tuya IoT Device List

3. **Generated Files:**
   - `devices.json` - Device list with keys
   - `tuya-raw.json` - Raw Tuya Cloud response
   - `snapshot.json` - Device status (if polled)

---

## 🐍 **Programming Guide**

### **Basic Device Control**
```python
import tinytuya

# Connect to Device
d = tinytuya.Device(
    dev_id='DEVICE_ID_HERE',
    address='192.168.1.100',      # Or 'Auto' for auto-discovery
    local_key='LOCAL_KEY_HERE',
    version=3.3
)

# Get Status
data = d.status()
print('Device status: %r' % data)

# Turn On/Off
d.turn_on()
d.turn_off()
```

### **Device Classes**

#### **OutletDevice (Smart Plugs/Switches)**
```python
outlet = tinytuya.OutletDevice('DEVICE_ID', 'IP_ADDRESS', 'LOCAL_KEY', version=3.3)

# Basic Controls
outlet.turn_on()
outlet.turn_off() 
outlet.set_status(True)  # True=On, False=Off

# Multi-Switch Control (for power strips)
outlet.turn_on(switch=4)   # Turn on 4th outlet
outlet.turn_off(switch=1)  # Turn off 1st outlet

# Dimmer Control
outlet.set_dimmer(50)      # Set to 50%
```

#### **BulbDevice (Smart Lights)**
```python
bulb = tinytuya.BulbDevice('DEVICE_ID', 'IP_ADDRESS', 'LOCAL_KEY')
bulb.set_version(3.3)
bulb.set_socketPersistent(True)  # Keep connection open

# Color Control
bulb.set_colour(255, 0, 0)       # Red (RGB)
bulb.set_hsv(120, 100, 100)      # Green (HSV)

# Brightness Control
bulb.set_brightness(800)         # Raw value
bulb.set_brightness_percentage(75)  # 75%

# White Light Control  
bulb.set_white(1000, 10)         # Brightness, Color Temp
bulb.set_white_percentage(80, 50)   # 80% bright, 50% temp

# Mode Control
bulb.set_mode('white')           # white, colour, scene, music
bulb.set_scene(3)               # 1=nature, 3=rave, 4=rainbow

# Status Queries
brightness = bulb.brightness()
temp = bulb.colourtemp()
r, g, b = bulb.colour_rgb()
h, s, v = bulb.colour_hsv()
```

#### **CoverDevice (Window Covers/Curtains)**
```python
cover = tinytuya.CoverDevice('DEVICE_ID', 'IP_ADDRESS', 'LOCAL_KEY')

# Cover Controls
cover.open_cover()
cover.close_cover()
cover.stop_cover()

# Multi-Cover Control
cover.open_cover(switch=2)   # For devices with multiple covers
```

### **Advanced Configuration**
```python
# Connection Settings
d.set_socketTimeout(10)          # Connection timeout (seconds)
d.set_socketRetryLimit(3)        # Retry attempts
d.set_socketRetryDelay(2)        # Delay between retries
d.set_socketPersistent(True)     # Keep connection open
d.set_socketNODELAY(True)       # TCP_NODELAY option

# Data Point Selection
d.set_dpsUsed([1, 2, 3])        # Request specific DPS
d.add_dps_to_request(25)         # Add DPS 25 to requests

# Advanced Controls
d.set_multiple_values({1: True, 2: 50})  # Set multiple DPS
d.heartbeat()                    # Send heartbeat
d.updatedps([1, 2])             # Request DPS update
```

### **Device Monitoring**
```python
import tinytuya

# Persistent Connection Monitoring
d = tinytuya.OutletDevice('DEVICEID', 'IP', 'KEY', version=3.3, persist=True)

print("Starting monitor...")
d.status(nowait=True)  # Initial status request

while True:
    # Check for updates
    data = d.receive()
    if data:
        print('Received: %r' % data)
    else:
        print("Sending heartbeat...")
        d.heartbeat()
```

---

## 💻 **Command Line Interface**

### **Installation**
```bash
# Option 1: pip install
python -m tinytuya

# Option 2: pipx install  
tinytuya
```

### **Available Commands**

#### **Setup Wizard**
```bash
tinytuya wizard [-debug] [-nocolor] [-yes] [-no-poll]
```

**Options:**
- `-debug`: Activate debug mode
- `-nocolor`: Disable color output
- `-yes`: Answer "yes" to all questions
- `-no-poll`: Skip device polling
- `-device-file FILE`: Custom devices file [Default: devices.json]

#### **Network Scanning**
```bash
# Basic network scan
tinytuya scan [max_time]

# Force scan specific networks
tinytuya scan -force 192.168.1.0/24 192.168.2.0/24

# Scan with options
tinytuya scan -debug -nocolor 30
```

#### **Device Operations**
```bash
# Poll all devices from devices.json
tinytuya devices [max_time]

# Quick status snapshot
tinytuya snapshot

# JSON output (non-interactive)
tinytuya json
```

### **Command Examples**
```bash
# Complete setup process
tinytuya wizard -yes

# Extended scan (50 retries)
tinytuya scan 50

# Debug mode scan
tinytuya scan -debug

# Force network scan
tinytuya scan -force 192.168.0.0/24

# Poll devices without interaction
tinytuya snapshot -no-poll
```

---

## 🔌 **Device Types & Functions**

### **Base Device Functions** (All Devices)
```python
# Status & Information
status = d.status()                    # Get device status
d.detect_available_dps()              # List available DPS

# Version & Protocol
d.set_version(3.3)                    # Set protocol version

# Network Configuration  
d.set_socketPersistent(True)          # Keep connection open
d.set_socketTimeout(10)               # Connection timeout
d.set_socketRetryLimit(5)             # Retry attempts

# Control Functions
d.set_status(True, switch=1)          # Set switch status
d.set_value(25, 'value')              # Set DPS value
d.set_timer(3600)                     # Set timer (seconds)
d.turn_on(switch=1)                   # Turn on
d.turn_off(switch=1)                  # Turn off

# Communication
d.heartbeat()                         # Send heartbeat
d.send(payload)                       # Send raw payload
data = d.receive()                    # Receive data
```

### **Device-Specific Functions**

#### **OutletDevice Functions**
```python
set_dimmer(percentage)                # Dimmer control (0-100%)
```

#### **BulbDevice Functions**
```python
# Color Controls
set_colour(r, g, b, nowait=False)     # RGB color (0-255 each)
set_hsv(h, s, v, nowait=False)        # HSV color
set_white(brightness, colourtemp)      # White light
set_white_percentage(bright%, temp%)   # White light (percentage)

# Brightness Controls  
set_brightness(brightness)             # Raw brightness value
set_brightness_percentage(percent)     # Brightness percentage (0-100%)

# Color Temperature
set_colourtemp(colourtemp)            # Raw color temperature  
set_colourtemp_percentage(percent)     # Color temp percentage

# Modes & Scenes
set_mode(mode)                        # 'white', 'colour', 'scene', 'music'
set_scene(scene)                      # 1=nature, 3=rave, 4=rainbow

# Status Queries
brightness()                          # Get current brightness
colourtemp()                         # Get current color temp  
colour_rgb()                         # Get RGB values (r,g,b)
colour_hsv()                         # Get HSV values (h,s,v)
state()                              # Get current state
```

#### **CoverDevice Functions**
```python
open_cover(switch=1)                  # Open cover
close_cover(switch=1)                 # Close cover  
stop_cover(switch=1)                  # Stop cover movement
```

### **Cloud Functions**
```python
# Cloud Setup
c = tinytuya.Cloud(apiRegion="us", apiKey="key", apiSecret="secret")

# Device Management
devices = c.getdevices()              # List all devices
status = c.getstatus(device_id)       # Get device status
properties = c.getproperties(device_id) # Get device properties
functions = c.getfunctions(device_id)  # Get available functions

# Device Control
result = c.sendcommand(device_id, commands)  # Send commands
logs = c.getdevicelog(device_id)      # Get device logs (1 week max)
```

---

## ☁️ **Tuya Cloud Integration**

### **Cloud Setup**
```python
import tinytuya

# Method 1: Use tinytuya.json file
c = tinytuya.Cloud()

# Method 2: Direct credentials
c = tinytuya.Cloud(
    apiRegion="us",                    # cn, us, us-e, eu, eu-w, sg, in
    apiKey="your_api_key",
    apiSecret="your_api_secret",
    apiDeviceID="sample_device_id"
)
```

### **Device Management**
```python
# List All Devices
devices = c.getdevices(verbose=True)
print("Devices: %r" % devices)

# Device Information  
device_id = "your_device_id"
properties = c.getproperties(device_id)
functions = c.getfunctions(device_id)
status = c.getstatus(device_id)
dps_info = c.getdps(device_id)
```

### **Device Control**
```python
# Send Commands
commands = {
    "commands": [
        {"code": "switch_1", "value": True},
        {"code": "countdown_1", "value": 0},
    ]
}

result = c.sendcommand(device_id, commands)
print("Command result:", result)

# Custom URI Commands
result = c.sendcommand(device_id, commands, uri="custom/endpoint")
```

### **Device Logs**
```python
import json

# Get Recent Logs (default: 1 day, max 5000 entries)
logs = c.getdevicelog(device_id)

# Custom Log Parameters
logs = c.getdevicelog(
    device_id,
    start=-7,          # 7 days ago
    end=0,             # now  
    evtype="1,2,3,7",  # event types (7 = data report)
    size=100           # max entries
)

print(json.dumps(logs, indent=2))
```

### **API Usage Limits**
⚠️ **CAUTION:** Free Tuya IoT Developer accounts have limited API calls
- Monitor usage in Tuya IoT Platform
- Avoid frequent automation calls
- Consider caching responses

---

## 📊 **Data Points (DPS) Reference**

### **Understanding DPS**
Data Points (DPS) define device state and functions. Each DPS has:
- **ID:** Numeric identifier (1, 2, 3, etc.)
- **Type:** bool, integer, enum, string, etc.
- **Range:** Valid values
- **Function:** What the DPS controls

### **Reading DPS Values**
```python
# Get all DPS values
data = d.status()
print("All DPS:", data['dps'])

# Read specific DPS
dps_25_value = data['dps']['25']
print("DPS 25 value:", dps_25_value)

# Set DPS value
d.set_value(25, 'new_value')
```

### **Common DPS Tables**

#### **Version 3.1 - Basic Plug/Switch**
| DPS ID | Function | Type | Range | Units |
|--------|----------|------|-------|-------|
| 1 | Switch | bool | True/False | |
| 2 | Countdown | integer | 0-86400 | seconds |
| 4 | Current | integer | 0-30000 | mA |
| 5 | Power | integer | 0-50000 | W |
| 6 | Voltage | integer | 0-5000 | V |

#### **Version 3.3 - Multi-Switch Power Strip**
| DPS ID | Function | Type | Range | Units |
|--------|----------|------|-------|-------|
| 1-7 | Switch 1-7 | bool | True/False | |
| 9-15 | Countdown 1-7 | integer | 0-86400 | seconds |
| 17 | Add Electricity | integer | 0-50000 | kWh |
| 18 | Current | integer | 0-30000 | mA |
| 19 | Power | integer | 0-50000 | W |
| 20 | Voltage | integer | 0-5000 | V |
| 38 | Power-on State | enum | off, on, memory | |
| 41 | Child Lock | bool | True/False | |

#### **Version 3.3 - RGB Light**
| DPS ID | Function | Type | Range | Units |
|--------|----------|------|-------|-------|
| 20 | Switch | bool | True/False | |
| 21 | Mode | enum | white, colour, scene, music | |
| 22 | Brightness | integer | 10-1000 | |
| 23 | Color Temp | integer | 0-1000 | |
| 24 | Color | hexstring | h:0-360,s:0-1000,v:0-1000 | HSV |
| 25 | Scene | string | scene data | |

#### **Version 3.3 - Temperature/Humidity Sensor**
| DPS ID | Function | Type | Range | Units |
|--------|----------|------|-------|-------|
| 1 | Door Sensor | bool | True/False | |
| 2 | Battery Level State | enum | low, middle, high | |
| 3 | Battery Level | integer | 0-100 | % |
| 8 | Current Temperature | integer | 400-2000 | 0.1°C |
| 9 | Current Humidity | integer | 0-100 | % |
| 12 | PIR State | enum | pir, none | |

#### **Version 3.3 - Thermostat (24V)**
| DPS ID | Function | Type | Range | Units |
|--------|----------|------|-------|-------|
| 2 | System Mode | enum | auto, cool, heat, off | |
| 16 | Setpoint (High-Res °C) | integer | 500-3200 | °C × 100 |
| 17 | Setpoint (°F) | integer | 20-102 | °F |
| 23 | Display Units | enum | f, c | |
| 24 | Current Temp (High-Res °C) | integer | 500-3200 | °C × 100 |
| 29 | Current Temp (°F) | integer | 20-102 | °F |
| 34 | Current Humidity | integer | 0-100 | % |
| 115 | Fan Mode | enum | auto, cycle, on | |
| 119 | Schedule Enabled | bool | True/False | |

### **Device-Specific DPS Examples**

#### **Smart Curtain/Cover**
```python
# Curtain Control DPS
d.set_value(1, 'open')    # DPS 1: open, stop, close, continue
d.set_value(2, 50)        # DPS 2: Position 0-100%
d.set_value(3, 'start')   # DPS 3: Calibration start/end
```

#### **IR Universal Remote**
```python
import json

# IR Command Format
command = {
    "control": "send_ir",
    "head": "",
    "key1": "base64_ir_signal_here",
    "type": 0,
    "delay": 300,
}

# Send IR Command (DPS 201)
payload = d.generate_payload(tinytuya.CONTROL, {"201": json.dumps(command)})
d.send(payload)
```

---

## ⚠️ **Error Codes**

TinyTuya returns error details in JSON format instead of raising exceptions:

```json
{
  "Error": "Invalid JSON Payload",
  "Err": "900", 
  "Payload": "{Tuya Message}"
}
```

### **Error Code Reference**
| Code | Constant | Description | Resolution |
|------|----------|-------------|------------|
| 900 | ERR_JSON | Invalid JSON Response | Check device connectivity |
| 901 | ERR_CONNECT | Network Connection Failed | Verify IP/network |
| 902 | ERR_TIMEOUT | Device Response Timeout | Check device power/network |
| 903 | ERR_RANGE | Value Out of Range | Verify DPS value limits |
| 904 | ERR_PAYLOAD | Unexpected Device Payload | Check protocol version |
| 905 | ERR_OFFLINE | Device Unreachable | Verify device online |
| 906 | ERR_STATE | Device in Unknown State | Reset/restart device |
| 907 | ERR_FUNCTION | Function Not Supported | Check device capabilities |
| 908 | ERR_DEVTYPE | Device22 Detected | Retry command |
| 909 | ERR_CLOUDKEY | Missing Cloud Credentials | Check API keys |
| 910 | ERR_CLOUDRESP | Invalid Cloud JSON Response | Verify cloud connectivity |
| 911 | ERR_CLOUDTOKEN | Unable to Get Cloud Token | Check API credentials |
| 912 | ERR_PARAMS | Missing Function Parameters | Provide required parameters |
| 913 | ERR_CLOUD | Tuya Cloud Error Response | Check cloud service status |
| 914 | ERR_KEY_OR_VER | Check Device Key/Version | Verify local key and version |

---

## 🔧 **Troubleshooting**

### **Connection Issues**

#### **"Unable to Connect" (ERR_CONNECT)**
```python
# Check network connectivity
import tinytuya

# Method 1: Auto-discover device IP
d = tinytuya.Device('DEVICE_ID', 'Auto', 'LOCAL_KEY', version=3.3)

# Method 2: Use network scanner
tinytuya.scan()

# Method 3: Find specific device
device_info = tinytuya.find_device('DEVICE_ID')
```

#### **"Decrypt Errors" - Invalid Local Key**
- Local key changes when device is re-paired
- Run wizard again to get new keys
- Verify device ID matches exactly

#### **TCP Connection Limit**
- Tuya devices allow only one TCP connection
- Close Smart Life app before using TinyTuya
- Use `persist=False` for single commands

### **Device-Specific Issues**

#### **22-Character Device IDs**
```python
# Special handling for 22-char IDs
d = tinytuya.OutletDevice('22_char_device_id', '192.168.1.100', 'key', 'device22')
d.set_version(3.3)
d.set_dpsUsed({"1": None})  # Must specify available DPS
data = d.status()
```

#### **Protocol Version Issues**
```python
# Try different versions if device doesn't respond
versions = [3.1, 3.2, 3.3, 3.4, 3.5]

for version in versions:
    d.set_version(version)
    data = d.status()
    if 'dps' in data:
        print(f"Working version: {version}")
        break
```

#### **Firmware Compatibility**
- Update device firmware via Smart Life app
- Older firmware may not support all features
- Version 3.1 devices may not require local key for status

### **Network & Firewall**

#### **Required Ports**
```bash
# UDP Ports (device discovery)
sudo ufw allow 6666/udp
sudo ufw allow 6667/udp  
sudo ufw allow 7000/udp

# TCP Port (device communication)
sudo ufw allow 6668/tcp
```

#### **Windows ANSI Color Issues**
```bash
# Option 1: Use nocolor flag
tinytuya scan -nocolor

# Option 2: Enable ANSI in Windows CMD
reg add HKEY_CURRENT_USER\Console /v VirtualTerminalLevel /t REG_DWORD /d 0x00000001 /f
```

### **Cloud API Issues**

#### **API Rate Limits**
```python
import time

# Add delays between API calls
for device_id in device_list:
    status = cloud.getstatus(device_id)
    time.sleep(1)  # 1 second delay
```

#### **Region Selection**
- Try different regions if devices don't appear
- EU users may need "Central Europe" instead of "Western Europe"
- Check Tuya IoT platform for device visibility

---

## 🚀 **Advanced Features**

### **Bulk Device Operations**
```python
import tinytuya

# Load devices from wizard-generated file
devices = tinytuya.deviceScan(verbose=False)

# Control multiple devices
for device in devices:
    d = tinytuya.Device(device['id'], device['ip'], device['key'], version=3.3)
    d.turn_on()
    print(f"Turned on device {device['id']}")
```

### **Custom Message Generation**
```python
# Generate custom payloads
payload = d.generate_payload(
    tinytuya.CONTROL,           # Command type
    {"1": True, "2": 50},       # DPS values
    cid="sub_device_id"         # Optional sub-device
)

# Send without waiting for response  
d.send(payload)

# Or send and get response
response = d.send(payload)
```

### **Multi-Device Gateway Support**
```python
# Gateway device with sub-devices
gateway = tinytuya.Device('GATEWAY_ID', 'IP', 'KEY', version=3.3)

# Sub-device control
sub_device = tinytuya.Device(
    'SUB_DEVICE_ID', 
    'IP', 
    'KEY', 
    version=3.3,
    cid='sub_device_cid',      # Child device ID
    parent=gateway             # Parent gateway object
)

# Query sub-devices
gateway.subdev_query()
```

### **Device Discovery & Monitoring**
```python
# Advanced device scanning
devices = tinytuya.deviceScan(
    verbose=True,        # Show detailed output
    maxretries=50,       # Increase scan attempts  
    color=False          # Disable color output
)

# Monitor specific device types
for device in devices:
    if device.get('version') == '3.3':
        print(f"Found v3.3 device: {device}")
```

### **Performance Optimization**
```python
# Persistent connections for multiple commands
d = tinytuya.BulbDevice('ID', 'IP', 'KEY', version=3.3)
d.set_socketPersistent(True)  # Keep connection open
d.set_socketNODELAY(True)     # Reduce latency

# Fast commands without waiting
d.set_colour(255, 0, 0, nowait=True)    # Red
d.set_colour(0, 255, 0, nowait=True)    # Green  
d.set_colour(0, 0, 255, nowait=True)    # Blue

# Close connection when done
d.close()
```

---

## 📚 **Additional Resources**

### **Related Projects**
- **tinytuya2mqtt** - MQTT bridge for Home Assistant
- **pymoebot** - MoeBot robotic lawn mower control
- **tuya-local** - Local Home Assistant support
- **Domoticz-TinyTUYA-Plugin** - Domoticz integration

### **Documentation Links**
- **Official Docs:** [Tuya Developer Platform](https://developer.tuya.com)
- **DPS Reference:** [TuyaMCU Documentation](https://tasmota.github.io/docs/TuyaMCU/)
- **GitHub Repository:** [TinyTuya Project](https://github.com/jasonacox/tinytuya)

### **Community Support**
- **Issues/Bugs:** GitHub Issues
- **Feature Requests:** GitHub Discussions  
- **Contributions:** Pull Requests Welcome

---

## 🏷️ **Quick Reference Card**

### **Essential Commands**
```bash
# Setup new devices
tinytuya wizard

# Scan network
tinytuya scan

# Device status  
tinytuya snapshot
```

### **Basic Python Usage**
```python
import tinytuya

# Standard device setup
d = tinytuya.Device('ID', 'IP', 'KEY', version=3.3)

# Essential functions
status = d.status()       # Get status
d.turn_on()              # Power on
d.turn_off()             # Power off  
d.set_value(1, True)     # Set DPS value
```

### **Emergency Debugging**
```python
# Enable debug output
tinytuya.set_debug(True)

# Check available DPS
dps_list = d.detect_available_dps()
print("Available DPS:", dps_list)

# Test connectivity
result = d.heartbeat()
print("Heartbeat result:", result)
```

---

**Manual Version:** Latest (2025-09-30)  
**Source:** [TinyTuya PyPI Documentation](https://pypi.org/project/tinytuya/)  
**Generated:** GitHub Copilot