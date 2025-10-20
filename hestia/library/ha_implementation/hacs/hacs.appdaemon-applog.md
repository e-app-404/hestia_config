# App Log

Starting from AD 4.0, it is now possible to determine which log as declared by the user, will be used by Apps by default when using the self.log() within the App; this can be very useful for debugging purposes. This is done by simply adding the log: directive entry, to its parameters. e.g.:

```yaml
downstairs_motion_light:
  module: motion_light
  class: MotionLight
  sensor: binary_sensor.downstairs_hall
  light: light.downstairs_hall
  log: lights_log
```

By declaring the above, each time the function self.log() is used within the App, the log entry is sent to the user defined lights_log. It is also possible to write to another log, within the same App if need be. This is done using the function self.log(text, log='main_log'). Without using any of the aforementioned log capabilities, all logs from apps by default will be sent to the main_log.
