import json, argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-file", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    
    data = json.load(open(args.graph_file, "r", encoding="utf-8"))
    nodes = data.get("nodes", [])
    idx = {n["entity_id"]: n for n in nodes}
    total = 0; ok = 0
    for n in nodes:
        for up in n.get("upstream_refs", []):
            if up in idx:
                total += 1
                if n["entity_id"] in idx[up].get("downstream_refs", []):
                    ok += 1
    pct = (ok/total*100.0) if total else 100.0
    out = {"bidir_consistency_percent": pct, "health_score": pct}
    open(args.output, "w", encoding="utf-8").write(json.dumps(out, indent=2))
    print(f"[INFO] Integrity report → {args.output} (health={pct:.1f}%)")

if __name__ == "__main__":
    main()
