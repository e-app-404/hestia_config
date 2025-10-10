---
title: "Valetudo Integration Guide"
authors: "Valetudo Team"
source: "https://valetudo.cloud"
slug: "valetudo-integration"
tags: ["home-assistant", "ops", "integration"]
original_date: "2025-10-07"
last_updated: "2025-10-07"
url: "https://valetudo.cloud"
---

# Valetudo

Valetudo is a cloud replacement for vacuum robots enabling local-only operation.

## Connecting Valetudo to Home Assistant

Valetudo connects to Home Assistant via MQTT + the MQTT Autodiscovery Feature of Home Assistant. This means that to connect Valetudo to Home Assistant, you will need an MQTT broker on your network.

For this, Mosquitto is the recommended choice. It is available in every relevant Linux distribution, can be dockerized, and can also be installed as a HAOS Add-On if you run the appliance version of Home Assistant.

It also has barely any resource footprint, meaning that there’s nothing to worry about if you just run it for Valetudo. Even more so, considering that it definitely won’t stay like that for long. Smarthome is a very slippery slope. :)

However you deploy the Mosquitto MQTT Broker, once deployed, you just point both Home Assistant and Valetudo at the same broker and then automagically a new Device + its Entities will appear in Home Assistant.

If it does not appear, make sure to check the logs in HA, the broker, and also Valetudo. Usually, it’s a network-related or ACL issue.

> **Note**: MQTT Autodiscovery will not create a “New devices discovered on your network” notification in Home Assistant. The new Valetudo Device will just be there.

## Building Dashboards with Valetudo

If you’d like to use the Valetudo Iconset as part of your dashboards, check out this repository: [hass-valetudo-icons](https://github.com/Hypfer/hass-valetudo-icons).

To display the map of your robot in a Home Assistant dashboard, the Valetudo Map Card is used. Setup instructions for that can be found on [hass.valetudo.cloud](https://hass.valetudo.cloud).

## Interacting with Valetudo

Basic interaction with Valetudo is done via the autodiscovered entities. They will allow you to observe state, toggle settings, trigger the auto-empty feature, start full cleanups, and more.

For more sophisticated use-cases like cleaning specific segments, the `mqtt.publish` action is used.

To determine the right payloads for your specific setup, in the Valetudo UI, simply configure/select the segments/zones/go-to locations like you’d normally do and then long-press the button that would start the action. This will bring up a dialog providing you with everything you’ll need:

![Valetudo Dialog](ha-demo-dialog.png)

To determine the right topic to publish that payload to, first determine the base topic by visiting **Connectivity - MQTT Connectivity** in the Valetudo UI:

![Valetudo Base Topic](ha-demo-base-topic.png)

Then, look up the rest of the topic + any other considerations for the desired capability in the MQTT documentation.

For the example in these screenshots, the full service call would look like this:

```yaml
action: mqtt.publish
data:
  topic: valetudo/InsecureYellowishGoldfish/MapSegmentationCapability/clean/set
  payload: '{"action":"start_segment_action","segment_ids":["3","2","5"],"iterations":2,"customOrder":true}'
```
