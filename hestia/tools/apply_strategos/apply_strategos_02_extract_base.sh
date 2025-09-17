#!/usr/bin/env bash
set -euo pipefail
source /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null

MERGED="${OUT_DIR}/merged/config/hestia/core"
mkdir -p "${MERGED}"

# Copy source folders directly
cp -r "${BASE_DEVICES}" "${MERGED}/devices"
cp -r "${BASE_INDEX}" "${MERGED}/index"
cp -r "${BASE_NETWORKING}" "${MERGED}/networking"

# Optional markdown export (if present in index or networking)
for cand in "ha_remote_config_export.md"; do
  if [[ -f "${BASE_INDEX}/$cand" ]]; then
    cp "${BASE_INDEX}/$cand" "${MERGED}/$cand"
  elif [[ -f "${BASE_NETWORKING}/$cand" ]]; then
    cp "${BASE_NETWORKING}/$cand" "${MERGED}/$cand"
  fi
done

echo "{\"merged_root\": \"${MERGED}\", \"children\": [$(ls -1 "${MERGED}" | jq -R -s -c 'split("\n")[:-1]')] }"