import json, argparse
from typing import List
from lineage_guardian.models import EntityNode

def load_graph(path: str) -> List[EntityNode]:
    data = json.load(open(path, "r", encoding="utf-8"))
    return [EntityNode(**n) for n in data.get("nodes", [])]

def compute_violations(nodes: List[EntityNode]):
    out=[]
    for n in nodes:
        exp_up = sorted(set([e for e in n.upstream_refs if "." in e]))
        dec_up = sorted(set(n.attributes_declared_upstream))
        miss_up = [e for e in exp_up if e not in dec_up]
        if miss_up:
            out.append({"violation_type":"MISSING_UPSTREAM","entity_id":n.entity_id,"file_path":n.file_path,"expected":exp_up,"actual":dec_up})
        
        exp_dn = sorted(set(n.downstream_refs))
        dec_dn = sorted(set(n.attributes_declared_downstream))
        miss_dn = [e for e in exp_dn if e not in dec_dn]
        if miss_dn:
            out.append({"violation_type":"MISSING_DOWNSTREAM","entity_id":n.entity_id,"file_path":n.file_path,"expected":exp_dn,"actual":dec_dn})
        
        if n.source_count_declared is not None:
            if int(n.source_count_declared) != len(exp_up):
                out.append({"violation_type":"COUNT_MISMATCH","entity_id":n.entity_id,"file_path":n.file_path,"expected":[str(len(exp_up))],"actual":[str(n.source_count_declared)]})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph-file", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    nodes = load_graph(args.graph_file)
    viols = compute_violations(nodes)
    open(args.output, "w", encoding="utf-8").write(json.dumps(viols, indent=2))
    print(f"[INFO] Violations written to {args.output} ({len(viols)} findings)")

if __name__ == "__main__":
    main()
