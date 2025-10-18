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
import sys
from pathlib import Path
from typing import Dict, Any, List

import yaml
import urllib.request
import urllib.error


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


def ha_api_get(path: str, token: str) -> Dict[str, Any]:
    url = f"{HA_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} for GET {path}") from e


def get_state(entity_id: str, token: str) -> Dict[str, Any]:
    return ha_api_get(f"/api/states/{entity_id}", token)


def parse_payload(attr_payload: Any) -> Dict[str, Any]:
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


def extract_rooms_from_sensor(entity_id: str, token: str) -> List[str]:
    try:
        st = get_state(entity_id, token)
    except Exception:
        return []
    attrs = st.get("attributes", {})
    payload = parse_payload(attrs.get("payload"))
    if not isinstance(payload, dict):
        return []
    return sorted([k for k in payload.keys() if isinstance(k, str)])


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


def main() -> int:
    token = load_token()
    summary: Dict[str, Any] = {"domains": {}, "union_rooms": [], "notes": []}

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

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
