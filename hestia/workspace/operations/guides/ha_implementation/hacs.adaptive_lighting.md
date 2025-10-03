---
title: "Adaptive Lighting (HACS)"
authors: "basnijholt / Adaptive Lighting"
source: "Adaptive Lighting (HACS)"
slug: "adaptive-lighting"
tags: ["home-assistant","hacs","adaptive-lighting","lights"]
original_date: "2019-01-01"
last_updated: "2025-10-03"
url: "https://github.com/basnijholt/adaptive-lighting"
---

🌞 Adaptive Lighting: Enhance Your Home's Atmosphere with Smart, Sun-Synchronized Lighting 🌙
logo
Adaptive Lighting is a custom component for Home Assistant that intelligently adjusts the brightness and color of your lights 💡 based on the sun's position, while still allowing for manual control.

Download and install directly through HACS (Home Assistant Community Store):

Open your Home Assistant instance and open the Adaptive Lighting integration inside the Home Assistant Community Store.

By automatically adapting the settings of your lights throughout the day, Adaptive Lighting helps maintain your natural circadian rhythm 😴, which can lead to improved sleep, mood, and overall well-being. Experience cooler color temperatures at noon, gradually transitioning to warmer colors at sunset and sunrise.

In addition to its regular mode, Adaptive Lighting also offers a "sleep mode" 🌜 which sets your lights to minimal brightness and a very warm color, perfect for winding down at night.

🌈 Visualize Adaptive Lighting's settings with the 🌞 Adaptive Lighting Simulator WebApp 🌛

https://github.com/basnijholt/adaptive-lighting/assets/6897215/68908f7d-fbf1-4991-98ce-3f2af6df996f

[ToC]

:bulb: Features
When initially turning on a light that is controlled by Adaptive Lighting, the light.turn_on service call is intercepted, and the light's brightness and color are automatically adjusted based on the sun's position. After that, the light's brightness and color are automatically adjusted at a regular interval.

Adaptive Lighting provides four switches (using "living_room" as an example component name):

switch.adaptive_lighting_living_room: Turn Adaptive Lighting on or off and view current light settings through its attributes.
switch.adaptive_lighting_sleep_mode_living_room: Activate "sleep mode" 😴 and set custom sleep_brightness and sleep_color_temp.
switch.adaptive_lighting_adapt_brightness_living_room: Enable or disable brightness adaptation 🔆 for supported lights.
switch.adaptive_lighting_adapt_color_living_room: Enable or disable color adaptation 🌈 for supported lights.
:control_knobs: Regain Manual Control
Adaptive Lighting is designed to automatically detect when you or another source (e.g., automation) manually changes light settings 🕹️. When this occurs, the affected light is marked as "manually controlled," and Adaptive Lighting will not make further adjustments until the light is turned off and back on or reset using the adaptive_lighting.set_manual_control service call. This feature is available when take_over_control is enabled.

Additionally, enabling detect_non_ha_changes allows Adaptive Lighting to detect all state changes, including those made outside of Home Assistant, by comparing the light's state to its previously used settings. The adaptive_lighting.manual_control event is fired when a light is marked as "manually controlled," allowing for integration with automations 🤖.

⚠️ Caution: Some lights might falsely indicate an 'on' state, which could result in lights turning on unexpectedly. Disable detect_non_ha_changes if you encounter such issues.

:books: Table of Contents
:gear: Configuration
:memo: Options
:hammer_and_wrench: Services
adaptive_lighting.apply
adaptive_lighting.set_manual_control
adaptive_lighting.change_switch_settings
:robot: Automation examples
Additional Information
:sos: Troubleshooting
:exclamation: Common Problems & Solutions
:bulb: Lights Not Responding or Turning On by Themselves
:signal_strength: WiFi Networks
:spider_web: Zigbee, Z-Wave, and Other Mesh Networks
:rainbow: Light Colors Not Matching
:bulb: Bulb-Specific Issues
:bar_chart: Graphs!
:sunny: Sun Position
:thermometer: Color Temperature
:high_brightness: Brightness
While using transition_until_sleep: true
Custom brightness ramps using brightness_mode with "linear" and "tanh"
:eyes: See also
:busts_in_silhouette: Contributors
Translating Adaptive Lighting
:gear: Configuration
Adaptive Lighting supports configuration through both YAML and the frontend (Settings -> Devices and Services -> Adaptive Lighting, Adaptive Lighting -> Options), with identical option names in both methods.

# Example configuration.yaml entry
adaptive_lighting:
  lights:
    - light.living_room_lights
Note: If you plan to strictly use the UI, the adaptive_lighting: entry must still be added to the YAML.

Transform your home's atmosphere with Adaptive Lighting 🏠, and experience the benefits of intelligent, sun-synchronized lighting today!

:memo: Options
All of the configuration options are listed below, along with their default values. The YAML and frontend configuration methods support all of the options listed below.

Variable name	Description	Default	Type
lights	List of light entity_ids to be controlled (may be empty). 🌟	[]	list of entity_ids
interval	Frequency to adapt the lights, in seconds. 🔄	90	int > 0
transition	Duration of transition when lights change, in seconds. 🕑	45	float 0-6553
initial_transition	Duration of the first transition when lights turn from off to on in seconds. ⏲️	1	float 0-6553
min_brightness	Minimum brightness percentage. 💡	1	int 1-100
max_brightness	Maximum brightness percentage. 💡	100	int 1-100
min_color_temp	Warmest color temperature in Kelvin. 🔥	2000	int 1000-10000
max_color_temp	Coldest color temperature in Kelvin. ❄️	5500	int 1000-10000
prefer_rgb_color	Whether to prefer RGB color adjustment over light color temperature when possible. 🌈	False	bool
sleep_brightness	Brightness percentage of lights in sleep mode. 😴	1	int 1-100
sleep_rgb_or_color_temp	Use either "rgb_color" or "color_temp" in sleep mode. 🌙	color_temp	one of ['color_temp', 'rgb_color']
sleep_color_temp	Color temperature in sleep mode (used when sleep_rgb_or_color_temp is color_temp) in Kelvin. 😴	1000	int 1000-10000
sleep_rgb_color	RGB color in sleep mode (used when sleep_rgb_or_color_temp is "rgb_color"). 🌈	[255, 56, 0]	RGB color
sleep_transition	Duration of transition when "sleep mode" is toggled in seconds. 😴	1	float 0-6553
transition_until_sleep	When enabled, Adaptive Lighting will treat sleep settings as the minimum, transitioning to these values after sunset. 🌙	False	bool
sunrise_time	Set a fixed time (HH:MM:SS) for sunrise. 🌅	None	str
min_sunrise_time	Set the earliest virtual sunrise time (HH:MM:SS), allowing for later sunrises. 🌅	None	str
max_sunrise_time	Set the latest virtual sunrise time (HH:MM:SS), allowing for earlier sunrises. 🌅	None	str
sunrise_offset	Adjust sunrise time with a positive or negative offset in seconds. ⏰	0	int
sunset_time	Set a fixed time (HH:MM:SS) for sunset. 🌇	None	str
min_sunset_time	Set the earliest virtual sunset time (HH:MM:SS), allowing for later sunsets. 🌇	None	str
max_sunset_time	Set the latest virtual sunset time (HH:MM:SS), allowing for earlier sunsets. 🌇	None	str
sunset_offset	Adjust sunset time with a positive or negative offset in seconds. ⏰	0	int
brightness_mode	Brightness mode to use. Possible values are default, linear, and tanh (uses brightness_mode_time_dark and brightness_mode_time_light). 📈	default	one of ['default', 'linear', 'tanh']
brightness_mode_time_dark	(Ignored if brightness_mode='default') The duration in seconds to ramp up/down the brightness before/after sunrise/sunset. 📈📉	900	int
brightness_mode_time_light	(Ignored if brightness_mode='default') The duration in seconds to ramp up/down the brightness after/before sunrise/sunset. 📈📉.	3600	int
take_over_control	Disable Adaptive Lighting if another source calls light.turn_on while lights are on and being adapted. Note that this calls homeassistant.update_entity every interval! 🔒	True	bool
detect_non_ha_changes	Detects and halts adaptations for non-light.turn_on state changes. Needs take_over_control enabled. 🕵️ Caution: ⚠️ Some lights might falsely indicate an 'on' state, which could result in lights turning on unexpectedly. Disable this feature if you encounter such issues.	False	bool
autoreset_control_seconds	Automatically reset the manual control after a number of seconds. Set to 0 to disable. ⏲️	0	int 0-31536000
only_once	Adapt lights only when they are turned on (true) or keep adapting them (false). 🔄	False	bool
adapt_only_on_bare_turn_on	When turning lights on initially. If set to true, AL adapts only if light.turn_on is invoked without specifying color or brightness. ❌🌈 This e.g., prevents adaptation when activating a scene. If false, AL adapts regardless of the presence of color or brightness in the initial service_data. Needs take_over_control enabled. 🕵️	False	bool
separate_turn_on_commands	Use separate light.turn_on calls for color and brightness, needed for some light types. 🔀	False	bool
send_split_delay	Delay (ms) between separate_turn_on_commands for lights that don't support simultaneous brightness and color setting. ⏲️	0	int 0-10000
adapt_delay	Wait time (seconds) between light turn on and Adaptive Lighting applying changes. Might help to avoid flickering. ⏲️	0	float > 0
skip_redundant_commands	Skip sending adaptation commands whose target state already equals the light's known state. Minimizes network traffic and improves the adaptation responsivity in some situations. 📉Disable if physical light states get out of sync with HA's recorded state.	False	bool
intercept	Intercept and adapt light.turn_on calls to enabling instantaneous color and brightness adaptation. 🏎️ Disable for lights that do not support light.turn_on with color and brightness.	True	bool
multi_light_intercept	Intercept and adapt light.turn_on calls that target multiple lights. ➗⚠️ This might result in splitting up a single light.turn_on call into multiple calls, e.g., when lights are in different switches. Requires intercept to be enabled.	True	bool
include_config_in_attributes	Show all options as attributes on the switch in Home Assistant when set to true. 📝	False	bool
Full example:

# Example configuration.yaml entry
adaptive_lighting:
- name: "default"
  lights: []
  prefer_rgb_color: false
  transition: 45
  initial_transition: 1
  interval: 90
  min_brightness: 1
  max_brightness: 100
  min_color_temp: 2000
  max_color_temp: 5500
  sleep_brightness: 1
  sleep_color_temp: 1000
  sunrise_time: "08:00:00"  # override the sunrise time
  sunrise_offset:
  sunset_time:
  sunset_offset: 1800  # in seconds or '00:30:00'
  take_over_control: true
  detect_non_ha_changes: false
  only_once: false
:hammer_and_wrench: Services
adaptive_lighting.apply
adaptive_lighting.apply applies Adaptive Lighting settings to lights on demand.

Service data attribute	Description	Required	Type
entity_id	The entity_id of the switch with the settings to apply. 📝	✅	list of entity_ids
lights	A light (or list of lights) to apply the settings to. 💡	❌	list of entity_ids
transition	Duration of transition when lights change, in seconds. 🕑	❌	float 0-6553
adapt_brightness	Whether to adapt the brightness of the light. 🌞	❌	bool
adapt_color	Whether to adapt the color on supporting lights. 🌈	❌	bool
prefer_rgb_color	Whether to prefer RGB color adjustment over light color temperature when possible. 🌈	❌	bool
turn_on_lights	Whether to turn on lights that are currently off. 🔆	❌	bool
adaptive_lighting.set_manual_control
adaptive_lighting.set_manual_control can mark (or unmark) whether a light is "manually controlled", meaning that when a light has manual_control, the light is not adapted.

Service data attribute	Description	Required	Type
entity_id	The entity_id of the switch in which to (un)mark the light as being manually controlled. 📝	✅	list of entity_ids
lights	entity_id(s) of lights, if not specified, all lights in the switch are selected. 💡	❌	list of entity_ids
manual_control	Whether to add ("true") or remove ("false") the light from the "manual_control" list. 🔒	❌	bool
adaptive_lighting.change_switch_settings
adaptive_lighting.change_switch_settings (new in 1.7.0) Change any of the above configuration options of Adaptive Lighting (such as sunrise_time or prefer_rgb_color) with a service call directly from your script/automation.

⚠️ Note: These settings will not be written to your config and will be reset on restart of Home Assistant! You can see the current settings in the switch.adaptive_lighting_XXX attributes if include_config_in_attributes is enabled.

Service data attribute	Required	Description
use_defaults	❌	(default: current for current settings) Choose from factory, configuration, or current to reset variables not being set with this service call. current leaves them as they are, configuration resets to initial startup values, factory resets to default values listed in the documentation.
all other keys (except the ones in the table below ⚠️)	❌	See the table below for disallowed keys.
The following keys are disallowed:

DISALLOWED service data	Description
entity_id	You cannot change the switch's entity_id, as it has already been registered.
lights	You may call adaptive_lighting.apply with your lights or create a new config instead.
name	You can rename your switch's display name in Home Assistant's UI.
interval	The interval is used only once when the config loads. A config change and restart are required.
:robot: Automation examples
Reset the manual_control status of a light after an hour.
Toggle multiple Adaptive Lighting switches to "sleep mode" using an input_boolean.sleep_mode.
Additional Information
For more details on adding the integration and setting options, refer to the documentation of the PR and this video tutorial on Reddit.

Adaptive Lighting was initially inspired by @claytonjn's hass-circadian_lighting, but has since been entirely rewritten and expanded with new features.

:sos: Troubleshooting
Encountering issues? Enable debug logging in your configuration.yaml:

logger:
  default: warning
  logs:
    custom_components.adaptive_lighting: debug
After the issue occurs, create a new issue report with the log (/config/home-assistant.log).

:exclamation: Common Problems & Solutions
:bulb: Lights Not Responding or Turning On by Themselves
Adaptive Lighting sends more commands to lights than a typical human user would. If your light control network is unhealthy, you may experience:

Laggy manual commands (e.g., turning lights on or off).
Unresponsive lights.
Home Assistant reporting incorrect light states, causing Adaptive Lighting to inadvertently turn lights back on.
Most issues that appear to be caused by Adaptive Lighting are actually due to unrelated problems. Addressing these issues will significantly improve your Home Assistant experience.

In case lights are suddenly turning on by themselves, this is most likely due to the light incorrectly reporting an "on" state to Home Assistant, leading to an undesired Adaptive Lighting action. To prevent adapting in cases where the state of the light is suddenly "on" and only adapt if there is an associated light.turn_on service call, set detect_non_ha_changes: false.

:signal_strength: WiFi Networks
Ensure your light bulbs have a strong WiFi connection. If the signal strength is less than -70dBm, the connection may be weak and prone to dropping messages.

:spider_web: Zigbee, Z-Wave, and Other Mesh Networks
Mesh networks typically require powered devices to act as routers, relaying messages back to the central coordinator (the radio connected to Home Assistant). Philips lights usually function as routers, while Ikea, Sengled, and generic Tuya bulbs often do not. If devices become unresponsive or fail to respond to commands, Adaptive Lighting can exacerbate the issue. Use network maps (available in ZHA, zigbee2mqtt, deCONZ, and ZWaveJS UI) to evaluate your network health. Smart plugs can be an affordable way to add more routers to your network.

For most Zigbee networks, using groups is essential for optimal performance. For example, if you want to use Adaptive Lighting in a hallway with six bulbs, adding each bulb individually to the Adaptive Lighting configuration could overwhelm the network with commands. Instead, create a group in your Zigbee software (not a regular Home Assistant group) and add that single group to the Adaptive Lighting configuration. This sends a single broadcast command to adjust all bulbs, improving response times and keeping the bulbs in sync.

As a rule of thumb, if you always control lights together (e.g., bulbs in a ceiling fixture), they should be in a Zigbee group. Expose only the group (not individual bulbs) in Home Assistant Dashboards and external systems like Google Home or Apple HomeKit.

:warning: If you control lights individually, manual_control cannot behave correctly! If you need to control lights individually as well, use a Home Assistant Light Group.

:rainbow: Light Colors Not Matching
Bulbs from different manufacturers or models may have varying color temperature specifications. For instance, if you have two Adaptive Lighting configurations—one with only Philips Hue White Ambiance bulbs and another with a mix of Philips Hue White Ambiance and Sengled bulbs—the Philips Hue bulbs may appear to have different color temperatures despite having identical settings.

To resolve this:

Include only bulbs of the same make and model in a single Adaptive Lighting configuration.
Rearrange bulbs so that different color temperatures are not visible simultaneously.
:bulb: Bulb-Specific Issues
These lights are known to exhibit disadvantageous behaviour due to firmware bugs, insufficient functionality, or hardware limitations:

Sengled Z01-A19NAE26
Unexpected turn-ons: If Adaptive Lighting sends a long transition time (like the default 45 seconds), and the bulb is turned off during that time, it may turn back on after approximately 10 seconds to continue the transition command. Since the bulb is turning itself on, there will be no obvious trigger in Home Assistant or other logs indicating the cause of the light turning on. To fix this, set a much shorter transition time, such as 1 second.
Heat sensitivity: Additionally, these bulbs may perform poorly in enclosed "dome" style ceiling lights, particularly when hot. While most LEDs (even non-smart ones) state in the fine print that they do not support working in enclosed fixtures, in practice, more expensive bulbs like Philips Hue generally perform better. To resolve this issue, move the problematic bulbs to open-air fixtures.
Ikea Tradfri bulbs/drivers (and related Ikea smart light products)
Unsupported simultaneous transition of brightness and color: When receiving such a command, they switch the brightness instantly and only transition the color. To get smooth transitions of both brightness and color, enable separate_turn_on_commands.
Unresponsiveness during color transitions: No other commands are processed during an ongoing color transition, e.g., turn-off commands are ignored and lights stay on despite being reported as off to Home Assistant. The default config with long transitions thus results in long periods of unresponsiveness. To work around this, disable transitions by setting transition to 0, and increase the adaptation frequency by setting interval to a short time, e.g., 15 seconds, to retain the impression of smooth continuous adaptations. Keeping the initial_transition is recommended for a smooth fade-in (lights are usually not turned off momentarily after being turned on, in which case a short period of unresponsiveness is tolerable).
:bar_chart: Graphs!
These graphs were generated using the values calculated by the Adaptive Lighting sensor/switch(es).

:sunny: Sun Position
cl_percent|690x131

:thermometer: Color Temperature
cl_color_temp|690x129

:high_brightness: Brightness
cl_brightness|690x130

While using transition_until_sleep: true
image

Custom brightness ramps using brightness_mode with "linear" and "tanh"
Enhance your control over brightness transitions during sunrise and sunset with brightness_mode (click here to learn more 🧠).
Notice the values of brightness_mode_time_light and brightness_mode_time_dark in the text box. image image image image

Check out the interactive webapp on https://basnijholt.github.io/adaptive-lighting/ to play with the parameters and see how the brightness changes!

:eyes: See also
Sleep better with Adaptive Lighting in Home Assistant by Florian Wartner on 2023-02-23 (blog post 📜)
Automatic smart light brightness and color based on the sun by Home Automation Guy on 2022-08-31 (YouTube video 📺)
Adaptive Lighting Blew My Mind in Home Assistant - How to set it up by Smart Home Junkie on 2022-06-26 (YouTube video 📺)