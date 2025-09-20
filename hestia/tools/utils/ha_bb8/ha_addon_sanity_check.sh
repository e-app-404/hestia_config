#!/usr/bin/env bash
# Home Assistant Add-on Health: Operational Sanity Checks
# Usage: bash ha_addon_sanity_check.sh
# Run on the HA box (SSH or Web Terminal add-on)

set -euo pipefail

# 1) Addressable name (Supervisor) and basic metadata
ha addons list | grep -E '^  slug:\s+local_beep_boop_bb8' && echo "TOKEN: ADDON_LISTED"

# 2) YAML view (works with default output)
ha addons info local_beep_boop_bb8 | yq '.slug, .version, .repository'

# Optional: JSON view (only if your HA CLI supports it)
# ha addons info local_beep_boop_bb8 --raw-json | jq '.data | {slug, version, repository}'

# 3) Build context folder must exist and be plain (no .git)
ls -la /addons/local/beep_boop_bb8
test -d /addons/local/beep_boop_bb8/.git && echo "DRIFT: runtime_nested_git" || echo "TOKEN: RUNTIME_PLAIN_OK"

# 4) Rebuild & (re)start (only when you intend to refresh the image)
ha addons reload
ha addons rebuild local_beep_boop_bb8
ha addons start  local_beep_boop_bb8

# 5) Verify state + version
ha addons info local_beep_boop_bb8 | grep -E '^(state|version|version_latest):' && echo "TOKEN: REBUILD_OK"
