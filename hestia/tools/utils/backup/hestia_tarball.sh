#!/bin/bash

# Create a tarball of the workspace, excluding logs, databases, temp, and large media
# Output: /config/hestia/workspace/archive/tarballs/<ISO_WEEK>/ha_hestia_$timestamp.tar.gz

: "${CONFIG_ROOT:=/config}"
: "${INCLUDE_STORAGE:=false}"  # Set to 'true' to create separate .storage backup
WORKSPACE_DIR="$CONFIG_ROOT"
ISO_WEEK=$(date +"%G-W%V")
TARBALL_DIR="$CONFIG_ROOT/hestia/workspace/archive/tarballs/$ISO_WEEK"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
TARBALL_NAME="ha_hestia_${ISO_WEEK}_${TIMESTAMP}.tar.gz"
STORAGE_TARBALL_NAME="ha_storage_${ISO_WEEK}_${TIMESTAMP}.tar.gz"

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
  --exclude='.cloud/'
  --exclude='.git/'
  --exclude='.github/'
  --exclude='.githooks/'
  --exclude='.storage/'
  --exclude='.cloud/'
  --exclude='.vscode/'
  --exclude='.venv/'
  --exclude='.venv_ha_governance/'
  --exclude='.mypy_cache/'
  --exclude='.ssh/'
  --exclude='.trash/'
  --exclude='.quarantine/'
  --exclude='www/'
  --exclude='ps5-mqtt/'
  --exclude='zigbee2mqtt/'
  --exclude='hestia/workspace/archive/tarballs/'
  --exclude='hestia/workspace/archive/backups/'
  --exclude='hestia/workspace/cache/'
  --exclude='custom_components/'
  --exclude='hacs/'
  --exclude='*.egg-info/'
  --exclude='*.bak*'
  --exclude='.trash/'
  --exclude='reports/checkpoints/'
  --exclude='**/*.mp4'
  --exclude='**/*.mkv'
  --exclude='**/*.avi'
  --exclude='**/*.wav'
  --exclude='**/*.mp3'
  --exclude='influx.cookie'
  --exclude='secrets.yaml'
  --exclude='.ha_run.lock'
  --exclude='.ps4-games.*.json'
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

# Optional .storage backup (opt-in only)
if [[ "$INCLUDE_STORAGE" == "true" ]]; then
  echo "Creating .storage backup (INCLUDE_STORAGE=true)..."
  if [[ -d "$WORKSPACE_DIR/.storage" ]]; then
    tar czf "$TARBALL_DIR/$STORAGE_TARBALL_NAME" -C "$WORKSPACE_DIR" .storage/
    STORAGE_EXIT=$?
    if [[ $STORAGE_EXIT -eq 0 ]]; then
      echo "Storage backup created at $TARBALL_DIR/$STORAGE_TARBALL_NAME"
    else
      echo "Warning: Storage backup failed with exit code $STORAGE_EXIT"
    fi
  else
    echo "Warning: .storage directory not found"
  fi
else
  echo "Skipping .storage backup (use INCLUDE_STORAGE=true to enable)"
fi
