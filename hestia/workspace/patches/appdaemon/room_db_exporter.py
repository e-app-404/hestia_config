# Minimal AppDaemon app to export Room-DB contents in a friendlier way
# Drop this into the AppDaemon add-on (apps/) and add a stanza in apps.yaml, e.g.:
# room_db_exporter:
#   module: room_db_exporter
#   class: RoomDbExporter
#   db_path: /config/room_database.db
# Then restart the add-on. Endpoint: /api/appdaemon/room_db_export

import contextlib
import json
import os
import sqlite3
import time

import appdaemon.plugins.hass.hassapi as hass


class RoomDbExporter(hass.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        self.export_path = self.args.get("export_path", "/config/hestia/workspace/operations/logs/room_db/room_db_export.json")
        self.schema_version = int(self.args.get("schema_version", 1))
        self._debounce_handle = None
        # Expose a simple global endpoint
        self.register_endpoint(self._handle_export, "room_db_export")
        self.register_endpoint(self._write_once_ep, "room_db_export_write_once", methods=["POST"])
        self.log(f"RoomDbExporter initialized with db_path={self.db_path} export_path={self.export_path}")

    def _handle_export(self, data):
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            result = {
                "schema_version": self.schema_version,
                "db_path": self.db_path,
                "exported_at": int(time.time()),
                "tables": tables,
                "by_domain": {},
                "counts": {},
            }
            # counts for each table
            for t in tables:
                try:
                    cur.execute(f"SELECT COUNT(1) FROM {t}")
                    result["counts"][t] = int(cur.fetchone()[0])
                except Exception:
                    result["counts"][t] = None
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
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            with contextlib.suppress(Exception):
                conn.close()

    # ---- Debounced write support ----
    def _write_once_ep(self, request, data):
        try:
            self.write_once()
            return ({"status": "ok"}, 200)
        except Exception as e:
            return ({"status": "error", "error": str(e)}, 500)

    def write_once(self):
        """Export once to disk (debounced via schedule)."""
        try:
            payload, code = self._handle_export({})
            if code != 200:
                raise RuntimeError(payload)
            self._atomic_write_json(self.export_path, payload)
            self.log(f"Room-DB exported to {self.export_path}")
        except Exception as e:
            self.error(f"Export write_once failed: {e}")

    def schedule_debounced(self, delay: float = 1.0):
        if self._debounce_handle:
            with contextlib.suppress(Exception):
                self.cancel_timer(self._debounce_handle)
        self._debounce_handle = self.run_in(lambda *_: self.write_once(), delay)

    def _atomic_write_json(self, path: str, data: dict):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp, path)
