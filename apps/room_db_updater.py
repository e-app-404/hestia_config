from appdaemon.plugins.hass import Hass
import json
import os
import re
import sqlite3
import time
import yaml

ROOM_ID_RE = re.compile(r"^[a-z0-9_]+$")

class RoomDbUpdater(hass.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        self.schema_expected = int(self.args.get("schema_expected", 1))
        self.canonical_mapping_file = self.args.get("canonical_mapping_file")
        self.allowed_domains = set(self.args.get("allowed_domains", ["motion_lighting","vacuum_control","shared"]))
        self.max_config_size_bytes = int(self.args.get("max_config_size_bytes", 4096))
        self.write_rate_limit_seconds = int(self.args.get("write_rate_limit_seconds", 2))

        self._last_write = {}  # key: (domain), value: last_ts
        self.register_endpoint(self.update_config, "room_db/update_config")
        self.log("RoomDbUpdater initialized")

    def _validate_room(self, room_id: str):
        if not ROOM_ID_RE.match(room_id or ""):
            raise ValueError("Invalid room_id slug")
        if not self.canonical_mapping_file or not os.path.exists(self.canonical_mapping_file):
            raise FileNotFoundError("Canonical mapping file not found")
        with open(self.canonical_mapping_file, "r") as f:
            amap = yaml.safe_load(f) or {}
        rooms = (amap.get("rooms") or {}) if isinstance(amap, dict) else {}
        if room_id not in rooms:
            raise ValueError("room_id not in canonical mapping")

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

    def update_config(self, data):
        try:
            room_id = data.get("room_id")
            domain = data.get("domain")
            cfg = data.get("config_data")
            if domain not in self.allowed_domains:
                raise ValueError("DOMAIN_NOT_ALLOWED")
            self._validate_room(room_id)
            cfg_json = json.dumps(cfg, separators=(",", ":"))
            if len(cfg_json.encode("utf-8")) > self.max_config_size_bytes:
                raise ValueError("CONFIG_TOO_LARGE")
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
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            return {"status": "ok"}
        except Exception as e:
            self.error(str(e))
            self.call_service("persistent_notification/create", title="Room DB Update Failed", message=str(e))
            return {"status": "error", "error": str(e)}
