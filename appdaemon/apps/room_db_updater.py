import json
import os
import random
import re
import sqlite3
import time
from typing import Any
import contextlib

import appdaemon.plugins.hass.hassapi as hass
import yaml

SCHEMA_VERSION = 1
ROOM_ID_RE = re.compile(r"^[a-z0-9_]+$")

class RateLimited(Exception):
    pass

class RoomDbUpdater(hass.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        self.schema_expected = int(self.args.get("schema_expected", SCHEMA_VERSION))
        self.canonical_mapping_file = self.args.get(
            "canonical_mapping_file",
            "/config/www/area_mapping.yaml",
        )
        self.allowed_domains = set(
            self.args.get(
                "allowed_domains",
                [
                    "motion_lighting",
                    "vacuum_control",
                    "shared",
                    "activity_tracking",
                ],
            )
        )
        self.max_config_size_bytes = int(self.args.get("max_config_size_bytes", 4096))
        self.write_rate_limit_seconds = int(self.args.get("write_rate_limit_seconds", 5))
        self.dry_run = bool(self.args.get("dry_run", False))

    self._next_write_ts: dict[str, float] = {}
    self._allowed_matrix: dict[str, set[str]] = {}
    self._canonical_rooms: set[str] = set()
    self._mapping_path: str | None = None
        self._init_error = None

        try:
            self._ensure_db()
        except Exception as e:
            self._init_error = f"DB init failed: {e}"
            self.error(self._init_error)

        try:
            self._load_mapping()
        except Exception as e:
            self._init_error = f"Mapping load failed: {e}"
            self.error(self._init_error)

        # Register endpoints with explicit methods parameter
        self.register_endpoint(self.index_ep, "room_db_index", methods=["GET"])
        self.register_endpoint(self.health_ep, "room_db_health", methods=["GET"])
        self.register_endpoint(self.test_ep, "room_db_test", methods=["GET"])
        self.register_endpoint(self.update_config_ep, "room_db_update_config", methods=["POST"])
        self.register_endpoint(self.bulk_update_ep, "room_db_bulk_update", methods=["POST"])
        self.register_endpoint(
            self.reload_mapping_ep,
            "room_db_reload_mapping",
            methods=["GET", "POST"],
        )
        # Temporary diagnostic endpoint
        self.register_endpoint(self.debug_request_ep, "room_db_debug_request", methods=["POST"])

        self.log("room_db_updater initialized")

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS room_configs (
                    config_domain TEXT NOT NULL,
                    room_id       TEXT NOT NULL,
                    config_data   TEXT NOT NULL,
                    version       INTEGER NOT NULL DEFAULT 1,
                    created_at    INTEGER NOT NULL,
                    updated_at    INTEGER NOT NULL,
                    PRIMARY KEY (config_domain, room_id)
                );
            """)
            cur.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);")
            cur.execute("SELECT COUNT(*) FROM schema_version;")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO schema_version(version) VALUES (?);", (SCHEMA_VERSION,))
            con.commit()

    def _load_mapping(self):
        path = self.canonical_mapping_file or "/config/www/area_mapping.yaml"
        self._mapping_path = path
        with open(path, encoding="utf-8") as f:
            mapping = yaml.safe_load(f) or {}
        self._canonical_rooms = set(
            (mapping.get("metadata") or {}).get("valid_rooms", []) or []
        )
        allowed: dict[str, set[str]] = {rid: set() for rid in self._canonical_rooms}
        for node in mapping.get("nodes", []) or []:
            rid = node.get("id")
            caps = (node.get("capabilities") or {})
            if not rid:
                continue
            if "motion_lighting" in caps:
                allowed.setdefault(rid,set()).add("motion_lighting")
            vc = caps.get("vacuum_control")
            if isinstance(vc, dict) and vc.get("segment_id") is not None:
                allowed.setdefault(rid,set()).add("vacuum_control")
        for rid in self._canonical_rooms:
            allowed.setdefault(rid,set()).update({"shared","activity_tracking"})
        self._allowed_matrix = allowed
        self.log(f"Loaded {len(self._canonical_rooms)} canonical rooms from {path}")

    def _respect_limiter(self, domain: str):
        limit = max(1, int(self.write_rate_limit_seconds))
        jitter = random.uniform(0.0, 1.0)
        now = time.time()
        next_ok = self._next_write_ts.get(domain, 0.0)
        if now < next_ok:
            raise RateLimited(f"{next_ok-now:.2f}s remain for domain={domain}")
        self._next_write_ts[domain] = now + limit + jitter

    def _is_allowed(self, domain: str, room_id: str) -> bool:
        if domain not in self.allowed_domains:
            return False
        if room_id not in self._allowed_matrix:
            return False
        return domain in self._allowed_matrix[room_id]

    def _cfg_size_ok(self, cfg: dict) -> bool:
        try:
            size = len(json.dumps(cfg, ensure_ascii=False))
        except Exception:
            return False
        return size <= self.max_config_size_bytes

    def _upsert(self, domain: str, room_id: str, cfg: dict):
        now = int(time.time())
        cfg_json = json.dumps(cfg, ensure_ascii=False, separators=(",",":"))
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO room_configs (config_domain, room_id, config_data, version, created_at, updated_at)
                VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(config_domain, room_id) DO UPDATE SET
                    config_data=excluded.config_data,
                    version=room_configs.version+1,
                    updated_at=excluded.updated_at;
            """, (domain, room_id, cfg_json, now, now))
            con.commit()

    def _export_async(self):
        with contextlib.suppress(Exception):
            self.run_in(
                lambda *_: self.call_service(
                    "appdaemon/call", app="room_db_exporter", function="write_once"
                ),
                0.5,
            )

    def debug_request_ep(self, request, data):
        """Diagnostic endpoint to inspect request structure"""
        info = {
            "request_type": str(type(request)),
            "data_type": str(type(data)),
            "data_value": str(data)[:200] if data else "None",
            "request_attrs": dir(request),
            "has_body": hasattr(request, 'body'),
            "has_json": hasattr(request, 'json'),
            "content_type": getattr(request, 'content_type', 'N/A')
        }
        
        if hasattr(request, 'body'):
            try:
                info["body_preview"] = request.body[:200].decode('utf-8')
            except Exception:
                info["body_preview"] = "decode_failed"
        
        if hasattr(request, 'json'):
            try:
                info["json_attr"] = request.json
            except Exception:
                info["json_attr"] = "access_failed"
        
        return (info, 200)

    def _read_json(self, request, data):
        """Robust JSON parsing from multiple sources"""
        # 1. Try data parameter directly (dict or JSON string)
        if isinstance(data, dict) and data:
            return data
        if isinstance(data, (str, bytes)):
            with contextlib.suppress(Exception):
                parsed = json.loads(data)
                if isinstance(parsed, dict):
                    return parsed
        
        # 2. Try reading request body directly (AppDaemon 4.x)
        try:
            if hasattr(request, 'body'):
                body_bytes = request.body
                if isinstance(body_bytes, bytes):
                    body_str = body_bytes.decode('utf-8')
                    parsed = json.loads(body_str)
                    if isinstance(parsed, dict):
                        return parsed
        except Exception as e:
            self.log(f"Body read failed: {e}", level="DEBUG")
        
        # 3. Try self.get_json(request) - may not work in all versions
        try:
            body = self.get_json(request)
            if isinstance(body, dict) and body:
                return body
        except Exception:
            pass
        
        # 4. Try query parameters (for GET-style calls)
        try:
            q = getattr(request, "query", {})
            if q:
                out = {}
                for k in ("domain", "room_id", "config_data", "items"):
                    if k in q:
                        out[k] = q[k]
                if "config_data" in out and isinstance(out["config_data"], str):
                    with contextlib.suppress(Exception):
                        out["config_data"] = json.loads(out["config_data"])
                if "items" in out and isinstance(out["items"], str):
                    with contextlib.suppress(Exception):
                        out["items"] = json.loads(out["items"])
                if out:
                    return out
        except Exception:
            pass
        
        return {}

    def index_ep(self, request, data):
        """List all available endpoints"""
        endpoints = {
            "health": "/api/appdaemon/room_db_health",
            "test": "/api/appdaemon/room_db_test",
            "update_config": "/api/appdaemon/room_db_update_config",
            "bulk_update": "/api/appdaemon/room_db_bulk_update",
            "reload_mapping": "/api/appdaemon/room_db_reload_mapping",
        }
        
        # Only advertise exporter if it's actually loaded
        try:
            self.get_state("appdaemon.room_db_exporter")
            endpoints["export"] = "/api/appdaemon/room_db_export"
            endpoints["export_write_once"] = "/api/appdaemon/room_db_export_write_once"
        except Exception:
            pass
        
        return ({"status":"ok", "endpoints": endpoints}, 200)

    def health_ep(self, request, data):
        """Health check endpoint"""
        return ({
            "status": "healthy",
            "db_path": self.db_path,
            "schema_expected": self.schema_expected,
            "mapping_path": self._mapping_path,
            "canonical_rooms_count": len(self._canonical_rooms),
            "allowed_domains": sorted(self.allowed_domains),
            "app_init_error": self._init_error
        }, 200)

    def test_ep(self, request, data):
        """Test endpoint to verify routing"""
        return ({
            "status":"test_success",
            "message":"Test endpoint is working",
            "app_name": self.name
        }, 200)

    def update_config_ep(self, request, data):
        """Single room/domain configuration update"""
        try:
            payload = self._read_json(request, data)
            
            # Debug logging for empty payloads
            if not payload:
                self.log(
                    f"Empty payload - request type: {type(request)}, data type: {type(data)}",
                    level="WARNING",
                )
                if hasattr(request, 'body'):
                    self.log(
                        f"Request body preview: {str(request.body[:200])}",
                        level="DEBUG",
                    )
            
            domain = payload.get("domain")
            room_id = payload.get("room_id")
            cfg = payload.get("config_data", {}) or {}
            
            if not isinstance(domain, str) or not isinstance(room_id, str):
                return ({"status":"error","error":"domain and room_id required"}, 400)
            if not ROOM_ID_RE.match(room_id):
                return ({"status":"error","error":"invalid room_id"}, 422)
            if not self._cfg_size_ok(cfg):
                return ({"status":"error","error":"config_data too large"}, 413)
            if not self._is_allowed(domain, room_id):
                return ({"status":"error","error":f"{domain}:{room_id} not allowed by mapping"}, 422)
            
            self._respect_limiter(domain)
            
            if not self.dry_run:
                self._upsert(domain, room_id, cfg)
                self._export_async()
            
            return ({"status":"ok","room_id":room_id,"domain":domain}, 200)
            
        except RateLimited as rl:
            return ({"status":"retry","error":"WRITE_RATE_LIMIT","detail":str(rl)}, 429)
        except Exception as e:
            self.error(f"update_config_ep error: {e}")
            return ({"status":"error","error":str(e)}, 500)

    def bulk_update_ep(self, request, data):
        """Bulk configuration updates with per-item results"""
        try:
            payload = self._read_json(request, data)
            items = None
            if isinstance(payload, list):
                items = payload
            elif isinstance(payload, dict):
                items = payload.get("items")
            
            if not items or not isinstance(items, list):
                return ({"status":"error","error":"no items"}, 400)
            
            results: list[dict[str, Any]] = []
            for it in items:
                domain = it.get("domain")
                room_id = it.get("room_id")
                cfg = it.get("config_data", {}) or {}
                
                try:
                    if not isinstance(domain, str) or not isinstance(room_id, str):
                        results.append({
                            "room_id":room_id,
                            "domain":domain,
                            "status":"error",
                            "error":"domain and room_id required"
                        })
                        continue
                    
                    if not self._is_allowed(domain, room_id):
                        results.append({
                            "room_id":room_id,
                            "domain":domain,
                            "status":"error",
                            "error":"not allowed"
                        })
                        continue
                    
                    self._respect_limiter(domain)
                    
                    if not self.dry_run:
                        self._upsert(domain, room_id, cfg)
                    
                    results.append({
                        "room_id":room_id,
                        "domain":domain,
                        "status":"ok"
                    })
                    
                except RateLimited:
                    results.append({
                        "room_id":room_id,
                        "domain":domain,
                        "status":"retry",
                        "error":"WRITE_RATE_LIMIT"
                    })
                except Exception as e:
                    results.append({
                        "room_id":room_id,
                        "domain":domain,
                        "status":"error",
                        "error":str(e)
                    })
            
            if not self.dry_run:
                self._export_async()
            
            return ({"status":"ok","results":results}, 200)
            
        except Exception as e:
            self.error(f"bulk_update_ep error: {e}")
            return ({"status":"error","error":str(e)}, 500)

    def reload_mapping_ep(self, request, data):
        """Reload canonical mapping file (GET or POST)"""
        try:
            self._load_mapping()
            return ({
                "status":"ok",
                "mapping":{
                    "rooms":len(self._canonical_rooms),
                    "path":self._mapping_path
                }
            }, 200)
        except Exception as e:
            self.error(f"reload_mapping_ep error: {e}")
            return ({"status":"error","error":str(e)}, 500)
