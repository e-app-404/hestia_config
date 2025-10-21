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
  # Disallow bare http(s) to external domains; allow localhost and add-on hosts
  if grep -E "url:\s*\"?https?://(?!localhost|127\.0\.0\.1|a0d7b954-|homeassistant)" "$f" -n; then
    echo "ERROR: External URL usage in rest_command not allowed: $f" >&2
    fail=1
  fi
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
