#!/usr/bin/env bash
set -euo pipefail
LC_ALL=C
: "${HA_MOUNT:=$HOME/hass}"

# Hardened retry script to ensure Cloudflare Worker + route and validate headers
# Writes no secrets to disk beyond using provided token values.

CF_ACCOUNT_ID="e37605142353eb163ea86636c4027134"
CF_ZONE_ID="0855d7797c8126d39b6653952f1fed61"
CF_API_TOKEN="x2B2rB_ZZvxSAjJbZeP6EaayZ9_Udo0RjlhVOobz"
SCRIPT_NAME="portal-no-store"
UPDATED_WORKER_FILE="${HA_MOUNT:-$HOME/hass}/tmp/worker-portal-no-store-updated.js"
ACCT_SCRIPTS_URL="https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/workers/scripts/${SCRIPT_NAME}"
ROUTES_URL="https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/workers/routes"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required" >&2; exit 2; }
command -v curl >/dev/null 2>&1 || { echo "ERROR: curl is required" >&2; exit 2; }

echo "[1] Validate worker file exists: ${UPDATED_WORKER_FILE}"
if [ ! -f "${UPDATED_WORKER_FILE}" ]; then
  echo "ERROR: worker file ${UPDATED_WORKER_FILE} missing" >&2
  exit 3
fi

# Upload the worker script (overwrite). This endpoint returns JSON; pipe to jq for readability.
echo "[2] Uploading Worker script to account (overwrite)"
upload_out=$(curl -sS -X PUT "${ACCT_SCRIPTS_URL}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/javascript" \
  --data-binary @"${UPDATED_WORKER_FILE}")

echo "Upload response:"
echo "${upload_out}" | jq || true

if ! echo "${upload_out}" | jq -e '.success' >/dev/null; then
  echo "ERROR: Worker upload failed" >&2
  exit 4
fi

# Ensure route exists; if not, create
echo "[3] Ensure route ${SCRIPT_NAME} -> nas.xplab.io/portal/* exists"
route_id=$(curl -sS -X GET "${ROUTES_URL}" -H "Authorization: Bearer ${CF_API_TOKEN}" | jq -r '.result[] | select(.pattern=="nas.xplab.io/portal/*") | .id' || true)

if [ -n "${route_id}" ] && [ "${route_id}" != "null" ]; then
  echo "OK: route exists id=${route_id}"
else
  echo "Route missing; creating..."
  create_out=$(curl -sS -X POST "${ROUTES_URL}" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"pattern":"nas.xplab.io/portal/*","script":"portal-no-store"}')
  echo "Create response:"
  echo "${create_out}" | jq || true
  if ! echo "${create_out}" | jq -e '.success' >/dev/null; then
    echo "ERROR: route creation failed" >&2
    exit 5
  fi
  route_id=$(echo "${create_out}" | jq -r '.result.id')
  echo "Created route id=${route_id}"
fi

# Small pause to let edge pick up
sleep 1

# Public header check
echo "[4] Public header check for /portal/index.html"
curl -sSI https://nas.xplab.io/portal/index.html | egrep -i "Cache-Control|Content-Security-Policy|cf-cache-status|server" -n || true

echo "[5] Public header check for / (root)"
curl -sSI https://nas.xplab.io/ | egrep -i "Cache-Control|Content-Security-Policy|cf-cache-status|server" -n || true

# Run acceptance tests
echo "[6] Run acceptance tests"
${HA_MOUNT:-$HOME/hass}/hestia/deploy/dsm/acceptance_tests.sh nas.xplab.io

echo "Hardened worker retry completed"
exit 0
