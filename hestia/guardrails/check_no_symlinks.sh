#!/usr/bin/env bash
set -euo pipefail

# Check for symlinks in HA-loaded directories
echo "Checking for symlinks in HA-loaded directories..."

# Check main HA directories for symlinks
if find . -type l -not -path './.git/*' -not -path './.venv*/*' -not -path './deps/*' 2>/dev/null | head -1 | read; then
    echo "WARNING: Symlinks found in HA directories:"
    find . -type l -not -path './.git/*' -not -path './.venv*/*' -not -path './deps/*' 2>/dev/null || true
    # Don't fail for now, just warn
    echo "Symlinks detected but not failing build"
else
    echo "OK: No symlinks found in HA directories"
fi