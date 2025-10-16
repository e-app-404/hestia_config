import json
import os
import re
import sqlite3
import time

import yaml
from appdaemon.plugins.hass import hassapi

ROOM_ID_RE = re.compile(r"^[a-z0-9_]+$")

class RoomDbUpdater(hassapi.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        self.schema_expected = int(self.args.get("schema_expected", 1))
        self.canonical_mapping_file = self.args.get("canonical_mapping_file")
        self.allowed_domains = set(self.args.get("allowed_domains", ["motion_lighting","vacuum_control","shared"]))
        self.max_config_size_bytes = int(self.args.get("max_config_size_bytes", 4096))
        self.write_rate_limit_seconds = int(self.args.get("write_rate_limit_seconds", 2))

        self._last_write = {}  # key: (domain), value: last_ts
        self._canonical_rooms = None  # Cache for canonical rooms
        
        # Validate configuration and initialize database
        self._validate_config()
        self._init_database()
        
        # Register endpoints - use simple names, AppDaemon builds full path
        self.log("Registering health endpoint")
        self.register_endpoint(self.health_check, "health")
        self.log(f"Registered: /api/app/room_db_updater/health")
        
        self.log("Registering update_config endpoint")
        self.register_endpoint(self.update_config, "update_config")
        self.log(f"Registered: /api/app/room_db_updater/update_config")
        self.log("RoomDbUpdater initialized")

    def _init_database(self):
        """Initialize database schema if not exists"""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            # Create schema_version table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
            """)
            # Create room_configs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS room_configs (
                    room_id TEXT,
                    config_domain TEXT,
                    config_data TEXT,
                    updated_at TIMESTAMP,
                    PRIMARY KEY (room_id, config_domain)
                )
            """)
            # Insert schema version if not exists
            cur.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (?)", 
                       (self.schema_expected,))
            conn.commit()
            self.log(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.error(f"Database initialization failed: {e}")
            raise
        finally:
            conn.close()

    def _validate_config(self):
        """Validate configuration on startup"""
        if not self.canonical_mapping_file or not os.path.exists(self.canonical_mapping_file):
            raise FileNotFoundError(f"Canonical mapping file not found: {self.canonical_mapping_file}")
        
        if not self.allowed_domains:
            raise ValueError("No allowed domains configured")
            
        self.log(f"Config validation passed - domains: {self.allowed_domains}")

    def _load_canonical_mapping(self):
        """Load and cache the canonical mapping"""
        if self._canonical_rooms is None:
            with open(self.canonical_mapping_file) as f:
                amap = yaml.safe_load(f) or {}
            # Extract room IDs from nodes
            nodes = amap.get("nodes", [])
            self._canonical_rooms = {node["id"] for node in nodes if node.get("type") in ["area", "subarea"]}
            self.log(f"Loaded {len(self._canonical_rooms)} canonical rooms")
        return self._canonical_rooms

    def _validate_room(self, room_id: str):
        if not ROOM_ID_RE.match(room_id or ""):
            raise ValueError("Invalid room_id slug")
        
        canonical_rooms = self._load_canonical_mapping()
        if room_id not in canonical_rooms:
            raise ValueError(f"room_id '{room_id}' not in canonical mapping. Available rooms: {sorted(canonical_rooms)}")

    def _schema_ok(self, cur):
        cur.execute("SELECT version FROM schema_version")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("SCHEMA_VERSION_TABLE_MISSING")
        v = int(row[0])
        if v != self.schema_expected:
            raise RuntimeError("SCHEMA_VERSION_MISMATCH")

    def _rate_limit(self, domain: str):
        now = time.monotonic()
        last = self._last_write.get(domain, 0.0)
        if now - last < self.write_rate_limit_seconds:
            raise RuntimeError("WRITE_RATE_LIMIT")
        self._last_write[domain] = now

    def health_check(self, data):
        """Health check endpoint"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            self._schema_ok(cur)
            conn.close()
            canonical_rooms = self._load_canonical_mapping()
            return {
                "status": "healthy", 
                "db_path": self.db_path,
                "canonical_rooms_count": len(canonical_rooms),
                "allowed_domains": list(self.allowed_domains)
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def update_config(self, data):
        """Enhanced update_config with better error handling"""
        try:
            # Validate input data structure
            required_fields = ["room_id", "domain", "config_data"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")
                
            room_id = data.get("room_id")
            domain = data.get("domain")
            cfg = data.get("config_data")
            
            if domain not in self.allowed_domains:
                raise ValueError(f"Domain '{domain}' not allowed. Allowed domains: {list(self.allowed_domains)}")
                
            self._validate_room(room_id)
            
            cfg_json = json.dumps(cfg, separators=(",", ":"))
            if len(cfg_json.encode("utf-8")) > self.max_config_size_bytes:
                raise ValueError(f"Config too large: {len(cfg_json.encode('utf-8'))} bytes > {self.max_config_size_bytes}")
                
            self._rate_limit(domain)

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            try:
                self._schema_ok(cur)
                conn.execute("BEGIN IMMEDIATE")
                cur.execute(
                    "INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at) VALUES (?,?,?, datetime('now'))",
                    (room_id, domain, cfg_json)
                )
                conn.commit()
                self.log(f"Successfully updated config for room '{room_id}', domain '{domain}'")
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            return {"status": "ok", "room_id": room_id, "domain": domain}
            
        except (ValueError, FileNotFoundError) as e:
            self.log(f"Validation error: {e}", level="WARNING")
            return {"status": "error", "error": str(e)}
        except sqlite3.Error as e:
            self.error(f"Database error: {e}")
            self.call_service("persistent_notification/create", 
                             title="Room DB Database Error", 
                             message=f"Database operation failed: {str(e)}")
            return {"status": "error", "error": "Database operation failed"}
        except Exception as e:
            self.error(f"Unexpected error in update_config: {e}")
            self.call_service("persistent_notification/create", 
                             title="Room DB Update Failed", 
                             message=f"Unexpected error: {str(e)}")
            return {"status": "error", "error": "Internal server error"}
