---
title: "MariaDB GRANT — concise examples for Home Assistant"
authors: "Hestia / MariaDB (trimmed)"
source: "MariaDB reference (condensed)"
slug: "mariadb-grant-hestia"
tags: ["mariadb","sql","ops","database","ha"]
original_date: "2019-01-01"
last_updated: "2025-10-03"
url: "https://mariadb.com/kb/en/grant/"
---

This page is a focused, practical reference of common GRANT examples for Home Assistant users running the MariaDB (or MySQL-compatible) add-on or an external MariaDB/MySQL server.

Keep this short and actionable: basic privilege levels, least-privilege examples for the Recorder integration, replication/replica user hints, TLS/host restrictions, and quick troubleshooting steps.

### Quick contract
- Inputs: SQL client with an administrative account (root or equivalent).
- Outputs: SQL GRANT statements for a least-privilege HA recorder user, optional replication user, and notes for TLS and host-scoped users.
- Error modes: permission denied, missing user (NO_AUTO_CREATE_USER), connection refused/TLS mismatch.

## Recommended: create a dedicated recorder user (least privilege)

Home Assistant's Recorder only needs to INSERT/UPDATE/DELETE and SELECT on the HA database. Create a dedicated user restricted to the database and host:

```sql
-- Replace values in UPPER_CASE
CREATE DATABASE IF NOT EXISTS homeassistant;
CREATE USER 'ha_recorder'@'192.168.1.%' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE, INDEX
  ON homeassistant.*
  TO 'ha_recorder'@'192.168.1.%';
FLUSH PRIVILEGES;
```

- Use a host restriction (here: `192.168.1.%`) or `localhost` when the DB is local. Avoid using `'%`' unless necessary.
- For MySQL/MariaDB 10.4+ you can also `CREATE USER` followed by `GRANT` rather than implicit creation.

Notes on host selection
- `localhost` (or socket) — safest when the DB runs on the same host/container as Home Assistant.
- `192.168.1.%` (subnet) — useful for LAN-only access; prefer a specific subnet rather than `'%'.
- `'%'` — allows any host and greatly increases exposure; avoid in production.

Minimal server privilege caveat
- Some servers or third-party integrations may require additional privileges (for example, `CREATE TEMPORARY TABLES` for large schema migrations or vendor tooling). If you see schema upgrade errors during a Core update, check the add-on logs and consider temporarily granting the required privilege only for the duration of the upgrade.

## Optional: readonly user for analytics or reporting

```sql
CREATE USER 'ha_readonly'@'%' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT SELECT ON homeassistant.* TO 'ha_readonly'@'%';
FLUSH PRIVILEGES;
```

## Optional: replica/replication user (if you run replicas)

Replication users require specific REPLICATION privileges:

```sql
CREATE USER 'ha_replica'@'replica-host.example' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'ha_replica'@'replica-host.example';
FLUSH PRIVILEGES;
```

## TLS and host restrictions
- Use `REQUIRE SSL` / `REQUIRE X509` if your server and clients support TLS and you need to protect traffic between Home Assistant and the DB.
- Prefer host-restricted accounts (`'user'@'host'`) to limit exposure.

Example requiring TLS (server must be configured with certificates):

```sql
CREATE USER 'ha_secure'@'10.0.0.%' IDENTIFIED BY 'STRONG';
GRANT SELECT, INSERT, UPDATE, DELETE ON homeassistant.* TO 'ha_secure'@'10.0.0.%' REQUIRE SSL;
FLUSH PRIVILEGES;
```

## When you might be tempted to use ALL PRIVILEGES (don't)
- Avoid `GRANT ALL PRIVILEGES ON *.*` for application users. That creates unnecessary blast radius and is not required for Recorder.

## Least-privilege checklist for HA Recorder users
- Database exists and owned by the DB admin (or created with the CREATE DATABASE statement above).
- User granted only db-scoped privileges (SELECT, INSERT, UPDATE, DELETE, INDEX) on `homeassistant.*`.
- Host restriction applied where possible (`localhost` or specific subnet).
- TLS enforced for cross-network connections.

## Common errors and quick fixes
- ERROR 1045 (28000): Access denied — verify username/host and password; check `SHOW GRANTS FOR 'user'@'host'`.
- ERROR 1133 (28000): Can't find any matching row in the user table — happens when NO_AUTO_CREATE_USER is set and you used GRANT to implicitly create a user without authentication info. Use `CREATE USER` first.
- Connection refused or TLS errors — verify MariaDB TLS config, client certs, and `REQUIRE` options on the account.

### Troubleshooting quick table

| Symptom | Likely cause | Quick action |
|---|---|---|
| Access denied (1045) | Wrong credentials or host mismatch | Verify `user@host` in `mysql.user`; run `SHOW GRANTS FOR 'user'@'host'` |
| Can't find user (1133) | NO_AUTO_CREATE_USER set and GRANT implicit create failed | Use `CREATE USER 'user'@'host' IDENTIFIED BY 'pw'` then `GRANT` |
| Connection refused / timeout | Server not reachable or port blocked | Check add-on network, container ports, firewall rules, and MariaDB service status |
| TLS handshake errors | Missing / mismatched certs or REQUIRE options | Ensure server has certs and client supports TLS; remove REQUIRE on account to test briefly |

## Privilege management tips
- Use `SHOW GRANTS FOR 'ha_recorder'@'host';` to confirm grants.
- Use `REVOKE` to remove privileges, then `FLUSH PRIVILEGES` if necessary.
- Avoid `WITH GRANT OPTION` for application users.

## Example: configure Home Assistant Recorder to use MariaDB add-on
In `configuration.yaml` (example):

```yaml
recorder:
  db_url: mysql://ha_recorder:REPLACE_WITH_STRONG_PASSWORD@192.168.1.10/homeassistant?charset=utf8mb4
  purge_keep_days: 7
```

If you run the MariaDB add-on in Home Assistant, use the add-on's exposed port and a host-restricted user (or `localhost` when running in the same host namespace).

## Emergency recovery (lost root password)
-- Start MariaDB with `--skip-grant-tables` to reset root credentials (operator task). This bypasses GRANTS — follow MariaDB docs and secure the server afterwards.

**Quick recovery checklist**
1. Stop MariaDB and restart with `--skip-grant-tables` (temporarily, in maintenance window).
2. Connect locally and reset the root password using `ALTER USER 'root'@'localhost' IDENTIFIED BY 'NEW_STRONG_PASSWORD';` (or follow your distro docs).
3. Restart MariaDB normally (remove `--skip-grant-tables`).
4. Verify `SHOW GRANTS FOR 'root'@'localhost';` and test connection from Home Assistant.
5. Rotate secrets and audit access logs — treat the server as potentially compromised while auth was disabled.

**Quick test command**
After creating the user, verify connectivity and privileges from a host that should be allowed:
  
```bash
# Test connection and a simple query (replace host/user/password)
mysql -u ha_recorder -p -h 192.168.1.10 -e "SELECT 1;"

# Show grants for the created account
mysql -u root -p -h 192.168.1.10 -e "SHOW GRANTS FOR 'ha_recorder'@'192.168.1.%';"
```

## Further reading
- Official MariaDB GRANT reference: https://mariadb.com/kb/en/grant/
- MariaDB user and authentication docs: https://mariadb.com/kb/en/authentication/

---

> Notes: This document is intentionally concise. For full privilege tables and plugin-specific auth options, consult the upstream MariaDB documentation linked above.

binlog_stmt_cache_size

expire_logs_days

log_bin_compress

log_bin_compress_min_len

log_bin_trust_function_creators

max_binlog_cache_size

max_binlog_size

max_binlog_stmt_cache_size

sql_log_bin and

sync_binlog.

BINLOG MONITOR
Current
< 10.5
New name for REPLICATION CLIENT. REPLICATION CLIENT can still be used, though.

Permits running SHOW commands related to the binary log, in particular the SHOW BINLOG STATUS and SHOW BINARY LOGS statements.

BINLOG REPLAY
Current
< 10.5
Enables replaying the binary log with the BINLOG statement (generated by mariadb-binlog), executing SET timestamp when secure_timestamp is set to replication, and setting the session values of system variables usually included in BINLOG output, in particular:

gtid_domain_id

gtid_seq_no

pseudo_thread_id

server_id.

CONNECTION ADMIN
Enables administering connection resource limit options. This includes ignoring the limits specified by max_user_connections and max_password_errors, and allowing one extra connection over max_connections

The statements specified in init_connect are not executed, killing connections and queries owned by other users is permitted. The following connection-related system variables can be changed:

connect_timeout

disconnect_on_expired_password

extra_max_connections

init_connect

max_connections

max_connect_errors

max_password_errors

proxy_protocol_networks

secure_auth

slow_launch_time

thread_pool_exact_stats

thread_pool_dedicated_listener

thread_pool_idle_timeout

thread_pool_max_threads

thread_pool_min_threads

thread_pool_oversubscribe

thread_pool_prio_kickup_timer

thread_pool_priority

thread_pool_size, and

thread_pool_stall_limit.

CREATE USER
Create a user using the CREATE USER statement, or implicitly create a user with the GRANT statement.

FEDERATED ADMIN
Current
< 10.5
Execute CREATE SERVER, ALTER SERVER, and DROP SERVER statements.

FILE
Read and write files on the server, using statements like LOAD DATA INFILE or functions like LOAD_FILE(). Also needed to create CONNECT outward tables. MariaDB server must have the permissions to access those files.

GRANT OPTION
Grant global privileges. You can only grant privileges that you have.

PROCESS
Show information about the active processes, for example via SHOW PROCESSLIST or mariadb-admin processlist. If you have the PROCESS privilege, you can see all threads. Otherwise, you can see only your own threads (that is, threads associated with the MariaDB account that you are using).

READ_ONLY ADMIN
Current
< 10.11
< 10.5
User ignores the read_only system variable, and can perform write operations even when the read_only option is active.

The READ_ONLY ADMIN privilege has been removed from SUPER. The benefit of this is that one can remove the READ_ONLY ADMIN privilege from all users and ensure that no one can make any changes on any non-temporary tables. This is useful on replicas when one wants to ensure that the replica is kept identical to the primary.

RELOAD
Execute FLUSH statements or equivalent mariadb-admin commands.

REPLICATION CLIENT
Current
< 10.5
Execute SHOW MASTER STATUS and SHOW BINARY LOGS informative statements. Renamed to BINLOG MONITOR (but still supported as an alias for compatibility reasons).

Current
< 10.6
Execute SHOW MASTER STATUS and SHOW BINARY LOGS informative statements. Using BINLOG MONITOR instead is still supported as an alias.

REPLICATION MASTER ADMIN
Current
< 10.5
Permits administration of primary servers, including the SHOW REPLICA HOSTS statement, and setting the gtid_binlog_state, gtid_domain_id, master_verify_checksum and server_id system variables.

REPLICA MONITOR
Current
Reasoning
< 10.5.9
Permit SHOW REPLICA STATUS and SHOW RELAYLOG EVENTS.

See Reasoning tab as to why this was implemented.

REPLICATION REPLICA
Current
< 10.5
Synonym for REPLICATION SLAVE.

REPLICATION SLAVE
Current
< 10.5
Accounts used by replica servers on the primary need this privilege. This is needed to get the updates made on the master. REPLICATION REPLICA is an alias for REPLICATION SLAVE.

REPLICATION SLAVE ADMIN
Current
< 10.5
Permits administering replica servers, including START REPLICA/SLAVE, STOP REPLICA/SLAVE, CHANGE MASTER, SHOW REPLICA/SLAVE STATUS, SHOW RELAYLOG EVENTS statements, replaying the binary log with the BINLOG statement (generated by mariadb-binlog), and setting the system variables:

gtid_cleanup_batch_size

gtid_ignore_duplicates

gtid_pos_auto_engines

gtid_slave_pos

gtid_strict_mode

init_slave

read_binlog_speed_limit

relay_log_purge

relay_log_recovery

replicate_do_db

replicate_do_table

replicate_events_marked_for_skip

replicate_ignore_db

replicate_ignore_table

replicate_wild_do_table

replicate_wild_ignore_table

slave_compressed_protocol

slave_ddl_exec_mode

slave_domain_parallel_threads

slave_exec_mode

slave_max_allowed_packet

slave_net_timeout

slave_parallel_max_queued

slave_parallel_mode

slave_parallel_threads

slave_parallel_workers

slave_run_triggers_for_rbr

slave_sql_verify_checksum

slave_transaction_retry_interval

slave_type_conversions

sync_master_info

sync_relay_log, and

sync_relay_log_info.

SET USER
Current
< 10.5
Enables setting the DEFINER when creating triggers, views, stored functions and stored procedures.

SHOW DATABASES
List all databases using the SHOW DATABASES statement. Without the SHOW DATABASES privilege, you can still issue the SHOW DATABASES statement, but it will only list databases containing tables on which you have privileges.

SHUTDOWN
Shut down the server using SHUTDOWN or the mariadb-admin shutdown command.

SUPER
Execute superuser statements: CHANGE MASTER TO, KILL (users who do not have this privilege can only KILL their own threads), PURGE LOGS, SET global system variables, or the mariadb-admin debug command. Also, this permission allows the user to write data even if the read_only startup option is set, enable or disable logging, enable or disable replication on replica, specify a DEFINER for statements that support that clause, connect once reaching the MAX_CONNECTIONS. If a statement has been specified for the init-connect mariadbd option, that command will not be executed when a user with SUPER privileges connects to the server.

Current
< 11.0.1
< 10.5
The SUPER privilege has been split into multiple smaller privileges to allow for more fine-grained privileges (MDEV-21743). The privileges are:

SET USER

FEDERATED ADMIN

CONNECTION ADMIN

REPLICATION SLAVE ADMIN

BINLOG ADMIN

BINLOG REPLAY

REPLICA MONITOR

BINLOG MONITOR

REPLICATION MASTER ADMIN

READ_ONLY ADMIN

These grants are no longer a part of SUPER and need to be granted separately.

The READ_ONLY ADMIN privilege has been removed from SUPER. The benefit of this is that one can remove the READ_ONLY ADMIN privilege from all users and ensure that no one can make any changes on any non-temporary tables. This is useful on replicas when one wants to ensure that the replica is kept identical to the primary (MDEV-29596).

Database Privileges
The following table lists the privileges that can be granted at the database level. You can also grant all table and function privileges at the database level. Table and function privileges on a database apply to all tables or functions in that database, including those created later.

To set a privilege for a database, specify the database usingdb_name.* for priv_level, or just use * to specify the default database.

Privilege
Description
CREATE

Create a database using the CREATE DATABASE statement, when the privilege is granted for a database. You can grant the CREATE privilege on databases that do not yet exist. This also grants the CREATE privilege on all tables in the database.

CREATE ROUTINE

Create Stored Programs using the CREATE PROCEDURE and CREATE FUNCTION statements.

CREATE TEMPORARY TABLES

Create temporary tables with the CREATE TEMPORARY TABLE statement. This privilege enable writing and dropping those temporary tables

DROP

Drop a database using the DROP DATABASE statement, when the privilege is granted for a database. This also grants the DROP privilege on all tables in the database.

EVENT

Create, drop and alter EVENTs.

GRANT OPTION

Grant database privileges. You can only grant privileges that you have.

LOCK TABLES

Acquire explicit locks using the LOCK TABLES statement; you also need to have the SELECT privilege on a table, in order to lock it.

SHOW CREATE ROUTINE

Permit viewing the SHOW CREATE definition statement of a routine, for example SHOW CREATE FUNCTION, even if not the routine owner. From MariaDB 11.3.0.

Table Privileges
Privilege
Description
ALTER

Change the structure of an existing table using the ALTER TABLE statement.

CREATE

Create a table using the CREATE TABLE statement. You can grant the CREATE privilege on tables that do not yet exist.

CREATE VIEW

Create a view using the CREATE_VIEW statement.

DELETE

Remove rows from a table using the DELETE statement.

DELETE HISTORY

Remove historical rows from a table using the DELETE HISTORY statement. Displays as DELETE VERSIONING ROWS when running SHOW PRIVILEGES until MariaDB 10.5.2 (MDEV-20382). If a user has the SUPER privilege but not this privilege, running mariadb-upgrade will grant this privilege as well.

DROP

Drop a table using the DROP TABLE statement or a view using the DROP VIEW statement. Also required to execute the TRUNCATE TABLE statement.

GRANT OPTION

Grant table privileges. You can only grant privileges that you have.

INDEX

Create an index on a table using the CREATE INDEX statement. Without the INDEX privilege, you can still create indexes when creating a table using the CREATE TABLE statement if the you have the CREATE privilege, and you can create indexes using the ALTER TABLE statement if you have the ALTER privilege.

INSERT

Add rows to a table using the INSERT statement. The INSERT privilege can also be set on individual columns; see Column Privileges below for details.

REFERENCES

Unused.

SELECT

Read data from a table using the SELECT statement. The SELECT privilege can also be set on individual columns; see Column Privileges below for details.

SHOW VIEW

Show the CREATE VIEW statement to create a view using the SHOW CREATE VIEW statement.

TRIGGER

Required to run the CREATE TRIGGER, DROP TRIGGER, and SHOW CREATE TRIGGER statements. When another user activates a trigger (running INSERT, UPDATE, or DELETE statements on the associated table), for the trigger to execute, the user that defined the trigger should have the TRIGGER privilege for the table. The user running the INSERT, UPDATE, or DELETE statements on the table is not required to have the TRIGGER privilege.

UPDATE

Update existing rows in a table using the UPDATE statement. UPDATE statements usually include a WHERE clause to update only certain rows. You must have SELECT privileges on the table or the appropriate columns for the WHERE clause. The UPDATE privilege can also be set on individual columns; see Column Privileges below for details.

Column Privileges
Some table privileges can be set for individual columns of a table. To use column privileges, specify the table explicitly and provide a list of column names after the privilege type. For example, the following statement would allow the user to read the names and positions of employees, but not other information from the same table, such as salaries.

Copy
GRANT SELECT (name, position) ON Employee TO 'jeffrey'@'localhost';
Privilege
Description
INSERT (column_list)

Add rows specifying values in columns using the INSERT statement. If you only have column-level INSERT privileges, you must specify the columns you are setting in the INSERT statement. All other columns will be set to their default values, or NULL.

REFERENCES (column_list)

Unused.

SELECT (column_list)

Read values in columns using the SELECT statement. You cannot access or query any columns for which you do not have SELECT privileges, including in WHERE, ON, GROUP BY, and ORDER BY clauses.

UPDATE (column_list)

Update values in columns of existing rows using the UPDATE statement. UPDATE statements usually include a WHERE clause to update only certain rows. You must have SELECT privileges on the table or the appropriate columns for the WHERE clause.

Function Privileges
Privilege
Description
ALTER ROUTINE

Change the characteristics of a stored function using the ALTER FUNCTION statement.

EXECUTE

Use a stored function. You need SELECT privileges for any tables or columns accessed by the function.

GRANT OPTION

Grant function privileges. You can only grant privileges that you have.

Procedure Privileges
Privilege
Description
ALTER ROUTINE

Change the characteristics of a stored procedure using the ALTER PROCEDURE statement.

EXECUTE

Execute a stored procedure using the CALL statement. The privilege to call a procedure may allow you to perform actions you wouldn't otherwise be able to do, such as insert rows into a table.

GRANT OPTION

Grant procedure privileges. You can only grant privileges that you have.

Copy
GRANT EXECUTE ON PROCEDURE mysql.create_db TO maintainer;
Proxy Privileges
Privilege
Description
PROXY

Permits one user to be a proxy for another.

The PROXY privilege allows one user to proxy as another user, which means their privileges change to that of the proxy user, and the CURRENT_USER() function returns the user name of the proxy user.

The PROXY privilege only works with authentication plugins that support it. The default mysql_native_password authentication plugin does not support proxy users.

The pam authentication plugin is the only plugin included with MariaDB that currently supports proxy users. The PROXY privilege is commonly used with the pam authentication plugin to enable user and group mapping with PAM.

For example, to grant the PROXY privilege to an anonymous account that authenticates with the pam authentication plugin, you could execute the following:

Copy
CREATE USER 'dba'@'%' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON *.* TO 'dba'@'%' ;

CREATE USER ''@'%' IDENTIFIED VIA pam USING 'mariadb';
GRANT PROXY ON 'dba'@'%' TO ''@'%';
A user account can only grant the PROXY privilege for a specific user account if the granter also has the PROXY privilege for that specific user account, and if that privilege is defined WITH GRANT OPTION. For example, the following example fails because the granter does not have the PROXY privilege for that specific user account at all:

Copy
SELECT USER(), CURRENT_USER();
Copy
+-----------------+-----------------+
| USER()          | CURRENT_USER()  |
+-----------------+-----------------+
| alice@localhost | alice@localhost |
+-----------------+-----------------+
Copy
SHOW GRANTS
Copy
+-----------------------------------------------------------------------------------------------------------------------+
| Grants for alice@localhost                                                                                            |
+-----------------------------------------------------------------------------------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO 'alice'@'localhost' IDENTIFIED BY PASSWORD '*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19' |
+-----------------------------------------------------------------------------------------------------------------------+
Copy
GRANT PROXY ON 'dba'@'localhost' TO 'bob'@'localhost';
ERROR 1698 (28000): Access denied for user 'alice'@'localhost'
And the following example fails because the granter does have the PROXY privilege for that specific user account, but it is not defined WITH GRANT OPTION:

Copy
SELECT USER(), CURRENT_USER();
Copy
+-----------------+-----------------+
| USER()          | CURRENT_USER()  |
+-----------------+-----------------+
| alice@localhost | alice@localhost |
+-----------------+-----------------+
Copy
SHOW GRANTS;
Copy
+-----------------------------------------------------------------------------------------------------------------------+
| Grants for alice@localhost                                                                                            |
+-----------------------------------------------------------------------------------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO 'alice'@'localhost' IDENTIFIED BY PASSWORD '*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19' |
| GRANT PROXY ON 'dba'@'localhost' TO 'alice'@'localhost'                                                               |
+-----------------------------------------------------------------------------------------------------------------------+
Copy
GRANT PROXY ON 'dba'@'localhost' TO 'bob'@'localhost';
ERROR 1698 (28000): Access denied for user 'alice'@'localhost'
But the following example succeeds because the granter does have the PROXY privilege for that specific user account, and it is defined WITH GRANT OPTION:

Copy
SELECT USER(), CURRENT_USER();
Copy
+-----------------+-----------------+
| USER()          | CURRENT_USER()  |
+-----------------+-----------------+
| alice@localhost | alice@localhost |
+-----------------+-----------------+
Copy
SHOW GRANTS;
Copy
+-----------------------------------------------------------------------------------------------------------------------------------------+
| Grants for alice@localhost                                                                                                              |
+-----------------------------------------------------------------------------------------------------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO 'alice'@'localhost' IDENTIFIED BY PASSWORD '*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19' WITH GRANT OPTION |
| GRANT PROXY ON 'dba'@'localhost' TO 'alice'@'localhost' WITH GRANT OPTION                                                               |
+-----------------------------------------------------------------------------------------------------------------------------------------+
Copy
GRANT PROXY ON 'dba'@'localhost' TO 'bob'@'localhost';
A user account can grant the PROXY privilege for any other user account if the granter has the PROXY privilege for the ''@'%' anonymous user account, like this:

Copy
GRANT PROXY ON ''@'%' TO 'dba'@'localhost' WITH GRANT OPTION;
For example, the following example succeeds because the user can grant the PROXY privilege for any other user account:

Copy
SELECT USER(), CURRENT_USER();
Copy
+-----------------+-----------------+
| USER()          | CURRENT_USER()  |
+-----------------+-----------------+
| alice@localhost | alice@localhost |
+-----------------+-----------------+
Copy
SHOW GRANTS;
Copy
+-----------------------------------------------------------------------------------------------------------------------------------------+
| Grants for alice@localhost                                                                                                              |
+-----------------------------------------------------------------------------------------------------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO 'alice'@'localhost' IDENTIFIED BY PASSWORD '*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19' WITH GRANT OPTION |
| GRANT PROXY ON ''@'%' TO 'alice'@'localhost' WITH GRANT OPTION                                                                          |
+-----------------------------------------------------------------------------------------------------------------------------------------+
Copy
GRANT PROXY ON 'app1_dba'@'localhost' TO 'bob'@'localhost';
Query OK, 0 rows affected (0.004 sec)
Copy
GRANT PROXY ON 'app2_dba'@'localhost' TO 'carol'@'localhost';
Query OK, 0 rows affected (0.004 sec)
The default root user accounts created by mariadb-install-db have this privilege. For example:

Copy
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT PROXY ON ''@'%' TO 'root'@'localhost' WITH GRANT OPTION;
This allows the default root user accounts to grant the PROXY privilege for any other user account, and it also allows the default root user accounts to grant others the privilege to do the same.

Authentication Options
The authentication options for the GRANT statement are the same as those for the CREATE USER statement.

IDENTIFIED BY 'password'
The optional IDENTIFIED BY clause can be used to provide an account with a password. The password should be specified in plain text. It will be hashed by the PASSWORD function prior to being stored.

For example, if our password is mariadb, then we can create the user with:

Copy
GRANT USAGE ON *.* TO foo2@test IDENTIFIED BY 'mariadb';
If you do not specify a password with the IDENTIFIED BY clause, the user will be able to connect without a password. A blank password is not a wildcard to match any password. The user must connect without providing a password if no password is set.

If the user account already exists and if you provide the IDENTIFIED BY clause, then the user's password will be changed. You must have the privileges needed for the SET PASSWORD statement to change a user's password with GRANT.

The only authentication plugins that this clause supports are mysql_native_password and mysql_old_password.

IDENTIFIED BY PASSWORD 'password_hash'
The optional IDENTIFIED BY PASSWORD clause can be used to provide an account with a password that has already been hashed. The password should be specified as a hash that was provided by the PASSWORD function. It will be stored as-is.

For example, if our password is mariadb, then we can find the hash with:

Copy
SELECT PASSWORD('mariadb');
Copy
+-------------------------------------------+
| PASSWORD('mariadb')                       |
+-------------------------------------------+
| *54958E764CE10E50764C2EECBB71D01F08549980 |
+-------------------------------------------+
1 row in set (0.00 sec)
And then we can create a user with the hash:

Copy
GRANT USAGE ON *.* TO foo2@test IDENTIFIED BY 
  PASSWORD '*54958E764CE10E50764C2EECBB71D01F08549980';
If you do not specify a password with the IDENTIFIED BY clause, the user will be able to connect without a password. A blank password is not a wildcard to match any password. The user must connect without providing a password if no password is set.

If the user account already exists and if you provide the IDENTIFIED BY clause, then the user's password will be changed. You must have the privileges needed for the SET PASSWORD tastatement to change a user's password with GRANT.

The only authentication plugins that this clause supports are mysql_native_password and mysql_old_password.

IDENTIFIED {VIA|WITH} authentication_plugin
The optional IDENTIFIED VIA authentication_plugin allows you to specify that the account should be authenticated by a specific authentication plugin. The plugin name must be an active authentication plugin as per SHOW PLUGINS. If it doesn't show up in that output, then you will need to install it with INSTALL PLUGIN or INSTALL SONAME.

For example, this could be used with the PAM authentication plugin:

Copy
GRANT USAGE ON *.* TO foo2@test IDENTIFIED VIA pam;
Some authentication plugins allow additional arguments to be specified after a USING or AS keyword. For example, the PAM authentication plugin accepts a service name:

Copy
GRANT USAGE ON *.* TO foo2@test IDENTIFIED VIA pam USING 'mariadb';
The exact meaning of the additional argument would depend on the specific authentication plugin.

The USING or AS keyword can also be used to provide a plain-text password to a plugin if it's provided as an argument to the PASSWORD() function. This is only valid for authentication plugins that have implemented a hook for the PASSWORD() function. For example, the ed25519 authentication plugin supports this:

Copy
CREATE USER safe@'%' IDENTIFIED VIA ed25519 
  USING PASSWORD('secret');
One can specify many authentication plugins, they all work as alternative ways of authenticating a user:

Copy
CREATE USER safe@'%' IDENTIFIED VIA ed25519 
  USING PASSWORD('secret') OR unix_socket;
By default, when you create a user without specifying an authentication plugin, MariaDB uses the mysql_native_password plugin.

Resource Limit Options
It is possible to set per-account limits for certain server resources. The following table shows the values that can be set per account:

Limit Type
Decription
MAX_QUERIES_PER_HOUR

Number of statements that the account can issue per hour (including updates)

MAX_UPDATES_PER_HOUR

Number of updates (not queries) that the account can issue per hour

MAX_CONNECTIONS_PER_HOUR

Number of connections that the account can start per hour

MAX_USER_CONNECTIONS

Number of simultaneous connections that can be accepted from the same account; if it is 0, max_connections will be used instead; if max_connections is 0, there is no limit for this account's simultaneous connections.

MAX_STATEMENT_TIME

Timeout, in seconds, for statements executed by the user. See also Aborting Statements that Exceed a Certain Time to Execute.

If any of these limits are set to 0, then there is no limit for that resource for that user.

To set resource limits for an account, if you do not want to change that account's privileges, you can issue a GRANT statement with the USAGE privilege, which has no meaning. The statement can name some or all limit types, in any order.

Here is an example showing how to set resource limits:

Copy
GRANT USAGE ON *.* TO 'someone'@'localhost' WITH
    MAX_USER_CONNECTIONS 0
    MAX_QUERIES_PER_HOUR 200;
The resources are tracked per account, which means 'user'@'server'; not per user name or per connection.

The count can be reset for all users using FLUSH USER_RESOURCES, FLUSH PRIVILEGES or mariadb-admin reload.

Current
< 10.5
Users with the CONNECTION ADMIN privilege or the SUPER privilege are not restricted by max_user_connections or max_password_errors , and they are allowed one additional connection when max_connections is reached.

Per account resource limits are stored in the user table, in the mysql database. Columns used for resources limits are named max_questions, max_updates, max_connections (for MAX_CONNECTIONS_PER_HOUR), and max_user_connections (for MAX_USER_CONNECTIONS).

TLS Options
By default, MariaDB transmits data between the server and clients without encrypting it. This is generally acceptable when the server and client run on the same host or in networks where security is guaranteed through other means. However, in cases where the server and client exist on separate networks or they are in a high-risk network, the lack of encryption does introduce security concerns as a malicious actor could potentially eavesdrop on the traffic as it is sent over the network between them.

To mitigate this concern, MariaDB allows you to encrypt data in transit between the server and clients using the Transport Layer Security (TLS) protocol. TLS was formerly known as Secure Socket Layer (SSL), but strictly speaking the SSL protocol is a predecessor to TLS and, that version of the protocol is now considered insecure. The documentation still uses the term SSL often and for compatibility reasons TLS-related server system and status variables still use the prefix ssl_, but internally, MariaDB only supports its secure successors.

See Secure Connections Overview for more information about how to determine whether your MariaDB server has TLS support.

You can set certain TLS-related restrictions for specific user accounts. For instance, you might use this with user accounts that require access to sensitive data while sending it across networks that you do not control. These restrictions can be enabled for a user account with the CREATE USER, ALTER USER, or GRANT statements. The following options are available:

Option
Description
REQUIRE NONE

TLS is not required for this account, but can still be used.

REQUIRE SSL

The account must use TLS, but no valid X509 certificate is required. This option cannot be combined with other TLS options.

REQUIRE X509

The account must use TLS and must have a valid X509 certificate. This option implies REQUIRE SSL. This option cannot be combined with other TLS options.

REQUIRE ISSUER 'issuer'

The account must use TLS and must have a valid X509 certificate. Also, the Certificate Authority must be the one specified via the string issuer. This option implies REQUIRE X509. This option can be combined with the SUBJECT, and CIPHER options in any order.

REQUIRE SUBJECT 'subject'

The account must use TLS and must have a valid X509 certificate. Also, the certificate's Subject must be the one specified via the string subject. This option implies REQUIRE X509. This option can be combined with the ISSUER, and CIPHER options in any order.

REQUIRE CIPHER 'cipher'

The account must use TLS, but no valid X509 certificate is required. Also, the encryption used for the connection must use a specific cipher method specified in the string cipher. This option implies REQUIRE SSL. This option can be combined with the ISSUER, and SUBJECT options in any order.

The REQUIRE keyword must be used only once for all specified options, and the AND keyword can be used to separate individual options, but it is not required.

For example, you can create a user account that requires these TLS options with the following:

Copy
GRANT USAGE ON *.* TO 'alice'@'%'
  REQUIRE SUBJECT '/CN=alice/O=My Dom, Inc./C=US/ST=Oregon/L=Portland'
  AND ISSUER '/C=FI/ST=Somewhere/L=City/ O=Some Company/CN=Peter Parker/emailAddress=p.parker@marvel.com'
  AND CIPHER 'SHA-DES-CBC3-EDH-RSA';
If any of these options are set for a specific user account, then any client who tries to connect with that user account will have to be configured to connect with TLS.

See Securing Connections for Client and Server for information on how to enable TLS on the client and server.

Roles
Syntax
Copy
GRANT role TO grantee [, grantee ... ]
[ WITH ADMIN OPTION ]

grantee:
    rolename
    username [authentication_option]
The GRANT statement is also used to grant the use of a role to one or more users or other roles. In order to be able to grant a role, the grantor doing so must have permission to do so (see WITH ADMIN in the CREATE ROLE article).

Specifying the WITH ADMIN OPTION permits the grantee to in turn grant the role to another.

For example, the following commands show how to grant the same role to a couple different users.

Copy
GRANT journalist TO hulda;

GRANT journalist TO berengar WITH ADMIN OPTION;
If a user has been granted a role, they do not automatically obtain all permissions associated with that role. These permissions are only in use when the user activates the role with the SET ROLE statement.

TO PUBLIC
Current
< 10.11.0
blog post

Syntax
Copy
GRANT <privilege> ON <DATABASE>.<object> TO PUBLIC;
REVOKE <privilege> ON <DATABASE>.<object> FROM PUBLIC;
GRANT ... TO PUBLIC grants privileges to all users with access to the server. The privileges also apply to users created after the privileges are granted. This can be useful when one only wants to state once that all users need to have a certain set of privileges.
When running SHOW GRANTS, a user will also see all privileges inherited from PUBLIC. SHOW GRANTS FOR PUBLIC will only show TO PUBLIC grants.

Grant Examples
Granting Root-like Privileges
You can create a user that has privileges similar to the default root accounts by executing the following:

Copy
CREATE USER 'alexander'@'localhost';
GRANT ALL PRIVILEGES ON  *.* TO 'alexander'@'localhost' WITH GRANT OPTION;
See Also
Troubleshooting Connection Issues

Authentication from MariaDB 10.4

--skip-grant-tables allows you to start MariaDB without GRANT. This is useful if you lost your root password.

CREATE USER

ALTER USER

DROP USER

SET PASSWORD

SHOW CREATE USER

mysql.global_priv table

mysql.user table

Password Validation Plugins - permits the setting of basic criteria for passwords

Authentication Plugins - allow various authentication methods to be used, and new ones to be developed.
