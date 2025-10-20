---
title: "Database Integration Guide"
authors: "Hestia Ops Team"
source: "Home Assistant Docs, Hestia notes"
slug: "integration-database"
tags: ["home-assistant", "ops", "integration"]
original_date: "2025-10-08"
last_updated: "2025-10-08"
url: ""
---

# Database Integration

Home Assistant uses databases to store events and parameters for history and tracking. The default database used is SQLite.


The database file is stored in your configuration directory (e.g., `<path to config dir>/home-assistant_v2.db`); however, other databases can be used. If you prefer to run a database server (e.g., PostgreSQL), use the recorder integration.

sqlite>

To work with SQLite database manually from the command-line, you will need an installation of `sqlite3`. Alternatively, DB Browser for SQLite provides a viewer for exploring the database data and an editor for executing SQL commands. First load your database with sqlite3:

```bash
sqlite3 home-assistant_v2.db
# SQLite version 3.13.0 2016-05-18 10:57:30
# Enter ".help" for usage hints.
sqlite>
```

It helps to set some options to make the output more readable:

```bash
sqlite> .header on
sqlite> .mode column
```

You could also start sqlite3 and attach the database later. Not sure what database you are working with? Check it, especially if you are going to delete data.

```bash
sqlite> .databases
# seq  name             file
# ---  ---------------  ----------------------------------------------------------
# 0    main             /home/fab/.homeassistant/home-assistant_v2.db
```

sensor.cpu                      28874
sun.sun                         21238
sensor.time                     18415
sensor.new_york                 18393
cover.kitchen_cover             17811
switch.mystrom_switch           14101
sensor.internet_time            12963
sensor.solar_angle1             11397
sensor.solar_angle              10440
group.all_switches              8018

## Schema

Get all available tables from your current Home Assistant database:

```bash
sqlite> SELECT sql FROM sqlite_master;
```

Example output (truncated):

```sql
CREATE TABLE event_data (
    data_id INTEGER NOT NULL,
    hash BIGINT,
    shared_data TEXT,
    PRIMARY KEY (data_id)
)

CREATE TABLE states (
    state_id INTEGER NOT NULL,
    entity_id CHAR(0),
    state VARCHAR(255),
    attributes CHAR(0),
    event_id SMALLINT,
    last_changed CHAR(0),
    last_changed_ts FLOAT,
    last_updated CHAR(0),
    last_updated_ts FLOAT,
    old_state_id INTEGER,
    attributes_id INTEGER,
    context_id CHAR(0),
    context_user_id CHAR(0),
    context_parent_id CHAR(0),
    origin_idx SMALLINT,
    context_id_bin BLOB,
    context_user_id_bin BLOB,
    context_parent_id_bin BLOB,
    metadata_id INTEGER, last_reported_ts FLOAT,
    PRIMARY KEY (state_id),
    FOREIGN KEY(old_state_id) REFERENCES states (state_id),
    FOREIGN KEY(attributes_id) REFERENCES state_attributes (attributes_id),
    FOREIGN KEY(metadata_id) REFERENCES states_meta (metadata_id)
)
```

To only show the details about the `states` table (since we are using that one in the next examples):

```bash
sqlite> SELECT sql FROM sqlite_master WHERE type = 'table' AND tbl_name = 'states';
```

## Query

The identification of the available columns in the table is done and we are now able to create a query. Let’s list your Top 10 entities:

```bash
sqlite> .width 30, 10
sqlite> SELECT states_meta.entity_id, COUNT(*) as count FROM states INNER JOIN states_meta ON states.metadata_id = states_meta.metadata_id GROUP BY states_meta.entity_id ORDER BY count DESC LIMIT 10;
```

Example output:

```
entity_id                       count
------------------------------  ----------
sensor.cpu                      28874
sun.sun                         21238
sensor.time                     18415
sensor.new_york                 18393
cover.kitchen_cover             17811
switch.mystrom_switch           14101
sensor.internet_time            12963
sensor.solar_angle1             11397
sensor.solar_angle              10440
group.all_switches              8018
```

## Delete

If you don’t want to keep certain entities, you can delete them permanently by using the actions provided by the recorder.