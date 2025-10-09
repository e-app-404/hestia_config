---
id: prompt_20250331_7917d7
slug: batch6-mac-import-hephaestus-config-updated
title: Batch6 Mac Import Hephaestus Config Updated
date: '2025-03-31'
tier: "\u03B1"
domain: operational
persona: promachos
status: approved
tags: []
version: '1.0'
source_path: batch6_mac-import_hephaestus_config_updated.yaml
author: Unknown
related: []
last_updated: '2025-10-09T02:33:22.948103'
redaction_log: []
---

hephaestus_configuration:
  template:
  - sensor:
    - name: Metadata - hephaestus/config
      unique_id: metadata_hephaestus_config
      state: ok
      attributes:
        module: Hephaestus Config
        type: config
        file: /config/hestia/packages/hephaestus/hephaestus_config.yaml
        description: Central configuration anchor for the Hephaestus tool governance
          subsystem
        subsystem: HEPHAESTUS
        dependencies: clio, charon, phanes, room_configurations.json, sensor.room_registry,
          tools
        version: 1.0.6
        last_updated: '2025-03-31'
        changelog: "{{ [\n  '2025-03-30: Initial deployment of tool cooldown and sensor\
          \ triggers',\n  '2025-03-31: Timezone-safe value_template comparisons for\
          \ cooldown logic',\n  '2025-03-31: Added changelog and metadata tracking',\n\
          \  '2025-03-31: Added Iris and Charon tools'\n] }}\n"
    - name: Hephaestus Subsystem Status
      unique_id: hephaestus_subsystem_status
      icon: mdi:check-network-outline
      state: '{% set checks = [  is_state(''binary_sensor.iris_audit_ok'', ''on''),  is_state(''binary_sensor.charon_audit_ok'',
        ''on''),  is_state(''binary_sensor.clio_cooldown_active'', ''off''),  is_state(''binary_sensor.template_monitor_problems'',
        ''off''),  is_state(''sensor.template_error_diagnostics'', ''0'')] %}{% set
        ok = checks | select(''equalto'', True) | list | count %}{% if ok == checks
        | length %}OPERATIONAL{% elif ok >= 3 %}PARTIAL{% else %}FAULT{% endif %}'
      attributes:
        last_check: '{{ now().strftime(''%Y-%m-%d %H:%M:%S'') }}'
        tools: '{{ { ''iris'': states(''binary_sensor.iris_audit_ok''), ''charon'':
          states(''binary_sensor.charon_audit_ok''), ''clio'': states(''binary_sensor.clio_cooldown_active''),
          ''template_monitor'': states(''binary_sensor.template_monitor_problems''),
          ''template_errors'': states(''sensor.template_error_diagnostics'') } }}'
    - name: Tool Cooldown Status Summary
      unique_id: tool_cooldown_status_summary
      state: "{% set clio = is_state('binary_sensor.clio_cooldown_active', 'on') %}\
        \ {% set phanes = is_state('binary_sensor.phanes_cooldown_active', 'on') %}\
        \ {% if clio or phanes %}\n  active\n{% else %}\n  clear\n{% endif %}\n"
      attributes:
        clio_cooldown: '{{ states(''binary_sensor.clio_cooldown_active'') }}'
        phanes_cooldown: '{{ states(''binary_sensor.phanes_cooldown_active'') }}'
    - name: Metadata - core/device_monitor
      unique_id: metadata_core_device_monitor_uid
      alias: meta_hestia_cerberus_protocol_variant_lights
      state: ok
      icon: mdi:access-point-check
      attributes: null
      type: watchdog
      module: Device Monitor
      file: /config/hestia/templates/device_monitor.yaml
      description: Tracks signal availability of light protocol variants (Wi-Fi, Matter)
        in real-time, with aggregated diagnostics, risk scoring, and passive trend
        metadata.
      version: 1.1.0
      last_updated: '{{ states(''sensor.device_monitor_last_updated'') }}'
      dependencies: device_abstraction.yaml, entity_registry.yaml
      changelog: '2025-04-01: Logic migrated to template library. Dynamic stats split
        into separate sensors.'
      protocol_distribution: '{{ state_attr(''sensor.device_monitor_protocol_distribution'',
        ''value'') }}'
      unavailable_count_by_protocol: '{{ state_attr(''sensor.device_monitor_unavailable_count'',
        ''value'') }}'
      offline_risk_score: '{{ states(''sensor.device_monitor_risk_score'') }}'
    - name: Abstraction Layer Health
      unique_id: sensor_abstraction_layer_health
      state: "{% set missing = namespace(count=0) %}{% for s in states if '_\u03B2\
        ' in s.entity_id or '_\u03B3' in s.entity_id or '_\u03B5' in s.entity_id or\
        \ '_\u03B6' in s.entity_id %}{% if s.state == 'unavailable' or s.state ==\
        \ 'unknown' %}{% set missing.count = missing.count + 1 %}{% endif %}{% endfor\
        \ %}{{ 'ok' if missing.count == 0 else 'missing: ' ~ missing.count }}"
      attributes:
        description: "Shows if any abstraction tier (\u03B2\u2013\u03B6) sensors are\
          \ missing or unavailable."
        tiers_monitored:
        - "_\u03B2"
        - "_\u03B3"
        - "_\u03B5"
        - "_\u03B6"
  - binary_sensor:
    - name: clio_cooldown_active
      friendly_name: Clio Cooldown Active
      value_template: '{% set last = as_datetime(states(''input_datetime.clio_last_run'')).replace(tzinfo=None)
        %} {% set cooldown = states(''input_number.tool_execution_cooldown'') | int
        %} {{ now().replace(tzinfo=None) < (last + timedelta(minutes=cooldown)) }}'
    - name: phanes_cooldown_active
      friendly_name: Phanes Cooldown Active
      value_template: '{% set last = as_datetime(states(''input_datetime.phanes_last_run'')).replace(tzinfo=None)
        %} {% set cooldown = states(''input_number.tool_execution_cooldown'') | int
        %} {{ now().replace(tzinfo=None) < (last + timedelta(minutes=cooldown)) }}'
    - name: hephaestus_room_registry_on_cooldown
      friendly_name: Room Registry Tool on Cooldown
      value_template: "{% set last = states('input_datetime.hephaestus_room_registry_last_run')\
        \ %} {% set cooldown = states('input_number.tool_execution_cooldown') | int\
        \ %} {% if last not in ['unknown', 'unavailable'] %}\n  {% set delta = (as_timestamp(now())\
        \ - as_timestamp(last)) %}\n  {{ delta < cooldown }}\n{% else %}\n  false\n\
        {% endif %}\n"
  automation:
  - alias: Check Hephaestus Package Integrity
    id: hephaestus_package_integrity
    description: Check Hephaestus integrity and notify on startup if not fully operational.
    trigger:
    - platform: homeassistant
      event: start
    condition:
    - condition: template
      value_template: '{{ states(''sensor.hephaestus_subsystem_status'') != ''OPERATIONAL''
        }}'
    action:
    - service: persistent_notification.create
      data:
        title: Hephaestus Package Health Check
        message: "\u26A0\uFE0F Hephaestus subsystem is not fully operational.\nCurrent\
          \ status: {{ states('sensor.hephaestus_subsystem_status') }}\nCheck tools\
          \ and diagnostics."

