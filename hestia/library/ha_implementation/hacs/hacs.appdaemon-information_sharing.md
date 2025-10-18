# Getting Information in Apps and Sharing information between Apps

Sharing information between different Apps is very simple if required. Each App gets access to a global dictionary stored in a class attribute called `self.global_vars`. Any App can add or read any key as required. This operation is not, however, threadsafe so some care is needed - see the section on threading for more details.

In addition, Apps have access to the entire configuration if required, meaning they can access AppDaemon configuration items as well as parameters from other Apps. To use this, there is a class attribute called `self.config`. It contains a standard Python nested Dictionary.

To get AppDaemon’s config parameters for example:

```python
app_timezone = self.config["time_zone"]
```

To access any apps parameters, use the class attribute called `app_config`. This is a Python Dictionary with an entry for each App, keyed on the App’s name.

```python
other_apps_arg = self.app_config["some_app"]["some_parameter"]
```

AppDaemon also exposes the configurations from configured plugins. For example, that of the HA plugin allows accessing configurations from Home Assistant such as the Latitude and Longitude configured in HA. All of the information available from the Home Assistant `/api/config` endpoint is available using the `get_config()` call. E.g.:

```python
config = self.get_config()
self.log("My current position is {}(Lat), {}(Long)".format(config["latitude"], config["longitude"]))
```

Using this method, it is also possible to use this function to access configurations of other plugins, from within apps in a different namespace. This is done by simply passing in the namespace parameter. E.g.:

## from within a HASS App, and wanting to access the client Id of the MQTT Plugin

```python
config = self.get_config(namespace = 'mqtt')
self.log("The Mqtt Client ID is ".format(config["client_id"]))
```

And finally, it is also possible to use config as a global area for sharing parameters across Apps. Simply add the required parameters inside the appdaemon section in the `appdaemon.yaml` file:

```yaml
logs:
...
appdaemon:
  global_var: hello world
```

Then access it as follows:

```python
my_global_var = self.config["global_var"]
```
