"""
Activity Tracker for Room-DB v3.1
Monitors occupancy/motion sensors and writes last_activity timestamps to Room-DB
Features: Defensive parsing, backoff+jitter, dedupe, enabled toggle
"""

import json
import random
import time
from datetime import datetime

import requests
import appdaemon.plugins.hass.hassapi as hass


class ActivityTracker(hass.Hass):
    def initialize(self):
        # Config
        self.update_url = self.args.get(
            "update_url", "http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_update_config"
        )
        self.rate_limit_seconds = int(self.args.get("rate_limit_seconds", 2))
        self.enabled = self.args.get("enabled", True)

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

        # Track last write per room (rate limiting and dedupe)
        self._last_write = {}
        self._last_key = None
        self._last_ts = 0

        # Listen to all sensors
        for room, sensor in self.room_sensors.items():
            self.listen_state(
                self.on_activity_detected,
                sensor,
                new="on",
                room_id=room,
                sensor=sensor
            )

        self.log(f"roomdb/activity_tracker/init level=INFO enabled={self.enabled} rooms={len(self.room_sensors)}")

    def on_activity_detected(self, entity, attribute, old, new, kwargs):
        """Handle sensor triggering"""
        room_id = kwargs["room_id"]
        sensor = kwargs["sensor"]

        if not self.enabled:
            self.log(f"roomdb/activity_tracker/sensor level=DEBUG event=skip_disabled room_id={room_id}")
            return

        # Get current trigger count
        current_count = self._get_current_count(room_id)

        # Prepare config data
        config_data = {
            "last_activity": datetime.now().isoformat(),
            "activity_source": sensor,
            "trigger_count": current_count + 1,
        }

        # Write to Room-DB with defensive handling
        success = self._post_update("activity_tracking", room_id, config_data)
        
        if success:
            self.log(f"roomdb/activity_tracker/write level=INFO event=activity_logged room_id={room_id} sensor={sensor} count={current_count + 1}")
        else:
            self.log(f"roomdb/activity_tracker/write level=WARNING event=write_failed room_id={room_id}")

    def _post_update(self, domain, room_id, cfg):
        """Post update with defensive parsing, backoff, and dedupe"""
        key = (domain, room_id, json.dumps(cfg, sort_keys=True))
        if key == self._last_key and time.time() - self._last_ts < 5:
            self.log(f"roomdb/activity_tracker/dedupe level=DEBUG room_id={room_id}")
            return True

        payload = {"domain": domain, "room_id": room_id, "config_data": cfg}
        delay = 2
        
        for attempt in range(5):
            try:
                r = requests.post(self.update_url, json=payload, timeout=5)
                content_type = r.headers.get("Content-Type", "")
                
                # Defensive parsing - handle HTML/non-JSON responses
                if "application/json" in content_type:
                    try:
                        data = r.json()
                    except json.JSONDecodeError:
                        data = {"status": "error", "code": r.status_code, "body": r.text[:200]}
                else:
                    data = {"status": "error", "code": r.status_code, "body": r.text[:200]}
                
            except Exception as e:
                data = {"status": "error", "error": str(e)}
                r = None

            # Check response
            if data.get("status") == "ok":
                self._last_key, self._last_ts = key, time.time()
                return True
            
            # Retry on rate limit or server error
            if r and r.status_code in (429, 500, 502, 503):
                jitter = random.uniform(0, 2)
                sleep_time = delay + jitter
                self.log(f"roomdb/activity_tracker/retry level=INFO room_id={room_id} attempt={attempt + 1} delay={sleep_time:.1f}s")
                time.sleep(sleep_time)
                delay = min(60, delay * 2)
                continue
            
            # Permanent failure
            self.log(f"roomdb/activity_tracker/error level=WARNING room_id={room_id} response={data}")
            return False
        
        self.log(f"roomdb/activity_tracker/error level=ERROR room_id={room_id} event=max_retries_exceeded")
        return False

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
            self.log(f"roomdb/activity_tracker/count level=WARNING room_id={room} error={str(e)}")

        return 0