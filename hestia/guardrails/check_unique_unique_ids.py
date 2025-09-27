#!/usr/bin/env python3
import collections
import glob
import sys

import yaml

uids=collections.Counter()
for p in glob.glob("**/*.yaml", recursive=True):
    try:
        doc=yaml.safe_load(open(p, "r", encoding="utf-8")) or {}
    except Exception:
        continue
    def walk(x):
        if isinstance(x, dict):
            if "unique_id" in x and isinstance(x["unique_id"], str):
                uids[x["unique_id"]] += 1
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(doc)
dups=[k for k,v in uids.items() if v>1]
if dups:
    print("Duplicate unique_id values:", dups, file=sys.stderr)
    sys.exit(1)
print("All unique_id values are unique.")
