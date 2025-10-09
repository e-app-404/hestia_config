    ---

title: "AppDaemon ADAPI Reference"
authors: "AppDaemon Project, Hestia Ops"
source: "AppDaemon documentation"
slug: "hacs-appdaemon-adapi"
tags: ["home-assistant", "ops", "integration"]
original_date: "2023-10-09"
last_updated: "2025-10-09"
url: "<https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html>"
---

# AppDaemon ADAPI Reference

## Table of Contents

- [Overview](#overview)
- [App Creation](#app-creation)
- [Entity Class](#entity-class)
- [Services](#services)
- [Reference](#reference)

## Overview

The AppDaemon API comes in the form of a class called `ADAPI`, which provides high-level functionality for users to create their apps. This includes common functions such as listening for events/state changes, scheduling, manipulating entities, and calling services. The API is designed to be easy to use and understand, while still providing the power and flexibility needed to create complex automations.

## App Creation

To use the API, create a new class that inherits from `ADAPI` and implement the `initialize()` method. This method is required for all apps and is called when the app is started.

```python
from appdaemon.adapi import ADAPI

class MyApp(ADAPI):
    def initialize(self):
        self.log("MyApp is starting")
        # Use any of the ADAPI methods
        # handle = self.listen_state(...)
        # handle = self.listen_event(...)
```

Alternatively, the `ADBase` class can be used, which can provide some advantages, such as being able to access APIs for plugins in multiple namespaces.

```python
from appdaemon.adapi import ADAPI
from appdaemon.adbase import ADBase
from appdaemon.plugins.mqtt import Mqtt

class MyApp(ADBase):
    adapi: ADAPI    # This type annotation helps your IDE with autocompletion
    mqttapi: Mqtt

    def initialize(self):
        self.adapi = self.get_ad_api()
        self.adapi.log("MyApp is starting")

        # This requires having defined a plugin in the mqtt namespace in appdaemon.yaml
        self.mqttapi = self.get_plugin_api('mqtt')

        # Use any of the ADAPI methods through self.adapi
        # handle = self.adapi.listen_state(...)
        # handle = self.adapi.listen_event(...)
        # handle = self.adapi.run_in(...)
        # handle = self.adapi.run_every(...)
```

## Entity Class

Interacting with entities is a core part of writing automation apps, so being able to easily access and manipulate them is important. AppDaemon supports this by providing entities as Python objects.

The `Entity` class is essentially a light wrapper around `ADAPI` methods that pre-fills some arguments. Because of this, the entity doesn't have to actually exist for the `Entity` object to be created and used. If the entity doesn't exist, some methods will fail, but others will not. For example, `get_state()` will fail, but calling `set_state()` for an entity that doesn't exist will create it. This is useful for creating sensor entities that are available in Home Assistant.

```python
from appdaemon.adapi import ADAPI

class MyApp(ADAPI):
    def initialize(self):
        self.log("MyApp is starting")

        # Get light entity class
        self.kitchen_light = self.get_entity("light.kitchen_ceiling_light")

        # Assign a callback for when the state changes to on
        self.kitchen_light.listen_state(
            self.state_callback,
            attribute="brightness",
            new='on'
        )

    def state_callback(self, entity, attribute, old, new, **kwargs):
        self.log(f'{self.kitchen_light.friendly_name} turned on')
```

## Services

AppDaemon provides some services from some built-in namespaces. These services can be called from any app, provided they use the correct namespace. These services are listed below.

> **Note**: A service call always uses the app's default namespace. See the section on [namespaces](https://appdaemon.readthedocs.io/en/latest/APPGUIDE.html#namespaces) for more information.

### Admin Namespace

| Service           | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| app/create        | Create a new app. Provide module/class, optional app name, app_file, app_dir |
| app/edit          | Edit an existing app's args in realtime                                     |
| app/remove        | Remove an existing app                                                      |
| app/start         | Start a terminated app                                                      |
| app/stop          | Stop a running app                                                          |
| app/restart       | Restart a running app                                                       |
| app/reload        | Check for app update                                                        |
| app/enable        | Enable a disabled app                                                       |
| app/disable       | Disable an enabled app                                                      |
| production_mode/set | Set production mode (True/False)                                          |

Example:

```python
# Create a new app
data = {
    "module": "web_app",
    "class": "WebApp",
    "namespace": "admin",
    "app": "web_app3",
    "endpoint": "endpoint3",
    "app_dir": "web_apps",
    "app_file": "web_apps.yaml"
}
self.call_service("app/create", **data)

# Edit an existing app
self.call_service("app/edit", app="light_app", module="light_system", namespace="admin")

# Remove an existing app
self.call_service("app/remove", app="light_app", namespace="admin")

# Start a terminated app
self.call_service("app/start", app="light_app", namespace="admin")

# Stop a running app
self.call_service("app/stop", app="light_app", namespace="admin")

# Restart a running app
self.call_service("app/restart", app="light_app", namespace="admin")

# Check for app update
self.call_service("app/reload", namespace="admin")

# Enable a disabled app
self.call_service("app/enable", app="living_room_app", namespace="admin")

# Disable an enabled app
self.call_service("app/disable", app="living_room_app", namespace="admin")

# Set production mode
self.call_service("production_mode/set", mode=True, namespace="admin")
```

### State Namespace

| Service           | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| state/add_entity  | Add an existing entity to the required namespace                            |
| state/set         | Set the state of an entity                                                  |
| state/remove_entity | Remove an existing entity from the required namespace                     |

Example:

```python

.. code:: python
    self.call_service("app/reload", namespace="admin")

    self.call_service("app/enable", app="living_room_app", namespace="admin")
    self.call_service("production_mode/set", mode=True, namespace="admin")

        "state/set",
        state="on",
        attributes={"friendly_name" : "Sensor Test"},
        namespace="default"
    )

**state/set**

Sets the state of an entity. This service allows any key-worded args to define what entity's values need to be set.

.. code:: python

    self.call_service(
        "state/set",
        entity_id="sensor.test",
        state="on",
        attributes={"friendly_name" : "Sensor Test"},
        namespace="default"
    )

**state/remove_entity**

Removes an existing entity from the required namespace.

.. code:: python

    self.call_service("state/remove_entity", entity_id="sensor.test", namespace="default")

All namespaces except ``admin``:

**event/fire**

Fires an event within the specified namespace. The `event` arg is required.

.. code:: python

    self.call_service("event/fire", event="test_event", entity_id="appdaemon.test", namespace="hass")

rules

~~~~~

**sequence/run**

Runs a predefined sequence. The `entity_id` arg with the sequence full-qualified entity name is required.

.. code:: python

    self.call_service("sequence/run", entity_id ="sequence.christmas_lights", namespace="rules")

**sequence/cancel**

Cancels a predefined sequence. The `entity_id` arg with the sequence full-qualified entity name is required.

.. code:: python

    self.call_service("sequence/cancel", entity_id ="sequence.christmas_lights", namespace="rules")

Reference
---------

Entity API
~~~~~~~~~~

.. automethod:: appdaemon.entity.Entity.add
.. automethod:: appdaemon.entity.Entity.call_service
.. automethod:: appdaemon.entity.Entity.copy
.. automethod:: appdaemon.entity.Entity.exists
.. automethod:: appdaemon.entity.Entity.get_state
.. automethod:: appdaemon.entity.Entity.listen_state
.. automethod:: appdaemon.entity.Entity.is_state
.. automethod:: appdaemon.entity.Entity.set_namespace
.. automethod:: appdaemon.entity.Entity.set_state
.. automethod:: appdaemon.entity.Entity.toggle
.. automethod:: appdaemon.entity.Entity.turn_off
.. automethod:: appdaemon.entity.Entity.turn_on
.. automethod:: appdaemon.entity.Entity.wait_state

In addition to the above, there are a couple of property attributes the Entity class supports:

- entity_id
- namespace
- domain
- entity_name
- state
- attributes
- friendly_name
- last_changed
- last_changed_seconds

State

~~~~~

.. automethod:: appdaemon.adapi.ADAPI.get_state
.. automethod:: appdaemon.adapi.ADAPI.set_state
.. automethod:: appdaemon.adapi.ADAPI.listen_state
.. automethod:: appdaemon.adapi.ADAPI.cancel_listen_state
.. automethod:: appdaemon.adapi.ADAPI.info_listen_state


Time
~~~~

.. automethod:: appdaemon.adapi.ADAPI.parse_utc_string
.. automethod:: appdaemon.adapi.ADAPI.get_tz_offset
.. automethod:: appdaemon.adapi.ADAPI.convert_utc
.. automethod:: appdaemon.adapi.ADAPI.sun_up
.. automethod:: appdaemon.adapi.ADAPI.sun_down
.. automethod:: appdaemon.adapi.ADAPI.parse_time
.. automethod:: appdaemon.adapi.ADAPI.parse_datetime
.. automethod:: appdaemon.adapi.ADAPI.get_now
.. automethod:: appdaemon.adapi.ADAPI.get_now_ts
.. automethod:: appdaemon.adapi.ADAPI.now_is_between
.. automethod:: appdaemon.adapi.ADAPI.sunrise
.. automethod:: appdaemon.adapi.ADAPI.sunset
.. automethod:: appdaemon.adapi.ADAPI.time
.. automethod:: appdaemon.adapi.ADAPI.datetime
.. automethod:: appdaemon.adapi.ADAPI.date
.. automethod:: appdaemon.adapi.ADAPI.get_timezone

Scheduler
~~~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.run_at
.. automethod:: appdaemon.adapi.ADAPI.run_in
.. automethod:: appdaemon.adapi.ADAPI.run_once
.. automethod:: appdaemon.adapi.ADAPI.run_every
.. automethod:: appdaemon.adapi.ADAPI.run_daily
.. automethod:: appdaemon.adapi.ADAPI.run_hourly
.. automethod:: appdaemon.adapi.ADAPI.run_minutely
.. automethod:: appdaemon.adapi.ADAPI.run_at_sunset
.. automethod:: appdaemon.adapi.ADAPI.run_at_sunrise
.. automethod:: appdaemon.adapi.ADAPI.timer_running
.. automethod:: appdaemon.adapi.ADAPI.cancel_timer
.. automethod:: appdaemon.adapi.ADAPI.info_timer
.. automethod:: appdaemon.adapi.ADAPI.reset_timer

Service

~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.register_service
.. automethod:: appdaemon.adapi.ADAPI.deregister_service
.. automethod:: appdaemon.adapi.ADAPI.list_services
.. automethod:: appdaemon.adapi.ADAPI.call_service

Sequence
~~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.run_sequence
.. automethod:: appdaemon.adapi.ADAPI.cancel_sequence

Events

~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.listen_event
.. automethod:: appdaemon.adapi.ADAPI.cancel_listen_event
.. automethod:: appdaemon.adapi.ADAPI.info_listen_event
.. automethod:: appdaemon.adapi.ADAPI.fire_event

Logging
~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.log
.. automethod:: appdaemon.adapi.ADAPI.error
.. automethod:: appdaemon.adapi.ADAPI.listen_log
.. automethod:: appdaemon.adapi.ADAPI.cancel_listen_log
.. automethod:: appdaemon.adapi.ADAPI.get_main_log
.. automethod:: appdaemon.adapi.ADAPI.get_error_log
.. automethod:: appdaemon.adapi.ADAPI.get_user_log
.. automethod:: appdaemon.adapi.ADAPI.set_log_level
.. automethod:: appdaemon.adapi.ADAPI.set_error_level

Dashboard

~~~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.dash_navigate

Namespace
~~~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.set_namespace
.. automethod:: appdaemon.adapi.ADAPI.get_namespace
.. automethod:: appdaemon.adapi.ADAPI.list_namespaces
.. automethod:: appdaemon.adapi.ADAPI.save_namespace

Threading

~~~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.set_app_pin
.. automethod:: appdaemon.adapi.ADAPI.get_app_pin
.. automethod:: appdaemon.adapi.ADAPI.set_pin_thread
.. automethod:: appdaemon.adapi.ADAPI.get_pin_thread

Async
~~~~~

.. automethod:: appdaemon.adapi.ADAPI.create_task
.. automethod:: appdaemon.adapi.ADAPI.run_in_executor
.. automethod:: appdaemon.adapi.ADAPI.sleep


Utility
~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.get_app
.. automethod:: appdaemon.adapi.ADAPI.get_ad_version
.. automethod:: appdaemon.adapi.ADAPI.entity_exists
.. automethod:: appdaemon.adapi.ADAPI.split_entity
.. automethod:: appdaemon.adapi.ADAPI.remove_entity
.. automethod:: appdaemon.adapi.ADAPI.split_device_list
.. automethod:: appdaemon.adapi.ADAPI.get_plugin_config
.. automethod:: appdaemon.adapi.ADAPI.friendly_name
.. automethod:: appdaemon.adapi.ADAPI.set_production_mode
.. automethod:: appdaemon.adapi.ADAPI.start_app
.. automethod:: appdaemon.adapi.ADAPI.stop_app
.. automethod:: appdaemon.adapi.ADAPI.restart_app
.. automethod:: appdaemon.adapi.ADAPI.reload_apps

Dialogflow
~~~~~~~~~~

.. automethod:: appdaemon.adapi.ADAPI.get_dialogflow_intent
.. automethod:: appdaemon.adapi.ADAPI.get_dialogflow_slot_value
.. automethod:: appdaemon.adapi.ADAPI.format_dialogflow_response

Alexa

~~~~~

.. automethod:: appdaemon.adapi.ADAPI.get_alexa_intent
.. automethod:: appdaemon.adapi.ADAPI.get_alexa_slot_value
.. automethod:: appdaemon.adapi.ADAPI.format_alexa_response
.. automethod:: appdaemon.adapi.ADAPI.get_alexa_error

API
~~~

.. automethod:: appdaemon.adapi.ADAPI.register_endpoint
.. automethod:: appdaemon.adapi.ADAPI.deregister_endpoint

WebRoute
~~~

.. automethod:: appdaemon.adapi.ADAPI.register_route
.. automethod:: appdaemon.adapi.ADAPI.deregister_route

Other
~~~~~

.. automethod:: appdaemon.adapi.ADAPI.run_in_thread
.. automethod:: appdaemon.adapi.ADAPI.submit_to_executor
.. automethod:: appdaemon.adapi.ADAPI.get_thread_info
.. automethod:: appdaemon.adapi.ADAPI.get_scheduler_entries
.. automethod:: appdaemon.adapi.ADAPI.get_callback_entries
.. automethod:: appdaemon.adapi.ADAPI.depends_on_module
