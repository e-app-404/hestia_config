"""
Activity Tracker for Room-DB
Monitors occupancy/motion sensors and writes last_activity timestamps to Room-DB
"""

from datetime import datetime

import appdaemon.plugins.hass.hassapi as hass


class ActivityTracker(hass.Hass):
    def initialize(self):
        # Config
        self.update_service = self.args.get(
            "room_db_update_service", "rest_command/room_db_update_config"
        )
        self.rate_limit_seconds = int(self.args.get("rate_limit_seconds", 2))
        
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
        
        # Listen to all sensors
        for room, sensor in self.room_sensors.items():
            self.listen_state(
                self.on_activity_detected,
                sensor,
                new="on",
                room_id=room,
                sensor=sensor
            )
        
        self.log(f"ActivityTracker initialized - monitoring {len(self.room_sensors)} rooms")
    
    def on_activity_detected(self, entity, attribute, old, new, kwargs):
        """Handle sensor triggering"""
        room = kwargs["room_id"]
        sensor = kwargs["sensor"]
        
        # Rate limiting check
        import time
        now = time.time()
        last = self._last_write.get(room, 0)
        
        if now - last < self.rate_limit_seconds:
            self.log(f"Rate limit: skipping write for {room} (last write {now - last:.1f}s ago)")
            return
        
        # Get current trigger count
        current_count = self._get_current_count(room)
        
        # Write to Room-DB
        try:
            self.call_service(
                self.update_service,
                room_id=room,
                domain="activity_tracking",
                config_data={
                    "last_activity": datetime.now().isoformat(),
                    "activity_source": sensor,
                    "trigger_count": current_count + 1,
                },
                schema_expected=1
            )
            
            # Write succeeded
            self._last_write[room] = now
            self.log(f"Activity logged: {room} from {sensor} (count: {current_count + 1})")
            
        except Exception as e:
            self.error(f"Failed to write activity for {room}: {e}")
    
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