# Events

Events are a fundamental part of how AppDaemon works internally. Plugins fire events and AppDaemon communicates them to apps as required.

For instance, the MQTT plugin will fire an event when a message is received, and the HASS plugin will fire events for all Home Assistant events.

## Event Callbacks
Refer to the callbacks section for more information.

## AppDaemon Events
In addition to the HASS and MQTT supplied events, AppDaemon adds 3 more events. These are internal to AppDaemon and are not visible on the Home Assistant bus:

AppDaemon Internal Events
Event Type

Namespace

Description

appd_started

global

Fired once when AppDaemon is first started and after Apps are initialized.

app_initialized

admin

Fired when each app is started with {"app": <app_name>} for its data.

app_terminated

admin

Fired when each app is terminated with {"app": <app_name>} for its data after all its callbacks have been removed.

plugin_started

<plugin>

Fired when a plugin notifies AppDaemon that is has started with {"name": <plugin_name>}. Called in the namespace of the plugin.

plugin_stopped

<plugin>

Fired when a plugin notifies AppDaemon that is has stopped with {"name": <plugin_name>}. Called in the namespace of the plugin.

service_registered

<service>

Fired when AppDaemon registers a service with {"namespace": <namespace>, "domain": <domain>, "service": <service>}. Called in the namespace of the service.

service_deregistered

<service>

Fired when AppDaemon deregisters a service with {"namespace": <namespace>, "domain": <domain>, "service": <service>}. Called in the namespace of the service.

stream_connected

admin

Fired when the AD stream connects

stream_disconnected

admin

Fired when the AD stream disconnects

Home Assistant Events
We have already seen how state changes can be propagated to AppDaemon via the HASS plugin - a state change however is merely an example of an event within Home Assistant. There are several other event types, among them are:

homeassistant_start

homeassistant_stop

state_changed

service_registered

call_service

service_executed

platform_discovered

component_loaded

Using the HASS plugin, it is possible to subscribe to specific events as well as fire off events.

MQTT Events
The MQTT plugin uses events as its primary (and only interface) to MQTT. The model is fairly simple - every time an MQTT message is received, and event of type MQTT_MESSAGE is fired. Apps are able to subscribe to this event and process it appropriately.

Use of Events for Signalling between Home Assistant and AppDaemon
Home Assistant allows for the creation of custom events, and existing components can send and receive them. This provides a useful mechanism for signaling back and forth between Home Assistant and AppDaemon. For instance, if you would like to create a UI Element to fire off some code in Home Assistant, all that is necessary is to create a script to fire a custom event, then subscribe to that event in AppDaemon. The script would look something like this:

alias: Day
sequence:
- event: MODE_CHANGE
  event_data:
    mode: Day
The custom event MODE_CHANGE would be subscribed to with:

self.listen_event(self.mode_event, "MODE_CHANGE")
Home Assistant can send these events in a variety of other places - within automations, and also directly from Alexa intents. Home Assistant can also listen for custom events with its automation component. This can be used to signal from AppDaemon code back to home assistant. Here is a sample automation:

automation:
  trigger:
    platform: event
    event_type: MODE_CHANGE
    ...
    ...
This can be triggered with a call to AppDaemon’s fire_event() as follows:

self.fire_event("MODE_CHANGE", mode = "Day")
Use of Events for Interacting with HADashboard
HADashboard listens for certain events. An event type of “hadashboard” will trigger certain actions such as page navigation. For more information see the Dashboard configuration pages

AppDaemon provides convenience functions to assist with this.

HASS Presence
Presence in Home Assistant is tracked using Device Trackers. The state of all device trackers can be found using the get_state() call. However, AppDaemon provides several convenience functions to make this easier.

Writing to Logfiles
AppDaemon uses 2 separate logs - the general log and the error log. An App can write to either of these using the supplied convenience methods log() and error(), which are provided as part of parent AppDaemon class, and the call will automatically prepend the name of the App making the call.

The functions are based on the Python logging module and are able to pass through parameters for interpolation, and additional parameters such as exc_info just as with the usual style of invocation. Use of loggers interpolation method over the use of format() is recommended for performance reasons, as logger will only interpolate of the line is actually written whereas format() will always do the substitution.

The -D option of AppDaemon can be used to specify a global logging level, and Apps can individually have their logging level set as required. This can be achieved using the set_log_level() API call, or by using the special debug argument to the apps settings in apps.yaml:

log_level: DEBUG
In addition, apps can select a default log for the log() call using the log directive in apps.yaml, referencing the section name in appdaemon.yaml. This can be one of the 4 builtin logs, main_log, error_log, diag_log and access_log, or a user-defined log, e.g.:

log: test_log
If an App has set a default log other than one of the 4 built in logs, these logs can still be accessed specifically using either the log= parameter of the log() call, or by getting the appropriate logger object using the get_user_log() call, which also works for default logs.

AppDaemon’s logging mechanism also allows you to use placeholders for the module, function, and line number. If you include the following in the test of your message:

__function__
__module__
__line__
They will automatically be expanded to the appropriate values in the log message.

