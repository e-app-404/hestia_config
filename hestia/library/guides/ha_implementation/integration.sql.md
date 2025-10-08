# SQL
The sql sensor integration enables you to use values from an SQL database supported by the sqlalchemy library, to populate a sensor state (and attributes). This can be used to present statistics about Home Assistant sensors if used with the recorder integration database. It can also be used with an external data source.

This integration can be configured using both config flow and by YAML.

Configurationbre
To add the SQL integration to your Home Assistant instance, use this My button:

Manual configuration steps
Configuration by YAML
To configure this sensor, define the sensor connection variables and a list of queries to your configuration.yaml file. A sensor will be created for each query.

To enable it, add the following lines to your configuration.yaml file. After changing the configuration.yaml file, restart Home Assistant to apply the changes. The integration is now shown on the integrations page under Settings > Devices & services. Its entities are listed on the integration card itself and on the Entities tab.

# Example configuration.yaml

sql:

- name: Sun state
  query: >
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
  where
  entity_id = 'sun.sun'
  )
  ORDER BY
  state_id DESC
  LIMIT
  1;
  column: "state"
  YAML
  Configuration Variables
  Looking for your configuration file?
  sql map Required
  Integration.

db_url string (Optional)
The URL which points to your database. See supported engines.

Default: Defaults to the recorder db_url.
name template Required
The name of the sensor.

query string Required
An SQL QUERY string, should return 1 result at most.

column string Required
The field name to select.

unit_of_measurement string (Optional)
Defines the units of measurement of the sensor, if any.

value_template template (Optional)
Defines a template to extract a value from the payload.

unique_id string (Optional)
Provide a unique id for this sensor.

device_class string (Optional)
Provide device class for this sensor.

state_class string (Optional)
Provide state class for this sensor.

icon template (Optional)
Defines a template for the icon of the entity.

picture template (Optional)
Defines a template for the entity picture of the entity.

availability template (Optional)
Defines a template if the entity state is available or not.

Data updates
By default, the integration executes the SQL query to update the sensor every 30 seconds. If you wish to update at a different interval, you can disable the automatic refresh in the integration’s system options (Enable polling for updates) and create your own automation with your desired frequency.

For more detailed steps on how to define a custom interval, follow the procedure below.

Defining a custom polling interval
If you want to define a specific interval at which your device is being polled for data, you can disable the default polling interval and create your own polling automation.

To add the automation:

Go to Settings > Devices & services, and select your integration.
On the integration entry, select the .
Then, select System options and toggle the button to disable polling. Disable polling for updates
To define your custom polling interval, create an automation.
Go to Settings > Automations & scenes and create a new automation.
Define any trigger and condition you like.
Select Add action, then, select Other actions.
Select Perform action, and from the list, select the homeassistant.update_entity action.
Choose your targets by selecting the Choose area, Choose device, Choose entity, or Choose label buttons. Update entity
Save your new automation to poll for data.
Information
See supported engines for which you can connect with this integration.

The SQL integration will connect to the Home Assistant Recorder database if “Database URL” has not been specified.

There is no explicit configuration required for attributes. The integration will set all columns returned by the query as attributes.

Note that in all cases only the first row returned will be used.

Using templates
For incoming data, a value template translates incoming JSON or raw data to a valid payload. Incoming payloads are rendered with possible JSON values, so when rendering, the value_json can be used to access the attributes in a JSON based payload, otherwise the value variable can be used for non-json based data.

Additional, the this can be used as variables in the template. The this attribute refers to the current entity state of the entity. Further information about this variable can be found in the template documentation

Note

Example value template with json:

With given payload:

{ "state": "ON", "temperature": 21.902 }
JSON
Template {{ value_json.temperature | round(1) }} renders to 21.9.

Examples
In this section, you find some real-life examples of how to use this sensor.

Current state of an entity
This example shows the previously recorded state of the sensor sensor.temperature_in.

sensor:

- platform: random
  name: Temperature in
  unit_of_measurement: "°C"
  YAML
  The query will look like this:

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
SQL
Use state as column for value.

Previous state of an entity
Based on previous example with temperature, the query to get the former state is :

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
SQL
Use state as column for value.

State of an entity x time ago
If you want to extract the state of an entity from a day, hour, or minute ago, the query is:

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
SQL
Replace -1 day with the target offset, for example, -1 hour. Use state as column for value.

Keep in mind that, depending on the update frequency of your sensor and other factors, this may not be a 100% accurate reflection of the actual situation you are measuring. Since your database won’t necessarily have a value saved exactly 24 hours ago, use “>=” or “<=” to get one of the closest values.

MariaDB
On MariaDB the following where clause can be used to compare the timestamp:

...
AND last_updated_ts <= UNIX_TIMESTAMP(NOW() - INTERVAL 1 DAY)
...
SQL
Replace - INTERVAL 1 DAY with the target offset, for example, - INTERVAL 1 HOUR.

Database size
Postgres
SELECT pg_database_size('dsmrreader')/1024/1024 as db_size;
SQL
Use db_size as column for value. Replace dsmrreader with the correct name of your database.

Tip

The unit of measurement returned by the above query is MiB, please configure this correctly.

Set the device class to Data size so you can use UI unit conversion.

MariaDB/MySQL
Change table_schema="homeassistant" to the name that you use as the database name, to ensure that your sensor will work properly.

SELECT table_schema "database", Round(Sum(data_length + index_length) / POWER(1024,2), 1) "value" FROM information_schema.tables WHERE table_schema="homeassistant" GROUP BY table_schema;
SQL
Use value as column for value.

Tip

The unit of measurement returned by the above query is MiB, please configure this correctly.

Set the device class to Data size so you can use UI unit conversion.

SQLite
If you are using the recorder integration then you don’t need to specify the location of the database. For all other cases, add sqlite:////path/to/database.db as Database URL.

SELECT ROUND(page_count \* page_size / 1024 / 1024, 1) as size FROM pragma_page_count(), pragma_page_size();
SQL
Use size as column for value.

Tip

The unit of measurement returned by the above query is MiB, please configure this correctly.

Set the device class to Data size so you can use UI unit conversion.
