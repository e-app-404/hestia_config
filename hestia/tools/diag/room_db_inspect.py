#!/usr/bin/env python3

"""
Room-DB read-only inspector
- Opens SQLite via URI with mode=ro (no writes)
- Prints tables, columns, row counts
- If a table includes columns (config_domain, room_id, payload), prints a compact per-domain summary
- Accepts optional --db <path> argument; otherwise attempts to read from appdaemon.log

Usage:
  python3 /config/hestia/tools/diag/room_db_inspect.py [--db /config/room_database.db]

ADR compliance:
- ADR-0024: Uses canonical /config paths only
- ADR-0027: Read-only; no writes; safe to run anytime
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

APPDAEMON_LOG = Path("/config/hestia/config/diagnostics/appdaemon.log")


def find_db_path_from_log(log_path: Path) -> str | None:
    if not log_path.exists():
        return None
    try:
        text = log_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    candidate = None
    for line in text.splitlines():
        if "Database initialized at" in line:
            parts = line.strip().split("Database initialized at", 1)
            if len(parts) == 2:
                c = parts[1].strip()
                if c:
                    candidate = c
    return candidate


def inspect_db(db_path: str) -> dict[str, Any]:
    result: dict[str, Any] = {"db_path": db_path, "tables": [], "by_domain": {}}
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except Exception as e:
        result["error"] = f"unable to open db read-only: {e}"
        return result
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            # columns
            try:
                cur.execute(f"PRAGMA table_info({t})")
                cols = [r[1] for r in cur.fetchall()]
            except Exception:
                cols = []
            # rows
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                count = int(cur.fetchone()[0])
            except Exception:
                count = -1
            result["tables"].append({"name": t, "columns": cols, "rows": count})
        # domain summary
        candidates = [
            ti["name"]
            for ti in result["tables"]
            if set(["config_domain", "room_id"]).issubset(set(ti.get("columns", [])))
        ]
        by_domain: dict[str, set] = {}
        for t in candidates:
            try:
                cur.execute(f"SELECT DISTINCT config_domain, room_id FROM {t}")
                for domain, room in cur.fetchall():
                    if isinstance(domain, str) and isinstance(room, str):
                        by_domain.setdefault(domain, set()).add(room)
            except Exception:
                continue
        result["by_domain"] = {k: sorted(v) for k, v in by_domain.items()}
        return result
    finally:
        import contextlib
        with contextlib.suppress(Exception):
            conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", dest="db", help="Path to room database (SQLite)")
    args = parser.parse_args()

    db = args.db or find_db_path_from_log(APPDAEMON_LOG)
    out: dict[str, Any] = {}
    if not db:
        out = {"error": "db path not provided and not found in appdaemon.log"}
    else:
        out = inspect_db(db)

    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
