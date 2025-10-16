---
id: ADR-0028
title: AppDaemon & Room-DB Canonicalization (Endpoints, Entities, SQL Migration)
slug: appdaemon-room-db-sql-migration
status: Proposed
related:
- ADR-0024
- ADR-0027
- ADR-0019
- ADR-0018
- ADR-0009
- ADR-0008
supersedes: []
last_updated: '2025-10-15'
date: 2025-10-12
decision: summary-concise)
author: evert-appels
tags:
- governance
- appdaemon
- room-db
- endpoints
- entities
- migration
- sql
- validation
references:
- tools: /config/bin/write-broker
- configuration: /config/packages/package_room_database.yaml, /addon_configs/a0d7b954_appdaemon/apps/**
- logs: /config/hestia/workspace/operations/logs/write_broker_*.json
- index: /config/hestia/config/index/appdaemon_index.yaml
---

# ADR-0028: AppDaemon & Room-DB Canonicalization (Endpoints, Entities, SQL Migration)

## Table of Contents

- [Decision Summary (concise)](#decision-summary-concise)
- [API_ROUTES](#api_routes)
- [ENTITY_INTERFACE](#entity_interface)
- [SQL_SCHEMA](#sql_schema)
- [MIGRATION_PLAN](#migration_plan)
- [GOVERNANCE_BLOCK](#governance_block)
- [VALIDATION_SUITE](#validation_suite)
- [ENFORCEMENT & DRIFT](#enforcement--drift)
- [ROLLBACK](#rollback)
- [ACCEPTANCE_CRITERIA](#acceptance_criteria)
- [STATUS_BLOCK](#status_block)
- [TOKEN_BLOCK](#token_block)
- [CHANGELOG](#changelog)


## Decision Summary (concise)

- **Endpoints:** AppDaemon routes **must** use the app-scoped pattern `/api/app/<app_name>/<endpoint>/...`. For Room-DB the canonical base is **`/api/app/room_db_updater/room_db`** with subpaths for health, update, sync, and reads.
- **HA Integration:** Home Assistant `rest_command` definitions **must** reference `hass_url()` and the canonical app-scoped routes; `/api/appdaemon/*` is **not** used for Room-DB operations.
- **Entities:** Expose deterministic, namespaced entities for consumers (templates/automations) with clear `device_class` mappings and regeneration rules tied to Room-DB updates.
- **Single Source of Truth:** The **SQL schema** holds authoritative room/zone configuration and telemetry. HA consumers read via AppDaemon APIs or generated entities derived from SQL.
- **Writes & Governance:** Any configuration changes (files, schemas, rest_commands) **must** be performed via **write-broker** (ADR-0027) with SHA-256 verification, atomic write, backup, and audit log.
- **Paths:** All paths resolve under the canonical `/config` root (ADR-0024). Non-canonical realpaths are read-only.

## API_ROUTES

```yaml
api_routes:
  # Canonical, app-scoped base for Room-DB operations
  base: "/api/app/room_db_updater/room_db"
  endpoints:
    health: "/health"            # GET: liveness/readiness probe
    update_config: "/update"     # POST: trigger config (re)load / regeneration
    sync: "/sync"                # POST: reconcile SQL↔HA derived artifacts
    read_room: "/room/{id}"      # GET: fetch room record by id
    read_zone: "/zone/{id}"      # GET: fetch zone record by id
validation:
  curl_examples:
    - GET "{{ hass_url('/api/app/room_db_updater/room_db/health') }}"
    - POST "{{ hass_url('/api/app/room_db_updater/room_db/update') }}"
    - POST "{{ hass_url('/api/app/room_db_updater/room_db/sync') }}"
notes:
  runtime_names:
    app_name: "room_db_updater"     # confirm in /addon_configs/a0d7b954_appdaemon/apps/**
    endpoint_group: "room_db"       # confirm in /addon_configs/a0d7b954_appdaemon/apps/**
```

## ENTITY_INTERFACE

```yaml
entities:
  naming:
    namespace_prefix: "roomdb"
    room_state_sensor: "sensor.roomdb_{room}_state"
    presence_binary: "binary_sensor.roomdb_{room}_presence"
    illuminance_sensor: "sensor.roomdb_{room}_illuminance"
    meta_last_update: "sensor.roomdb_last_update"
  device_class_map:
    presence_binary: ["presence","occupancy","motion"]
    illuminance_sensor: ["illuminance"]
  attributes_contract:
    room_state_sensor:
      must_include: ["room_id","zone_id","profile","updated_at"]
    presence_binary:
      must_include: ["room_id","confidence","updated_at"]
  update_policy:
    source_of_truth: "sql"
    regeneration_trigger: "POST /update (app route) succeeds"
    ha_side_effects:
      - "template entity regeneration where applicable"
      - "notify meta_last_update"
  deprecation:
    legacy_templates:
      policy: "maintain read-only until migration Phase 'switch' completes"
```

## SQL_SCHEMA

```yaml
sql:
  engine: "sqlite (default); optional: PostgreSQL"
  tables:
    rooms:
      columns:
        - id INTEGER PRIMARY KEY
        - name TEXT NOT NULL UNIQUE
        - zone_id INTEGER
        - enabled INTEGER NOT NULL DEFAULT 1
        - created_at TEXT NOT NULL
        - updated_at TEXT NOT NULL
    room_attributes:
      columns:
        - id INTEGER PRIMARY KEY
        - room_id INTEGER NOT NULL
        - key TEXT NOT NULL
        - value TEXT NOT NULL
        - updated_at TEXT NOT NULL
      constraints:
        - UNIQUE(room_id, key)
        - FK room_id -> rooms.id ON DELETE CASCADE
    zones:
      columns:
        - id INTEGER PRIMARY KEY
        - name TEXT NOT NULL UNIQUE
        - created_at TEXT NOT NULL
        - updated_at TEXT NOT NULL
    telemetry:
      columns:
        - id INTEGER PRIMARY KEY
        - room_id INTEGER NOT NULL
        - metric TEXT NOT NULL
        - value REAL
        - ts TEXT NOT NULL
      indexes:
        - "idx_tel_room_ts(room_id, ts)"
      constraints:
        - FK room_id -> rooms.id ON DELETE CASCADE
ddl: |
  CREATE TABLE IF NOT EXISTS rooms(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    zone_id INTEGER,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS room_attributes(
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(room_id, key),
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
  );
  CREATE TABLE IF NOT EXISTS zones(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS telemetry(
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,
    metric TEXT NOT NULL,
    value REAL,
    ts TEXT NOT NULL,
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
  );
  CREATE INDEX IF NOT EXISTS idx_tel_room_ts ON telemetry(room_id, ts);
constraints:
  - "rooms.name UNIQUE"
  - "room_attributes UNIQUE(room_id,key)"
  - "FKs ON DELETE CASCADE"
indexes:
  - "idx_tel_room_ts(room_id, ts)"
migrations:
  idempotent: true
  journal_mode: "WAL recommended"
```

## MIGRATION_PLAN

```yaml
migration:
  phases:
    - id: discovery
      actions:
        - scan_templates: "/config/packages/**"
        - inventory_entities: "/config/.storage/core.entity_registry"
        - enumerate_rest_commands: "/config/packages/package_room_database.yaml"
        - confirm_app_names: "/config/appdaemon/apps/** (ensure app='room_db_updater', endpoint='room_db')"
    - id: mapping
      actions:
        - map_automations_to_sql:
            groups: ["motion groups","lighting modes","presence policies"]
        - define_entity_mappings:
            from: "legacy template ids"
            to: "roomdb_* canonical"
    - id: implement
      actions:
        - create_sql_schema: "execute DDL"
        - seed_sql_from_yaml: "parse current YAML → INSERT rooms/attributes"
        - add_rest_commands: "hass_url() with canonical app routes"
    - id: switch
      actions:
        - flip_consumers_to_api: "templates/automations consume API or generated entities"
        - mark_legacy_read_only: true
        - deprecate_legacy_templates: "after 14-day stability window"
  rollback:
    - "restore previous YAML entities"
    - "restore database from timestamped backup"
    - "repoint rest_commands to legacy providers if needed"
  evidence:
    - "write-broker logs for all file changes"
    - "AppDaemon logs show /update and /sync invocations"
```

## GOVERNANCE_BLOCK

```yaml
governance:
  path_policy:
    canonical_root: "/config"
    readonly_roots: ["/System/Volumes/Data/homeassistant","/Volumes/HA"]
  write_policy:
    tool: "/config/bin/write-broker"
    sha256_required: true
    audit_log: "/config/hestia/workspace/operations/logs"
  endpoint_policy:
    app_scoped_only: true
    base: "/api/app/room_db_updater/room_db"
    disallow:
      - "/api/appdaemon/*"
  ci:
    validators:
      - "ha core check"
      - "curl health endpoint == 200"
      - "curl update endpoint returns 2xx"
      - "entity registry contains roomdb_* interfaces"
```

## VALIDATION_SUITE

```bash
# 1) App health (expect 200)
curl -s -o /dev/null -w "%{http_code}\n" \
  "$(hass-cli info url 2>/dev/null || echo http://127.0.0.1:8123)"/api/app/room_db_updater/room_db/health \
  -H "Authorization: Bearer ${HASS_TOKEN:?missing}"

# 2) Trigger update (expect 2xx)
curl -s -o /dev/null -w "%{http_code}\n" \
  "$(hass-cli info url 2>/dev/null || echo http://127.0.0.1:8123)"/api/app/room_db_updater/room_db/update \
  -H "Authorization: Bearer ${HASS_TOKEN:?missing}" \
  -H "Content-Type: application/json" -d '{"actor":"adr-0028","ts":"'"$(date -Iseconds)"'"}'

# 3) HA config validity
ha core check || docker exec -it homeassistant ha core check

# 4) Entities present (names are examples; adjust to your rooms)
hass-cli entity get sensor.roomdb_kitchen_state | grep '"entity_id":' || true
hass-cli entity get binary_sensor.roomdb_kitchen_presence | grep '"device_class":' || true

# 5) Write-broker evidence for any file changes
ls -1 /config/hestia/workspace/operations/logs/write_broker_*.json | tail -3
```

## ENFORCEMENT & DRIFT

```yaml
enforcement:
  drift_codes:
    - PATH_VIOLATION
    - WRITE_TOOL_BYPASS
    - MISSING_AUDIT_TRAIL
    - ENDPOINT_MISMATCH
    - ENTITY_CONTRACT_BROKEN
  on_violation:
    - block_change
    - emit_drift_event
    - require_strategist_review
  acceptance_gates:
    - "validation_suite passes"
    - "write-broker audit present for each file change"
```

## ROLLBACK

```yaml
rollback:
  file_restore: "mv <file>.wbak.<ts> <file>"
  sql_restore: "sqlite3 roomdb.sqlite '.read backup_<ts>.sql' (or pg_restore)"
  route_revert: "switch consumers to legacy YAML entities; disable API consumers"
```

## ACCEPTANCE_CRITERIA

- Health endpoint returns **200** at `/api/app/room_db_updater/room_db/health`.
- `rest_command` calls using `hass_url()` to the canonical base return **2xx** and are logged by AppDaemon.
- Canonical `roomdb_*` entities exist with correct `device_class` and required attributes.
- All configuration writes were performed via **write-broker** with SHA-256 before/after, backup, and audit JSON.
- `ha core check` passes.


## STATUS_BLOCK

```yaml
status: Proposed
governance_level: Critical
enforcement: Automated
rollout_strategy: phased
```

## TOKEN_BLOCK

```yaml
accepted_tokens:
  - ROOM_DB_GOVERNANCE
  - APPDAEMON_ENDPOINTS
  - ENTITY_CANONICALIZATION
  - SQL_MIGRATION_PATH
  - VALIDATION_GUARDRAILS
requirements:
  - canonical_config_root: "/config"
  - sha256_verification_mandatory: true
  - audit_logging_required: true
  - path_enforcement: "ADR-0024, ADR-0027"
produces:
  - canonical_endpoints
  - entity_interface_contracts
  - sql_schema_and_constraints
  - migration_runbook
  - validation_suite
```

## CHANGELOG

```yaml
changelog:
  - date: 2025-10-12
    change: "Initial proposal; codifies app-scoped endpoints, entity contracts, SQL schema, and phased migration with ADR-0024/0027 alignment."
```
