"""
Room-DB Exporter v3.1
Provides stable HTTP GET endpoint and debounced file export
Features: Reliable JSON response, debounced writes, schema versioning
"""

import contextlib
import json
import os
import sqlite3
import time

import appdaemon.plugins.hass.hassapi as hass


class RoomDbExporter(hass.Hass):
    def initialize(self):
        self.db_path = self.args.get("db_path", "/config/room_database.db")
        self.export_path = self.args.get("export_path", "/config/room_db_export.json")
        self._debounce_handle = None
        
        # Register endpoint
        self.register_endpoint(self.export_ep, "room_db_export")
        self.log(f"roomdb/exporter/init level=INFO db_path={self.db_path} export_path={self.export_path}")

    def export_ep(self, data=None, **kwargs):
        """HTTP GET endpoint - always returns JSON, never 500"""
        try:
            blob = self._collect()
            return blob, 200
        except Exception as e:
            self.error(f"roomdb/exporter/export level=ERROR error={str(e)}")
            return {"status": "error", "error": str(e), "schema_version": 1, "counts": {}, "by_domain": {}}, 200

    def write_once(self, *args, **kwargs):
        """Write export to file immediately"""
        try:
            blob = self._collect()
            tmp = self.export_path + ".tmp"
            
            with open(tmp, "w") as f:
                json.dump(blob, f, indent=2)
            
            os.replace(tmp, self.export_path)
            self.log(f"roomdb/exporter/write level=INFO event=file_written path={self.export_path}")
            return True
            
        except Exception as e:
            self.error(f"roomdb/exporter/write level=ERROR event=write_failed error={str(e)}")
            return False

    def write_debounced(self):
        """Debounced write - coalesces multiple requests"""
        if self._debounce_handle:
            self.cancel_timer(self._debounce_handle)
        
        self._debounce_handle = self.run_in(self.write_once, 0.5)
        self.log("roomdb/exporter/debounce level=DEBUG event=write_scheduled")

    def _collect(self):
        """Collect all room database data into structured JSON"""
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cur = conn.cursor()
            
            # Check schema version
            schema_version = 1
            try:
                cur.execute("SELECT version FROM schema_version LIMIT 1")
                row = cur.fetchone()
                if row:
                    schema_version = int(row[0])
            except Exception:
                pass
            
            # Get table list
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            
            result = {
                "status": "ok",
                "schema_version": schema_version,
                "mtime": int(time.time()),
                "db_path": self.db_path,
                "tables": tables,
                "counts": {},
                "by_domain": {}
            }
            
            # If room_configs exists, extract domain data
            if "room_configs" in tables:
                # Get counts by domain
                cur.execute("SELECT config_domain, COUNT(*) FROM room_configs GROUP BY config_domain")
                result["counts"] = dict(cur.fetchall())
                
                # Get all data grouped by domain
                cur.execute("SELECT config_domain, room_id, config_data, updated_at FROM room_configs ORDER BY config_domain, room_id")
                by_domain = {}
                
                for domain, room_id, config_data, updated_at in cur.fetchall():
                    if domain not in by_domain:
                        by_domain[domain] = {}
                    
                    try:
                        config_obj = json.loads(config_data) if config_data else {}
                    except json.JSONDecodeError:
                        config_obj = {"raw": config_data}
                    
                    by_domain[domain][room_id] = {
                        "config_data": config_obj,
                        "updated_at": updated_at
                    }
                
                result["by_domain"] = by_domain
            
            return result
            
        except Exception as e:
            self.error(f"roomdb/exporter/collect level=ERROR error={str(e)}")
            return {
                "status": "error", 
                "error": str(e),
                "schema_version": 1,
                "mtime": int(time.time()),
                "counts": {},
                "by_domain": {}
            }
        finally:
            with contextlib.suppress(Exception):
                conn.close()