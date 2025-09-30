---
title: "RESTful Command"
authors: "Home Assistant"
source: "Home Assistant Docs"
slug: "restful_command"
tags: ["home-assistant","ops","integration"]
original_date: "2022-04-05"
last_updated: "2025-09-24"
url: "https://www.home-assistant.io/integrations/rest_command/"
---

# RESTful Command (Home Assistant)

This document summarizes the `rest_command` integration for Home Assistant and provides examples for configuration, testing, and usage in automations.

For full official documentation see: https://www.home-assistant.io/integrations/rest_command/

## Example configuration.yaml entry

```yaml
rest_command:
  example_request:
    url: "http://example.com/"
```

## Configuration variables

- **`service_name` (map, required)**: The name used to expose the action, e.g. `rest_command.example_request`
- **`url` (string/template, required)**: The URL (supports templates) for the request
- **`method` (string, optional, default: `get`)**: HTTP method to use: `get`, `patch`, `post`, `put`, or `delete`
- **`headers` (map, optional)**: Headers for the request
- **`payload` (string/template, optional)**: Body to send with the request
- **`authentication` (string, optional, default: `basic`)**: `basic` or `digest`
- **`username` (string, optional)**: Username for HTTP auth
- **`password` (string, optional)**: Password for HTTP auth
- **`timeout` (string, optional, default: `10`)**: Timeout in seconds
- **`content_type` (string, optional)**: Content type for the request
- **`verify_ssl` (boolean, optional, default: `true`)**: Verify SSL certificate
- **`insecure_cipher` (boolean, optional, default: `false`)**: Allow insecure ciphers for legacy servers

## Examples

### Digest authentication

```yaml
rest_command:
  secured_command:
    url: "http://example.com/api/secure-endpoint"
    method: post
    authentication: digest
    username: "your_username"
    password: "your_password"
    payload: '{"data": "example"}'
    content_type: "application/json"
```

### Simple GET command

```yaml
rest_command:
  traefik_get_rawdata:
    url: http://127.0.0.1:8080/api/rawdata
    method: GET
```

## Using REST command responses in automations

REST commands return a response dictionary with `status` (HTTP code), `content` (body as text or JSON), and `headers`. You can capture the response in automations using `response_variable` and act on it.

Example: call a REST command and process the Traefik response

```yaml
automation:
  - alias: "Check API response"
    triggers:
      - platform: time_pattern
        minutes: "/5"
    action:
      - service: rest_command.traefik_get_rawdata
        data: {}
        response_variable: traefik_response
      - condition: template
        value_template: "{{ traefik_response.status == 200 }}"
      - variables:
          routers: "{{ traefik_response.content.routers }}"
          router_errors: >
            {%- for router in routers -%}
              {%- if 'error' in routers[router] -%}
                {{ router }}: {{ routers[router]['error'] }}
              {% endif -%}
            {%- endfor -%}
      - condition: template
        value_template: "{{ router_errors|length > 0 }}"
      - service: notify.mobile_app_iphone
        data:
          title: "Traefik errors"
          message: "{{ router_errors }}"
```

If the REST command fails to reach the endpoint, fallback notifications may be used.

## Templates for dynamic payloads

Commands can use Jinja templates. Variables passed to the action are available for templating.

**Example with dynamic variables:**

```yaml
rest_command:
  my_request:
    url: https://slack.com/api/users.profile.set
    method: POST
    headers:
      authorization: !secret rest_headers_secret
      accept: "application/json, text/html"
      user-agent: 'Mozilla/5.0 {{ useragent }}'
    payload: '{"profile":{"status_text": "{{ status }}","status_emoji": "{{ emoji }}"}}'
    content_type: 'application/json; charset=utf-8'
    verify_ssl: true
```

## How to test your new REST command

Call the action from **Developer Tools → Services** with JSON data, for example:

```json
{
  "status": "My Status Goes Here",
  "emoji": ":plex:"
}
```

## Using a REST command as an action in an automation

```yaml
automation:
  - alias: "Arrive at Work"
    trigger:
      - platform: zone
        entity_id: device_tracker.my_device
        zone: zone.work
        event: enter
    action:
      - service: rest_command.my_request
        data:
          status: "At Work"
          emoji: ":calendar:"
```