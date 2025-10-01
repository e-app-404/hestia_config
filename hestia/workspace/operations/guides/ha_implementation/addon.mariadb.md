Home Assistant Add-on: MariaDB
Installation
Follow these steps to get the add-on installed on your system:

Navigate in your Home Assistant frontend to Settings -> Add-ons -> Add-on store.
Find the "MariaDB" add-on and click it.
Click on the "INSTALL" button.
How to use
Set the logins -> password field to something strong and unique.
Start the add-on.
Check the add-on log output to see the result.
Add the recorder integration to your Home Assistant configuration.
Add-on Configuration
The MariaDB server add-on can be tweaked to your likings. This section describes each of the add-on configuration options.

Example add-on configuration:

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
Option: databases (required)
Database name, e.g., homeassistant. Multiple are allowed.

Option: logins (required)
This section defines a create user definition in MariaDB. Create User documentation.

Option: logins.username (required)
Database user login, e.g., homeassistant. User Name documentation.

Option: logins.password (required)
Password for user login. This should be strong and unique.

Option: rights (required)
This section grant privileges to users in MariaDB. Grant documentation.

Option: rights.username (required)
This should be the same user name defined in logins -> username.

Option: rights.database (required)
This should be the same database defined in databases.

Option: rights.privileges (optional)
A list of privileges to grant to this user from grant like SELECT and CREATE. If omitted, grants ALL PRIVILEGES to the user. Restricting privileges of the user that Home Assistant uses is not recommended but if you want to allow other applications to view recorder data should create a user limited to read-only access on the database.

Option: mariadb_server_args (optional)
Some users have experienced errors during Home Assistant schema updates on large databases. Defining the recommended parameters can help if there is RAM available.

Example: --innodb_buffer_pool_size=512M

Home Assistant Configuration
MariaDB will be used by the recorder and history components within Home Assistant. For more information about setting this up, see the recorder integration documentation for Home Assistant.

Example Home Assistant configuration:

recorder:
  db_url: mysql://homeassistant:password@core-mariadb/homeassistant?charset=utf8mb4
Support
Got questions?

You have several options to get them answered:

The Home Assistant Discord Chat Server.
The Home Assistant Community Forum.
Join the Reddit subreddit in /r/homeassistant
In case you've found a bug, please open an issue on our GitHub.