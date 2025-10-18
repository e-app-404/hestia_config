import json, os, re, sqlite3, time, random
from typing import Dict, Set, Any, List
import yaml
import appdaemon.plugins.hass.hassapi as hass

SCHEMA_VERSION = 1
ROOM_ID_RE = re.compile(r"^[a-z0-9_]+$")

class RateLimited(Exception): pass

class RoomDbUpdater(hass.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        self.schema_expected = int(self.args.get("schema_expected", SCHEMA_VERSION))
        self.canonical_mapping_file = self.args.get("canonical_mapping_file", "/config/www/area_mapping.yaml")
        self.allowed_domains = set(self.args.get("allowed_domains", ["motion_lighting","vacuum_control","shared","activity_tracking"]))
        self.max_config_size_bytes = int(self.args.get("max_config_size_bytes", 4096))
        self.write_rate_limit_seconds = int(self.args.get("write_rate_limit_seconds", 5))
        self.dry_run = bool(self.args.get("dry_run", False))

        self._next_write_ts: Dict[str,float] = {}
        self._allowed_matrix: Dict[str, Set[str]] = {}
        self._canonical_rooms: Set[str] = set()
        self._mapping_path = None
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

        self.register_endpoint(self.health_ep, "room_db_health")
        self.register_endpoint(self.test_ep, "room_db_test")
        self.register_endpoint(self.update_config_ep, "room_db_update_config", methods=["POST"])
        self.register_endpoint(self.bulk_update_ep, "room_db_bulk_update", methods=["POST"])
        self.register_endpoint(self.reload_mapping_ep, "room_db_reload_mapping", methods=["POST"])
        self.register_endpoint(self.index_ep, "room_db_index")

        self.log("room_db_updater initialized")

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""                CREATE TABLE IF NOT EXISTS room_configs (
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
        with open(path, "r", encoding="utf-8") as f:
            mapping = yaml.safe_load(f) or {}
        self._canonical_rooms = set((mapping.get("metadata") or {}).get("valid_rooms", []) or [])
        allowed: Dict[str, Set[str]] = {rid:set() for rid in self._canonical_rooms}
        for node in mapping.get("nodes", []) or []:
            rid = node.get("id")
            caps = (node.get("capabilities") or {})
            if not rid: continue
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
        jitter = random.uniform(-1.0, 1.0)
        now = time.time()
        next_ok = self._next_write_ts.get(domain, 0.0)
        if now < next_ok:
            raise RateLimited(f"{next_ok-now:.2f}s remain for domain={domain}")
        self._next_write_ts[domain] = now + limit + jitter

    def _is_allowed(self, domain: str, room_id: str) -> bool:
        if domain not in self.allowed_domains: return False
        if room_id not in self._allowed_matrix: return False
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
            cur.execute("""                INSERT INTO room_configs (config_domain, room_id, config_data, version, created_at, updated_at)
                VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(config_domain, room_id) DO UPDATE SET
                    config_data=excluded.config_data,
                    version=room_configs.version+1,
                    updated_at=excluded.updated_at;
            """, (domain, room_id, cfg_json, now, now))
            con.commit()

    def _export_async(self):
        try:
            self.run_in(lambda *_: self.call_service("appdaemon/call", app="room_db_exporter", function="write_once"), 0.5)
        except Exception:
            pass

    def index_ep(self, request, data):
        return ({ "status":"ok", "endpoints": {
            "health": "/api/appdaemon/room_db_health",
            "test": "/api/appdaemon/room_db_test",
            "update_config": "/api/appdaemon/room_db_update_config",
            "bulk_update": "/api/appdaemon/room_db_bulk_update",
            "reload_mapping": "/api/appdaemon/room_db_reload_mapping",
            "export": "/api/appdaemon/room_db_export",
            "export_write_once": "/api/appdaemon/room_db_export_write_once"
        }}, 200)

    def health_ep(self, request, data):
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
        return ({"status":"test_success","message":"Test endpoint is working","app_name": self.name}, 200)

    def update_config_ep(self, request, data):
        try:
            payload = {}
            if isinstance(data, dict):
                payload = data
            elif isinstance(data, (str, bytes)):
                try:
                    payload = json.loads(data)
                except Exception:
                    payload = {}
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
        items = None
        raw = data
        if isinstance(raw, (str, bytes)):
            try:
                raw = json.loads(raw)
            except Exception:
                raw = None
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            items = raw.get("items")
        if not items or not isinstance(items, list):
            return ({"status":"error","error":"no items"}, 400)
        results: List[Dict[str, Any]] = []
        for it in items:
            domain = it.get("domain"); room_id = it.get("room_id"); cfg = it.get("config_data", {}) or {}
            try:
                if not self._is_allowed(domain, room_id):
                    results.append({"room_id":room_id,"domain":domain,"status":"error","error":"not allowed"})
                    continue
                self._respect_limiter(domain)
                if not self.dry_run:
                    self._upsert(domain, room_id, cfg)
                results.append({"room_id":room_id,"domain":domain,"status":"ok"})
            except RateLimited:
                results.append({"room_id":room_id,"domain":domain,"status":"retry","error":"WRITE_RATE_LIMIT"})
            except Exception as e:
                results.append({"room_id":room_id,"domain":domain,"status":"error","error":str(e)})
        if not self.dry_run:
            self._export_async()
        return ({"status":"ok","results":results}, 200)

    def reload_mapping_ep(self, request, data):
        try:
            self._load_mapping()
            return ({"status":"ok","mapping":{"rooms":len(self._canonical_rooms)}}, 200)
        except Exception as e:
            return ({"status":"error","error":str(e)}, 500)
