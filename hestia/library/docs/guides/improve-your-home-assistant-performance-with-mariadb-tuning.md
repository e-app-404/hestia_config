---
title: "Improve Your Home Assistant Performance with MariaDB Tuning"
source: "community.home-assistant.io"
date: "2025-01-10"
summary:
  recommended_runtime_changes:
    innodb_buffer_pool_size: "12G"
    innodb_log_buffer_size: "8M"
    max_connections: 128
    thread_cache_size: 32
    tmp_table_size: "256M"
    query_cache_size: "64M"
    query_cache_type: 1
  persistence_notes:
    - "Runtime SQL changes are immediate but may not persist across full container restarts."
    - "phpMyAdmin variable edits have been reported to persist after some HA updates."
    - "Recommend reapply at boot using mysql command integration (jmrplens approach)."
url: "https://community.home-assistant.io/t/improve-your-home-assistant-performance-with-mariadb-tuning/813785"
---

# Turbocharge Your Home Assistant with MariaDB Tuning

Over the past few months, the author observed progressive performance degradation on Home Assistant over time. Dashboards and device responses (e.g., Shelly devices flashed with ESPHome) became unreliable despite stable CPU and power metrics. Increasing host RAM did not resolve the issue — MariaDB defaults were the likely culprit.

## A Word of Warning
Back up your database before making changes. These steps should not corrupt data when applied carefully, but backups are critical.

This guide assumes you're using the MariaDB add-on and have at least an entry-level understanding of databases.

## Why tuning is tricky

- The MariaDB add-on is managed by the Home Assistant Supervisor and built from a preconfigured image; editing configuration inside the container does not necessarily persist across container or host restarts.
- The `ha addons rebuild` command doesn’t apply to image-based add-ons like MariaDB.
- Runtime changes (SQL commands) are immediate but may be lost on full container/host restart unless re-applied at boot.

Edits via phpMyAdmin variables UI have been reported to persist after certain HA updates; however, the safest approach is an automated reapply-on-boot (for example, the `mysql command` custom integration as suggested by @jmrplens).

## Default settings (tuned for low-end devices)

The default `mariadb-server.cnf` includes conservative values suitable for Pi-like devices (excerpt):

```ini
port=3306
log_error=mariadb.err
datadir=/data/databases
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
skip-name-resolve
key_buffer_size = 16M
max_connections = 64
myisam_sort_buffer_size = 8M
net_buffer_length = 16K
read_buffer_size = 256K
read_rnd_buffer_size = 512K
sort_buffer_size = 512K
join_buffer_size = 128K
table_open_cache = 64
thread_cache_size = 8
tmp_table_size = 16M
query_cache_limit = 1M
query_cache_size = 0M
query_cache_type = 0
innodb_buffer_pool_size = 128M
innodb_log_buffer_size = 8M
innodb_log_file_size = 48M
max_binlog_size = 96M
```

These defaults are low for more capable hardware (e.g., NUC with 32GB RAM). Increasing buffer sizes allows MariaDB to cache more data in memory and reduce I/O.

## How to tune MariaDB settings (runtime SQL)

Use the SQL console in phpMyAdmin or a MySQL client to set runtime variables. Example commands:

```sql
-- Set InnoDB Buffer Pool Size to 12 GB
SET GLOBAL innodb_buffer_pool_size = 12 * 1024 * 1024 * 1024;

-- Set InnoDB Log Buffer Size to 8 MB
SET GLOBAL innodb_log_buffer_size = 8 * 1024 * 1024;

-- Set Max Connections to 128
SET GLOBAL max_connections = 128;

-- Set Thread Cache Size to 32
SET GLOBAL thread_cache_size = 32;

-- Set Temporary Table Size to 256 MB
SET GLOBAL tmp_table_size = 256 * 1024 * 1024;

-- Set Query Cache Size to 64 MB
SET GLOBAL query_cache_size = 64 * 1024 * 1024;

-- Enable Query Cache
SET GLOBAL query_cache_type = 1;
```

### Verify your changes

```sql
SHOW VARIABLES WHERE Variable_name IN (
        'innodb_buffer_pool_size',
        'innodb_log_buffer_size',
        'max_connections',
        'thread_cache_size',
        'tmp_table_size',
        'query_cache_size',
        'query_cache_type'
);
```

## Observed results

- Improved dashboard performance (especially with many ApexCharts cards).
- Faster device response (snappy light switching).
- Increased host memory usage as MariaDB caches more data in RAM.

## Final thoughts & developer suggestions

- Predefined configuration profiles in the MariaDB add-on (Pi / NUC / Server) would be helpful.
- Exposing more my.cnf options in the add-on UI would allow safer persistence of tuned values.

If you found this guide helpful or want improvements (example scripts to reapply settings at boot), say so and I can add them.
