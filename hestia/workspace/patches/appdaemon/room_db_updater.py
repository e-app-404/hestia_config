import json
import os
import re
import sqlite3
import time
import random

import yaml

try:
    from appdaemon.plugins.hass import hassapi
except Exception:
    class _DummyHass:
        def log(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

        def register_endpoint(self, *args, **kwargs):
            pass

        def call_service(self, *args, **kwargs):
            pass

        @property
        def name(self):
            return "RoomDbUpdater"

    class hassapi:  # type: ignore
        Hass = _DummyHass

ROOM_ID_RE = re.compile(r"^[a-z0-9_]+$")


class RoomDbUpdater(hassapi.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        self.schema_expected = int(self.args.get("schema_expected", 1))
        self.canonical_mapping_file = self.args.get("canonical_mapping_file")
        self.allowed_domains = set(
            self.args.get("allowed_domains", ["motion_lighting", "vacuum_control", "shared"])
        )
        self.max_config_size_bytes = int(self.args.get("max_config_size_bytes", 4096))
        self.write_rate_limit_seconds = int(self.args.get("write_rate_limit_seconds", 2))

        self._last_write = {}
    self._canonical_rooms = None
    self._allowed_matrix = None  # {room_id: set(domains)} built from mapping capabilities
    self._next_write_ts = {}  # per-domain limiter with jitter
        self._mapping_path = None
        self._init_error = None

        self.log("Registering health endpoint")
        self.register_endpoint(self.health_check, "health")
        self.log("Health endpoint registered with name: health")

    self.log("Registering update_config endpoint")
    self.register_endpoint(self.update_config, "update_config")
        self.log("Update_config endpoint registered with name: update_config")

        try:
            self.register_endpoint(self.health_check, "room_db/health")
            self.register_endpoint(self.update_config, "room_db/update_config")
            self.log("Compat endpoints registered under room_db/*")
        except Exception as e:
            self.log(f"Compat endpoint registration failed: {e}", level="WARNING")

        self.register_endpoint(self.test_endpoint, "test")
        self.log(f"Test endpoint registered: /api/app/{self.name}/test")

        try:
            self.register_endpoint(self.health_check, "room_db_health")
            self.register_endpoint(self.update_config, "room_db_update_config")
            self.register_endpoint(self.test_endpoint, "room_db_test")
            # New endpoints
            self.register_endpoint(self.bulk_update_ep, "room_db_bulk_update", methods=["POST"]) 
            self.register_endpoint(self.reload_mapping_ep, "room_db_reload_mapping", methods=["POST"]) 
            self.log(
                "Global endpoints registered: "
                "room_db_health, room_db_update_config, room_db_test, room_db_bulk_update, room_db_reload_mapping"
            )
        except Exception as e:
            self.log(f"Global endpoint registration failed: {e}", level="WARNING")

        try:
            self.register_endpoint(self.index_endpoint, "index")
            self.log(f"Index endpoint registered: /api/app/{self.name}/index")
        except Exception as e:
            self.log(f"Index endpoint registration failed: {e}", level="WARNING")

        self.log(f"App name for URL construction: {self.name}")
        self.log(f"Expected health URL: /api/app/{self.name}/health")
        self.log(f"Expected update_config URL: /api/app/{self.name}/update_config")

        try:
            self._validate_config()
            self._init_database()
            # Build allowed matrix from mapping
            try:
                self._load_allowed_matrix()
            except Exception as me:
                self.log(f"Failed to build allowed matrix from mapping: {me}", level="WARNING")
            self.log("RoomDbUpdater initialized")
        except Exception as e:
            self._init_error = str(e)
            self.error(f"Initialization encountered an issue: {e}")

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS room_configs (
                    room_id TEXT,
                    config_domain TEXT,
                    config_data TEXT,
                    updated_at TIMESTAMP,
                    PRIMARY KEY (room_id, config_domain)
                )
            """
            )
            cur.execute(
                "INSERT OR IGNORE INTO schema_version (version) VALUES (?)", (self.schema_expected,)
            )
            conn.commit()
            self.log(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.error(f"Database initialization failed: {e}")
            raise
        finally:
            conn.close()

    def _validate_config(self):
        self._mapping_path = self._resolve_mapping_path()
        if not self._mapping_path:
            raise FileNotFoundError(
                f"Canonical mapping file not found. Tried: {self._mapping_candidates()}"
            )

        if not self.allowed_domains:
            raise ValueError("No allowed domains configured")

        self.log(
            f"Config validation passed - mapping: {self._mapping_path} - "
            f"domains: {self.allowed_domains}"
        )

    def _mapping_candidates(self):
        candidates = [
            self.canonical_mapping_file,
            "/config/www/area_mapping.yaml",
            "/config/domain/architecture/area_mapping.yaml",
        ]
        seen = set()
        ordered = []
        for c in candidates:
            if c and c not in seen:
                ordered.append(c)
                seen.add(c)
        return ordered

    def _resolve_mapping_path(self):
        for path in self._mapping_candidates():
            try:
                if path and os.path.exists(path):
                    return path
            except Exception:
                continue
        return None

    def _load_canonical_mapping(self):
        if self._canonical_rooms is None:
            if not self._mapping_path:
                self._mapping_path = self._resolve_mapping_path()
            if not self._mapping_path or not os.path.exists(self._mapping_path):
                raise FileNotFoundError(
                    f"Canonical mapping file not found. Tried: {self._mapping_candidates()}"
                )
            with open(self._mapping_path) as f:
                amap = yaml.safe_load(f) or {}
            nodes = amap.get("nodes", [])
            self._canonical_rooms = {
                node["id"] for node in nodes if node.get("type") in ["area", "subarea"]
            }
            self.log(
                f"Loaded {len(self._canonical_rooms)} canonical rooms from {self._mapping_path}"
            )
        return self._canonical_rooms

    def _load_allowed_matrix(self):
        """Build {room_id: set(domains)} from mapping capabilities.
        Requires v3.1 mapping with nodes[*].capabilities.{motion_lighting|vacuum_control|shared}.
        Vacuum writes are allowed only if a segment_id is present in capabilities.
        """
        if not self._mapping_path:
            self._mapping_path = self._resolve_mapping_path()
        if not self._mapping_path or not os.path.exists(self._mapping_path):
            raise FileNotFoundError(
                f"Canonical mapping file not found. Tried: {self._mapping_candidates()}"
            )
        with open(self._mapping_path, encoding="utf-8") as f:
            amap = yaml.safe_load(f) or {}
        nodes = amap.get("nodes", [])
        allowed = {}
        for node in nodes:
            rid = (node or {}).get("id")
            if not rid:
                continue
            caps = ((node or {}).get("capabilities") or {})
            doms = set()
            # Motion lighting capability
            if caps.get("motion_lighting") is not None:
                doms.add("motion_lighting")
            # Vacuum control requires segment_id
            vc = caps.get("vacuum_control") or {}
            if isinstance(vc, dict) and vc.get("segment_id") is not None:
                doms.add("vacuum_control")
            # Shared domain always allowed for all rooms when present
            if caps.get("shared") is not None:
                doms.add("shared")
            if doms:
                allowed[rid] = doms
        self._allowed_matrix = allowed
        # Also make sure canonical rooms loaded
        self._canonical_rooms = None
        self._load_canonical_mapping()
        return {"rooms": len(self._allowed_matrix)}

    def _is_allowed(self, domain: str, room_id: str) -> bool:
        try:
            if not self._allowed_matrix:
                self._load_allowed_matrix()
            return domain in (self._allowed_matrix or {}).get(room_id, set())
        except Exception:
            return False

    def _validate_room(self, room_id: str):
        if not ROOM_ID_RE.match(room_id or ""):
            raise ValueError("Invalid room_id slug")

        canonical_rooms = self._load_canonical_mapping()
        if room_id not in canonical_rooms:
            raise ValueError(
                f"room_id '{room_id}' not in canonical mapping. "
                f"Available rooms: {sorted(canonical_rooms)}"
            )

    def _schema_ok(self, cur):
        cur.execute("SELECT version FROM schema_version")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("SCHEMA_VERSION_TABLE_MISSING")
        v = int(row[0])
        if v != self.schema_expected:
            raise RuntimeError("SCHEMA_VERSION_MISMATCH")

    def _respect_write_limiter(self, domain: str):
        limit = int(self.write_rate_limit_seconds)
        jitter = random.uniform(-1.0, 1.0)
        now = time.monotonic()
        next_ts = self._next_write_ts.get(domain, 0.0)
        if now < next_ts:
            raise RuntimeError("WRITE_RATE_LIMIT")
        # set next write time with jitter but never less than 1s in the future
        self._next_write_ts[domain] = now + max(1.0, limit + jitter)

    def index_endpoint(self, data=None, **kwargs):
        return {
            "app_name": self.name,
            "endpoints": [
                f"/api/app/{self.name}/health",
                f"/api/app/{self.name}/test",
                f"/api/app/{self.name}/update_config",
                f"/api/app/{self.name}/room_db/health",
                f"/api/app/{self.name}/room_db/update_config",
                "/api/appdaemon/room_db_health",
                "/api/appdaemon/room_db_test",
                "/api/appdaemon/room_db_update_config",
                "/api/appdaemon/room_db_bulk_update",
                "/api/appdaemon/room_db_reload_mapping",
            ],
        }, 200

    def test_endpoint(self, data=None, **kwargs):
        return {
            "status": "test_success",
            "message": "Test endpoint is working",
            "app_name": self.name,
        }, 200

    def health_check(self, data=None, **kwargs):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            self._schema_ok(cur)
            conn.close()
            canonical_rooms = []
            try:
                canonical_rooms = list(self._load_canonical_mapping())
            except Exception as me:
                return {
                    "status": "degraded",
                    "message": f"Mapping issue: {str(me)}",
                    "db_path": self.db_path,
                    "allowed_domains": list(self.allowed_domains),
                    "app_init_error": self._init_error,
                }, 200
            return {
                "status": "healthy",
                "db_path": self.db_path,
                "canonical_rooms_count": len(canonical_rooms),
                "allowed_domains": list(self.allowed_domains),
                "app_init_error": self._init_error,
            }, 200
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "app_init_error": self._init_error}, 200

    def update_config(self, data=None, **kwargs):
        try:
            data = data or {}
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                self._schema_ok(cur)
                conn.close()
            except Exception:
                self._init_database()

            required_fields = ["room_id", "domain", "config_data"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")

            room_id = data.get("room_id")
            domain = data.get("domain")
            cfg = data.get("config_data")

            if domain is None:
                raise ValueError("domain is required and cannot be None")

            if domain not in self.allowed_domains:
                raise ValueError(
                    f"Domain '{domain}' not allowed. Allowed domains: {list(self.allowed_domains)}"
                )

            if room_id is None:
                raise ValueError("room_id is required and cannot be None")

            self._validate_room(room_id)

            # Mapping-based admission control (capability check)
            if not self._is_allowed(domain, room_id):
                return {"status": "error", "error": f"{domain}:{room_id} not allowed by mapping"}, 422

            cfg_json = json.dumps(cfg, separators=(",", ":"))
            if len(cfg_json.encode("utf-8")) > self.max_config_size_bytes:
                raise ValueError(
                    f"Config too large: {len(cfg_json.encode('utf-8'))} bytes > "
                    f"{self.max_config_size_bytes}"
                )

            self._respect_write_limiter(domain)

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            try:
                self._schema_ok(cur)
                conn.execute("BEGIN IMMEDIATE")
                cur.execute(
                    "INSERT OR REPLACE INTO room_configs "
                    "(room_id, config_domain, config_data, updated_at) "
                    "VALUES (?,?,?, datetime('now'))",
                    (room_id, domain, cfg_json),
                )
                conn.commit()
                self.log(f"Successfully updated config for room '{room_id}', domain '{domain}'")
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            # exporter hook (debounced)
            self._export_async()
            return {"status": "ok", "room_id": room_id, "domain": domain}, 200

        except (ValueError, FileNotFoundError) as e:
            self.log(f"Validation error: {e}", level="WARNING")
            return {"status": "error", "error": str(e)}, 400
        except sqlite3.Error as e:
            self.error(f"Database error: {e}")
            room_id = (data or {}).get("room_id")
            domain = (data or {}).get("domain")
            notif_id = None
            if room_id and domain:
                notif_id = f"roomdb_err__{domain}__{room_id}"
            kwargs = {
                "title": "Room DB Database Error",
                "message": f"Database operation failed: {str(e)}",
            }
            if notif_id:
                kwargs["notification_id"] = notif_id
            self.call_service("persistent_notification/create", **kwargs)
            return {"status": "error", "error": "Database operation failed"}, 500
        except Exception as e:
            self.error(f"Unexpected error in update_config: {e}")
            room_id = (data or {}).get("room_id")
            domain = (data or {}).get("domain")
            since_last = None
            try:
                last_ts = float(self._last_write.get(domain, 0.0))
                now = float(time.monotonic())
                since_last = max(0.0, now - last_ts)
            except Exception:
                since_last = None
            rate = self.write_rate_limit_seconds
            parts = [str(e)]
            if str(e) == "WRITE_RATE_LIMIT":
                if isinstance(since_last, float):
                    since = f"since_last={since_last:.1f}s)"
                else:
                    since = "since_last=unknown)"
                parts = [
                    "WRITE_RATE_LIMIT",
                    f"(room={room_id}, domain={domain}, rate={rate}s",
                    since,
                ]
            msg = " ".join(parts)
            notif_id = None
            try:
                if room_id and domain:
                    notif_id = f"roomdb_err__{domain}__{room_id}"
            except Exception:
                notif_id = None
            kwargs = {"title": "Room DB Update Failed", "message": f"Unexpected error: {msg}"}
            if notif_id:
                kwargs["notification_id"] = notif_id
            self.call_service("persistent_notification/create", **kwargs)
            return {"status": "error", "error": "Internal server error"}, 500

    # -------- New endpoints --------
    def bulk_update_ep(self, request, data):
        """POST endpoint to process array of updates with per-item backoff.
        Accepts either a list of items or an object with 'items' key.
        """
        try:
            items = data if isinstance(data, list) else (data or {}).get("items", [])
            if not items:
                return ({"status": "error", "error": "no items"}, 400)
            results = []
            for it in items:
                payload = {
                    "room_id": it.get("room_id"),
                    "domain": it.get("domain"),
                    "config_data": it.get("config_data", {}),
                }
                res, code = self.update_config(payload)
                # On rate limit, backoff a bit and retry once
                if code == 500 and res.get("error") == "Internal server error":
                    time.sleep(0.5 + random.uniform(0, 0.5))
                    res, code = self.update_config(payload)
                results.append({"code": code, "result": res})
            # exporter hook once after batch
            self._export_async()
            return ({"status": "ok", "results": results}, 200)
        except Exception as e:
            self.error(f"bulk_update_ep failed: {e}")
            return ({"status": "error", "error": str(e)}, 500)

    def reload_mapping_ep(self, request, data):
        try:
            stats = self._load_allowed_matrix()
            return ({"status": "ok", "mapping": stats}, 200)
        except Exception as e:
            return ({"status": "error", "error": str(e)}, 500)

    def _export_async(self):
        """If exporter app is present, schedule a write_once soon (debounced)."""
        try:
            # Slight delay to coalesce bursts
            self.run_in(
                lambda *_: self.call_service(
                    "appdaemon/call", app="room_db_exporter", function="write_once"
                ),
                0.5,
            )
        except Exception:
            # exporter not available is non-fatal
            pass
