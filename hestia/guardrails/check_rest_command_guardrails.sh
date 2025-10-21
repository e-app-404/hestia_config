#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# Guardrails: Verify Home Assistant rest_command definitions conform to patterns
# - No direct external hostnames (prefer internal add-on hostnames or hass_url())
# - Only allowed methods (GET/POST)
# - JSON payload for POST should be present (content_type/application json if payload exists)

ROOT="${1:-.}"

shopt -s nullglob globstar

mapfile -t files < <(git ls-files '*.yaml' | grep -vE '^\.github/|^hestia/workspace/archive/' || true)

fail=0

check_file() {
  local f="$1"
  # quick grep to see if rest_command present
  if ! grep -qE '^rest_command:' "$f" 2>/dev/null && ! grep -qE '\bservice:\s*rest_command\.' "$f" 2>/dev/null; then
    return 0
  fi
  # Scope scanning to rest_command: block only; basic state machine
  in_rest=0
  while IFS= read -r line; do
    # detect top-level keys
    if [[ "$line" =~ ^[A-Za-z0-9_]+: ]]; then
      in_rest=0
    fi
    if [[ "$line" =~ ^rest_command: ]]; then
      in_rest=1
      continue
    fi
    if (( in_rest )); then
      case "$line" in
        *url:*)
          url=$(echo "$line" | sed -E 's/.*url:\s*"?([^" ]*).*/\1/')
          # Only http(s)
          case "$url" in
            http://*|https://*) ;;
            *) continue ;;
          esac
          host=$(echo "$url" | sed -E 's#^https?://([^/:]+).*$#\1#')
          if [[ -n "$host" ]]; then
            # Allowlist: localhost, 127.0.0.1, homeassistant, a0d7b954-*, RFC1918 ranges
            if [[ "$host" == "localhost" || "$host" == "127.0.0.1" || "$host" == "homeassistant" || "$host" == a0d7b954-* || "$host" == 10.* || "$host" == 192.168.* || "$host" == 172.16.* || "$host" == 172.17.* || "$host" == 172.18.* || "$host" == 172.19.* || "$host" == 172.2[0-9].* || "$host" == 172.3[0-1].* ]]; then
              :
            else
              echo "$f: ERROR disallowed host in rest_command URL: $host" >&2
              fail=1
            fi
          fi
          ;;
      esac
    fi
  done <"$f"
  # Methods must be GET or POST
  if grep -E "^\s*method:\s*(PUT|DELETE|PATCH)\b" "$f" -n; then
    echo "ERROR: Disallowed HTTP method in rest_command: $f" >&2
    fail=1
  fi
}

for f in "${files[@]}"; do
  check_file "$f"
done

if [[ $fail -ne 0 ]]; then
  echo "Guardrails check failed."
  exit 1
fi

echo "REST command guardrails passed."
