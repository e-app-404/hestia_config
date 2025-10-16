import os, json, argparse

def main():
ap = argparse.ArgumentParser()
ap.add_argument("--graph", required=True)
ap.add_argument("--violations", required=True)
ap.add_argument("--integrity", required=True)
ap.add_argument("--outdir", required=True)
args = ap.parse_args()

```
os.makedirs(args.outdir, exist_ok=True)
graph = json.load(open(args.graph, "r", encoding="utf-8"))
viols = json.load(open(args.violations, "r", encoding="utf-8"))
integ = json.load(open(args.integrity, "r", encoding="utf-8"))

md = os.path.join(args.outdir, "REPORT.md")
with open(md, "w", encoding="utf-8") as f:
    f.write("# Lineage Guardian Report\n\n")
    f.write(f"- Entities: {graph.get('meta', {}).get('count', 0)}\n")
    f.write(f"- Violations: {len(viols)}\n")
    f.write(f"- Health Score: {integ.get('health_score', 0):.1f}\n")
    f.write(f"- Bidirectional Consistency: {integ.get('bidir_consistency_percent', 0):.1f}%\n")
print(f"[INFO] Report written → {md}")
```

if **name** == "**main**":
main()
