#!/bin/bash
set -e
REPO="/n/ha"

# Fail if any tracked file contains /Volumes/HA or /Volumes/ha
if git -C "$REPO" ls-files &>/dev/null; then
  if git -C "$REPO" grep -qE '/Volumes/(HA|ha)'; then
    echo "ERROR: Tracked file contains forbidden path /Volumes/HA or /Volumes/ha"
    exit 1
  fi
fi

# Fail if configuration.yaml is missing
if [ ! -f "$REPO/configuration.yaml" ]; then
  echo "ERROR: $REPO/configuration.yaml missing"
  exit 1
fi

exit 0
