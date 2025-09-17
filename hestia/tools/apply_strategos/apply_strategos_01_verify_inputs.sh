#!/usr/bin/env bash
set -euo pipefail
source /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null


missing=()

# existence checks for source folders
[[ -d "${BASE_DEVICES}" ]] || missing+=("${BASE_DEVICES}")
[[ -d "${BASE_INDEX}" ]] || missing+=("${BASE_INDEX}")
[[ -d "${BASE_NETWORKING}" ]] || missing+=("${BASE_NETWORKING}")

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

python3 - "$BASE_DEVICES" "$BASE_INDEX" "$BASE_NETWORKING" "$SCRATCH_TGZ" "$SCRATCH_DIR" "$OUT_DIR" "$USE_SCRATCH_DIR" <<'PY'
import os,sys,hashlib,tarfile,json,glob
BASE_DEVICES,BASE_INDEX,BASE_NETWORKING,SCRATCH_TGZ,SCRATCH_DIR,OUT_DIR,USE_DIR=sys.argv[1:8]
def sha_dir(p):
  h=hashlib.sha256()
  for root,dirs,files in os.walk(p):
    for f in sorted(files):
      fp=os.path.join(root,f)
      with open(fp,'rb') as fd:
        for b in iter(lambda:fd.read(1<<20), b''): h.update(b)
  return h.hexdigest()

res={"inputs":[],"scratch_required":{}}
for path in [BASE_DEVICES, BASE_INDEX, BASE_NETWORKING]:
  res["inputs"].append({"path":path,"exists":True,"sha256":sha_dir(path)})
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
  res["inputs"].append({"path":SCRATCH_TGZ,"exists":True})
else:
  files=sorted(glob.glob(os.path.join(SCRATCH_DIR,"*")))
  res["inputs"].append({"path":SCRATCH_DIR,"exists":True,"files":[os.path.basename(f) for f in files]})

open(os.path.join(OUT_DIR,"evidence_inputs.json"),"w").write(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
PY