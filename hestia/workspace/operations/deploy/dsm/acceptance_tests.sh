#!/usr/bin/env bash
set -euo pipefail
NAS_HOST=${1:-nas.xplab.io}
PORTAL_PATH=${2:-/portal/}
ASSETS_PATH=${3:-/_assets/}

fail(){
  echo "FAIL: $1" >&2
  exit 6
}

info(){
  echo "INFO: $1"
}

http_code(){
  curl -sS -o /dev/null -w '%{http_code}' "$@"
}

get_header(){
  # $1: url, $2: header name (case-insensitive)
  # Portable: use grep -i to find header then strip name and whitespace
  curl -sSI "$1" | tr -d '\r' | grep -i "^$2:" | sed -E "s/^$2:[ \t]*//I" | sed -n '1p' || true
}

info "Running acceptance tests against $NAS_HOST"

# 1) Root should return 200
if [ "$(http_code "https://$NAS_HOST/")" != "200" ]; then
  fail "root_not_200"
fi
info "root_200"

# 2) Portal should return 200 or an auth/redirect (depending on setup) — accept 200/302/401
PPORTAL_CODE=$(http_code "https://$NAS_HOST$PORTAL_PATH")
case "$PPORTAL_CODE" in
  200|302|301|401) info "portal_status_$PPORTAL_CODE" ;; 
  *) fail "portal_unexpected_status_$PPORTAL_CODE" ;;
esac

# 3) Asset should be cached with Cache-Control: max-age= or similar (read header)
ASSET_URL="https://$NAS_HOST${ASSETS_PATH}app.js"
ASSET_CC=$(get_header "$ASSET_URL" "Cache-Control" || true)
if [ -z "$ASSET_CC" ]; then
  fail "asset_cache_control_missing"
fi
echo "EVIDENCE: asset_cache_control='$ASSET_CC'"

# 4) Portal page must be no-store or at least not cached (no max-age). Check for 'no-store' or 'no-cache' or 'private'
PORTAL_URL="https://$NAS_HOST${PORTAL_PATH}index.html"
PORTAL_CC=$(get_header "$PORTAL_URL" "Cache-Control" || true)
if echo "$PORTAL_CC" | grep -qiE "no-store|no-cache|private"; then
  echo "EVIDENCE: portal_cache_control='$PORTAL_CC'"
else
  echo "EVIDENCE: portal_cache_control_observed='$PORTAL_CC'"
  echo "ACTION: Portal pages should be served with Cache-Control: no-store. If DSM Web Station isn't managing headers, run the deploy script with --write-htaccess to install the template that enforces this:"
  echo "  hestia/deploy/dsm/apply_portal_changes.sh --apply --write-htaccess"
  echo "  (or ensure your origin/webserver sets Cache-Control: no-store for /portal/)"
  fail "portal_cache_control_incorrect (observed='$PORTAL_CC')"
fi

# 5) CSP presence on root or portal
CSP=$(get_header "https://$NAS_HOST/" "Content-Security-Policy" || true)
if [ -n "$CSP" ]; then
  echo "EVIDENCE: csp_present"
else
  fail "csp_missing"
fi

info "All acceptance tests passed"
exit 0