# Using Multiple APIs From One App
The way apps are constructed, they inherit from a superclass that contains all the methods needed to access a particular plugin. This is convenient as it hides a lot of the complexity by automatically selecting the right configuration information based on namespaces. One drawback of this approach is that an App cannot inherently speak to multiple plugin types as the API required is different, and the App can only choose one API to inherit from.

To get around this, a function called `get_plugin_api()` is provided to instantiate API objects to handle multiple plugins, as a distinct objects, not part of the APPs inheritance. Once the new API object is obtained, you can make plugin-specific API calls on it directly, as well as call `listen_state()` on it to listen for state changes specific to that plugin.

In this case, it is cleaner not to have the App inherit from one or the other specific APIs, and for this reason, the ADBase class is provided to create an App without any specific plugin API. The App will also use `get_ad_api()` to get access to the AppDaemon API for the various scheduler calls.

As an example, this App is built using ADBase, and uses `get_plugin_api()` to access both HASS and MQTT, as well as `get_ad_api()` to access the AppDaemon base functions.

```py
from appdaemon import adbase as ad

class GetAPI(ad.ADBase):
  def initialize(self):

    # Grab an object for the HASS API
    hass = self.get_plugin_api("HASS")
    # Hass API Call
    hass.turn_on("light.office")
    # Listen for state changes for this plugin only
    hass.listen_state(my_callback, "light.kitchen")

    # Grab an object for the MQTT API
    mqtt = self.get_plugin_api("MQTT")
    # Make MQTT API Call
    mqtt.mqtt_publish("topic", "Payload"):

    # Make a scheduler call using the ADBase class
    adbase = self.get_ad_api()
    handle = adbase.run_in(callback, 20)
```

By default, each plugin API object has it’s namespace correctly set for that plugin, which makes it much more convenient to handle calls and callbacks form that plugin. This way of working can often be more convenient and clearer than changing namespaces within apps or on the individual calls, so is the recommended way to handle multiple plugins of the same or even different types. The AD base API’s namespace defaults to “default”:

```py
# Listen for state changes specific to the "HASS" plugin
hass.listen_state(hass_callback, "light.office")
# Listen for state changes specific to the "MQTT" plugin
mqtt.listen_state(mqtt_callback, "light.office")
# Listen for global state changes
adbase.listen_state(global_callback, namespace="global")
```

API objects are fairly lightweight and can be created and discarded at will. There may be a slight performance increase by creating an object for each API in the initialize function and using it throughout the App, but this is likely to be minimal.

# Custom Constraints
An App can also register its own custom constraints which can then be used in exactly the same way as App level or callback level constraints. A custom constraint is simply a Python function that returns True or False when presented with the constraint argument. If it returns True, the constraint is regarded as satisfied, and the callback will be made subject to any other constraints also evaluating to True. Likewise, a False return means that the callback won’t fire. Custom constraints are a handy way to control multiple callbacks that have some complex logic and enable you to avoid duplicating code in all callbacks.

To use a custom constraint, it is first necessary to register the function to be used to evaluate it using the `register_constraint()` API call. Constraints can also be unregistered using the `deregister_constraint()` call, and the `list_constraints()` call will return a list of currently registered constraints.

Here is an example of how this all fits together.

We start off with a python function that accepts a value to be evaluated like this:

```py
def is_daylight(self, value):
    if self.sun_up():
        return True
    else:
        return False
```
To use this in a callback level constraint simply use:

```py
self.register_constraint("is_daylight")
handle = self.run_every(self.callback, time, 1, is_daylight=1)
```

Now `callback()` will only fire if the sun is up.

Using the value parameter you can parameterize the constraint for more complex behavior and use in different situations for different callbacks. For instance:

```py
def sun(self, value):
    if value == "up":
        if self.sun_up():
        return True
    elif value == "down":
        if self.sun_down():
        return True
    return False
```

You can use this with 2 separate constraints like so:

```py
self.register_constraint("sun")
handle = self.run_every(self.up_callback, time, 1, sun="up")
handle = self.run_every(self.down_callback, time, 1, sun="down")
```

# Sequences

AppDaemon supports sequences as a simple way of reusing predefined steps of commands. The initial usecase for sequences is to allow users to create scenes within AppDaemon, however they are useful for many other things. Sequences are fairly simple and allow the user to define 3 types of activities:

A `call_service` command with arbitrary parameters

A configurable delay between steps.

Pause execution, until an entity has a certain state

In the case of a scene, of course you would not want to use the delay, and would just list all the devices to be switched on or off, however, if you wanted a light to come on for 30 seconds, you could use a script to turn the light on, wait 30 seconds and then turn it off. Unlike in synchronous apps, delays are fine in scripts as they will not hold the apps_thread up.

There are 2 types of sequence - predefined sequences and inline sequences.

## Defining a Sequence
A predefined sequence is created by adding a sequence section to your `apps.yaml` file. If you have apps.yaml split into multiple files, you can have sequences defined in each one if desired. For clarity, it is strongly recommended that sequences are created in their own standalone yaml files, ideally in a separate directory from the app argument files.

An example of a simple sequence entry to create a couple of scenes might be:

```py
sequence:
  office_on:
    name: Office On
    namespace: hass
    steps:
    - homeassistant/turn_on:
        entity_id: light.office_1
        brightness: 254
    - homeassistant/turn_on:
        entity_id: light.office_2
        brightness: 254
  office_off:
    name: Office Off
    steps:
    - homeassistant/turn_off:
        entity_id: light.office_1
    - homeassistant/turn_off:
        entity_id: light.office_2
```

The names of the sequences defined above are `sequence.office_on` and `sequence.office_off`. The name entry is optional and is used to provide a friendly name for `HADashboard`. The steps entry is simply a list of steps to be taken. They will be processed in the order defined, however without any delays the steps will be processed practically instantaneously.

A sequence to turn a light on then off after a delay might look like this:

```py
sequence:
  outside_motion_light:
    name: Outside Motion
    steps:
    - homeassistant/turn_on:
        entity_id: light.outside
        brightness: 254
    - sleep: 30
    - homeassistant/turn_off:
        entity_id: light.outside
```

If you prefer, you can use YAML’s inline capabilities for a more compact representation that looks better for longer sequences:

```yaml
sequence:
  outside_motion_light:
    name: Outside Motion
    steps:
    - homeassistant/turn_on: {"entity_id": "light.outside", "brightness": 254}
    - sleep: 30
    - homeassistant/turn_off: {"entity_id": "light.outside"}
```

## Looping a Sequence
Sequences can be created that will loop forever by adding the value loop: True to the sequence:

```yaml
sequence:
  outside_motion_light:
    name: Outside Motion
    loop: True
    steps:
    - homeassistant/turn_on: {"entity_id": "light.outside", "brightness": 254}
    - sleep: 30
    - homeassistant/turn_off: {"entity_id": "light.outside"}
```

This sequence once started will loop until either the sequence is canceled, the app is restarted or terminated, or AppDaemon is shutdown.

Not only can the whole sequence be looped, but steps can be looped to if wanting to run a certain step multiple times. Below is an example of increasing the volume of a device 5 times with 0.5 interval

```yaml
sequence:
  setup_tv:
    name: Setup TV
    namespace: hass
    steps:
    - homeassistant/turn_on:
        entity_id: switch.living_room_tv

    - sleep: 30

    - remote/send_command:
        entity_id: roku.living_room
        loop_step:
            times: 5
            interval: 0.5
```

## Defining a Sequence Call Namespace

By default, a sequence will run on entities in the current namespace, however , the namespace can be specified on a per call basis if required. Also it can be specified at the top tier level, allowing for all service calls in the sequence to use the same namespace

```yaml
sequence:
  office_on:
    name: Office On
    namespace: hass
    steps:
    - homeassistant/turn_on:
        entity_id: light.office_1
        brightness: 254
        namespace: "hass1"
    - homeassistant/turn_on:
        entity_id: light.office_2
        brightness: 254
        namespace: "hass2"
```

Just like app parameters and code, sequences will be reloaded after any change has been made allowing scenes to be developed and modified without restarting AppDaemon.

## Sequence Commands

In addition to a straightforward service name plus data, sequences can take a few additional commands:

`sleep` - pause execution of the sequence for a number of seconds. e.g. sleep: 30 will pause the sequence for 30 seconds

`sequence` - run a sub sequence. This must be a predefined sequence, and cannot be an inline sequence. Provide the entity name of the sub-sequence to be run, e.g. sequence: sequcene.my_sub_sequence. Sub sequences can be nested arbitrarily to any desired level.

## Sequence Wait State

In addition to a straightforward service name plus data, sequences can paused, to continue after an entity’s state is a condition. This allows formore powerful use of sequence calls, for example you want to turn activate the conditioner, only after the window has been shut. Entities can be created in user defined namespaces, which will hold the state of conditions of interest and the sequence made to make use of the entity.

```yaml
sequence:
  air_condition_on:
    name: Air Con On
    namespace: mqtt
    steps:
    - mqtt/publish:
        topic: "hermes/tts"
        payload: "Turning on the AirCon, ensure windows are shut"

    - wait_state:
        entity_id: condition.living_room_window
        state: "closed"
        timeout: 60 # defaults to 15 minutes
        namespace: rules

    - mqtt/publish:
        topic: "air_condition/state"
        payload: "on"
```

# Running a Sequence

Once you have the sequence defined, you can run it in one of 2 ways:

using the `self.run_sequence()` api call

Using a sequence widget in HADashboard

A call to run the above sequence would look like this:

`handle = self.run_sequence("sequence.outside_motion_light")`
The handle value can be used to terminate a running sequence by supplying it to the `cancel_sequence()` call.

When an app is terminated or reloaded, all running sequences that it started are immediately terminated. There is no way to terminate a sequence started using HADashboard.

# Inline Sequences

Sequences can be run without the need to predefine them by specifying the steps to the `run_sequence()` command like so:

```yaml
handle = self.run_sequence([
       {'light/turn_on': {'entity_id': 'light.office_1', 'brightness': '5', 'color_name': 'white', 'namespace': 'default'}},
       {'sleep': 1},
       {'light/turn_off': {'entity_id': 'light.office_1'}},
       ])
```


# Keeping Your IDE Happy

Although it is possible to develop AppDaemon apps using a straight forward text editor, most users prefer to use some flavor of IDE. In order to simplify App development however, AppDaemon hides some of the complexity of import paths which makes for simpler coding but does have the side effect of confusing modern IDEs that are much stricter with import paths, and will show errors for modules that don’t conform to these rules, and will not understand enough about the import paths to supply helpful information about AppDaemon’s API. Fortunately however, with a few simple steps, the IDE can be persuaded to work as desired. In addition, AppDaemon’s APIs now have full type hints to make use of a modern IDE a lot easier and more helpful. This capability has been tested in Microsoft’s VS Code but these steps should apply equally to other IDEs such as `PyCharm`.

To set your IDE up properly there are a few initial steps, and a couple of rules to follow.

## Initial Setup
In order for your IDE to properly understand AppDaemon’s API, we need to give the IDE access to AppDaemon’s code, although this is not normally necessary for developing apps. The way to do this is to simply use pip to install AppDaemon in the virtual environment that your IDE is using. How this works varies between IDEs, but once you have worked out which virtual environment to target, simply activate it then use pip` to install AppDaemon:

```bash
$ source /path/to/venv/bin/activate
$ pip install appdaemon
```

After this step, your IDE will have access to the code for AppDaemon’s APIs and will understand how to assist with error checking and completions etc.

## Import Statements
For your IDE to be able to link things appropriately, it needs to be pointed at the interpreter you are using, with AppDaemon installed in it. This is usually done by setting the interpreter in the IDE’s settings, and pointing it at the virtual environment you are using.

The AppDaemon API classes can be imported as in the below example, or any other standard way you prefer.

```python
from appdaemon import adbase as ad      # Minimalist app base
from appdaemon.adapi import ADAPI       # Basic API
from appdaemon.plugins.hass import Hass # Home Assistant-specific API
from appdaemon.plugins.mqtt import Mqtt # MQTT-specific API
```
Imports of other python modules/packages from your apps can be done in the standard python ways. See the section on the app directory for more information.

With these preparations in place your IDE should give you correct error reporting and completion of API functions along with type hints and help text.
