#!/usr/bin/env python3
import json, sys, os, pathlib

def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)

if len(sys.argv) != 3:
    die("Usage: ps4_recent_games.py <json_path> <limit>")

json_path = sys.argv[1]
limit = None
try:
    limit = int(sys.argv[2])
except (ValueError, IndexError):
    die("limit must be an integer")
if limit is None:
    die("limit argument is missing")

if not os.path.exists(json_path):
    # Not found → still return valid JSON so HA doesn't choke
    print(json.dumps({
        "count": 0, "first": None, "games": [],
        "titles": [], "images": {}
    }))
    sys.exit(0)

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Try to normalize unknown structures
# Accept either a list of games or an object with a list under a common key.
if isinstance(data, dict):
    games = list(data.values())
elif isinstance(data, list):
    games = data
else:
    games = []

# Helper to pull a title & image from a game dict with different field names
def get_title(g):
    for k in ("title", "name", "titleName", "npTitle", "title_name"):
        if isinstance(g, dict) and k in g and g[k]:
            return str(g[k])
    return None

def get_image(g):
    # common keys; adjust if your JSON uses different fields
    for k in ("image", "icon", "cover", "thumbnail", "img"):
        if isinstance(g, dict) and k in g and g[k]:
            return g[k]
    return None

# Slice and build outputs
games_out = games[:limit]
titles = [t for t in (get_title(g) for g in games_out) if t]
images = {get_title(g): get_image(g) for g in games_out if get_title(g)}

first_game = games_out[0] if games_out else None
if isinstance(first_game, dict) and "title" not in first_game:
    t = get_title(first_game)
    if t is not None:
        # add a "title" field so your template works
        first_game = {**first_game, "title": t}

out = {
    "count": len(games),
    "first": first_game,
    "games": games_out,
    "titles": titles,
    "images": images
}
print(json.dumps(out, ensure_ascii=False))
