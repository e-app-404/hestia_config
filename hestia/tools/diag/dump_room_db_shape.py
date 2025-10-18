#!/usr/bin/env python3

"""
Dump Room-DB shape (canonical rooms per domain) without direct SQL access.

Strategy:
- Read HA long-lived token from /config/secrets.yaml (key: HA_TOKEN)
- Query HA API states for room_db sensors and parse attributes.payload JSON:
  - sensor.room_configs_motion_lighting
  - sensor.room_configs_vacuum_control
  - sensor.room_configs_activity_tracking_dict (if present)
- Parse AppDaemon log to extract Room-DB path and recent metadata lines

Outputs a compact JSON summary with:
- db_path (from appdaemon.log if found)
- domains: {domain: [sorted room_ids]}
- union_rooms: sorted unique set across domains
- notes: anomalies or missing entities

This script is read-only and adheres to ADR-0008/0027 policies.
"""

from __future__ import annotations

import json
import sqlite3
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

HA_URL = "http://homeassistant.local:8123"
SECRETS_PATH = Path("/config/secrets.yaml")
APPDAEMON_LOG = Path("/config/hestia/config/diagnostics/appdaemon.log")

SENSOR_ENTITIES = [
    ("motion_lighting", "sensor.room_configs_motion_lighting"),
    ("vacuum_control", "sensor.room_configs_vacuum_control"),
    ("activity_tracking", "sensor.room_configs_activity_tracking_dict"),
]


def load_token() -> str:
    with SECRETS_PATH.open("r", encoding="utf-8") as f:
        secrets = yaml.safe_load(f) or {}
    token = secrets.get("HA_TOKEN") or secrets.get("hass_token")
    if not token:
        raise RuntimeError("HA_TOKEN not found in /config/secrets.yaml")
    return token


def ha_api_get(path: str, token: str) -> dict[str, Any]:
    url = f"{HA_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} for GET {path}") from e


def get_state(entity_id: str, token: str) -> dict[str, Any]:
    return ha_api_get(f"/api/states/{entity_id}", token)


def parse_payload(attr_payload: Any) -> dict[str, Any]:
    # payload is typically a JSON string; tolerate dict too
    if attr_payload is None:
        return {}
    if isinstance(attr_payload, str):
        s = attr_payload.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return {}
        return {}
    if isinstance(attr_payload, dict):
        return attr_payload
    return {}


def extract_rooms_from_sensor(entity_id: str, token: str) -> list[str]:
    try:
        st = get_state(entity_id, token)
    except Exception:
        return []
    attrs = st.get("attributes", {})
    payload = parse_payload(attrs.get("payload"))
    if not isinstance(payload, dict):
        return []
    return sorted([k for k in payload if isinstance(k, str)])


def tail_appdaemon_db_path(log_path: Path) -> str | None:
    if not log_path.exists():
        return None
    try:
        text = log_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    db_path = None
    for line in text.splitlines():
        if "Database initialized at" in line:
            # example: "Database initialized at /config/room_database.db"
            parts = line.strip().split("Database initialized at", 1)
            if len(parts) == 2:
                candidate = parts[1].strip()
                if candidate:
                    db_path = candidate
    return db_path


def find_area_mapping_file() -> Path | None:
    """Return the first existing canonical area mapping file.

    Preference order (left→right):
    - /config/www/area_mapping.yaml (runtime served static)
    - /config/domain/architecture/area_mapping.yaml (new canonical per docs)
    - /config/hestia/workspace/patches/appdaemon/area_mapping.yaml (workspace patch)
    """
    candidates = [
        Path("/config/www/area_mapping.yaml"),
        Path("/config/domain/architecture/area_mapping.yaml"),
        Path("/config/hestia/workspace/patches/appdaemon/area_mapping.yaml"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def parse_expected_rooms(mapping_path: Path) -> list[str]:
    """Parse canonical expected rooms from area mapping YAML.

    Strategy:
    - Use metadata.valid_rooms if present
    - Else, collect ids from nodes[] where id is a string
    - Return sorted unique list
    """
    try:
        data = yaml.safe_load(mapping_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return []

    rooms: list[str] = []
    meta = data.get("metadata") or {}
    valid = meta.get("valid_rooms")
    if isinstance(valid, list):
        rooms.extend([x for x in valid if isinstance(x, str)])

    if not rooms:
        nodes = data.get("nodes")
        if isinstance(nodes, list):
            for n in nodes:
                if isinstance(n, dict):
                    rid = n.get("id")
                    if isinstance(rid, str):
                        rooms.append(rid)

    # unique + sorted
    return sorted(sorted(set(rooms)))


def try_sqlite_enumeration(db_path_str: str | None) -> dict[str, Any]:
    """Best-effort read-only SQLite introspection for room/domain pairs.

    - Opens the DB in read-only URI mode if file exists locally
    - Lists tables and row counts
    - If a table contains both columns 'room_id' and 'config_domain',
      returns distinct pairs aggregated by domain under by_domain
    """
    result: dict[str, Any] = {"by_domain": {}, "tables": []}
    if not db_path_str:
        result["error"] = "db_path unavailable"
        return result
    db_file = Path(db_path_str)
    if not db_file.exists():
        result["error"] = f"db file not found at {db_path_str} (not on this workspace)"
        return result
    try:
        conn = sqlite3.connect(f"file:{db_path_str}?mode=ro", uri=True)
    except Exception as e:
        result["error"] = f"unable to open db read-only: {e}"
        return result
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            # row count
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                count = int(cur.fetchone()[0])
            except Exception:
                count = -1
            # columns
            try:
                cur.execute(f"PRAGMA table_info({t})")
                cols = [r[1] for r in cur.fetchall()]
            except Exception:
                cols = []
            result["tables"].append({"name": t, "rows": count, "columns": cols})

        # find table(s) with desired columns
        candidate_tables = [
            ti["name"]
            for ti in result["tables"]
            if set(["room_id", "config_domain"]).issubset(set(ti.get("columns", [])))
        ]
        by_domain: dict[str, set] = {}
        for t in candidate_tables:
            try:
                cur.execute(f"SELECT DISTINCT config_domain, room_id FROM {t}")
                for domain, room in cur.fetchall():
                    if isinstance(domain, str) and isinstance(room, str):
                        by_domain.setdefault(domain, set()).add(room)
            except Exception:
                # skip silently; keep best-effort behavior
                continue
        result["by_domain"] = {k: sorted(v) for k, v in by_domain.items()}
        return result
    finally:
        import contextlib
        with contextlib.suppress(Exception):
            conn.close()


def main() -> int:
    token = load_token()
    summary: dict[str, Any] = {
        "domains": {},
        "union_rooms": [],
        "notes": [],
    }

    for domain, entity in SENSOR_ENTITIES:
        rooms = extract_rooms_from_sensor(entity, token)
        if rooms:
            summary["domains"][domain] = rooms
        else:
            summary["notes"].append(f"No data for {entity}")

    # union of rooms
    union = set()
    for rooms in summary["domains"].values():
        union.update(rooms)
    summary["union_rooms"] = sorted(union)

    # db path from logs
    db_path = tail_appdaemon_db_path(APPDAEMON_LOG)
    if db_path:
        summary["db_path"] = db_path
    else:
        summary["notes"].append("DB path not found in appdaemon.log")

    # cross-check against canonical area mapping
    mapping_file = find_area_mapping_file()
    if mapping_file:
        expected = parse_expected_rooms(mapping_file)
        summary["expected_rooms"] = expected
        summary["mapping_file"] = str(mapping_file)
        if expected:
            present = set(summary["union_rooms"]) if summary["union_rooms"] else set()
            exp = set(expected)
            missing = sorted(list(exp - present))
            unexpected = sorted(list(present - exp))
            if missing:
                summary["missing_in_db"] = missing
            if unexpected:
                summary["unexpected_in_db"] = unexpected
    else:
        summary["notes"].append("Area mapping file not found in any canonical location")

    # optional: try read-only sqlite enumeration (only if local file exists)
    sql_info = try_sqlite_enumeration(summary.get("db_path"))
    # Only include if we found anything meaningful to avoid noise
    if sql_info.get("by_domain") or sql_info.get("tables") or sql_info.get("error"):
        summary["db_sql"] = sql_info

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
