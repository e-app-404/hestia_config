---
id: prompt_20250422_7652ca
slug: batch2-task-reconstruct-enriched-room-wise-se
title: 'Batch2 Task: "Reconstruct Enriched Room Wise Se'
date: '2025-04-22'
tier: "α"
domain: extraction
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: 'batch 2/batch2-task: "Reconstruct enriched room-wise se.yml'
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.781358'
redaction_log: []
---

task: "Reconstruct enriched room-wise sensor mappings from HESTIA core registries"

source_files:
  - path: "/config/hestia/core/registry/omega_room_registry.json"
  - path: "/config/hestia/core/registry/omega_device_registry.json"
  - path: "/config/hestia/core/registry/alpha_sensor_registry.json"
  - path: "/config/hestia/core/registry/alpha_light_registry.json"

instructions:
  - For each `room` in `omega_room_registry`, extract and structure all available sensor signals.
  - Map each sensor signal type (`temperature`, `humidity`, `motion`, `occupancy`, `illuminance`, `contact`) to its device ID (omega/alpha/etc).
  - For each sensor ID, hydrate with canonical metadata from `alpha_sensor_registry`:
      - signal type
      - protocol origin and stack
      - reliability score
      - fallback protocol settings
      - last_seen timestamp
      - device confidence metrics
      - history of protocol transitions
  - If a sensor reports multiple signals (e.g., `living_room_multipurpose_sensor_omega`), split signals into separate logical sensor blocks with shared base attributes.
  - Use `omega_device_registry` to normalize platform, firmware, and entity origin context.
  - Include integration-specific fields such as `entity_id`, `canonical_id`, and `device_class`.
  - Do not omit sensors listed under `alpha` or `omega` keys even if `beta...mu` are null.
  - Structure each output block by `room_id`, including `room_name` and array of enriched sensors.

output_format:
  type: "yaml"
  structure:
    room_id:
      room_name: ...
      sensors:
        - signal_type: ...
          source: ...
          protocols: [mqtt, zha]
          location: {area: desk, room: bedroom}
          metrics:
            reliability: 98
            last_seen: 2025-04-22T15:30:00
          confidence:
            entity: 90
            device: 85
            relationship: 95
          integrations:
            - platform: mqtt
              entity_id: binary_sensor.bedroom_occupancy
              canonical_id: bedroom_occupancy_α

