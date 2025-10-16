"""
Plan-only corrector stub: writes a suggested unified diff-style note per file.
Copilot can implement ruamel.yaml-based non-destructive merges later.
"""
import os, json, argparse, difflib, datetime
from collections import defaultdict

def main():
ap = argparse.ArgumentParser()
ap.add_argument("--violations-file", required=True)
ap.add_argument("--plan-dir", required=True)
args = ap.parse_args()

```
os.makedirs(args.plan_dir, exist_ok=True)
data = json.load(open(args.violations_file, "r", encoding="utf-8"))
by_file = defaultdict(list)
for v in data:
    by_file[v["file_path"]].append(v)

for fp, items in by_file.items():
    try:
        before = open(fp, "r", encoding="utf-8").read()
    except Exception:
        before = ""
    note = ["", f"# lineage_guardian plan {datetime.datetime.utcnow().isoformat()}Z"]
    for v in items:
        note.append(f"# {v['violation_type']} :: {v['entity_id']}")
        note.append(f"# expected: {v['expected']}")
        note.append(f"# actual:   {v['actual']}")
    after = before + "\n" + "\n".join(note) + "\n"
    plan = os.path.join(args.plan_dir, os.path.basename(fp) + ".plan.patch")
    diff = difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=fp, tofile=fp+".planned", n=3)
    with open(plan, "w", encoding="utf-8") as f:
        f.writelines(diff)
    print(f"[INFO] Plan written: {plan}")
```

if **name** == "**main**":
main()
