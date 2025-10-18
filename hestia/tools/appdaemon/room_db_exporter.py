# Minimal AppDaemon app to export Room-DB contents in a friendlier way
# Drop this into the AppDaemon add-on (apps/) and add a stanza in apps.yaml, e.g.:
# room_db_exporter:
#   module: room_db_exporter
#   class: RoomDbExporter
#   db_path: /config/room_database.db
# Then restart the add-on. Endpoint: /api/appdaemon/room_db_export

import contextlib
import json
import sqlite3

import appdaemon.plugins.hass.hassapi as hass


class RoomDbExporter(hass.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        # Expose a simple global endpoint
        self.register_endpoint(self._handle_export, "room_db_export")
        self.log(f"RoomDbExporter initialized with db_path={self.db_path}")

    def _handle_export(self, data):
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            result = {"db_path": self.db_path, "tables": tables, "by_domain": {}}
            # If room_configs exists, extract domain→rooms
            if "room_configs" in tables:
                cur.execute("PRAGMA table_info(room_configs)")
                cols = [r[1] for r in cur.fetchall()]
                if set(["config_domain", "room_id"]).issubset(set(cols)):
                    cur.execute("SELECT DISTINCT config_domain, room_id FROM room_configs")
                    by_domain = {}
                    for domain, room in cur.fetchall():
                        if isinstance(domain, str) and isinstance(room, str):
                            by_domain.setdefault(domain, set()).add(room)
                    result["by_domain"] = {k: sorted(list(v)) for k, v in by_domain.items()}
            return json.dumps(result), 200
        except Exception as e:
            return json.dumps({"error": str(e)}), 500
        finally:
            with contextlib.suppress(Exception):
                conn.close()
