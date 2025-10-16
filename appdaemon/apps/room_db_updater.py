#!/usr/bin/env python3
"""
Room Database Updater - AppDaemon Integration
Provides REST endpoints for updating room configurations in SQLite database

Endpoints:
- POST /api/appdaemon/room_db_update_config
- GET /api/appdaemon/room_db_health

Compliance: ADR-0024 (canonical paths)
"""

import json
import sqlite3
import os
from datetime import datetime, UTC
import appdaemon.plugins.hass.hassapi as hass


class RoomDbUpdater(hass.Hass):
    def initialize(self):
        """Initialize the room database updater"""
        self.db_path = "/config/room_database.db"
        self._validate_config()
        self._init_database()
        
        # Register endpoints - NO leading slash for register_endpoint
        # AppDaemon will mount at /api/appdaemon/<name>
        self.register_endpoint(self.update_config, "room_db_update_config")
        self.register_endpoint(self.health_check, "room_db_health")
        self.log("RoomDbUpdater initialized")

    def _validate_config(self):
        """Validate configuration and database path"""
        if not os.path.exists("/config"):
            raise ValueError("Config directory not found")
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_database(self):
        """Initialize database schema if needed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS room_configs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_id TEXT NOT NULL,
                        config_domain TEXT NOT NULL,
                        config_data TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(room_id, config_domain)
                    )
                """)
                conn.commit()
                self.log("Database schema initialized")
        except Exception as e:
            self.log(f"Database initialization failed: {e}", level="ERROR")
            raise

    def update_config(self, data):
        """
        Update room configuration endpoint
        
        Expected POST data:
        {
            "room_id": "bedroom",
            "domain": "motion_lighting", 
            "config_data": {...}
        }
        """
        try:
            # Parse request data
            if isinstance(data, str):
                request_data = json.loads(data)
            else:
                request_data = data

            # Validate required fields
            required_fields = ["room_id", "domain", "config_data"]
            for field in required_fields:
                if field not in request_data:
                    return {"error": f"Missing required field: {field}"}, 400

            room_id = request_data["room_id"]
            domain = request_data["domain"]
            config_data = request_data["config_data"]

            # Serialize config_data to JSON if it's not already a string
            if isinstance(config_data, (dict, list)):
                config_json = json.dumps(config_data)
            else:
                config_json = str(config_data)

            # Update database
            timestamp = datetime.now(UTC).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO room_configs 
                    (room_id, config_domain, config_data, created_at, updated_at)
                    VALUES (?, ?, ?, 
                            COALESCE((SELECT created_at FROM room_configs 
                                    WHERE room_id=? AND config_domain=?), ?),
                            ?)
                """, (room_id, domain, config_json, room_id, domain, timestamp, timestamp))
                conn.commit()

            self.log(f"Updated config: {room_id}/{domain}")
            
            return {
                "status": "success",
                "room_id": room_id,
                "domain": domain,
                "timestamp": timestamp
            }, 200

        except json.JSONDecodeError as e:
            self.log(f"JSON decode error: {e}", level="ERROR")
            return {"error": f"Invalid JSON: {e}"}, 400
        except sqlite3.Error as e:
            self.log(f"Database error: {e}", level="ERROR")
            return {"error": f"Database error: {e}"}, 500
        except Exception as e:
            self.log(f"Unexpected error: {e}", level="ERROR")
            return {"error": f"Internal server error: {e}"}, 500

    def health_check(self, data):
        """Health check endpoint"""
        try:
            # Test database connection
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM room_configs")
                config_count = cursor.fetchone()[0]

            return {
                "status": "healthy",
                "database": "connected",
                "config_count": config_count,
                "timestamp": datetime.now(UTC).isoformat()
            }, 200

        except Exception as e:
            self.log(f"Health check failed: {e}", level="ERROR")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }, 500