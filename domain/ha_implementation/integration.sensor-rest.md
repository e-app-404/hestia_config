---
title: "RESTful Sensor Integration"
authors: "Home Assistant"
source: "Home Assistant Docs"
slug: "restful-sensor-integration"
tags: ["home-assistant", "rest", "restful", "sensor", "binary-sensor", "api", "http", "json"]
original_date: "2022-01-01"
last_updated: "2025-10-06"
url: "https://www.home-assistant.io/integrations/rest/"
---

# RESTful Sensor Integration

The REST sensor platform consumes a given endpoint which is exposed by a RESTful API of a device, an application, or a web service. The sensor has support for GET and POST requests.

RESTful Sensor and RESTful Binary Sensor can also be set up as platforms if there is only a single sensor per endpoint.

## Example Configuration

```yaml
# Example configuration.yaml entry
rest:
  - authentication: basic
    username: "admin"
    password: "password"
    scan_interval: 60
    resource: http://192.168.1.12/status.xml
    sensor:
      - name: "Adult Pool Data System"
        json_attributes_path: "$.response.system"
        value_template: "OK"
        json_attributes:
          - "runstate"
          - "model"
          - "opmode"
          - "freeze"
          - "time"
          - "sensor1"
          - "sensor2"
          - "sensor3"
          - "sensor4"
          - "sensor5"
          - "version"
      - name: "Adult Pool Data Equipment"
        json_attributes_path: "$.response.equipment"
        value_template: "OK"
        json_attributes:
          - "circuit1"
          - "circuit2"
          - "circuit3"
          - "circuit4"
          - "circuit5"
          - "circuit6"
          - "circuit7"
          - "circuit8"
      - name: "Adult Pool Data Temp"
        json_attributes_path: "$.response.temp"
        value_template: "OK"
        json_attributes:
          - "htstatus"
          - "poolsp"
          - "spasp"
          - "pooltemp"
          - "spatemp"
          - "airtemp"
  - authentication: basic
    username: "admin"
    password: "password"
    scan_interval: 60
    resource: "http://192.168.1.13/status.xml"
    sensor:
      - name: "Kiddie Pool Data System"
        json_attributes_path: "$.response.system"
        value_template: "OK"
        json_attributes:
          - "runstate"
          - "model"
          - "opmode"
          - "freeze"
          - "time"
          - "sensor1"
          - "sensor2"
          - "sensor3"
          - "sensor4"
          - "version"
      - name: "Kiddie Pool Data Equipment"
        json_attributes_path: "$.response.equipment"
        value_template: "OK"
        json_attributes:
          - "circuit1"
          - "circuit2"
          - "circuit3"
          - "circuit4"
          - "circuit5"
          - "circuit6"
          - "circuit7"
          - "circuit8"
      - name: "Kiddie Pool Data Temp"
        json_attributes_path: "$.response.temp"
        value_template: "OK"
        json_attributes:
          - "htstatus"
          - "poolsp"
          - "spasp"
          - "pooltemp"
          - "spatemp"
          - "airtemp"
```
## Configuration Variables

- **`rest` (map, required)**: Integration block
- **`resource` (string, required)**: The resource or endpoint that contains the value
- **`resource_template` (template, required)**: The resource or endpoint that contains the value with template support
- **`method` (string, optional, default: GET)**: The method of the request. Either POST or GET
- **`payload` (string, optional)**: The payload to send with a POST request. Depends on the service, but usually formed as JSON
- **`payload_template` (template, optional)**: The payload to send with a POST request, with template support. Depends on the service, but usually formed as JSON
- **`verify_ssl` (boolean, optional, default: true)**: Whether to verify the SSL certificate of the endpoint
- **`ssl_cipher_list` (string, optional, default: default)**: The list of SSL ciphers to be accepted from this endpoint. `python_default` (default), `modern` or `intermediate` (inspired by Mozilla Security/Server Side TLS)
- **`timeout` (integer, optional, default: 10)**: The maximum time in seconds to wait for data from the endpoint. If the timeout is reached, the sensor will become unavailable
- **`authentication` (string, optional)**: Type of the HTTP authentication. `basic` or `digest`
- **`username` (string, optional)**: The username for accessing the REST endpoint
- **`password` (string, optional)**: The password for accessing the REST endpoint
- **`headers` (list | template, optional)**: The headers for the requests
- **`params` (list | template, optional)**: The query params for the requests
- **`scan_interval` (integer, optional, default: 30)**: The frequency in seconds to call the REST endpoint
- **`encoding` (string, optional, default: UTF-8)**: The character encoding to use if none provided in the header of the shared data
- **`sensor` (list, optional)**: A list of sensors to create from the shared data. All configuration settings that are supported by RESTful Sensor not listed above can be used here
- **`binary_sensor` (list, optional)**: A list of binary sensors to create from the shared data. All configuration settings that are supported by RESTful Binary Sensor not listed above can be used here

> **⚠️ Important**: Use either `resource` or `resource_template`.

## Using Templates

For incoming data, a value template translates incoming JSON or raw data to a valid payload. Incoming payloads are rendered with possible JSON values, so when rendering, the `value_json` can be used to access the attributes in a JSON based payload, otherwise the `value` variable can be used for non-JSON based data.

Additionally, the `this` can be used as variables in the template. The `this` attribute refers to the current entity state of the entity. Further information about this variable can be found in the template documentation.

> **Note**: Example value template with JSON:
>
> With given payload:
> ```json
> { "state": "ON", "temperature": 21.902 }
> ```
>
> Template `{{ value_json.temperature | round(1) }}` renders to `21.9`.