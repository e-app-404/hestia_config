#!/usr/bin/env python3
import collections
import glob
import sys

import yaml

ids=collections.Counter()
for p in glob.glob("**/*.yaml", recursive=True):
    try:
        with open(p, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
    except Exception:
        continue
    # hunt for automation lists anywhere
    def walk(x):
        if isinstance(x, dict):
            # direct automation list under "automation"
            if "automation" in x and isinstance(x["automation"], list):
                for a in x["automation"]:
                    if isinstance(a, dict) and "id" in a:
                        ids[a["id"]] += 1
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(doc)
dups=[k for k,v in ids.items() if v>1]
if dups:
    print("Duplicate automation ids:", dups, file=sys.stderr)
    sys.exit(1)
print("Automation ids are unique.")
