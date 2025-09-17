#!/usr/bin/env python3
import hashlib
import json
import os
import re
from pathlib import Path

import yaml

# env

ENV = {}
with open(os.environ["OUT_DIR"] + "/.env.meta") as f:
    for line in f:
        if "=" in line:
            k, v = line.strip().split("=", 1)
            ENV[k] = v

OUT_DIR = Path(ENV["OUT_DIR"])
MERGED = OUT_DIR / "merged" / "config" / "hestia" / "core"
GRAPH = OUT_DIR / "graph"
GRAPH.mkdir(parents=True, exist_ok=True)
NOTES = OUT_DIR / "notes"
NOTES.mkdir(parents=True, exist_ok=True)

# YAML audit: ensure 'cidrs:' is top-level in any network.conf*.yaml

yaml_fix = "PASS"
for p in MERGED.rglob("network.conf*.y*ml"):
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        continue
    changed = False
    if isinstance(data, dict) and "cidrs" not in data and "network" in data:

        def find_cidrs(o):
            if isinstance(o, dict) and "cidrs" in o:
                return o["cidrs"]
            if isinstance(o, list):
                for i in o:
                    r = find_cidrs(i)
                    if r:
                        return r

        c = find_cidrs(data["network"])
        if c:
            data["cidrs"] = c

        def strip(o):
            if isinstance(o, dict) and "cidrs" in o:
                o.pop("cidrs", None)
            if isinstance(o, dict):
                for v in o.values():
                    strip(v)
            elif isinstance(o, list):
                for v in o:
                    strip(v)

        strip(data["network"])
        changed = True
    if changed:
        p.write_text(
            yaml.safe_dump(data, sort_keys=True, allow_unicode=True),
            encoding="utf-8",
        )
        yaml_fix = "FIXED"

# Ops idempotency: guard duplicate 'http:' blocks (non-functional)

ops_fix = "PASS"
for p in MERGED.rglob("suggested_commands.conf"):
    txt = p.read_text(encoding="utf-8")
    if "tee -a" in txt:
        txt = re.sub(r"tee -a", 'grep -qxF "${LINE}" FILE || tee -a', txt)
        p.write_text(txt, encoding="utf-8")
        ops_fix = "FIXED"

# Relationship graph (VLAN 1 only; untagged_on ports 1–24)

graph = {
    "nodes": [
        {
            "id": "device:switch-1",
            "type": "device",
            "name": "netgear_gs724t_v3",
        },
        {
            "id": "vlan:1",
            "type": "vlan",
            "name": "default",
            "cidr": "192.168.0.0/24",
            "role": "mgmt",
        },
    ]
    + [
        {"id": f"port:{i}", "type": "port", "name": f"port{i}"}
        for i in range(1, 25)
    ],
    "edges": [{"type": "managed_by", "from": "device:switch-1", "to": "vlan:1"}]
    + [
        {"type": "untagged_on", "from": "vlan:1", "to": f"port:{i}"}
        for i in range(1, 25)
    ],
}
(GRAPH / "relationships.graph.json").write_text(
    json.dumps(graph, indent=2), encoding="utf-8"
)
(NOTES / "RELATIONSHIPS_NOTES.md").write_text(
    "# Relationships Notesnn- VLAN 1 untagged on ports 1–24.n- No tagged VLANs in this release.n",
    encoding="utf-8",
)

# Family normalization & property-hash


def canon_bytes(path: Path):
    t = path.suffix.lower()
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return path.read_bytes()
    txt = re.sub(r"[ t]+(r?n)", r"1", txt).replace("rn", "n").replace("r", "n")
    if t in (".yaml", ".yml"):
        obj = yaml.safe_load(txt)
        txt = yaml.safe_dump(obj, sort_keys=True, allow_unicode=True)
    elif t == ".json":
        obj = json.loads(txt)
        txt = json.dumps(
            obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )

    # INI/CONF/MD/CSV just normalized spacing/newlines

    if not txt.endswith("n"):
        txt += "n"
    return txt.encode("utf-8")


h = hashlib.sha256()
manifest = []
for path in sorted(OUT_DIR.rglob("*")):
    if path.is_dir():
        continue
    rel = path.relative_to(OUT_DIR)
    if rel.parts[0] == ".work":
        continue
    b = canon_bytes(path)
    path.write_bytes(b)
    dig = hashlib.sha256(b).hexdigest()
    manifest.append((str(rel), dig))
    h.update(b)

(OUT_DIR / "manifest.sha256").write_text(
    "n".join(f"{d}  {p}" for p, d in manifest) + "n", encoding="utf-8"
)
(OUT_DIR / "property_hash.txt").write_text(
    h.hexdigest() + "n", encoding="utf-8"
)

# Export status line for orchestrator

print(
    json.dumps(
        {
            "yaml_audit_cidrs": yaml_fix,
            "ops_idempotency": ops_fix,
            "manifest_entries": len(manifest),
        },
        indent=2,
    )
)
