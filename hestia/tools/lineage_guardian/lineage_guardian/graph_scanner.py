import os, json, yaml, argparse
from typing import List, Dict, Any
from lineage_guardian.models import EntityNode
from lineage_guardian.utils import extract_entities_from_state_block

def list_yaml_files(root: str) -> List[str]:
    files=[]
    for d,_,fs in os.walk(root):
        for fn in fs:
            if fn.endswith((".yaml",".yml")):
                files.append(os.path.join(d,fn))
    return sorted(files)

def derive_entity_id(domain: str, ent: Dict[str, Any]) -> str:
    uid = ent.get("unique_id")
    if isinstance(uid, str) and uid.strip():
        slug = uid.strip()
    else:
        name = ent.get("name") or "unnamed"
        slug = str(name).lower().replace(" ","_").replace("-","_")
    return f"{domain}.{slug}"

def scan_file(path: str) -> List[EntityNode]:
    try:
        raw = open(path, "r", encoding="utf-8").read()
        data = yaml.safe_load(raw)
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    nodes=[]
    for domain in ("binary_sensor","sensor"):
        items = data.get(domain)
        if not isinstance(items, list): continue
        for ent in items:
            if not isinstance(ent, dict): continue
            state = ent.get("state")
            attrs = ent.get("attributes") or {}
            us_decl,_ = extract_entities_from_state_block(str(attrs.get("upstream_sources")))
            ds_decl,_ = extract_entities_from_state_block(str(attrs.get("downstream_consumers")))
            ents,macs  = extract_entities_from_state_block(state or "")
            sc = attrs.get("source_count")
            try: sc = int(str(sc).strip('"').strip("'")) if sc is not None else None
            except Exception: sc = None
            nodes.append(EntityNode(
                entity_id = derive_entity_id(domain, ent),
                file_path = path,
                unique_id = ent.get("unique_id"),
                domain    = domain,
                tier      = attrs.get("tier"),
                upstream_refs = ents,
                downstream_refs = [],
                macro_imports   = macs,
                attributes_declared_upstream = us_decl,
                attributes_declared_downstream = ds_decl,
                source_count_declared = sc
            ))
    # downstream = reverse edges
    idx = {n.entity_id: n for n in nodes}
    for n in nodes:
        for up in n.upstream_refs:
            if up in idx and n.entity_id not in idx[up].downstream_refs:
                idx[up].downstream_refs.append(n.entity_id)
    for n in nodes:
        n.downstream_refs = sorted(n.downstream_refs)
    return nodes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template-dir", default="/config/domain/templates/")
    ap.add_argument("--output", required=True)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    
    files = list_yaml_files(args.template_dir)
    all_nodes=[]
    for f in files:
        all_nodes += scan_file(f)
    graph = {"nodes":[n.__dict__ for n in all_nodes], "meta":{"count":len(all_nodes)}}
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    open(args.output,"w",encoding="utf-8").write(json.dumps(graph, indent=2))
    print(f"[INFO] Scanned {len(files)} files → {len(all_nodes)} entities → {args.output}")

if __name__ == "__main__":
    main()
