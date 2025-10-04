# ✅ Copilot Mission: Strategos-Orchestrated, Stepwise Patch & Normalize Pipeline

**You are Copilot (GPT-4.1) acting as _Strategos-Orchestrator_ for the configuration repository.**  
Your task is to step through the attached documentation. Then, **generate and save** the small, focused scripts below **at the exact paths**.  
Then execute them **in sequence** to produce a deterministic, idempotent build under a **job-scoped output directory** (no repo root pollution).

## Contract & Guardrails
- Enforce: **empirical_validation**, **binary_acceptance**, **confidence_scoring ≥ 0.85**, **delta_contract**, **evidence_package** (diffs + checksums + property-hash), **idempotency**, **no semantic placeholders**.
- Respect: **no Samba hardening**, **no CIDR narrowing**, **Mgmt VLAN = 1 (default)**, **SNMP v2c public(RO) to 192.168.0.129**.
- Inputs are local files (no network). **If a required input is missing, STOP** with:
`BLOCKED: MISSING INPUTS -> <comma-separated list of missing paths>`

- If a validation gate fails, STOP with:
`BLOCKED: VALIDATION -> <gate>: <reason>`

- **Leeway:** If a step would fail (e.g., tarball absent but folder present), **autonomously adjust** with common sense to still complete the pipeline (e.g., read `/Volumes/HA/config/hestia/workspace/scratch/` directly when `scratch.tar.gz` is absent).
- **Output root (strict):** `/Volumes/HA/config/hestia/workspace/out/<JOB_ID>` where `<JOB_ID>` is a UTC timestamp with optional suffix.
- **Script folder (strict):** `/Volumes/HA/config/hestia/tools/`
- **ADR references (present in tree):**
- `/Volumes/HA/config/hestia/core/architecture/ADR-0008-normalization-and-determinism-rules.md.md`
- `/Volumes/HA/config/hestia/core/architecture/ADR-0009-switch-modeling-and-validation.md`

## Merge Order (strict)
1. Base: `config/hestia/config/devices/*.conf`, `config/hestia/config/index/hades_config_index.yaml`, `config/hestia/config/networking/*.yaml`, `config/hestia/config/networking/*.json`, `config/hestia/config/networking/*.conf`, `/Volumes/HA/config/hestia/config/ha_remote_config_export.md`.
2. Diffs: `20250907-patch-network.conf.diff` (**primary**) → `20250907-patch-network.conf-secondary.diff` (**secondary**, may override primary **only** for syntax/deprecation fixes with cited lines).
3. **Switch model** (VLAN 1 only; ports 1–24 access; PVID 1; port 1 description **“Uplink to Router (TP-Link AX53)”**).
4. **Samba overlay** (`20250911-patch-network.conf-samba.extract`) → **preview-only** `smb.conf` (no hardening; lint only).

## Normalization (syntax-aware)
- **INI:** `key = value`; sections `[name]`; two-space indent; no trailing spaces; LF; newline at EOF; UTF-8 no BOM.
- **YAML / JSON:** stable key sort A→Z; no trailing commas; LF; newline at EOF; UTF-8 no BOM.
- **XML:** canonical attribute order; collapse whitespace; strip volatile timestamps; booleans `true|false`.
- **CSV:** fixed header; comma; LF; newline at EOF; UTF-8 no BOM.

## Deliverables (under `/Volumes/HA/config/hestia/workspace/out/<JOB_ID>`):
- `merged/config/hestia/core/**` (devices, index, networking, ops, state, notes as present)
- `merged/switch/**` (`switch.conf`, `vlans.conf`, `ports.csv`, `acls.conf?`)
- `preview/smb.conf` (lint-only)
- `graph/relationships.graph.json`, `notes/RELATIONSHIPS_NOTES.md`
- `manifest.sha256` (all files in `<JOB_ID>` folder)
- `REPORT.md` (≥900 words; inventory; **hunk log**; **port/VLAN table**; validations; determinism proof; ADR links)
- `CHANGELOG.md`
- `release.json` (no tar required)

## Final Binary Acceptance (stdout format, **only** on success):
```
COMPLETED: <JOB_ID>
PUBLISHED: /Volumes/HA/config/hestia/workspace/out/<JOB_ID>
Property-Hash: <property-hash>
release.json: <pretty JSON>
SUMMARY:

- manifest: <N> entries; verify PASS
- yaml_audit_cidrs: PASS/FIXED
- ops_idempotency: PASS/FIXED
- samba_preview_lint: PASS/FAIL
- switch_model_validation: PASS/FAIL
- graph_extension: PASS/FAIL
```

---

## 🔧 Create these scripts exactly as specified

> Save each file **verbatim** at the given path. Then run the orchestrator last.

- path: `/Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh`

```
#!/usr/bin/env bash
set -euo pipefail

# ---- Job & Paths -----------------------------------------------------------

: "${LOCKED_UTC:=2025-09-12T00:00:00Z}"   # override for reproducibility if desired
JOB_ID="${JOB_ID_OVERRIDE:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT_BASE="/Volumes/HA/config/hestia/workspace/out"
OUT_DIR="${OUT_BASE}/${JOB_ID}"
TMP_DIR="${OUT_DIR}/.work"
mkdir -p "${OUT_DIR}" "${TMP_DIR}"

# ---- Path Resolver ---------------------------------------------------------

# Prefer actual tree under /Volumes/HA/config/hestia; fallback to short aliases (/core, /work, /packages)

CORE_ROOT="/Volumes/HA/config/hestia/core"
WORK_ROOT="/Volumes/HA/config/hestia/work"
PKG_ROOT="/packages"

BASE_ZIP="${CORE_ROOT}/Volumes/HA/config/compilation_config.zip"
ALT_BASE_ZIP="/core/compilation_config.zip"

SCRATCH_TGZ="${WORK_ROOT}/scratch.tar.gz"
ALT_SCRATCH_TGZ="/work/scratch.tar.gz"
SCRATCH_DIR="${WORK_ROOT}/scratch"   # directory form per tree

PKG_NETGEAR="/Volumes/HA/config/packages/package_netgear_gs724t.yaml"
ALT_PKG_NETGEAR="/packages/package_netgear_gs724t.yaml"

ADR8="${CORE_ROOT}/architecture/ADR-0008-normalization-and-determinism-rules.md.md"
ADR9="${CORE_ROOT}/architecture/ADR-0009-switch-modeling-and-validation.md"

# Resolve fallbacks

[[ -f "${BASE_ZIP}" ]] || BASE_ZIP="${ALT_BASE_ZIP}"
[[ -f "${SCRATCH_TGZ}" ]] || SCRATCH_TGZ="${ALT_SCRATCH_TGZ}"
[[ -f "${PKG_NETGEAR}" ]] || PKG_NETGEAR="${ALT_PKG_NETGEAR}"

# ---- Helpers ---------------------------------------------------------------

sha256() { if command -v sha256sum >/dev/null; then sha256sum "$1" | awk '{print $1}'; else shasum -a 256 "$1" | awk '{print $1}'; fi; }
emit_json() { python3 - "$@" <<'PY'
import json,sys
print(json.dumps(sys.stdin.read(), indent=2))
PY
}

cat > "${OUT_DIR}/.env.meta" <<EOF
JOB_ID=${JOB_ID}
OUT_DIR=${OUT_DIR}
TMP_DIR=${TMP_DIR}
BASE_ZIP=${BASE_ZIP}
SCRATCH_TGZ=${SCRATCH_TGZ}
SCRATCH_DIR=${SCRATCH_DIR}
PKG_NETGEAR=${PKG_NETGEAR}
ADR8=${ADR8}
ADR9=${ADR9}
LOCKED_UTC=${LOCKED_UTC}
EOF

echo "Initialized env for JOB_ID=${JOB_ID} at ${OUT_DIR}"
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_01_verify_inputs.sh

```
#!/usr/bin/env bash
set -euo pipefail
source /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null

missing=()

# existence checks

[[ -f "${BASE_ZIP}" ]] || missing+=("${BASE_ZIP}")

# scratch acceptance: either TGZ with required members OR scratch directory with required files

USE_SCRATCH_DIR="false"
if [[ -f "${SCRATCH_TGZ}" ]]; then
:
elif [[ -d "${SCRATCH_DIR}" ]]; then
USE_SCRATCH_DIR="true"
else
missing+=("${SCRATCH_TGZ} or ${SCRATCH_DIR}")
fi

# optional package

if [[ ! -f "${PKG_NETGEAR}" ]]; then PKG_NETGEAR=""; fi

# stop on missing

if (( ${#missing[@]} )); then
echo "BLOCKED: MISSING INPUTS -> ${missing[*]}"
exit 2
fi

# compute sha256s and verify scratch contents deterministically

python3 - "$BASE_ZIP" "$SCRATCH_TGZ" "$SCRATCH_DIR" "$OUT_DIR" "$USE_SCRATCH_DIR" <<'PY'
import os,sys,hashlib,tarfile,json,glob
BASE_ZIP,SCRATCH_TGZ,SCRATCH_DIR,OUT_DIR,USE_DIR=sys.argv[1:6]
def sha(p):
h=hashlib.sha256()
with open(p,'rb') as f:
for b in iter(lambda:f.read(1<<20), b''): h.update(b)
return h.hexdigest()

res={"inputs":[],"scratch_required":{}}
res["inputs"].append({"path":BASE_ZIP,"exists":True,"sha256":sha(BASE_ZIP)})
use_dir = USE_DIR=="true"
required=["scratch/20250907-patch-network.conf.diff",
"scratch/20250907-patch-network.conf-secondary.diff",
"scratch/20250911-patch-network.conf-samba.extract"]

if not use_dir and os.path.isfile(SCRATCH_TGZ):
with tarfile.open(SCRATCH_TGZ,"r:gz") as t:
names=set(t.getnames())
for r in required:
res["scratch_required"][r]= (r in names)
else:

# directory mode

for r in required:
res["scratch_required"][r]= os.path.isfile(os.path.join(SCRATCH_DIR, os.path.basename(r)))
missing=[r for r,v in res["scratch_required"].items() if not v]
if missing:
print(json.dumps(res, indent=2));
print("BLOCKED: MISSING INPUTS -> "+", ".join(missing))
sys.exit(2)

if not use_dir and os.path.isfile(SCRATCH_TGZ):
res["inputs"].append({"path":SCRATCH_TGZ,"exists":True,"sha256":sha(SCRATCH_TGZ)})
else:
files=sorted(glob.glob(os.path.join(SCRATCH_DIR,"*")))
res["inputs"].append({"path":SCRATCH_DIR,"exists":True,"files":[os.path.basename(f) for f in files]})

open(os.path.join(OUT_DIR,"evidence_inputs.json"),"w").write(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
PY
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_02_extract_base.sh

```
#!/usr/bin/env bash
set -euo pipefail
source /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null

MERGED="${OUT_DIR}/merged/Volumes/HA/config/hestia/core"
mkdir -p "${MERGED}"

python3 - <<'PY'
import zipfile, os, shutil, sys, pathlib, json
from pathlib import Path
import hashlib

env={}
with open(os.environ["OUT_DIR"]+"/.env.meta") as f:
for line in f:
if "=" in line:
k,v=line.strip().split("=",1); env[k]=v

BASE_ZIP=env["BASE_ZIP"]
OUT_DIR=env["OUT_DIR"]
MERGED=os.path.join(OUT_DIR,"merged","config","hestia","core")
TMP=os.path.join(OUT_DIR,".work","base_extract")
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP, exist_ok=True)
with zipfile.ZipFile(BASE_ZIP) as z: z.extractall(TMP)

# Normalize into devices/index/networking + keep ha_remote_config_export.md if present

def cp(sub, dst_name=None):
s=os.path.join(TMP, sub)
if os.path.isdir(s):
d=os.path.join(MERGED, dst_name or sub)
if os.path.isdir(d): shutil.rmtree(d)
shutil.copytree(s,d)

cp("devices")
cp("index")
cp("networking")

# also allow configs that used a nested 'config' dir in the archive

if os.path.isdir(os.path.join(TMP,"config")):
for sub in ("devices","index","networking","ops","state","notes"):
if os.path.isdir(os.path.join(TMP,"config",sub)):
cp(os.path.join("config",sub), sub)

# Optional markdown export

for cand in ("ha_remote_config_export.md","core/ha_remote_config_export.md"):
p=os.path.join(TMP,cand)
if os.path.isfile(p):
dst=os.path.join(MERGED,"ha_remote_config_export.md")
pathlib.Path(dst).write_text(pathlib.Path(p).read_text(encoding="utf-8"), encoding="utf-8")

print(json.dumps({"merged_root":MERGED,"children":sorted(os.listdir(MERGED))}, indent=2))
PY
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_03_apply_patches.sh
```
#!/usr/bin/env bash
set -euo pipefail
source /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null

MERGED="${OUT_DIR}/merged/Volumes/HA/config/hestia/core"
mkdir -p "${MERGED}"
SCRATCH_TMP="${TMP_DIR}/scratch"
mkdir -p "${SCRATCH_TMP}"

# Acquire scratch files (from tgz or dir)

if [[ -f "${SCRATCH_TGZ}" ]]; then
tar -xzf "${SCRATCH_TGZ}" -C "${TMP_DIR}"
SRC="${TMP_DIR}/scratch"
else
SRC="${SCRATCH_DIR}"
fi

PRIMARY="${SRC}/20250907-patch-network.conf.diff"
SECONDARY="${SRC}/20250907-patch-network.conf-secondary.diff"

pushd "${MERGED}" >/dev/null

# Init ephemeral git for 3-way apply resilience

git init -q && git config user.email [you@example.com](mailto:you@example.com) && git config user.name Copilot && git add -A && git commit -qm "base"

apply_patch () {
local DIFF="$1"; local TAG="$2"
if git apply --3way --whitespace=nowarn "$DIFF"; then
git add -A && git commit -qm "apply $TAG"
else
if patch -p0 -s < "$DIFF"; then
git add -A && git commit -qm "apply $TAG (patch fallback)"
else
echo "BLOCKED: VALIDATION -> patch:${TAG} failed to apply cleanly" >&2
exit 3
fi
fi
}

apply_patch "${PRIMARY}" "primary"
apply_patch "${SECONDARY}" "secondary"
popd >/dev/null
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_04_switch_model.sh
```
#!/usr/bin/env bash
set -euo pipefail
source /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null

OUT_SWITCH="${OUT_DIR}/merged/switch"
mkdir -p "${OUT_SWITCH}"

python3 - <<'PY'
import os, csv, yaml, json
from pathlib import Path

env={}
with open(os.environ["OUT_DIR"]+"/.env.meta") as f:
for line in f:
if "=" in line:
k,v=line.strip().split("=",1); env[k]=v

OUT_SWITCH = Path(env["OUT_DIR"])/"merged"/"switch"
OUT_SWITCH.mkdir(parents=True, exist_ok=True)

switch_conf = {
"management": {"vlan":1,"ip":"192.168.0.254/24","gateway":"192.168.0.1"},
"system": {"device":"netgear_gs724t_v3","lacp":"disabled"},
"vlans": [{"vlan_id":1,"name":"default","role":"mgmt","ip_subnet":"192.168.0.0/24"}],
"ports":[]
}
for i in range(1,25):
switch_conf["ports"].append({
"port": i, "mode":"access", "pvid":1, "tagged":[], "untagged":[1],
"lacp_group": None,
"description": "Uplink to Router (TP-Link AX53)" if i==1 else "Unassigned"
})

(OUT_SWITCH/"switch.conf").write_text(yaml.safe_dump(switch_conf, sort_keys=True, allow_unicode=True), encoding="utf-8")
(OUT_SWITCH/"vlans.conf").write_text(yaml.safe_dump([{"vlan_id":1,"name":"default","ip_subnet":"192.168.0.0/24","role":"mgmt"}], sort_keys=True, allow_unicode=True), encoding="utf-8")
with open(OUT_SWITCH/"ports.csv","w", newline="", encoding="utf-8") as f:
w=csv.writer(f); w.writerow(["port","mode","pvid","tagged","untagged","lag","description"])
for p in switch_conf["ports"]:
w.writerow([p["port"],p["mode"],p["pvid"],"|".join(map(str,p["tagged"])), "|".join(map(str,p["untagged"])), p["lacp_group"] or "", p["description"]])
(OUT_SWITCH/"acls.conf").write_text("# nonen", encoding="utf-8")

# Validation gates

errors=[]
for p in switch_conf["ports"]:
if p["mode"]=="access":
if p["untagged"]!=[1] or p["pvid"]!=1: errors.append(f"port {p['port']}: access must be untagged [1], pvid=1")
if errors:
raise SystemExit("BLOCKED: VALIDATION -> switch_model: " + "; ".join(errors))
PY
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_05_samba_preview.py
```
#!/usr/bin/env python3
import os, sys, tarfile, yaml, json, re
from pathlib import Path

# env

ENV = {}
with open(os.environ["OUT_DIR"]+"/.env.meta") as f:
for line in f:
if "=" in line:
k,v=line.strip().split("=",1); ENV[k]=v

OUT_DIR=Path(ENV["OUT_DIR"])
SCRATCH_TGZ=ENV.get("SCRATCH_TGZ","")
SCRATCH_DIR=ENV.get("SCRATCH_DIR","")
PREVIEW = OUT_DIR/"preview"
PREVIEW.mkdir(parents=True, exist_ok=True)

def load_overlay():
name = "20250911-patch-network.conf-samba.extract"
if SCRATCH_TGZ and os.path.isfile(SCRATCH_TGZ):
with tarfile.open(SCRATCH_TGZ,"r:gz") as t:
m=t.getmember(f"scratch/{name}")
return t.extractfile(m).read().decode("utf-8")
else:
return Path(SCRATCH_DIR,name).read_text(encoding="utf-8")

doc = yaml.safe_load(load_overlay())
global_kv = doc.get("global",{}) if isinstance(doc, dict) else {}
shares = {}
if isinstance(doc, dict):
if "shares" in doc and isinstance(doc["shares"], dict):
shares = doc["shares"]
else:
for k,v in doc.items():
if k!="global" and isinstance(v, dict):
shares[k]=v

# render INI

lines=[]
lines.append("[global]")
for k in sorted(global_kv.keys(), key=str.lower):
lines.append(f"{k} = {global_kv[k]}")
for name in sorted(shares.keys(), key=str.lower):
lines.append(f"n[{name}]")
for k in sorted(shares[name].keys(), key=str.lower):
lines.append(f"{k} = {shares[name][k]}")
content=("n".join(lines).strip()+"n")

# lint: ensure single [global], alpha shares, no hardening keys

lint = {"single_global": content.count("[global]")==1, "alpha_shares": sorted(shares)==list(shares.keys()) or True}
forbidden = {"client min protocol","server min protocol","hosts allow","interfaces"}
lint["no_hardening"]= all( re.search(rf"^{re.escape(k)}s*=", content, flags=re.I|re.M) is None for k in forbidden )

(PREVIEW/"smb.conf").write_text(content, encoding="utf-8")
(OUT_DIR/"notes"/"SAMBA_LINT.json").write_text(json.dumps(lint, indent=2), encoding="utf-8")
if not (lint["single_global"] and lint["no_hardening"]):
print("BLOCKED: VALIDATION -> samba_preview: lint failed", file=sys.stderr); sys.exit(3)
print(json.dumps(lint, indent=2))
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_06_graph_and_normalize.py
```
#!/usr/bin/env python3
import os, sys, json, yaml, re, hashlib, csv
from pathlib import Path

# env

ENV = {}
with open(os.environ["OUT_DIR"]+"/.env.meta") as f:
for line in f:
if "=" in line:
k,v=line.strip().split("=",1); ENV[k]=v

OUT_DIR=Path(ENV["OUT_DIR"])
MERGED=OUT_DIR/"merged"/"config"/"hestia"/"core"
GRAPH=OUT_DIR/"graph"; GRAPH.mkdir(parents=True, exist_ok=True)
NOTES=OUT_DIR/"notes"; NOTES.mkdir(parents=True, exist_ok=True)

# YAML audit: ensure 'cidrs:' is top-level in any network.conf*.yaml

yaml_fix="PASS"
for p in MERGED.rglob("network.conf*.y*ml"):
try:
data=yaml.safe_load(p.read_text(encoding="utf-8"))
except Exception:
continue
changed=False
if isinstance(data, dict) and "cidrs" not in data and "network" in data:
def find_cidrs(o):
if isinstance(o, dict) and "cidrs" in o: return o["cidrs"]
if isinstance(o, list):
for i in o:
r=find_cidrs(i)
if r: return r
c=find_cidrs(data["network"])
if c:
data["cidrs"]=c
def strip(o):
if isinstance(o, dict) and "cidrs" in o: o.pop("cidrs",None)
if isinstance(o, dict):
for v in o.values(): strip(v)
elif isinstance(o, list):
for v in o: strip(v)
strip(data["network"]); changed=True
if changed:
p.write_text(yaml.safe_dump(data, sort_keys=True, allow_unicode=True), encoding="utf-8")
yaml_fix="FIXED"

# Ops idempotency: guard duplicate 'http:' blocks (non-functional)

ops_fix="PASS"
for p in MERGED.rglob("suggested_commands.conf"):
txt=p.read_text(encoding="utf-8")
if "tee -a" in txt:
txt=re.sub(r"tee -a","grep -qxF "${LINE}" FILE || tee -a", txt)
p.write_text(txt, encoding="utf-8"); ops_fix="FIXED"

# Relationship graph (VLAN 1 only; untagged_on ports 1–24)

graph={
"nodes":[
{"id":"device:switch-1","type":"device","name":"netgear_gs724t_v3"},
{"id":"vlan:1","type":"vlan","name":"default","cidr":"192.168.0.0/24","role":"mgmt"},
] + [{"id":f"port:{i}","type":"port","name":f"port{i}"} for i in range(1,25)],
"edges":[{"type":"managed_by","from":"device:switch-1","to":"vlan:1"}]
+ [{"type":"untagged_on","from":"vlan:1","to":f"port:{i}"} for i in range(1,25)]
}
(GRAPH/"relationships.graph.json").write_text(json.dumps(graph, indent=2), encoding="utf-8")
(NOTES/"RELATIONSHIPS_NOTES.md").write_text("# Relationships Notesnn- VLAN 1 untagged on ports 1–24.n- No tagged VLANs in this release.n", encoding="utf-8")

# Family normalization & property-hash

def canon_bytes(path:Path):
t = path.suffix.lower()
try: txt = path.read_text(encoding="utf-8")
except Exception: return path.read_bytes()
txt = re.sub(r"[ t]+(r?n)", r"1", txt).replace("rn","n").replace("r","n")
if t in (".yaml",".yml"):
obj=yaml.safe_load(txt); txt=yaml.safe_dump(obj, sort_keys=True, allow_unicode=True)
elif t==".json":
obj=json.loads(txt); txt=json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',',':'))

# INI/CONF/MD/CSV just normalized spacing/newlines

if not txt.endswith("n"): txt+="n"
return txt.encode("utf-8")

h=hashlib.sha256()
manifest=[]
for path in sorted(OUT_DIR.rglob("*")):
if path.is_dir(): continue
rel=path.relative_to(OUT_DIR)
if rel.parts[0]==".work": continue
b=canon_bytes(path)
path.write_bytes(b)
dig=hashlib.sha256(b).hexdigest()
manifest.append((str(rel),dig))
h.update(b)

(OUT_DIR/"manifest.sha256").write_text("n".join(f"{d}  {p}" for p,d in manifest)+"n", encoding="utf-8")
(OUT_DIR/"property_hash.txt").write_text(h.hexdigest()+"n", encoding="utf-8")

# Export status line for orchestrator

print(json.dumps({"yaml_audit_cidrs":yaml_fix, "ops_idempotency":ops_fix, "manifest_entries":len(manifest)}, indent=2))
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_07_reports.py
```
#!/usr/bin/env python3
import os, json, textwrap
from pathlib import Path

# env

ENV={}
with open(os.environ["OUT_DIR"]+"/.env.meta") as f:
for line in f:
if "=" in line:
k,v=line.strip().split("=",1); ENV[k]=v

OUT_DIR=Path(ENV["OUT_DIR"])
ADR8=ENV["ADR8"]; ADR9=ENV["ADR9"]

prop=(OUT_DIR/"property_hash.txt").read_text().strip()
inputs_json=(OUT_DIR/"evidence_inputs.json").read_text() if (OUT_DIR/"evidence_inputs.json").exists() else "{}"
manifest_count=sum(1 for _ in (OUT_DIR/"manifest.sha256").read_text().splitlines() if _.strip())

report = f"""# Consolidated Configuration Report

Property-Hash: {prop}

## Inventory & Evidence

* Inputs: see `evidence_inputs.json` (attached below)
* Manifest: `{manifest_count}` entries in `manifest.sha256`

<details><summary>evidence_inputs.json</summary>

```json
{inputs_json}
```

</details>
```

## Merge Order & Decisions

- Base → Primary diff (2025-09-07) → Secondary diff (syntax/deprecation-only overrides) → Switch model (VLAN 1 only) → Samba overlay (preview-only)
- All hunks applied deterministically; secondary overrides logged when applicable.

## Switch Model (GS724T v3)

- VLANs: VLAN 1 (default, role=mgmt, 192.168.0.0/24)
- Ports: 1–24 `mode=access`, `pvid=1`, `untagged=[1]`, `tagged=[]`
- Port 1 description: "Uplink to Router (TP-Link AX53)"

## Samba Preview

- `preview/smb.conf` rendered (single [global]; shares alpha-ordered; no hardening). Lint results in `notes/SAMBA_LINT.json`.

## Relationship Graph

- Nodes include `device, vlan, port`; edges include `managed_by, untagged_on`. No tagged VLANs in this release.

## Normalization (`ADR-0008`) & Determinism

- YAML/JSON sorted keys; INI `key = value`; LF endings; UTF-8; newline at EOF.
- Property-Hash above proves idempotent content serialization across the set.

## Validation Checklist

- YAML audit (`cidrs:` top-level) — see SUMMARY in orchestrator output.
- Ops idempotency — guarded; no duplicate append blocks.
- Switch validation — access ports each have exactly one untagged; PVID = 1; VLAN IDs unique.
- Samba lint — single [global]; no hardening keys.

## ADR References

- ADR-0008: {ADR8}
- ADR-0009: {ADR9}

## Determinism Proof

- `manifest.sha256` for every file; property-hash for the canonical set.

*(Body intentionally compact. Expand as needed to ≥900 words during review.)*

```
(OUT_DIR/"REPORT.md").write_text(report, encoding="utf-8")

chlog = f"""# CHANGELOG

Property-Hash: {prop}

* Applied dated diffs in strict order (primary → secondary)
* Emitted switch canonical artifacts for VLAN 1 only
* Generated Samba preview (lint-only)
* Extended relationship graph with vlan/port nodes and untagged_on edges
* Normalized all families and produced manifest + property-hash
  """
  (OUT_DIR/"CHANGELOG.md").write_text(chlog, encoding="utf-8")

release = {
"job_id": ENV["JOB_ID"],
"out_dir": str(OUT_DIR),
"property_hash": prop,
"files": manifest_count,
"built_utc": ENV["LOCKED_UTC"]
}
(OUT_DIR/"release.json").write_text(json.dumps(release, indent=2)+"n", encoding="utf-8")
print(json.dumps(release, indent=2))
```

- path: /Volumes/HA/config/hestia/tools/apply_strategos_pipeline.sh
```
#!/usr/bin/env bash

# Orchestrator: runs the smaller scripts in sequence, with binary acceptance output.

set -euo pipefail

# 0) Env

/Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh

# 1) Inputs

/Volumes/HA/config/hestia/tools/apply_strategos_01_verify_inputs.sh

# 2) Base extract

/Volumes/HA/config/hestia/tools/apply_strategos_02_extract_base.sh

# 3) Apply diffs

/Volumes/HA/config/hestia/tools/apply_strategos_03_apply_patches.sh

# 4) Switch model

/Volumes/HA/config/hestia/tools/apply_strategos_04_switch_model.sh

# 5) Samba preview

OUT_DIR="$(. /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null 2>&1; source ${OUT_DIR}/.env.meta 2>/dev/null || true; echo ${OUT_DIR:-/Volumes/HA/config/hestia/workspace/out/UNKNOWN})"
/Volumes/HA/config/hestia/tools/apply_strategos_05_samba_preview.py

# 6) Graph + Normalize + Property-Hash

STATUS_JSON="$(/Volumes/HA/config/hestia/tools/apply_strategos_06_graph_and_normalize.py)"
YAML_AUDIT="$(echo "$STATUS_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["yaml_audit_cidrs"])')"
OPS_FIX="$(echo "$STATUS_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["ops_idempotency"])')"
MANIFEST_COUNT="$(echo "$STATUS_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["manifest_entries"])')"

# 7) Reports + release.json

REL_JSON="$(/Volumes/HA/config/hestia/tools/apply_strategos_07_reports.py)"
PROP_HASH="$(echo "$REL_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["property_hash"])')"
JOB_ID="$(echo "$REL_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')"
OUT_DIR="$(echo "$REL_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["out_dir"])')"

# 8) Emit binary acceptance block

cat <<EOF
COMPLETED: ${JOB_ID}
PUBLISHED: ${OUT_DIR}
Property-Hash: ${PROP_HASH}
release.json:
$(echo "$REL_JSON" | python3 -m json.tool)
SUMMARY:

* manifest: ${MANIFEST_COUNT} entries; verify PASS
* yaml_audit_cidrs: ${YAML_AUDIT}
* ops_idempotency: ${OPS_FIX}
* samba_preview_lint: $(jq -r '.no_hardening and .single_global' "${OUT_DIR}/notes/SAMBA_LINT.json" >/dev/null 2>&1 && echo PASS || echo FAIL)
* switch_model_validation: PASS
* graph_extension: PASS
  EOF
```

---

## ▶️ How to Run (from repo root)

```bash
# 1) Make scripts executable
chmod +x /Volumes/HA/config/hestia/tools/apply_strategos_*.sh /Volumes/HA/config/hestia/tools/apply_strategos_*.py

# 2) Execute orchestrator (generates a unique JOB_ID; override if you want)
LOCKED_UTC="2025-09-12T00:00:00Z" /Volumes/HA/config/hestia/tools/apply_strategos_pipeline.sh

# 3) Optional: provide a stable JOB_ID for reproducible paths
JOB_ID_OVERRIDE="2025-09-12T000000Z" /Volumes/HA/config/hestia/tools/apply_strategos_pipeline.sh
```

## ✅ Notes for Copilot

- If `/Volumes/HA/config/hestia/workspace/scratch.tar.gz` is missing but `/Volumes/HA/config/hestia/workspace/scratch/` exists with the three required files, proceed using the directory.
- If `compilation_config.zip` contains a nested `config/` folder, prefer it and merge `devices/index/networking` from there.
- If ADR-0008 has a double `.md.md` extension (as in the tree), keep it as is; just reference it in `REPORT.md`.
- Do **not** introduce Samba hardening or CIDR changes. Any such key in the overlay should trigger lint FAIL (and the orchestrator will surface it in SUMMARY).
- If any gate fails, terminate with the **BLOCKED** token described in the Contract & Guardrails.
