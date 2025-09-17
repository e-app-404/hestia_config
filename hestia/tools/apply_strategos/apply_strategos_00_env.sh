#!/usr/bin/env bash
set -euo pipefail

# ---- Job & Paths -----------------------------------------------------------

: "${LOCKED_UTC:=2025-09-12T00:00:00Z}"   # override for reproducibility if desired
JOB_ID="${JOB_ID_OVERRIDE:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT_BASE="/Volumes/HA/config/hestia/work/out"
OUT_DIR="${OUT_BASE}/${JOB_ID}"
TMP_DIR="${OUT_DIR}/.work"
mkdir -p "${OUT_DIR}" "${TMP_DIR}"

# ---- Path Resolver ---------------------------------------------------------

# Prefer actual tree under /Volumes/HA/config/hestia; fallback to short aliases (/core, /work, /packages)

CORE_ROOT="/Volumes/HA/config/hestia/core"
WORK_ROOT="/Volumes/HA/config/hestia/work"
PKG_ROOT="/packages"


# Direct source folders for base extraction
BASE_DEVICES="${CORE_ROOT}/config/devices"
BASE_INDEX="${CORE_ROOT}/config/index"
BASE_NETWORKING="${CORE_ROOT}/config/networking"

SCRATCH_TGZ="${WORK_ROOT}/scratch.tar.gz"
ALT_SCRATCH_TGZ="/work/scratch.tar.gz"
SCRATCH_DIR="${WORK_ROOT}/scratch"   # directory form per tree

PKG_NETGEAR="/Volumes/HA/config/packages/package_netgear_gs724t.yaml"
ALT_PKG_NETGEAR="/packages/package_netgear_gs724t.yaml"

ADR8="${CORE_ROOT}/architecture/ADR-0008-normalization-and-determinism-rules.md.md"
ADR9="${CORE_ROOT}/architecture/ADR-0009-switch-modeling-and-validation.md"

# Resolve fallbacks

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
BASE_DEVICES=${BASE_DEVICES}
BASE_INDEX=${BASE_INDEX}
BASE_NETWORKING=${BASE_NETWORKING}
SCRATCH_TGZ=${SCRATCH_TGZ}
SCRATCH_DIR=${SCRATCH_DIR}
PKG_NETGEAR=${PKG_NETGEAR}
ADR8=${ADR8}
ADR9=${ADR9}
LOCKED_UTC=${LOCKED_UTC}
EOF

echo "Initialized env for JOB_ID=${JOB_ID} at ${OUT_DIR}"