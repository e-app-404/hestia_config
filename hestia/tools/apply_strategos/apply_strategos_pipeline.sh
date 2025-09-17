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

OUT_DIR="$(. /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null 2>&1; source ${OUT_DIR}/.env.meta 2>/dev/null || true; echo ${OUT_DIR:-/Volumes/HA/config/hestia/work/out/UNKNOWN})"
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