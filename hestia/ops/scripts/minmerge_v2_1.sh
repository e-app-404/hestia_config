#!/usr/bin/env bash
# KYBERNETES — MINIMAL OVERLAY MERGE INTO v2.1 (EXECUTE EXACTLY)
# Purpose: apply overlay YAMLs to v2.1/system_instruction.yaml with basic gates only.

set -euo pipefail
CORE_PATH="${CORE_PATH:-hestia/core/governance/system_instruction/v2.1/system_instruction.yaml}"
test -f "$CORE_PATH" || { echo "ERR: CORE_PATH not found: $CORE_PATH"; exit 2; }

# scratch
rm -rf .kyb_minmerge 2>/dev/null || true
mkdir -p .kyb_minmerge/norm

# 1) collect overlays (broadened search + optional derivation from governance artifacts)
python3 - <<'PY'
import os, glob, json, re, io, yaml, hashlib
os.makedirs(".kyb_minmerge/norm", exist_ok=True)

def rel(p): 
  try: return os.path.relpath(p)
  except Exception: return p

def sha(path):
  h=hashlib.sha256()
  with open(path,'rb') as f:
    for ch in iter(lambda:f.read(65536), b''): h.update(ch)
  return h.hexdigest()

# Allow override from env (space- or comma-separated)
extra = os.environ.get("OVERLAY_GLOBS_EXTRA","")
extra_globs = [g for g in re.split(r'[,\s]+', extra) if g]

globs = [
  # common overlay names/locations
  "**/*_overlay.yaml",
  "**/overlays/*.yaml",
  "**/zzz_rehydrate__*.yaml",
  # prior kyb merge outputs (artifact bundles)
  "hestia/**/kyb-merge-artifacts*/.kyb_overlay_merge/overlays/*.yaml",
  "hestia/**/.kyb_overlay_merge/overlays/*.yaml",
  ".kyb_overlay_merge/overlays/*.yaml",
] + extra_globs

seen=set(); overlays=[]
for g in globs:
  for p in glob.glob(g, recursive=True):
    if not os.path.isfile(p): continue
    if p.endswith("system_instruction.yaml"): continue
    rp=rel(p)
    if rp in seen: continue
    seen.add(rp); overlays.append(rp)

# If none found, derive overlays from governance inputs (.diff/.md) by extracting YAML blocks
derived=[]
if not overlays:
  candidates = []
  candidates += glob.glob("**/*.diff", recursive=True)
  candidates += glob.glob("**/*.md", recursive=True)
  outdir = ".kyb_minmerge/derived_overlays"
  os.makedirs(outdir, exist_ok=True)
  fence = re.compile(r"```yaml\s*(.*?)```", re.DOTALL|re.IGNORECASE)
  for src in candidates:
    try:
      if os.path.getsize(src) > 512_000:  # skip huge files
        continue
      text = open(src, 'r', errors='ignore').read()
    except Exception:
      continue
    blocks = fence.findall(text)
    # also accept raw YAML “overlay:” top-level without fences
    if not blocks and src.endswith(".diff"):
      # heuristic: grab lines that look like YAML additions starting with '+' but keep structure
      adds = [ln[1:] for ln in text.splitlines() if ln.startswith('+') and not ln.startswith('+++')]
      snippet = "\n".join(adds).strip()
      if snippet and snippet.lstrip().startswith(('{','[','#','a','c','p','o','m','y')):  # weak gate
        blocks = [snippet]
    idx=0
    for blk in blocks:
      try:
        data = yaml.safe_load(io.StringIO(blk)) or {}
      except Exception:
        continue
      if not isinstance(data, dict) or not data:
        continue
      # require that the overlay touches at least one plausible top-level key
      if not (set(data.keys()) & {"protocols","metadata","condensation","personas","prompt_registry","templates","prompt_tests","architectures","profiles"}):
        continue
      out = os.path.join(outdir, f"{os.path.basename(src)}__overlay_{idx}.yaml")
      with open(out,"w") as f:
        yaml.safe_dump(data, f, sort_keys=False)
      derived.append(rel(out)); idx+=1

overlays = sorted(set(overlays + derived))
open(".kyb_minmerge/norm/overlays_found.json","w").write(json.dumps(overlays,indent=2))
report = {
  "overlays_found_count": len(overlays),
  "overlays_found": overlays,
  "derived_from_artifacts_count": len(derived),
  "derived_from_artifacts": derived,
  "globs_used": globs
}
open(".kyb_minmerge/norm/overlay_discovery_report.json","w").write(json.dumps(report,indent=2))
print(json.dumps(report, indent=2))
if not overlays:
  raise SystemExit("NO_OVERLAYS: none found or derived. Provide overlays or set OVERLAY_GLOBS_EXTRA.")
PY

# 2) merge in governance order
python3 - <<'PY'
import yaml, json, os, re, copy, hashlib
CORE=os.environ["CORE_PATH"]
base = yaml.safe_load(open(CORE)) or {}
overlays = json.load(open(".kyb_minmerge/norm/overlays_found.json"))

def bucket(p):
  n=os.path.basename(p)
  if n.startswith("meta_system_instruction_PR_overlay"): return (0,n)
  if n.startswith("protocol_condensation_overlay"):     return (1,n)
  if n.endswith("__canonical.yaml"):                     return (3,n)
  if n.startswith("zzz_rehydrate__"):                    return (2,n)
  return (2,n)

overlays.sort(key=bucket)

def sha(p):
  h=hashlib.sha256()
  with open(p,'rb') as f:
    for ch in iter(lambda:f.read(65536),b''): h.update(ch)
  return h.hexdigest()

def contains_delete(x):
  if isinstance(x,dict):
    if any(k in x for k in ("__delete__","$delete")): return True
    return any(contains_delete(v) for v in x.values())
  if isinstance(x,list):
    return any(contains_delete(i) for i in x)
  return False

def deep_merge(a,b):
  if isinstance(a,dict) and isinstance(b,dict):
    o=dict(a)
    for k,v in b.items():
      o[k]=deep_merge(a.get(k),v) if k in a else copy.deepcopy(v)
    return o
  return copy.deepcopy(b)

merged = copy.deepcopy(base)
touched=[]
for p in overlays:
  d = yaml.safe_load(open(p)) or {}
  if contains_delete(d):
    raise SystemExit(f"CONFLICT: deletion marker found in overlay {p}")
  merged = deep_merge(merged, d)
  touched.append({"overlay":p,"sha256":sha(p),"top_keys":sorted(list((d or {}).keys()))})

os.makedirs(".kyb_minmerge", exist_ok=True)
open(".kyb_minmerge/base.yaml","w").write(yaml.safe_dump(base, sort_keys=False))
open(".kyb_minmerge/merged.yaml","w").write(yaml.safe_dump(merged, sort_keys=False))
open(".kyb_minmerge/norm/touched.json","w").write(json.dumps(touched,indent=2))
PY

# 3) synthetic diff (audit)
diff -u .kyb_minmerge/base.yaml .kyb_minmerge/merged.yaml > .kyb_minmerge/norm/synthetic_merged.diff || true

# 4) lean governance checks
python3 - <<'PY'
import yaml, re, json, collections, sys
M=".kyb_minmerge/merged.yaml"
doc=yaml.safe_load(open(M)) or {}
text=open(M).read()
yaml_ok=True
forbidden=bool(re.search(r'\b(TODO|DRAFT)\b', text))
required_blocks_ok = all(k in doc for k in ("protocols","metadata"))
proto_ids=[]
for cat,blocks in (doc.get("protocols") or {}).items():
  if isinstance(blocks,dict):
    for name,blk in blocks.items():
      if isinstance(blk,dict) and "id" in blk: proto_ids.append(blk["id"])
dups=[k for k,v in collections.Counter(proto_ids).items() if v>1]
ids_unique = (len(dups)==0)
cond_ok = isinstance(doc.get("condensation"), dict) or ("condensation" not in doc)
ALL_OK = yaml_ok and (not forbidden) and required_blocks_ok and ids_unique and cond_ok
out = {
  "yaml_parse_ok": yaml_ok,
  "forbidden_terms_found": forbidden,
  "required_blocks_ok": required_blocks_ok,
  "protocol_ids_unique": ids_unique,
  "dup_ids": dups,
  "condensation_block_present_or_absent_ok": cond_ok,
  "all_ok": ALL_OK
}
open(".kyb_minmerge/checks.json","w").write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
if not ALL_OK: sys.exit(10)
PY

# 5) atomic writeback + receipt
python3 - <<'PY'
import os, hashlib, yaml, json, time, shutil
core=os.environ["CORE_PATH"]
src=".kyb_minmerge/merged.yaml"
tmp=core+".tmp"
shutil.copyfile(src,tmp); os.replace(tmp,core)
h=hashlib.sha256(); h.update(open(core,'rb').read()); sha=h.hexdigest()
rec={"minimal_merge_receipt":{
  "core_path": core,
  "synthetic_diff": ".kyb_minmerge/norm/synthetic_merged.diff",
  "touched_overlays": ".kyb_minmerge/norm/touched.json",
  "checks": json.load(open(".kyb_minmerge/checks.json")),
  "sha256_after": sha,
  "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
}}
open(".kyb_minmerge/receipt.yaml","w").write(yaml.safe_dump(rec, sort_keys=False))
print("WRITEBACK_OK sha256:", sha)
PY

echo "✅ Minimal overlay merge complete."
echo "Artifacts:"
echo "  - .kyb_minmerge/receipt.yaml"
echo "  - .kyb_minmerge/norm/synthetic_merged.diff"
echo "  - .kyb_minmerge/norm/touched.json"
echo "  - ${CORE_PATH}"
