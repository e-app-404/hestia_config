#!/usr/bin/env sh
# patch_ha_templates.sh
# Idempotent patcher to fix unsupported Jinja loop-controls and normalize imports
# Usage: sh patch_ha_templates.sh
set -eu
[ "${DEBUG:-}" = "" ] || set -x
TS=$(date -u +%Y%m%d-%H%M%S)
ROOT_CONFIG="${ROOT_CONFIG:-/config}"
LIB_DIR="$ROOT_CONFIG/custom_templates"
LIB_FILE="$LIB_DIR/template.library.jinja"
BACKUP_FILE="$LIB_FILE.bak-$TS"
TMP_FILE="$LIB_FILE.new"
PATCH_DIR="$(dirname "$0")/patches"

echo "[INFO] Starting template patcher: $TS"

# Ensure lib dir exists
if [ ! -d "$LIB_DIR" ]; then
  echo "[INFO] Creating missing library directory: $LIB_DIR"
  mkdir -p -- "$LIB_DIR"
fi

# Ensure lib exists
if [ ! -f "$LIB_FILE" ]; then
  echo "ERROR: library not found at $LIB_FILE" >&2
  exit 2
fi

# Backup
echo "[INFO] Creating backup: $BACKUP_FILE"
cp -a -- "$LIB_FILE" "$BACKUP_FILE"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum -- "$BACKUP_FILE" > "$BACKUP_FILE.sha256" || true
fi

# Apply bounded macro replacement using a portable shell loop to avoid awk regex/quoting issues
# We replace from a line that contains 'macro any_child_active' until the next line that contains 'endmacro'.
> "$TMP_FILE"
in_replace=0
while IFS= read -r line || [ -n "$line" ]; do
  if [ "$in_replace" -eq 0 ]; then
    case "$line" in
      *"macro any_child_active("*)
        # Write the replacement macro block
        cat >> "$TMP_FILE" <<'JINJA'
{% macro any_child_active(children, active_states=None, output='on') -%}
  {%- set active_states = active_states or ['playing','paused','buffering','on'] -%}
  {%- set children = [children] if (children is string) else children -%}
  {%- set ns = namespace(found=false) -%}
  {%- for c in children -%}
    {%- if states(c) in active_states -%}
      {%- set ns.found = true -%}
    {%- endif -%}
  {%- endfor -%}
  {{ output if ns.found else ('off' if output == 'on' else 'false') }}
{%- endmacro %}
JINJA
        in_replace=1
        ;;
      *)
        printf '%s
' "$line" >> "$TMP_FILE"
        ;;
    esac
  else
    # We're in the replacement skip mode; look for endmacro to resume copying
    case "$line" in
      *endmacro*) in_replace=0 ;;
      *) ;; # skip
    esac
  fi
done < "$LIB_FILE"

if [ $? -ne 0 ]; then
  echo "ERROR: failed to create patched file" >&2
  exit 3
fi
# Atomic move with fallback to in-place overwrite when rename/mv is blocked
if mv -f -- "$TMP_FILE" "$LIB_FILE" 2>/dev/null; then
  echo "[INFO] Atomic move succeeded"
else
  echo "[WARN] Atomic move failed (resource busy or rename blocked). Trying fallbacks..."
  # 1) Try cp -f (BSD/GNU cp)
  if cp -f -- "$TMP_FILE" "$LIB_FILE" 2>/dev/null; then
    echo "[INFO] Fallback cp -f succeeded"
    rm -f -- "$TMP_FILE" || true
  # 2) Try install (creates file with permissions)
  elif command -v install >/dev/null 2>&1 && install -m 644 "$TMP_FILE" "$LIB_FILE" 2>/dev/null; then
    echo "[INFO] Fallback install succeeded"
    rm -f -- "$TMP_FILE" || true
  # 3) Try writing via Perl to force truncate/write (POSIX-perl expected)
  elif perl -e 'open(F,">", shift) or exit 1; binmode F; local $/; undef $/; print F <STDIN>; close F' "$LIB_FILE" < "$TMP_FILE" 2>/dev/null; then
    echo "[INFO] Fallback perl write succeeded"
    rm -f -- "$TMP_FILE" || true
  else
    echo "ERROR: all fallback write methods failed (mv/cp/install/perl)." >&2
    echo "       This may be due to the target filesystem disallowing replacements (SMB/remote mount) or file locks." >&2
    echo "       Consider editing the file directly on the Home Assistant host or remounting with different options." >&2
    exit 3
  fi
fi
chmod 644 "$LIB_FILE"

echo "[INFO] Macro patched in $LIB_FILE"

# Normalize imports across /config (safe, skip binary and .git)
echo "[INFO] Normalizing imports under $ROOT_CONFIG"
find "$ROOT_CONFIG" -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.jinja" -o -name "*.js" -o -name "*.py" -o -name "*.cfg" \) -not -path "*/.git/*" -print0 |
  xargs -0 grep -Il "template.library.jinja" 2>/dev/null | while IFS= read -r file; do
    echo "[INFO] Normalizing imports in: $file"
    sed -i "s@from ['\"]template\.library\.jinja['\"]@from 'custom_templates/template.library.jinja'@g" "$file" || true
    sed -i "s@import ['\"]template\.library\.jinja['\"]@import 'custom_templates/template.library.jinja'@g" "$file" || true
  done

# Legacy symlink creation intentionally disabled
# The canonical location for template.library.jinja is in custom_templates and
# the operator has requested we do not create or repair a root-level symlink.
echo "[INFO] Skipping legacy symlink creation; canonical path is: $LIB_FILE"

# Verifications
echo "[INFO] Running verifications"
FAIL=0
# Check for remaining return/break tags in library (use POSIX [[:space:]] for portability)
if grep -En "\{%-?[[:space:]]*(return|break)" "$LIB_FILE" >/dev/null 2>&1; then
  echo "FAIL: loop-control tags remain in $LIB_FILE" >&2
  grep -En "\{%-?\s*(return|break)" "$LIB_FILE" || true
  FAIL=1
else
  echo "PASS: no loop-control tags in $LIB_FILE"
fi

# Check if legacy import strings remain
if grep -RIn "['\"]template\.library\.jinja['\"]" "$ROOT_CONFIG" >/dev/null 2>&1; then
  echo "WARN: Some files still reference 'template.library.jinja' (legacy imports). The script attempted to normalize imports to 'custom_templates/template.library.jinja' but repository files may need updating."
  grep -RIn "['\"]template\.library\.jinja['\"]" "$ROOT_CONFIG" || true
else
  echo "PASS: no legacy import strings found"
fi

# Print a snippet around the macro for human verification
echo "[INFO] Showing patched macro context (lines containing any_child_active +/- 6):"
awk '{printf "%6d  %s\n", NR, $0}' "$LIB_FILE" | sed -n "1,999p" | grep -n -C6 "any_child_active" || true

# Optional ha core check
if command -v ha >/dev/null 2>&1; then
  echo "[INFO] Running 'ha core check' (may report non-actionable warnings)"
  if ha core check >/dev/null 2>&1; then
    echo "PASS: ha core check OK"
  else
    echo "FAIL: ha core check failed (see 'ha core check' output)" >&2
    FAIL=1
  fi
else
  echo "INFO: ha CLI not found; skipped 'ha core check'"
fi

if [ "$FAIL" -eq 0 ]; then
  echo "SUMMARY: PATCH SUCCESS"
  exit 0
else
  echo "SUMMARY: PATCH FAILED (see messages)" >&2
  exit 4
fi
