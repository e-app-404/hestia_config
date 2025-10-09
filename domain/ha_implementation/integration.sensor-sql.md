---
title: "SQL sensor integration"
authors: "Home Assistant"
source: "Home Assistant Docs"
slug: "sql-sensor-integration"
tags: ["home-assistant","sql","sensor","database","recorder","ops", "adr", "governance"]
original_date: "2022-04-05"
last_updated: "2025-09-28"
url: "https://www.home-assistant.io/integrations/sql/"
---

# SQL sensor integration

The SQL sensor integration lets you populate a Home Assistant sensor's state and
attributes from an SQL database supported by SQLAlchemy. It's commonly used with
the Recorder database but also supports external data sources.

This integration can be configured via the UI (config flow) or by YAML.

## Example (YAML)

Add one or more queries to your `configuration.yaml`. A sensor is created per
query. After saving, restart Home Assistant and the integration will appear at
Settings > Devices & Services.

```yaml
# Example configuration.yaml
sql:
  - name: Sun state
    query: >-
      SELECT
        states.state
      FROM
        states
        LEFT JOIN state_attributes ON (
          states.attributes_id = state_attributes.attributes_id
        )
      WHERE
        metadata_id = (
          SELECT
            metadata_id
          FROM
            states_meta
          WHERE
            entity_id = 'sun.sun'
        )
      ORDER BY
        state_id DESC
      LIMIT
        1;
    column: "state"
```

## Configuration variables

- **`sql` (map, required)**: integration block
- **`db_url` (string, optional)**: database URL (defaults to recorder db_url if omitted)
- **`name` (template, required)**: sensor name
- **`query` (string, required)**: SQL query (should return at most one row)
- **`column` (string, required)**: column name to use for the sensor state
- **`unit_of_measurement` (string, optional)**
- **`value_template` (template, optional)**
- **`unique_id` (string, optional)**
- **`device_class` (string, optional)**
- **`state_class` (string, optional)**
- **`icon` (template, optional)**
- **`picture` (template, optional)**
- **`availability` (template, optional)**

## Data updates and custom polling

By default the integration polls the query every 30 seconds. To use a custom
polling interval, disable polling in the integration's System options and create
an automation that calls `homeassistant.update_entity` at your desired rate.

Example automation action to update one or more entities:

```yaml
service: homeassistant.update_entity
target:
  entity_id:
    - sensor.your_sql_sensor
    - sensor.another_sql_sensor
```

## Templates

If your query returns JSON or raw payload, use `value_template` to extract the
value. `value_json` is available for JSON payloads and `value` for non-JSON
payloads. The `this` variable refers to the current entity state in templates.

Example value template (JSON payload):

Given payload:

```json
{ "state": "ON", "temperature": 21.902 }
```

Template:

```jinja
{{ value_json.temperature | round(1) }}
```

Renders to `21.9`.

## Examples (SQL queries)

### Current state of an entity

Retrieve the last recorded state for `sensor.temperature_in`:

```sql
SELECT
  states.state
FROM
  states
WHERE
  metadata_id = (
    SELECT
      metadata_id
    FROM
      states_meta
    WHERE
      entity_id = 'sensor.temperature_in'
  )
ORDER BY
  state_id DESC
LIMIT
  1;
```

Use `state` as the `column`.

### Previous state of an entity

Get the previously recorded state:

```sql
SELECT
  states.state
FROM
  states
WHERE
  state_id = (
    SELECT
      states.old_state_id
    FROM
      states
    WHERE
      metadata_id = (
        SELECT
          metadata_id
        FROM
          states_meta
        WHERE
          entity_id = 'sensor.temperature_in'
      )
      AND old_state_id IS NOT NULL
    ORDER BY
      last_updated_ts DESC
    LIMIT
      1
  );
```

### State of an entity X time ago

Get the state from a relative time (e.g. 1 day ago):

```sql
SELECT
  states.state
FROM
  states
  INNER JOIN states_meta ON
    states.metadata_id = states_meta.metadata_id
WHERE
  states_meta.entity_id = 'sensor.temperature_in'
  AND last_updated_ts <= strftime('%s', 'now', '-1 day')
ORDER BY
  last_updated_ts DESC
LIMIT
  1;
```

Replace `-1 day` with e.g. `-1 hour` for different offsets. Note results may
not be exact depending on your recording frequency.

On MariaDB use this where clause instead:

```sql
AND last_updated_ts <= UNIX_TIMESTAMP(NOW() - INTERVAL 1 DAY)
```

### Database size queries

- Postgres:

```sql
SELECT pg_database_size('dsmrreader')/1024/1024 as db_size;
```

Use `db_size` as the `column` and set the device class to `Data size`.

- MariaDB/MySQL (replace `homeassistant` with your DB name):

```sql
SELECT table_schema "database", Round(Sum(data_length + index_length) / POWER(1024,2), 1) "value"
FROM information_schema.tables
WHERE table_schema="homeassistant"
GROUP BY table_schema;
```

- SQLite:

```sql
SELECT ROUND(page_count * page_size / 1024 / 1024, 1) as size FROM pragma_page_count(), pragma_page_size();
```

Use `size` as the column. The returned unit is MiB—configure the unit and
device class accordingly for UI unit conversion.

## Notes

> **Important considerations:**
> 
> - If `db_url` is not provided the integration connects to the Recorder database
> - Only the first row returned by the query is used
> - The integration sets all returned columns as attributes on the entity

## Good vs bad patterns

When authoring YAML for SQL sensors you may encounter two styles. Prefer the top-level `sql:` list form shown below — it's clearer when included from `domain/sensor` and aligns with Home Assistant's documentation.

❌ **Old/deprecated style (avoid)**:

```yaml
sensor:
  - platform: sql
    db_url: ...
    queries:
      - name: "Some sensor"
        query: "..."
        column: "value"
```

✅ **Recommended style (use this)**:

```yaml
sql:
  - name: "Some sensor"
    db_url: ...
    query: "..."
    column: "value"
```

The recommended `sql:` style makes it easy to include these files via `!include_dir_merge_list` for `domain/sensor` and avoids confusion when multiple sensor files are merged.
