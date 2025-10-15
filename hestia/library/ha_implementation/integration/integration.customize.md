---
title: "Customizing entities"
description: "Simple customization for entities."
source: https://github.com/home-assistant/home-assistant.io/blob/current/source/_docs/configuration/customizing-devices.markdown
---

# Home Assistant Entity Customization

After adding a new device, you might find the automatically assigned entity ID too technical and the entity lacking a friendly name. You can personalize these elements to better fit your naming conventions or modify other attributes like the icon.

To change entity attributes, follow these steps:

1. Go to **Settings** > **Devices & services** > **Entities** and select the entity from the list.
2. In the top-right corner, select the {% icon "mdi:cog" %} cog icon.
3. Enter or edit the attributes:

   - For example, the entity ID here could be shortened to `binary_sensor.lumi_sensor_aq2_opening`.

     - You can use lowercase letters, numbers, and underscores.
     - The ID must not start or end with an underscore.
     - To undo the change and revert the ID to the default, select the {% icon "mdi:restore" %} icon.
       - **Note**: You can only reset the ID to the default ID for entities with a unique ID.
         - IDs of entities that are disabled or for which the integration is not set up cannot be reverted.
     - To revert all the entity IDs for a device, on the device page, select the three dots {% icon "mdi:dots-vertical" %} menu, then select **Recreate entity IDs**.
     - **Result**: This resets the entity ID and applies the current default naming convention.

       - The terms used to generate the entity ID depends on a few factors. Prioritization is as follows:
         1. If you changed the friendly name of the entity, the friendly name will be used.
         2. The entity ID suggested by the integration (just a few integrations do this).
         3. The default name in the user language, if using Latin script.
            - If the something other than Latin script is used, the entity ID is based on the English default name.
            - This is because entity IDs must use lowercase alphanumeric characters in the range of [a-z,1-9].

   - Enter or edit the friendly name.
     - In this example, this would change "Opening".
   - If needed, from the **Shown as** menu, you can select a different [device class].
   - If you like, add a [label].

4. To apply the changes, select **Update**.
5. If you have used this entity in automations and scripts, you need to rename the entity ID there, too.
   - Go to {% my automations title="**Settings** > **Automations & Scenes**" %} open the respective tab and find your automation or script.

### Customizing an entity in YAML

If your entity is not supported, or you could not customize what you need via the user interface, you need to edit the settings in your {% term "`configuration.yaml`" %} file. For a detailed description of the entity configuration variables and [device class] information, refer to the [Home Assistant Core integration documentation].
