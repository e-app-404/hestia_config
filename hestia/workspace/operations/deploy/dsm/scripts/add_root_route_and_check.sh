#!/usr/bin/env bash
set -euo pipefail
LC_ALL=C
: "${HA_MOUNT:=$HOME/hass}"

CF_ZONE_ID="0855d7797c8126d39b6653952f1fed61"
CF_API_TOKEN="x2B2rB_ZZvxSAjJbZeP6EaayZ9_Udo0RjlhVOobz"
ROUTE_PATTERN="nas.xplab.io/*"
SCRIPT_NAME="portal-no-store"
ROUTES_URL="https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/workers/routes"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required" >&2; exit 2; }
command -v curl >/dev/null 2>&1 || { echo "ERROR: curl is required" >&2; exit 2; }

echo "Checking for existing route pattern=${ROUTE_PATTERN}"
existing=$(curl -sS -X GET "${ROUTES_URL}" -H "Authorization: Bearer ${CF_API_TOKEN}" | jq -r --arg pat "${ROUTE_PATTERN}" '.result[] | select(.pattern==$pat) | .id' || true)

if [ -n "${existing}" ] && [ "${existing}" != "null" ]; then
  echo "Route already exists: id=${existing}"
else
  echo "Creating route ${ROUTE_PATTERN} -> ${SCRIPT_NAME}"
  create_resp=$(curl -sS -X POST "${ROUTES_URL}" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{\"pattern\":\"${ROUTE_PATTERN}\",\"script\":\"${SCRIPT_NAME}\"}")
  echo "Create response:" | jq -r '.' || true
  echo "${create_resp}" | jq || true
  ok=$(echo "${create_resp}" | jq -r '.success')
  if [ "${ok}" != "true" ]; then
    echo "ERROR: failed to create route" >&2
    echo "Response: ${create_resp}" >&2
    exit 3
  fi
  echo "Route created"
fi

sleep 1

echo "\nPublic header check for root (https://nas.xplab.io/)"
curl -sSI https://nas.xplab.io/ | egrep -i "Cache-Control|Content-Security-Policy|cf-cache-status|server" -n || true

echo "\nPublic header check for portal (https://nas.xplab.io/portal/index.html)"
curl -sSI https://nas.xplab.io/portal/index.html | egrep -i "Cache-Control|Content-Security-Policy|cf-cache-status|server" -n || true


echo "\nRunning acceptance tests"
${HA_MOUNT:-$HOME/hass}/hestia/deploy/dsm/acceptance_tests.sh nas.xplab.io

exit 0
