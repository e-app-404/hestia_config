#TODO: Apply proper Markdown formatting to this document.

Samsung Smart TV
The samsungtv platform allows you to control a Samsung Smart TV.

Configuration 
To add the Samsung Smart TV device to your Home Assistant instance, use this My button:



Samsung Smart TV can be auto-discovered by Home Assistant. If an instance was found, it will be shown as Discovered. You can then set it up right away.

 Manual configuration steps
host
The IP address of the TV.

name
The friendly name of the TV.

Data updates 
The SamsungTV integration uses a local REST API with a WebSocket notification channel for immediate state information for media metadata, playback progress, volume etc.

Turn on action 
If the integration knows the MAC address of the TV from discovery, it will attempt to wake it using wake on LAN when calling turn on. Wake on LAN must be enabled on the TV for this to work. If the TV is connected to a smart strip or requires a more complex turn-on process, a turn_on action can be provided that will take precedence over the built-in wake on LAN functionality.

You can create an automation from the user interface, from the device create a new automation and select the Device is requested to turn on automation. Automations can also be created using an automation action:

# Example configuration.yaml entry
wake_on_lan: # enables `wake_on_lan` integration

automation:
  - alias: "Turn On Living Room TV with WakeOnLan"
    triggers:
      - trigger: samsungtv.turn_on
        entity_id: media_player.samsung_smart_tv
    actions:
      - action: wake_on_lan.send_magic_packet
        data:
          mac: aa:bb:cc:dd:ee:ff
YAML
Any other actions to power on the device can be configured.

Usage 
Changing channels 
Changing channels can be done by calling the media_player.play_media action with the following payload:

entity_id: media_player.samsung_tv
media_content_id: 590
media_content_type: channel
YAML
Selecting a source 
It’s possible to switch between the 2 sources TV and HDMI. Some older models also expose the installed applications through the WebSocket, in which case the source list is adjusted accordingly.

Remote 
The integration supports the remote platform. The remote allows you to send key commands to your TV with the remote.send_command action. The supported keys vary between TV models.

Full keycodes list
Example to send sequence of commands:

action: remote.send_command
target:
  device_id: 72953f9b4c9863e28ddd52c87dcebe05
data:
  command:
    - KEY_MENU
    - KEY_RIGHT
    - KEY_UP
    - KEY_UP
    - KEY_ENTER
YAML
Known issues and restrictions 
Subnet/VLAN 
Samsung SmartTV does not allow WebSocket connections across different subnets or VLANs. If your TV is not on the same subnet as Home Assistant this will fail. It may be possible to bypass this issue by using IP masquerading or a proxy.

H and J models 
Some televisions from the H and J series use an encrypted protocol and require manual pairing with the TV. This should be detected automatically when attempting to send commands using the WebSocket connection, and trigger the corresponding authentication flow.

Samsung TV keeps asking for permission 
The default setting on newer televisions is to ask for permission on every connection attempt. To avoid this behavior, please ensure that you adjust this to First time only in the Device connection manager > Access notification settings of your television. It is also recommended to cleanup the previous attempts in Device connection manager > Device list

Removing the integration 
This integration follows standard integration removal. No extra steps are required.

To remove an integration instance from Home Assistant 
Go to Settings > Devices & services and select the integration card.
From the list of devices, select the integration instance you want to remove.
Next to the entry, select the three dots  menu. Then, select Delete.
