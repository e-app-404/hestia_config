---
title: "AppDaemon MQTT API Reference"
authors: "AppDaemon Project, Hestia Ops"
source: "AppDaemon documentation"
slug: "hacs-appdaemon-mqttapi"
tags: ["home-assistant", "ops", "integration"]
original_date: "2023-10-09"
last_updated: "2025-10-09"
url: "https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html"
---

# MQTT API Reference

## Table of Contents
- [App Creation](#app-creation)
- [Making Calls to MQTT](#making-calls-to-mqtt)
- [Examples](#examples)
- [Reference](#reference)
- [MQTT Config](#mqtt-config)
- [See More](#see-more)

## App Creation

To create apps based on just the MQTT API, use code like the following:

```python
import mqttapi as mqtt

class MyApp(mqtt.Mqtt):
    def initialize(self):
        # Your initialization code here
```

## Making Calls to MQTT

The MQTT Plugin uses the inherited `call_service()` helper function from the AppDaemon API to carry out service calls from within an AppDaemon app. See the documentation of this function [here](https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.call_service) for a detailed description.

The function `call_service()` allows the app to carry out one of the following services:

- `mqtt/publish`
- `mqtt/subscribe`
- `mqtt/unsubscribe`

By simply specifying within the function what is to be done. It uses configuration specified in the plugin configuration which simplifies the call within the app significantly. Different brokers can be accessed within an App, as long as they are all declared when the plugins are configured, and using the `namespace` parameter. See the section on [namespaces](https://appdaemon.readthedocs.io/en/latest/APPGUIDE.html#namespaces) for a detailed description.

## Examples

```python
# Publish data to a broker
self.call_service("mqtt/publish", topic="homeassistant/bedroom/light", payload="ON")
# Unsubscribe a topic from a broker in a different namespace
self.call_service("mqtt/unsubscribe", topic="homeassistant/bedroom/light", namespace="mqtt2")
```

The MQTT API also provides 3 convenience functions to make calling of specific functions easier and more readable:
- mqtt_subscribe
- mqtt_unsubscribe
- mqtt_publish

Reference
---------

Services
--------

.. autofunction:: appdaemon.plugins.mqtt.mqttapi.Mqtt.mqtt_subscribe
.. autofunction:: appdaemon.plugins.mqtt.mqttapi.Mqtt.mqtt_unsubscribe
.. autofunction:: appdaemon.plugins.mqtt.mqttapi.Mqtt.mqtt_publish
.. autofunction:: appdaemon.plugins.mqtt.mqttapi.Mqtt.is_client_connected


Events
------

.. autofunction:: appdaemon.plugins.mqtt.mqttapi.Mqtt.listen_event

MQTT Config
-----------

Developers can get the MQTT configuration data (i.e., client_id or username) using the
helper function ``get_plugin_config()`` inherited from the AppDaemon API. See the
documentation of this function `here <AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_plugin_config>`__
for a detailed description.

See More
---------

Read the `AppDaemon API Reference <AD_API_REFERENCE.html>`__ to learn other inherited helper functions that
can be used by Hass applications.