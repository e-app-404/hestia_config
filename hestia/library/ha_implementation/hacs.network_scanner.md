---
title: "Network Scanner (HACS)"
authors: "parvez"
source: "Network Scanner (HACS)"
slug: "network-scanner-hacs"
version: 1.0.7
tags: ["home-assistant", "hacs", "network", "scanner", "discovery", "mac", "windows", "linux", "raspberry-pi", "python", "nmap", "ip", "cidr"]
original_date: 2019-01-01
last_updated: 2025-10-05
url: "https://github.com/parvez/network_scanner"
---

# Home Assistant Network Scanner Integration

This Home Assistant integration provides a network scanner that identifies devices on your local network. Using a configured IP range and optional MAC address mappings, it gives each discovered device a friendly name and vendor information.

## Features

- Scan a local network range (CIDR or start-end) for devices.
- Use user-provided MAC address → (name, id, vendor) mappings for custom labeling.
- Support multiple IP ranges in a single configuration.
- Periodic updates (default interval defined by the integration).
- Expose a sensor with device list metadata suitable for Lovelace cards.

## Installation

### Install via HACS

1. Open Home Assistant, go to **HACS > Integrations**.
2. Search for **Network Scanner** and install it.
3. Add the configuration to your `configuration.yaml` (examples below) or use the integration UI.
4. Restart Home Assistant.

### Manual installation

1. Copy the `network_scanner` directory into `custom_components/` in your Home Assistant installation.
2. Add the configuration to `configuration.yaml` (see examples).
3. Restart Home Assistant.

## Configuration

You can configure the integration either through the UI (config flow) or by editing `configuration.yaml`.

### Config flow (UI)

Use **Configuration > Integrations > + Add Integration** and search for **Network Scanner**. Provide the IP range (CIDR or start-end) and optional MAC mappings.

#### MAC mapping format (per line)

The component accepts newline-separated MAC mapping entries. Each line is split on `;` and the component expects three fields. The current implementation parses each line as:

```log
MAC_ADDRESS ; NAME_OR_ID ; VENDOR_OR_TYPE
```

*Notes*:
- The component's parser requires at least three `;`-separated fields. Additional fields are ignored.
- The second field is used as the display name (or identifier) and the third field is treated as a type/vendor string.

*Example*:

```log
bc:14:14:f1:81:1b;Brother Printer;Cloud Network Technology Singapore Pte. Ltd.
b1:81:11:31:a1:b1;Evert's iPhone;Apple Inc.
```

### configuration.yaml example

```yaml
network_scanner:
  ip_range: "10.100.1.0/24 10.1.1.0/24"
  mac_mapping_1: "bc:14:14:f1:81:1b;brother_printer;Cloud Network Technology Singapore Pte. Ltd."
  mac_mapping_2: "b1:81:11:31:a1:b1;firstname_phone;Apple Inc."
```

The integration also supports the single-line mapping format used by the config flow; each mapping is provided as its own `mac_mapping_N` key.

## Displaying devices in the UI

### Lovelace Markdown card

You can render the device list using a Markdown card. This example shows a simple table generated from the sensor's `devices` attribute:

```yaml
type: markdown
content: >
  ## Devices

  | IP Address | MAC Address | Custom Name | Custom Description | Hostname | Vendor |
  |------------|-------------|-------------|--------------------|----------|--------|

  {% for device in state_attr('sensor.network_scanner', 'devices') %}
  | {{ device.ip }} | {{ device.mac }} | {{ device.name }} | {{ device.type }} | {{ device.hostname }} | {{ device.vendor }} |
  {% endfor %}
```

### Flex Table (custom card)

If you use the `flex-table-card` (community card), you can display the devices with richer column configuration:

```yaml
type: custom:flex-table-card
title: Devices
entities:
  include: sensor.network_scanner
sort_by: x.ip+
columns:
  - name: IP Address
    data: devices
    modify: x.ip
  - name: MAC Address
    data: devices
    modify: x.mac
  - name: Custom Name
    data: devices
    modify: x.name
  - name: Custom Description
    data: devices
    modify: x.type
  - name: Hostname
    data: devices
    modify: x.hostname
  - name: Vendor
    data: devices
    modify: x.vendor
```

## Technical details

The integration consists of a few Python modules:

- `config_flow.py` — handles the integration UI and config flow.
- `const.py` — integration constants.
- `__init__.py` — initialization and unload logic.
- `sensor.py` — the main sensor implementation that performs the scan and parses the MAC mappings.

Scan interval and state

- Default scan interval: 15 minutes (the sensor's implementation uses a 15 minute interval).
- Primary entity id: `sensor.network_scanner` (the integration exposes a single sensor entity named "Network Scanner").
- Entity state: integer device count (number of discovered devices).
- Entity attributes: `devices` — a list of device objects discovered during the last scan.

Sample `devices` attribute (one entry):

```json
{
  "ip": "192.168.0.42",
  "mac": "d4:ad:fc:12:ff:3f",
  "name": "ha_devtools_template_device_id_list_2",
  "type": "Raspberry Pi (Trading) Ltd",
  "vendor": "Raspberry Pi (Trading) Ltd",
  "hostname": "raspberrypi.local"
}
```

MAC mapping handling

- The sensor reads configuration keys named `mac_mapping_1` .. `mac_mapping_25` from YAML and the config flow. Additional `mac_mapping_N` keys are supported beyond 25 if present.
- All provided `mac_mapping_N` values are concatenated into a newline-separated mapping string and parsed by the component.

Dependencies

- Python requirement (declared in `manifest.json`): `python-nmap` — this Python package is installed by Home Assistant when the integration is installed via HACS or custom component install.
- Runtime dependency (not installed by `pip`): the `nmap` binary must be present on the host for `python-nmap` to perform scans. On common platforms:
  - macOS (Homebrew): `brew install nmap`
  - Debian/Ubuntu: `sudo apt update && sudo apt install nmap`
  - Raspberry Pi OS: `sudo apt install nmap`

If `nmap` is not available or the integration lacks permission to run it, scans will fail — check the Home Assistant logs for error messages.

## Troubleshooting

If something doesn't work as expected:

- Check Home Assistant logs for errors related to `network_scanner`.
- Verify the `ip_range` and `mac_mapping` entries are correctly formatted.
- Ensure `nmap` is installed and accessible if your install requires it for host discovery.

If you need help, open an issue in the integration's repository or ask for help in the HACS/discussion forums.
