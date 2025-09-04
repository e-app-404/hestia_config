#!/bin/bash

# Create a tarball of the workspace, excluding logs, databases, temp, and large media
# Output: /Volumes/config/hestia/vault/tarballs/hestia_snapshot_$timestamp.tar.gz

WORKSPACE_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TARBALL_DIR="/Volumes/config/hestia/vault/tarballs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TARBALL_NAME="ha_hestia_snapshot_${TIMESTAMP}.tar.gz"

mkdir -p "$TARBALL_DIR" || { echo "Failed to create tarball directory $TARBALL_DIR"; exit 1; }

# Exclusion patterns
EXCLUDES=(
  --exclude='*.log*'
  --exclude='*.db'
  --exclude='*.tar*'
  --exclude='tmp/'
  --exclude='tts/'
  --exclude='staging/'
  --exclude='deps/'
  --exclude='.git/'
  --exclude='.storage/'
  --exclude='.cloud/'
  --exclude='.vscode/'
  --exclude='.venv/'
  --exclude='www/'
  --exclude='ps5-mqtt/'
  --exclude='zigbee2mqtt/'
  --exclude='home-assistant_v2.db'
  --exclude='home-assistant.log*'
  --exclude='hestia/tarballs/'
  --exclude='custom_components/'
  --exclude='hestia/vault/'
  --exclude='hacs/'
)

cd "$WORKSPACE_DIR" || { echo "Failed to change directory to $WORKSPACE_DIR"; exit 1; }

# Log the tar command for debugging
echo "Running: tar czf '$TARBALL_DIR/$TARBALL_NAME' ${EXCLUDES[*]} ."

tar czf "$TARBALL_DIR/$TARBALL_NAME" "${EXCLUDES[@]}" .
TAR_EXIT=$?
if [ $TAR_EXIT -ne 0 ]; then
  echo "Tarball creation failed with exit code $TAR_EXIT"
  exit $TAR_EXIT
fi

echo "Tarball created at $TARBALL_DIR/$TARBALL_NAME"
