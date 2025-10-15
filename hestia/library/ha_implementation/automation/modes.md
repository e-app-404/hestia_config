---
title: "Automation modes"
authors: "Hestia / Home Assistant docs"
source: "Local Hestia copy"
slug: "automation-modes"
tags: ["home-assistant", "automation"]
original_date: "2025-10-15"
last_updated: "2025-10-15"
url: ""

---

# Automation modes

An {% term automation %} can be triggered while it is already running.

The automation's `mode` configuration option controls what happens when the automation is triggered while the {% term actions %} are still running from a previous {% term trigger %}.

| Mode       | Description                                                                                                                                                                                                                                         |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `single`   | (Default) Do not start a new run. Issue a warning.                                                                                                                                                                                                  |
| `restart`  | Start a new run after first stopping the previous run. The automation only restarts if the conditions are met.                                                                                                                                      |
| `queued`   | Start a new run after all previous runs complete. Runs are guaranteed to execute in the order they were queued. Note that subsequent queued automations will only join the queue if any conditions it may have are met at the time it is triggered. |
| `parallel` | Start a new, independent run in parallel with previous runs.                                                                                                                                                                                        |

![Automation modes](/images/integrations/script/script_modes.jpg)

For both `queued` and `parallel` modes, configuration option `max` controls the maximum number of runs that can be executing and/or queued up at a time. The default is 10.

When `max` is exceeded (which is effectively 1 for `single` mode) a log message will be emitted to indicate this has happened. Configuration option `max_exceeded` controls the severity level of that log message. Set it to `silent` to ignore warnings or set it to a [log level](/integrations/logger/#log-levels). The default is `warning`.

## Example throttled automation

Some automations you only want to run every 5 minutes. This can be achieved using the `single` mode and silencing the warnings when the automation is triggered while it's running.

```yaml
- mode: single
  max_exceeded: silent
  triggers:
    - ...
  actions:
    - ...
    - delay: 300 # seconds (=5 minutes)
```

## Example queued

Sometimes an automation is doing an action on a device that does not support multiple simultaneous actions. In such cases, a queue can be used. In that case, the automation will be executed once it's current invocation and queue are done.

```yaml
- mode: queued
  max: 25
  triggers:
    - ...
  actions:
    - ...
```
