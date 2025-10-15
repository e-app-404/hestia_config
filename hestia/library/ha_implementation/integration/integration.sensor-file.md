---
title: "File integration"
authors: "Hestia"
source: "Home Assistant"
slug: "integration-file"
tags: ["home-assistant", "integration", "file", "sensor", "notification", "action", "read", "write", "log", "yaml", "json", "csv"]
original_date: "2023-01-01"
last_updated: "2025-10-05"
url: "https://www.home-assistant.io/integrations/file/"
---

# File integration

The File integration lets Home Assistant store notifications in a file and expose a sensor that reads the last line of a file. It is enabled by default when `default_config:` is present. If you disabled `default_config:`, add the integration explicitly in `configuration.yaml` as shown below.

> **Important**: The File sensor is not available for YAML configuration, you must add sensors via the UI.

## Basic configuration

```yaml
file:
```

## Actions — read a file

The `file.read_file` action reads a file and returns the parsed content. Important notes:

- `file_name`: [required] path relative to your Home Assistant config directory (UTF-8 encoded)
- `file_encoding`: [optional] file extension, e.g. `JSON` or `YAML`

*Note*: You must add file paths relative to the Home Assistant config directory root, and configure `allowlist_external_dirs` in `configuration.yaml` to allow reads/writes.


### Example: read a JSON file in `www` and store the parsed content into a variable.

```yaml
- action: file.read_file
  data:
    file_name: config/www/myfile.json
    file_encoding: JSON
  response_variable: file_content
```

Contents of `config/www/myfile.json` (example):

```json
{
  "latitude": 32.87336,
  "longitude": -117.22743,
  "gps_accuracy": 1.2
}
```

Response example (the action sets `file_content`):

```yaml
data:
  latitude: 32.87336
  longitude: -117.22743
  gps_accuracy: 1.2
```

## Notifications

Use the File integration to persist notification messages. Ensure the file path is included in `allowlist_external_dirs`. If the file does not exist it will be created (the folder must exist). You can set `timestamp: true` to prefix entries with a timestamp.

Use `notify.send_message` or the notify platform to write messages to the file and reference those messages in automations/scripts.

## Sensor platform

The file sensor reads the last line of a plain-text file and evaluates the value using a template. This behaves like `tail -n 1 file` — only the last line is used. File paths used by the sensor must also be listed in `allowlist_external_dirs`.

### JSON log example

If the log contains JSON objects per line:

```json
{"temperature": 21, "humidity": 39}
{"temperature": 22, "humidity": 36}
```

File sensor configuration (extract temperature):

```yaml
file_path: /config/sensor.json
value_template: "{{ value_json.temperature }}"
unit_of_measurement: "°C"
```

> Note: file sensors must be configured via the UI, not YAML.

### CSV log example

Log contents:

```log
timestamp,temperature,humidity
1631472948,21,39
1631472949,22,36
```

Sensor configuration (extract temperature):


```log
timestamp,temperature,humidity
1631472948,21,39
1631472949,22,36
```

Sensor configuration (extract temperature):

```yaml
file_path: /config/sensor.csv
value_template: "{{ value.split(',')[1] }}"
unit_of_measurement: "°C"
```

## Tips and related topics

- Ensure `allowlist_external_dirs` includes any external path you use.
- Prefer structured formats (JSON/YAML) for easy templating in `value_template`.
- See Home Assistant automation docs for examples of using the read result.