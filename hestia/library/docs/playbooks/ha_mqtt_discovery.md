# Home Assistant MQTT Discovery — Practical Playbook

## What you’ll achieve

Expose a single **Device** in Home Assistant that contains multiple entities (e.g., 10 MQTT **button** entities), created entirely by publishing discovery JSON to your MQTT broker—no YAML files required. You’ll also wire those button presses to actions (e.g., IR via `remote.send_command`). ([Home Assistant][1])

---

## 1) Prereqs (5 quick checks)

* **MQTT integration installed** and connected to your broker. In HA: *Settings → Devices & services → MQTT*. ([Home Assistant][1])
* **Discovery enabled** and **prefix** (default `homeassistant`) confirmed in MQTT options. ([Home Assistant][1])
* You can **Publish**/**Listen** from the integration UI (*MQTT → Configure → Publish a packet / Listen to a topic*). ([Home Assistant][1])
* Broker (e.g., **Mosquitto add-on**) running; HA docs recommend the official add-on. ([Home Assistant][1])
* (If using Broadlink IR) you’ve **learned commands** and can send them with `remote.send_command`. ([Home Assistant][2])

---

## 2) Pick your discovery method

### A. **Device-based discovery** (modern, one payload)

Publish one retained JSON to:

`<discovery_prefix>/device/<object_id>/config`

This defines the device and *all* its components via a `cmps` map. Requires root `device` and `origin` blocks. Supported by current HA and preferred when a device exposes many entities. ([Home Assistant][1])

### B. **Per-component discovery** (fallback, many payloads)

Publish one payload per entity to:

`<discovery_prefix>/<component>/<object_id>/config`

Still fully supported; if your HA build is older or you prefer simple, use this. ([Home Assistant][1])

---

## 3) Minimal working examples

> Use the **MQTT → Configure → Publish a packet** UI or `mosquitto_pub`. Ensure **QoS 1** and **Retain ON** for discovery messages. ([Home Assistant][1])

### A. Device-based (1 device, 2 buttons demo)

**Topic**

`homeassistant/device/bedroom_hdmi_matrix/config`

**Payload**

```json
{
  "device": { "identifiers": ["bedroom_hdmi_matrix"], "name": "Bedroom HDMI Matrix" },
  "origin": { "name": "matrix-virtual", "sw_version": "1.1.0" },
  "cmps": {
    "power": {
      "p": "button",
      "unique_id": "bedroom_hdmi_matrix_power",
      "name": "Power",
      "command_topic": "ha/bedroom_hdmi_matrix/cmd",
      "payload_press": "power"
    },
    "arc": {
      "p": "button",
      "unique_id": "bedroom_hdmi_matrix_arc",
      "name": "ARC",
      "command_topic": "ha/bedroom_hdmi_matrix/cmd",
      "payload_press": "arc"
    }
  }
}
```

You should now see a **Bedroom HDMI Matrix** device with two MQTT **button** entities. The `p` field declares the platform; each entity needs a stable `unique_id`. ([Home Assistant][1])

> Add more entities by adding more keys under `cmps` (e.g., `a_1` … `b_4`). ([Home Assistant][1])

### B. Per-component (one payload per entity)

**Topic**

`homeassistant/button/bedroom_hdmi_matrix/power/config`

**Payload**

```json
{
  "unique_id": "bedroom_hdmi_matrix_power",
  "name": "Power",
  "command_topic": "ha/bedroom_hdmi_matrix/cmd",
  "device": { "identifiers": ["bedroom_hdmi_matrix"], "name": "Bedroom HDMI Matrix" }
}
```

HA groups the entity under the same device via `device.identifiers`. Repeat for each button (power, arc, a\_1…b\_4). ([Home Assistant][1])

---

## 4) Availability & startup behavior (recommended)

* Publish retained **online** to your availability topic (if you include `availability_topic` in entities):
  `ha/bedroom_hdmi_matrix/status = online` (retain). ([Home Assistant][3])
* HA **sends** its own birth/LWT on `homeassistant/status` (`online`/`offline`). Best practice: have your publisher **re-send discovery** when HA announces `online` (or use retained discovery). ([Home Assistant][1])

---

## 5) Wire button presses to actions (example: Broadlink IR)

**Automation (hardened, whitelist + queue):**

```yaml
automation:
  - alias: "Matrix: MQTT → Broadlink"
    id: matrix_mqtt_to_broadlink
    initial_state: true
    mode: queued
    max: 5
    trigger:
      - platform: mqtt
        topic: ha/bedroom_hdmi_matrix/cmd
        qos: 1
    variables:
      allowed: ["power","arc","a_1","a_2","a_3","a_4","b_1","b_2","b_3","b_4"]
    condition:
      - condition: template
        value_template: "{{ trigger.payload in allowed }}"
    action:
      - action: remote.send_command
        target:
          entity_id: remote.bedroom_broadlink_rm3_alpha
        data:
          device: bedroom_hdmi_matrix
          command: "{{ trigger.payload }}"
```

Broadlink: learn codes with `remote.learn_command`, send with `remote.send_command`. ([Home Assistant][2])

---

## 6) Test, observe, and clean up

* **Listen**: MQTT → Configure → *Listen to a topic* (`ha/bedroom_hdmi_matrix/#`), then press a button entity and watch the payload. ([Home Assistant][1])
* **CLI**: `mosquitto_sub -v -t 'homeassistant/#'` or `-t 'ha/bedroom_hdmi_matrix/#'`. ([Home Assistant][1])
* **Remove device** (device-based): publish **empty retained** payload to the device discovery topic — HA will delete the device/entities. ([Home Assistant][1])
* **Remove one component** (device-based): send an **empty** component config (must include `"p"`), then send an updated full config without that component. ([Home Assistant][1])

---

## 7) Security notes (broker-side)

* Use the **official Mosquitto add-on** or another supported broker; HA explicitly recommends Mosquitto. ([Home Assistant][1])
* Create **dedicated credentials** for publishers; the add-on integrates with HA users and supports additional logins and ACLs (topic scoping). ([Home Assistant][1])
* Prefer TLS if traffic can leave a trusted LAN. (General MQTT guidance; consult your broker docs.) ([Eclipse Mosquitto][4])

---

## 8) Common pitfalls

* **Wrong topic/prefix**: confirm discovery prefix in MQTT options; publish to that prefix. ([Home Assistant][1])
* **Not retained**: retained discovery ensures HA re-hydrates entities on restart; large fleets should republish on HA birth. ([Home Assistant][1])
* **Missing required fields**: device-based discovery needs root `device` and `origin`, and each component under `cmps` needs `p` (`platform`) and (for entity types) `unique_id`. ([Home Assistant][1])

---

## Appendix: Scaling up your matrix example

Add these to the `cmps` map (device-based) or publish separate button configs (per-component):

```
a_1 … a_4 → payload_press: "a_1" … "a_4"
b_1 … b_4 → payload_press: "b_1" … "b_4"
```

If you include availability, set `availability_topic` for each entity and publish retained `online` to that topic. ([Home Assistant][3])

---

## Official references (docs & repos)

* **MQTT integration** — discovery, prefix, birth/LWT, UI publish/listen, device-based discovery, `cmps`/`p`, removal semantics. ([Home Assistant][1])
* **MQTT Button** — `command_topic`, `payload_press`, availability, `unique_id` (required for device-based). ([Home Assistant][3])
* **Broadlink integration** — `remote.learn_command`, `remote.send_command`. ([Home Assistant][2])
* **Mosquitto config (reference man page)** — ACLs/TLS and general broker configuration. ([Eclipse Mosquitto][4])

---

### Acceptance checklist (binary)

* [ ] Device appears under *Devices & services* with expected entities.
* [ ] Pressing any button publishes the expected MQTT payload (observed in UI listener). ([Home Assistant][1])
* [ ] Automation triggers and performs the desired action (trace shows payload → service call).
* [ ] Discovery retained or rebroadcast on HA birth; restart HA and entities re-hydrate. ([Home Assistant][1])

---

If you want this tailored to your exact prefixes and entity names, say “generate my device-based JSON (10 buttons)”, and I’ll drop a ready-to-publish payload with your IDs baked in.

[1]: https://www.home-assistant.io/integrations/mqtt/ "MQTT - Home Assistant"
[2]: https://www.home-assistant.io/integrations/broadlink/?utm_source=chatgpt.com "Broadlink"
[3]: https://www.home-assistant.io/integrations/button.mqtt/ "MQTT button - Home Assistant"
[4]: https://mosquitto.org/man/mosquitto-conf-5.html?utm_source=chatgpt.com "mosquitto.conf man page"
