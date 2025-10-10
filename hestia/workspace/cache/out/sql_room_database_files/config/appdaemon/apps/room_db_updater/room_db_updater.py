import appdaemon.plugins.hass.hassapi as hass
import json, sqlite3, yaml, re, time, os
ROOM_ID_RE = re.compile(r"^[a-z0-9_]+$")
class RoomDbUpdater(hass.Hass):
    def initialize(self):
        self.register_endpoint(self.update_config, "room_db/update_config")
        self.log("RoomDbUpdater initialized")
    def _validate_room(self, room_id):
        if not ROOM_ID_RE.match(room_id or ""):
            raise ValueError("Invalid room_id slug")
        cfile = self.args.get("canonical_mapping_file")
        if not cfile or not os.path.exists(cfile):
            raise FileNotFoundError("Canonical mapping file not found")
        with open(cfile, "r") as f:
            amap = yaml.safe_load(f) or {}
        rooms = (amap.get("rooms") or {}) if isinstance(amap, dict) else {}
        if room_id not in rooms:
            raise ValueError("room_id not in canonical mapping")
    def _schema_ok(self, cur, expected):
        cur.execute("SELECT version FROM schema_version")
        v = cur.fetchone()[0]
        if int(v) != int(expected):
            raise RuntimeError("SCHEMA_VERSION_MISMATCH")
    def update_config(self, data):
        try:
            room_id = data.get("room_id"); domain = data.get("domain"); cfg = data.get("config_data")
            self._validate_room(room_id)
            conn = sqlite3.connect(self.args.get("db_path")); cur = conn.cursor()
            try:
                self._schema_ok(cur, self.args.get("schema_expected"))
                conn.execute("BEGIN IMMEDIATE")
                cur.execute("INSERT OR REPLACE INTO room_configs (room_id, config_domain, config_data, updated_at) VALUES (?,?,?, datetime('now'))",
                            (room_id, domain, json.dumps(cfg)))
                conn.commit()
            except Exception:
                conn.rollback(); raise
            finally:
                conn.close()
            return {"status":"ok"}
        except Exception as e:
            self.error(str(e))
            self.call_service("persistent_notification/create", title="Room DB Update Failed", message=str(e))
            return {"status":"error","error":str(e)}
