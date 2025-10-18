"""
Activity Tracker for Room-DB
Monitors occupancy/motion sensors and writes last_activity timestamps to Room-DB
"""

from datetime import datetime
import time
import json
import random

import appdaemon.plugins.hass.hassapi as hass


class ActivityTracker(hass.Hass):
    def initialize(self):
        # Config
        self.enabled = bool(self.args.get("enabled", True))
        self.update_service = self.args.get(
            "room_db_update_service", "rest_command/room_db_update_config"
        )
        self.rate_limit_seconds = int(self.args.get("rate_limit_seconds", 2))
        self._dedupe_ttl = int(self.args.get("dedupe_ttl_seconds", 5))
        
        # Room → Sensor mapping (occupancy preferred, motion fallback)
        # IMPORTANT: room_id (key) must match canonical mapping in area_mapping.yaml
        self.room_sensors = {
            "bedroom": "binary_sensor.bedroom_occupancy_beta",
            "kitchen": "binary_sensor.kitchen_occupancy_beta",
            "living_room": "binary_sensor.living_room_occupancy_beta",
            "ensuite": "binary_sensor.ensuite_occupancy_beta",
            "downstairs": "binary_sensor.hallway_downstairs_occupancy_beta",
            "upstairs": "binary_sensor.hallway_upstairs_occupancy_beta",
            "desk": "binary_sensor.desk_occupancy_beta",
            "entrance": "binary_sensor.entrance_motion_beta",
        }
        
    # Track last write per room (rate limiting)
    self._last_write = {}
    # Track last event per room:sensor for dedupe
    self._last_event = {}
        
        # Listen to all sensors
        for room, sensor in self.room_sensors.items():
            self.listen_state(
                self.on_activity_detected,
                sensor,
                new="on",
                room_id=room,
                sensor=sensor
            )
        
        self.log(
            f"ActivityTracker initialized - monitoring {len(self.room_sensors)} rooms; enabled={self.enabled}"
        )
    
    def on_activity_detected(self, entity, attribute, old, new, kwargs):
        """Handle sensor triggering"""
        if not self.enabled:
            return
        room = kwargs["room_id"]
        sensor = kwargs["sensor"]
        
        # Dedupe identical sensor spikes within a short TTL
        now = time.time()
        ekey = f"{room}:{sensor}"
        last_evt = self._last_event.get(ekey, 0)
        if now - last_evt < self._dedupe_ttl:
            return
        self._last_event[ekey] = now

        # Rate limiting check (per room)
        last = self._last_write.get(room, 0)
        
        if now - last < self.rate_limit_seconds:
            self.log(f"Rate limit: skipping write for {room} (last write {now - last:.1f}s ago)")
            return
        
        # Get current trigger count
        current_count = self._get_current_count(room)
        
        # Write to Room-DB
        payload = dict(
            room_id=room,
            domain="motion_lighting",
            config_data={
                "last_activity": datetime.now().isoformat(),
                "activity_source": sensor,
                "trigger_count": current_count + 1,
            },
            schema_expected=1,
        )
        if self._post_update(payload):
            self._last_write[room] = now
            self.log(
                f"Activity logged: {room} from {sensor} (count: {current_count + 1})"
            )
        else:
            self.error(f"Failed to write activity for {room}")
    
    def _get_current_count(self, room):
        """Read current trigger count from Room-DB sensor"""
        try:
            sensor_data = self.get_state(
                "sensor.room_configs_activity_tracking_dict",
                attribute="payload"
            )
            
            if sensor_data and isinstance(sensor_data, dict) and room in sensor_data:
                return sensor_data[room].get("trigger_count", 0)
        except Exception as e:
            self.log(f"Could not read trigger count for {room}: {e}", level="WARNING")
        
        return 0

    def _post_update(self, payload: dict) -> bool:
        """Post update via HA rest_command or AppDaemon endpoint with backoff+jitter.
        Returns True on success, False on failure.
        """
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                # Primary: HA rest_command
                self.call_service(self.update_service, **payload)
                return True
            except Exception as e:
                # Backoff with small jitter
                jitter = random.uniform(0.2, 0.8)
                delay = min(2.0, 0.3 * attempt) + jitter
                self.log(
                    f"post_update attempt {attempt} failed: {e}. retrying in {delay:.2f}s",
                    level="WARNING",
                )
                time.sleep(delay)
        return False