---
title: "Home Assistant Add-on: MariaDB"
authors: "Home Assistant"
source: "Home Assistant Docs"
slug: "addon-mariadb"
tags: ["home-assistant","addon","mariadb","database"]
original_date: "2022-04-05"
last_updated: "2025-10-03"
url: "https://www.home-assistant.io/addons/mariadb/"
---

# Home Assistant Add-on: MariaDB

> High-performance MySQL-compatible database server add-on for Home Assistant, providing a robust alternative to the default SQLite database for the recorder integration.

## Internal References

- **Database Configuration**: [`integration.recorder.md`](integration.recorder.md) - Recorder integration setup
- **GRANT Reference**: [`addon.mariadb_grant.md`](addon.mariadb_grant.md) - MariaDB permissions and user management
- **Related Components**: `recorder`, `history`, `logbook`
- **External Database**: Recommended for high-write scenarios and improved performance

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Settings** → **Add-ons** → **Add-on store**
2. Find the "MariaDB" add-on and click it
3. Click on the **INSTALL** button

## How to Use

1. **Set Strong Password**: Set the `logins` → `password` field to something strong and unique
2. **Start the Add-on**: Start the add-on from the Home Assistant interface
3. **Verify Installation**: Check the add-on log output to see the result
4. **Configure Recorder**: Add the recorder integration to your Home Assistant configuration

## Add-on Configuration

The MariaDB server add-on can be tweaked to your likings. This section describes each of the add-on configuration options.

### Example Configuration

```yaml
databases:
  - homeassistant
logins:
  - username: homeassistant
    password: PASSWORD
  - username: read_only_user
    password: PASSWORD
rights:
  - username: homeassistant
    database: homeassistant
  - username: read_only_user
    database: homeassistant
    privileges:
      - SELECT
```

### Configuration Options

#### Database Settings

- **`databases`** (required) - Database name, e.g., `homeassistant`. Multiple databases are allowed

#### User Management

- **`logins`** (required) - This section defines user creation in MariaDB. See [MariaDB CREATE USER documentation](https://mariadb.com/kb/en/create-user/)
  - **`logins.username`** (required) - Database user login, e.g., `homeassistant`. See [User Name documentation](https://mariadb.com/kb/en/create-user/#user-name)
  - **`logins.password`** (required) - Password for user login. This should be strong and unique

#### Permissions

- **`rights`** (required) - This section grants privileges to users in MariaDB. See [GRANT documentation](https://mariadb.com/kb/en/grant/)
  - **`rights.username`** (required) - This should be the same user name defined in `logins` → `username`
  - **`rights.database`** (required) - This should be the same database defined in `databases`
  - **`rights.privileges`** (optional) - A list of privileges to grant to this user (for example `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `INDEX`).

Important note on privileges
- Some older examples or default add-on behaviors may grant broad privileges when `rights.privileges` is omitted; do not assume this is safe. Prefer explicitly declaring the privileges you want to grant to avoid accidental wide access.
- Recommended minimal privileges for Home Assistant Recorder: `SELECT, INSERT, UPDATE, DELETE, INDEX` (and `CREATE TEMPORARY TABLES` only if you encounter errors during schema migration).

Minimal example (recommended)

```yaml
rights:
  - username: homeassistant
    database: homeassistant
    privileges:
      - SELECT
      - INSERT
      - UPDATE
      - DELETE
      - INDEX
```

If you prefer the add-on to manage users automatically for convenience, accept that it may create broader rights; for production-critical databases we recommend managing users and grants externally and pointing the add-on at those credentials.

#### Advanced Options

- **`mariadb_server_args`** (optional) - Some users have experienced errors during Home Assistant schema updates on large databases. Defining the recommended parameters can help if there is RAM available

**Example**: `--innodb_buffer_pool_size=512M`

## Home Assistant Configuration

MariaDB will be used by the recorder and history components within Home Assistant. For more information about setting this up, see the [recorder integration documentation](integration.recorder.md).

### Example Home Assistant Configuration

```yaml
recorder:
  db_url: mysql://homeassistant:password@core-mariadb/homeassistant?charset=utf8mb4
```

### Connection String Format

The connection string follows this pattern:
`mysql://username:password@hostname/database?charset=utf8mb4`

Where:
- `username`: The database username (from your `logins` configuration)
- `password`: The database password (from your `logins` configuration)  
- `hostname`: `core-mariadb` (the add-on's internal hostname)
- `database`: The database name (from your `databases` configuration)
- `charset=utf8mb4`: Required character set for proper Unicode support
## Support

Got questions? You have several options to get them answered:

- [Home Assistant Discord Chat Server](https://discord.gg/home-assistant)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
- [Reddit subreddit /r/homeassistant](https://reddit.com/r/homeassistant)
- [GitHub Issues](https://github.com/home-assistant/addons/issues) - For bug reports

## Performance Considerations

- MariaDB is recommended for high-write scenarios (many sensors, frequent updates)
- Requires more RAM than SQLite but provides better performance for large databases
- Consider using `mariadb_server_args` to tune performance for your specific hardware
- Regular backups are essential - MariaDB data is not included in Home Assistant snapshots
- Monitor database size and implement appropriate purge policies