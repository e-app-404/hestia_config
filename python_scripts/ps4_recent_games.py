#!/usr/bin/env python3
# ps4_recent_games.py
# Usage:
#   python3 /config/python_scripts/ps4_recent_games.py /config/.ps4-games.BC60A7454CD9_10e7.json 4
#
# Emits JSON to stdout:
#   {
#     "count": <int>,
#     "first": {"title": <str>, "image": <str>},
#     "games": [{"title": <str>, "image": <str>}, ...],
#     "titles": [<str>, ...],
#     "images": [<str>, ...]
#   }

import json
import sys
from datetime import datetime

PLACEHOLDER = "/media/ps-placeholder.png"

def _coerce_str(v):
    if v is None:
        return ""
    return str(v)

def _best_title(d):
    # Try a few likely keys / structures
    for k in ("title", "name", "titleName"):
        if isinstance(d.get(k), str) and d[k].strip():
            return d[k].strip()
    # Nested variants
    if isinstance(d.get("game"), dict):
        for k in ("title", "name"):
            v = d["game"].get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""

def _best_image(d):
    # Common keys
    for k in ("image", "imageUrl", "cover", "coverUrl", "cover_url"):
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # Some payloads store images in arrays/objects
    imgs = d.get("images")
    if isinstance(imgs, list) and imgs:
        # pick the first string-like URL
        for v in imgs:
            if isinstance(v, str) and v.strip():
                return v.strip()
            if isinstance(v, dict):
                for key in ("url", "href", "image", "src"):
                    vv = v.get(key)
                    if isinstance(vv, str) and vv.strip():
                        return vv.strip()
    return ""

def _best_timestamp(d):
    # Return sortable timestamp (ISO8601 → datetime) where possible
    # Many exports have "lastPlayed" or "last_played" or "updatedAt"
    for k in ("lastPlayed", "last_played", "updatedAt", "last_used", "lastLaunch"):
        v = d.get(k)
        if isinstance(v, str) and v:
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except Exception:
                pass
    # Sometimes numeric epoch seconds
    for k in ("lastPlayedTs", "last_played_ts", "updated_at_ts"):
        v = d.get(k)
        if isinstance(v, (int, float)):
            try:
                return datetime.fromtimestamp(v)
            except Exception:
                pass
    return None

def normalize_items(raw):
    """Return list of dicts: {'title': str, 'image': str, '_ts': datetime|None}"""
    items = []
    if isinstance(raw, dict):
        # Common top-level wrappers
        for key in ("games", "recent", "items", "data"):
            if isinstance(raw.get(key), list):
                raw = raw[key]
                break
        else:
            # If it's a dict but not a list wrapper, bail to empty
            raw = []
    if not isinstance(raw, list):
        raw = []

    for entry in raw:
        if not isinstance(entry, dict):
            continue
        title = _best_title(entry)
        image = _best_image(entry)
        ts = _best_timestamp(entry)
        if not title and not image:
            # Try nested 'game' object as a last resort
            g = entry.get("game")
            if isinstance(g, dict):
                title = title or _best_title(g)
                image = image or _best_image(g)
                ts = ts or _best_timestamp(g)
        items.append({"title": _coerce_str(title), "image": _coerce_str(image), "_ts": ts})
    return items

def sort_items(items):
    # Sort by timestamp desc if available, else preserve order
    with_ts = [x for x in items if x["_ts"] is not None]
    without_ts = [x for x in items if x["_ts"] is None]
    with_ts.sort(key=lambda x: x["_ts"], reverse=True)
    return with_ts + without_ts

def main():
    # Args
    try:
        path = sys.argv[1]
    except IndexError:
        print(json.dumps({"count": 0, "first": None, "games": [], "titles": [], "images": []}))
        return
    try:
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    except Exception:
        limit = 4

    # Load file safely
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        print(json.dumps({"count": 0, "first": None, "games": [], "titles": [], "images": []}))
        return

    items = normalize_items(data)
    items = sort_items(items)
    items = items[: max(0, limit)]

    # Prepare output
    out_games = []
    for it in items:
        title = it["title"] or "Unknown"
        image = it["image"] or PLACEHOLDER
        out_games.append({"title": title, "image": image})

    out = {
        "count": len(out_games),
        "first": (out_games[0] if out_games else None),
        "games": out_games,
        "titles": [g["title"] for g in out_games],
        "images": [g["image"] for g in out_games],
    }
    print(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    main()
