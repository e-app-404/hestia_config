---
title: "MariaDB Addon — Adjust settings to improve performance"
source: "community.home-assistant.io"
date: "2025-01-10"
summary:
  suggested_defaults:
    innodb_buffer_pool_size: "12G"
    innodb_log_buffer_size: "32M"
    innodb_log_file_size: "512M"
    innodb_io_capacity: 2000
    innodb_io_capacity_max: 4000
    max_connections: 512
    table_open_cache: 4000
    tmp_table_size: "512M"
  security_recommendations:
    - "secure-file-priv=/tmp"
    - "skip-symbolic-links"
    - "local-infile=0"
  notes:
    - "Disabling binary logging (`--skip-log-bin`) improves write performance when point-in-time or replication is not required."
references:
  - "https://community.home-assistant.io/t/improve-your-home-assistant-performance-with-mariadb-tuning"
url: "https://community.home-assistant.io/t/mariadb-addon-adjust-settings-to-improve-performance-and-persists-after-reboot/825841"
---

# [MariaDB Addon] Adjust settings to improve performance and persist after reboot

With the addon update, two new optional configuration options were introduced: `parameters.innodb_buffer_pool_size` and `mariadb_server_args`. These allow more control over MariaDB server parameters and improved performance tuning.

Repository change reference: github.com/home-assistant/addons (fixes #3754)

## Overview

This guide shares a template of useful `mariadb_server_args` entries (commented) and examples to monitor MariaDB directly from Home Assistant using `sql` sensors.

## mariadb_server_args template

Place the following list under your MariaDB addon configuration (as `mariadb_server_args`) to tune the server. All lines are examples — uncomment or adjust as required for your hardware.

```yaml
# Example mariadb_server_args (list of server arguments)
mariadb_server_args:
  # InnoDB Buffer Pool Settings
  # Controls how much RAM is allocated to InnoDB to cache table and index data.
  # Recommendation: 70-80% of available RAM for dedicated servers.
  - "--innodb_buffer_pool_size=12G"

  # InnoDB Log Settings
  - "--innodb_log_buffer_size=32M"
  - "--innodb_log_file_size=512M"

  # InnoDB File and I/O Settings
  - "--innodb_file_per_table=1"
  - "--innodb_flush_log_at_trx_commit=2"
  - "--innodb_flush_method=O_DIRECT"
  - "--innodb_io_capacity=2000"
  - "--innodb_io_capacity_max=4000"
  - "--innodb_read_io_threads=8"
  - "--innodb_write_io_threads=8"

  # InnoDB Optimization Settings
  - "--innodb_stats_persistent=1"
  - "--innodb_adaptive_hash_index=1"

  # Buffer and Cache Settings
  - "--sort_buffer_size=4M"
  - "--read_buffer_size=2M"
  - "--read_rnd_buffer_size=2M"
  - "--join_buffer_size=2M"
  - "--tmp_table_size=512M"
  - "--max_heap_table_size=512M"

  # Connection and Cache Settings
  - "--max_connections=512"
  - "--table_open_cache=4000"
  - "--table_definition_cache=2000"
  - "--thread_cache_size=200"
  - "--open_files_limit=65535"

  # Network Settings
  - "--max_allowed_packet=64M"
  - "--net_buffer_length=1M"
  - "--interactive_timeout=28800"
  - "--wait_timeout=28800"

  # Performance and Monitoring Settings
  - "--performance_schema=ON"
  - "--skip-log-bin"
  - "--slow_query_log=1"
  - "--long_query_time=2"
  - "--skip-name-resolve"

  # Security Settings
  - "--secure-file-priv=/tmp"
  - "--skip-symbolic-links"
  - "--local-infile=0"
```

## Monitoring

As an example, you can add these SQL queries in `configuration.yaml` (no plugin is needed, it comes integrated in HA):

```yaml
sql:
  # MariaDB Status
  - name: "MariaDB Status"
    query: >-
      SELECT 'running' as status 
      FROM information_schema.GLOBAL_STATUS 
      WHERE VARIABLE_NAME = 'Uptime' 
      AND CAST(VARIABLE_VALUE AS UNSIGNED) > 0;
    column: "status"
    value_template: "{{ value if value else 'stopped' }}"

  # MariaDB Version
  - name: "MariaDB Version"
    query: >-
      SELECT @@version as version;
    column: "version"

  # MariaDB Performance (queries per second)
  - name: "MariaDB Performance"
    query: >-
      SELECT CONCAT(
        ROUND(
          (SELECT VARIABLE_VALUE 
           FROM information_schema.GLOBAL_STATUS 
           WHERE VARIABLE_NAME = 'Queries') / 
          (SELECT VARIABLE_VALUE 
           FROM information_schema.GLOBAL_STATUS 
           WHERE VARIABLE_NAME = 'Uptime')
        ), ' q/s') as performance;
    column: "performance"

  # Database size
  - name: "Database Size"
    query: >-
      SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size 
      FROM information_schema.tables 
      WHERE table_schema = 'homeassistant';
    column: "size"
    unit_of_measurement: "MB"
    value_template: "{{ value | float }}"

  # Table count
  - name: "Database Tables Count"
    query: >-
      SELECT COUNT(*) as count 
      FROM information_schema.tables 
      WHERE table_schema = 'homeassistant';
    column: "count"
    unit_of_measurement: "tables"

  # Total records
  - name: "Database Total Records"
    query: >-
      SELECT COUNT(*) as count 
      FROM states;
    column: "count"
    unit_of_measurement: "records"

  # MariaDB uptime
  - name: "MariaDB Uptime"
    query: >-
      SELECT VARIABLE_VALUE as value
      FROM information_schema.GLOBAL_STATUS 
      WHERE VARIABLE_NAME = 'Uptime';
    column: "value"
    unit_of_measurement: "seconds"

  # Active connections
  - name: "MariaDB Connections"
    query: >-
      SELECT VARIABLE_VALUE as value
      FROM information_schema.GLOBAL_STATUS 
      WHERE VARIABLE_NAME = 'Threads_connected';
    column: "value"
    unit_of_measurement: "connections"

  # Total queries
  - name: "MariaDB Questions"
    query: >-
      SELECT VARIABLE_VALUE as value
      FROM information_schema.GLOBAL_STATUS 
      WHERE VARIABLE_NAME = 'Questions';
    column: "value"
    unit_of_measurement: "queries"

  # MariaDB Buffer Pool Size
  - name: "MariaDB Buffer Pool Size"
    query: >-
      SELECT CONCAT(ROUND(@@innodb_buffer_pool_size/1024/1024/1024, 1), ' GB') as value;
    column: "value"

  # MariaDB Max Connections
  - name: "MariaDB Max Connections"
    query: >-
      SELECT @@max_connections as value;
    column: "value"

  # MariaDB InnoDB Log File Size
  - name: "MariaDB Log File Size"
    query: >-
      SELECT CONCAT(ROUND(@@innodb_log_file_size/1024/1024, 0), ' MB') as value;
    column: "value"

  # MariaDB Tmp Table Size
  - name: "MariaDB Tmp Table Size"
    query: >-
      SELECT CONCAT(ROUND(@@tmp_table_size/1024/1024, 0), ' MB') as value;
    column: "value"

  # MariaDB IO Capacity
  - name: "MariaDB IO Capacity"
    query: >-
      SELECT @@innodb_io_capacity as value;
    column: "value"

  # MariaDB IO Threads
  - name: "MariaDB IO Threads"
    query: >-
      SELECT CONCAT(
        'Read: ', @@innodb_read_io_threads,
        ', Write: ', @@innodb_write_io_threads
      ) as value;
    column: "value"

  # MariaDB Table Cache
  - name: "MariaDB Table Cache"
    query: >-
      SELECT @@table_open_cache as value;
    column: "value"

  # MariaDB Buffer Sizes
  - name: "MariaDB Buffer Sizes"
    query: >-
      SELECT CONCAT(
        'Sort: ', ROUND(@@sort_buffer_size/1024/1024, 0), 'M, ',
        'Read: ', ROUND(@@read_buffer_size/1024/1024, 0), 'M, ',
        'Join: ', ROUND(@@join_buffer_size/1024/1024, 0), 'M'
      ) as value;
    column: "value"
```

## Notes and recommendations

- The `innodb_buffer_pool_size` default (128M) is conservative; increase for dedicated DB hosts.
- For systems without replication or point-in-time recovery needs, disabling binary logs (`--skip-log-bin`) improves write performance.
- Monitor slow queries and buffer pool usage after changing sizes; adjust incrementally.
- Ensure `tmp_table_size` and `max_heap_table_size` are aligned to avoid on-disk tmp tables.

