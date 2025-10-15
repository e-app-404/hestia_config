---
title: File size
description: Integration for monitoring the size of a file.
ha_category:
  - Sensor
  - Utility
ha_iot_class: Local Polling
ha_release: 0.64
ha_domain: filesize
ha_platforms:
  - sensor
ha_config_flow: true
ha_integration_type: integration
source: https://github.com/home-assistant/home-assistant.io/blob/current/source/_integrations/filesize.markdown
---

# Home Assistant File Size Integration

The **File size** integration is for displaying the size in MB of a file.

> important: File paths must also be added to [allowlist_external_dirs](/integrations/homeassistant/#allowlist_external_dirs) in your `configuration.yaml`.

## Configuration.yaml setup

Example `allowlist_external_dirs` configuration to monitor a file in your configuration folder.

```yaml
homeassistant:
  allowlist_external_dirs:
    - "/config" # Default configuration directory
```

File paths should be absolute paths. For example: `/config/home-assistant_v2.db` to monitor the size of the default database.
