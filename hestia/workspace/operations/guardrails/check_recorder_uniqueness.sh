#!/usr/bin/env bash
set -euo pipefail

# Check for single recorder configuration
echo "Checking for single recorder configuration..."

# Look for recorder config in main files
recorder_configs=0

if grep -r "^recorder:" . --include="*.yaml" --include="*.yml" 2>/dev/null; then
    recorder_configs=$((recorder_configs + 1))
fi

if [ $recorder_configs -eq 0 ]; then
    echo "WARNING: No recorder configuration found"
elif [ $recorder_configs -eq 1 ]; then
    echo "OK: Single recorder configuration found"
else
    echo "ERROR: Multiple recorder configurations found"
    exit 1
fi