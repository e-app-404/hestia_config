
#!/usr/bin/env bash
set -euo pipefail

ROOT="${PWD}"
TS="$(date -u +%Y%m%d_%H%M%S)"
BUNDLE_DIR="${ROOT}/lineage_guardian_bundle_${TS}"

echo "[+] Creating bundle at ${BUNDLE_DIR}"
mkdir -p "${BUNDLE_DIR}"/{lineage_guardian,.vscode,prompts,config/snippets,tests,.artifacts}

# ---------------------------
# README
# ---------------------------
cat > "${BUNDLE_DIR}/README.md" <<'EOF'
# Hestia — Lineage Guardian (Copilot Bundle)

> Validate and correct entity lineage metadata across Home Assistant template YAML files.

## Quick Start

1. Merge `config/snippets/hestia.toml.patch` into your real config:
   `/config/hestia/config/system/hestia.toml`
2. (Optional) Create venv & install:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
````

3. Run the pipeline (dry-run safe):

   ```bash
   python lineage_guardian/graph_scanner.py --output ./.artifacts/graph.json --template-dir /config/domain/templates/ --verbose
   python lineage_guardian/lineage_validator.py --graph-file ./.artifacts/graph.json --output ./.artifacts/violations.json --verbose
   python lineage_guardian/lineage_corrector.py --violations-file ./.artifacts/violations.json --plan-dir ./.artifacts/_plan
   python lineage_guardian/graph_integrity_checker.py --graph-file ./.artifacts/graph.json --output ./.artifacts/integrity.json
   python lineage_guardian/lineage_report.py --graph ./.artifacts/graph.json --violations ./.artifacts/violations.json --integrity ./.artifacts/integrity.json --outdir ./.artifacts/report
   ```
4. Or in VSCode: **Terminal → Run Task → Lineage: Full Pipeline (dry-run)**

## What’s inside

* `lineage_guardian/` — modular components

  * `graph_scanner.py` (build graph)
  * `lineage_validator.py` (check vs declared metadata)
  * `lineage_corrector.py` (non-destructive plan; ruamel-based merge placeholder)
  * `graph_integrity_checker.py` (post-checks)
  * `lineage_report.py` (markdown + JSON summary)
  * `models.py`, `utils.py`, `lineage_guardian.py` (orchestrator)
* `.vscode/` — tasks & launch
* `prompts/COPILOT_GUIDE.md` — paste into Copilot Chat
* `config/snippets/hestia.toml.patch` — config extension

## Safety & Guardrails

* **Dry-run by default** (only writes plan files under `./.artifacts/_plan`)
* **Backups + atomic writes** (when you implement ruamel merges)
* **Scope validation** to `/config/domain/templates/` only
* Idempotent; no destructive edits.

EOF

# ---------------------------

# Copilot Prompt

# ---------------------------

cat > "${BUNDLE_DIR}/prompts/COPILOT_GUIDE.md" <<'EOF'

# Copilot Coaching Script — Hestia Lineage Guardian

You’re assisting on a modular YAML lineage tool. Expand parsers, harden regexes, and make the corrector safe and idempotent.

## Targets to read

* `lineage_guardian/utils.py` — regexes, helpers
* `lineage_guardian/models.py` — dataclasses
* `lineage_guardian/graph_scanner.py` — extract upstream refs & macros from Jinja in `state:` blocks
* `lineage_guardian/lineage_validator.py` — compute violations vs declared `attributes.upstream_sources`/`downstream_consumers`/`source_count`
* `lineage_guardian/lineage_corrector.py` — plan-only now; implement ruamel-based merges later (non-destructive, backup-first)
* `lineage_guardian/graph_integrity_checker.py` — bidirectional checks & health score
* `lineage_guardian/lineage_report.py` — markdown + JSON

## Parsing rules (strict)

* Extract **entity_ids** from:

  * `states('domain.object')`
  * `is_state('domain.object', 'on')`
  * `state_attr('domain.object','attr')`
  * Jinja lists: `{% set sources = [{'entity': 'binary_sensor.foo'}, ...] %}`
* Valid domains only: `binary_sensor,sensor,light,switch,automation,script,person,input_boolean,device_tracker`
* Capture macro includes: `{% from 'template.library.jinja' import ... %}` as **macro dependencies** (not counted in source_count).
* Ignore MQTT topics (`zigbee2mqtt/...`) — not HA entities.

## Corrector rules

* Never delete existing arrays; **merge** missing items.
* `source_count` must equal number of **entity IDs** in `upstream_sources` (exclude macros).
* Update `last_updated` (YYYY-MM-DD) only if upstream/downstream changed.
* If `ruamel.yaml` present, write in-place with backups (suffix `.lineage_backup_{ISO}`) using atomic replace. Else, write a plan patch into `./.artifacts/_plan/`.

## Deliverables

* All README commands should work.
* Tight unit tests for `utils.extract_entities_from_state_block`.
* Keep changes minimal and reversible.

EOF

# ---------------------------

# Config patch (TOML extension)

# ---------------------------

cat > "${BUNDLE_DIR}/config/snippets/hestia.toml.patch" <<'EOF'

# Merge this into /config/hestia/config/system/hestia.toml

[automation.lineage_guardian]
enabled = true
schedule_cron = "0 3 * * *"
verbose_logging = true
log_location = "/config/hestia/reports/{date}/lineage__{timestamp}__validation.log"

[automation.lineage_guardian.scanner]
template_directory = "/config/domain/templates/"
recursive = true
file_patterns = ["*.yaml", "*.yml"]
exclude_patterns = ["*_test.yaml", "*_backup.yaml"]
parse_macros = true
macro_files = ["template.library.jinja"]

[automation.lineage_guardian.validator]
enforce_bidirectional = true
allow_self_references = false
require_source_count = true
valid_domains = [
"binary_sensor","sensor","light","switch",
"automation","script","person","input_boolean","device_tracker"
]

[automation.lineage_guardian.corrector]
backup_before_modify = true
backup_suffix = ".lineage_backup"
atomic_writes = true
preserve_formatting = true
update_timestamp_field = "last_updated"
timestamp_format = "%Y-%m-%d"

[automation.lineage_guardian.integrity]
check_circular_dependencies = true
check_orphaned_entities = true
check_missing_references = true
check_duplicate_ids = true
health_score_threshold = 95.0

[automation.lineage_guardian.safety]
dry_run_default = true
scope_validation_required = true
allowed_paths = ["/config/domain/templates/"]
max_file_size_mb = 5
backup_retention_days = 30
EOF

# ---------------------------

# Python deps

# ---------------------------

cat > "${BUNDLE_DIR}/requirements.txt" <<'EOF'
ruamel.yaml>=0.18.6
pyyaml>=6.0.1
networkx>=3.2.1
EOF

cat > "${BUNDLE_DIR}/pyproject.toml" <<'EOF'
[build-system]
requires = ["setuptools>=67", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "hestia-lineage-guardian"
version = "0.1.0"
description = "Validate and correct lineage metadata across Home Assistant template YAMLs"
requires-python = ">=3.10"
dependencies = [
"ruamel.yaml>=0.18.6",
"pyyaml>=6.0.1",
"networkx>=3.2.1"
]
EOF

# ---------------------------

# VSCode tasks/launch

# ---------------------------

mkdir -p "${BUNDLE_DIR}/.vscode"
cat > "${BUNDLE_DIR}/.vscode/tasks.json" <<'EOF'
{
"version": "2.0.0",
"tasks": [
{
"label": "Lineage: Full Pipeline (dry-run)",
"type": "shell",
"command": "python lineage_guardian/lineage_guardian.py",
"problemMatcher": []
},
{
"label": "Lineage: Scanner",
"type": "shell",
"command": "python lineage_guardian/graph_scanner.py --output ./.artifacts/graph.json --template-dir /config/domain/templates/ --verbose",
"problemMatcher": []
}
]
}
EOF

cat > "${BUNDLE_DIR}/.vscode/launch.json" <<'EOF'
{
"version": "0.2.0",
"configurations": [
{
"name": "Lineage: Orchestrator",
"type": "python",
"request": "launch",
"program": "${workspaceFolder}/lineage_guardian/lineage_guardian.py",
"console": "integratedTerminal",
"args": []
}
]
}
EOF

# ---------------------------

# Code: models, utils, modules

# ---------------------------

cat > "${BUNDLE_DIR}/lineage_guardian/models.py" <<'EOF'
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class EntityNode:
entity_id: str
file_path: str
unique_id: Optional[str] = None
domain: Optional[str] = None
tier: Optional[str] = None
upstream_refs: List[str] = field(default_factory=list)
downstream_refs: List[str] = field(default_factory=list)
macro_imports: List[str] = field(default_factory=list)
attributes_declared_upstream: List[str] = field(default_factory=list)
attributes_declared_downstream: List[str] = field(default_factory=list)
source_count_declared: Optional[int] = None
EOF

cat > "${BUNDLE_DIR}/lineage_guardian/utils.py" <<'EOF'
import re, datetime, sys

VALID_DOMAINS = [
"binary_sensor","sensor","light","switch",
"automation","script","person","input_boolean","device_tracker"
]

RE_STATES      = re.compile(r"states(['"]([A-Za-z0-9_]+.[A-Za-z0-9_]+)['"])")
RE_STATE_ATTR  = re.compile(r"state_attr(['"]([A-Za-z0-9_]+.[A-Za-z0-9_]+)['"],\s*['"][^'^"]+['"])")
RE_IS_STATE    = re.compile(r"is_state(['"]([A-Za-z0-9_]+.[A-Za-z0-9_]+)['"],\s*['"][^'^"]+['"])")
RE_SOURCES     = re.compile(r"{%[\s]*set\s+sources\s*=\s*[(.*?)][\s%]*}", re.S)
RE_SOURCES_ENT = re.compile(r"'entity'\s*:\s*'([A-Za-z0-9_]+.[A-Za-z0-9_]+)'")
RE_MACRO       = re.compile(r"{%[\s]*from\s+'([^']+)'\s+import\s+[^%]+%}")

def is_valid_entity(eid: str) -> bool:
try:
d, _ = eid.split(".", 1)
return d in VALID_DOMAINS
except Exception:
return False

def extract_entities_from_state_block(txt: str):
if not isinstance(txt, str):
return [], []
ents=set(); macros=set()
for rx in (RE_STATES, RE_STATE_ATTR, RE_IS_STATE):
for m in rx.findall(txt):
if is_valid_entity(m): ents.add(m)
for blk in RE_SOURCES.findall(txt):
for m in RE_SOURCES_ENT.findall(blk):
if is_valid_entity(m): ents.add(m)
for m in RE_MACRO.findall(txt):
macros.add(m)
return sorted(ents), sorted(macros)

def today_iso_date() -> str:
return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def dbg(msg: str):
print(f"[DEBUG] {msg}", file=sys.stderr)
EOF

cat > "${BUNDLE_DIR}/lineage_guardian/graph_scanner.py" <<'EOF'
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
slug = str(name).lower().replace(" ","*").replace("-","*")
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

```
files = list_yaml_files(args.template_dir)
all_nodes=[]
for f in files:
    all_nodes += scan_file(f)
graph = {"nodes":[n.__dict__ for n in all_nodes], "meta":{"count":len(all_nodes)}}
os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
open(args.output,"w",encoding="utf-8").write(json.dumps(graph, indent=2))
print(f"[INFO] Scanned {len(files)} files → {len(all_nodes)} entities → {args.output}")
```

if **name** == "**main**":
main()
EOF

cat > "${BUNDLE_DIR}/lineage_guardian/lineage_validator.py" <<'EOF'
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

```
    exp_dn = sorted(set(n.downstream_refs))
    dec_dn = sorted(set(n.attributes_declared_downstream))
    miss_dn = [e for e in exp_dn if e not in dec_dn]
    if miss_dn:
        out.append({"violation_type":"MISSING_DOWNSTREAM","entity_id":n.entity_id,"file_path":n.file_path,"expected":exp_dn,"actual":dec_dn})

    if n.source_count_declared is not None:
        if int(n.source_count_declared) != len(exp_up):
            out.append({"violation_type":"COUNT_MISMATCH","entity_id":n.entity_id,"file_path":n.file_path,"expected":[str(len(exp_up))],"actual":[str(n.source_count_declared)]})
return out
```

def main():
ap = argparse.ArgumentParser()
ap.add_argument("--graph-file", required=True)
ap.add_argument("--output", required=True)
args = ap.parse_args()
nodes = load_graph(args.graph_file)
viols = compute_violations(nodes)
open(args.output, "w", encoding="utf-8").write(json.dumps(viols, indent=2))
print(f"[INFO] Violations written to {args.output} ({len(viols)} findings)")

if **name** == "**main**":
main()
EOF

cat > "${BUNDLE_DIR}/lineage_guardian/lineage_corrector.py" <<'EOF'
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
EOF

cat > "${BUNDLE_DIR}/lineage_guardian/graph_integrity_checker.py" <<'EOF'
import json, argparse

def main():
ap = argparse.ArgumentParser()
ap.add_argument("--graph-file", required=True)
ap.add_argument("--output", required=True)
args = ap.parse_args()

```
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
```

if **name** == "**main**":
main()
EOF

cat > "${BUNDLE_DIR}/lineage_guardian/lineage_report.py" <<'EOF'
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
EOF

cat > "${BUNDLE_DIR}/lineage_guardian/lineage_guardian.py" <<'EOF'
import os, sys

ART = ".artifacts"
os.makedirs(ART, exist_ok=True)
graph = os.path.join(ART, "graph.json")
viol  = os.path.join(ART, "violations.json")
integ = os.path.join(ART, "integrity.json")
report= os.path.join(ART, "report")

os.system(f"python lineage_guardian/graph_scanner.py --template-dir /config/domain/templates/ --output {graph} --verbose")
os.system(f"python lineage_guardian/lineage_validator.py --graph-file {graph} --output {viol}")
os.system(f"python lineage_guardian/lineage_corrector.py --violations-file {viol} --plan-dir ./.artifacts/_plan")
os.system(f"python lineage_guardian/graph_integrity_checker.py --graph-file {graph} --output {integ}")
os.system(f"python lineage_guardian/lineage_report.py --graph {graph} --violations {viol} --integrity {integ} --outdir {report}")

print('[INFO] Pipeline complete. See ./.artifacts/')
EOF

# ---------------------------

# Tiny test placeholder

# ---------------------------

cat > "${BUNDLE_DIR}/tests/test_utils_smoke.py" <<'EOF'
from lineage_guardian.utils import extract_entities_from_state_block

def test_extract_basic():
txt = "states('binary_sensor.foo_bar') and is_state('person.evert','home')"
ents, macros = extract_entities_from_state_block(txt)
assert 'binary_sensor.foo_bar' in ents
assert 'person.evert' in ents
EOF

echo
echo "[✓] Bundle created."
echo "Open this folder in VSCode:"
echo "  ${BUNDLE_DIR}"
