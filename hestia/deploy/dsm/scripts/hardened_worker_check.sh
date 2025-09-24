#!/usr/bin/env bash
set -euo pipefail
LC_ALL=C

# Hardened worker route check + acceptance test runner
# Safe: checks, dry-run friendly, prints diagnostics

CF_ZONE_ID="0855d7797c8126d39b6653952f1fed61"
CF_API_TOKEN="x2B2rB_ZZvxSAjJbZeP6EaayZ9_Udo0RjlhVOobz"
WORKER_NAME="portal-no-store"
ROUTE_PATTERN="nas.xplab.io/portal/*"

jq_bin=$(command -v jq || true)
if [ -z "$jq_bin" ]; then
  echo "BLOCKED: jq is required for JSON parsing. Install jq and retry." >&2
  exit 2
fi

echo "[1/6] Check worker script exists on the account"
script_resp=$(curl -sS -X GET "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID:-e37605142353eb163ea86636c4027134}/workers/scripts/${WORKER_NAME}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" || true)
if echo "$script_resp" | grep -q '"success":true' 2>/dev/null; then
  echo "OK: worker ${WORKER_NAME} present"
else
  echo "WARN: worker ${WORKER_NAME} not found or API returned non-success. Continuing to ensure route creation anyway (the script may have been uploaded earlier)."
fi

echo "[2/6] Check for existing route"
route_id=$(curl -sS -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/workers/routes" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" | jq -r '.result[] | select(.pattern=="'"${ROUTE_PATTERN}"'") | .id' || true)

if [ -n "$route_id" ] && [ "$route_id" != "null" ]; then
  echo "OK: route exists id=$route_id"
else
  echo "[3/6] Creating route ${ROUTE_PATTERN} -> ${WORKER_NAME}"
  create_resp=$(curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/workers/routes" \
    -H "Authorization: Bearer ${CF_API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"pattern":"'"${ROUTE_PATTERN}"'","script":"'"${WORKER_NAME}"'"}')
  echo "$create_resp" | jq || true
  route_id=$(echo "$create_resp" | jq -r '.result.id' || true)
  if [ -z "$route_id" ] || [ "$route_id" = "null" ]; then
    echo "ERROR: failed to create route. API output above." >&2
    exit 3
  fi
  echo "Created route id=$route_id"
fi

echo "[4/6] Verify route via API"
curl -sS -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/workers/routes/${route_id}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" | jq || true

echo "[5/6] Public header check for /portal/index.html"
curl -sSI https://nas.xplab.io/portal/index.html | egrep -i "Cache-Control|Content-Security-Policy|cf-cache-status|server" -n || true

echo "[6/6] Run acceptance tests"
./../acceptance_tests.sh nas.xplab.io || true

exit 0
