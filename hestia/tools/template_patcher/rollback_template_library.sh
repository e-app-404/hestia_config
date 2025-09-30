#!/usr/bin/env sh
# rollback_ha_templates.sh
# Restore the most recent backup of template.library.jinja
set -eu
[ "${DEBUG:-}" = "" ] || set -x
ROOT_CONFIG="/config"
LIB_DIR="$ROOT_CONFIG/custom_templates"
PATTERN="$LIB_DIR/template.library.jinja.bak-*"

LATEST=$(ls -1t $PATTERN 2>/dev/null | head -n1)
if [ -z "$LATEST" ]; then
  echo "No backups found matching $PATTERN" >&2
  exit 1
fi

echo "Restoring $LATEST -> $LIB_DIR/template.library.jinja"
cp -a -- "$LATEST" "$LIB_DIR/template.library.jinja"
if command -v sha256sum >/dev/null 2>&1 && [ -f "$LATEST.sha256" ]; then
  echo "Restoring checksum file as well"
  cp -a -- "$LATEST.sha256" "$LIB_DIR/template.library.jinja.sha256" || true
fi

# Verify
if command -v ha >/dev/null 2>&1; then
  echo "Running 'ha core check' after rollback"
  if ha core check >/dev/null 2>&1; then
    echo "PASS: ha core check OK"
    exit 0
  else
    echo "WARN: ha core check failed after rollback" >&2
    exit 2
  fi
else
  echo "INFO: ha CLI not available; rollback completed"
  exit 0
fi
