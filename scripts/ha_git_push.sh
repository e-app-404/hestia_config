#!/usr/bin/env bash
set -euo pipefail

# Usage: ./ha_git_push.sh [/path/to/repo]
CFG_DIR="${1:-/config}"
REMOTE_NAME="${REMOTE_NAME:-dsm-git}"
REMOTE_HOST_ALIAS="${REMOTE_HOST_ALIAS:-dsm-git-host}"

if [ ! -d "$CFG_DIR/.git" ]; then
  echo "ERROR: $CFG_DIR is not a git repository."
  echo "Hint: rerun as: ./ha_git_push.sh \"$PWD\""
  exit 1
fi

git -C "$CFG_DIR" config core.sshCommand "ssh -F $CFG_DIR/.ssh/config" || true
echo "core.sshCommand => $(git -C "$CFG_DIR" config --get core.sshCommand || echo '(unset)')"

if command -v ha >/dev/null 2>&1; then
  echo "Running: ha core check"
  ha core check || true
else
  echo "Skip ha core check (ha CLI not found)."
fi

echo
echo "=== Git status (before) ==="
git -C "$CFG_DIR" status -s || true

echo
echo "=== Diff summary (skip storage/db) ==="
git -C "$CFG_DIR" diff --name-only -- . ':!*.storage/*' ':!home-assistant_v2.db' || true

git -C "$CFG_DIR" add -A

TMPMSG="$(mktemp)"
cat > "$TMPMSG" <<'EOF'
feat(ha): LocalTuya entities + dehumidifier DP maps, PS4 package, and docs

• LocalTuya
  - Added/confirmed lights: ensuite_accent_alpha_local, laundry_ceiling_alpha_local
  - Added dehumidifier (PB-D-18 OmniDry 12L) via LocalTuya with full DP map:
    power(1), target%(2), fan(4), mode(5), humidity(6), temp(7),
    ionizer(10), child_lock(16), timer(17), fault(19), filter_reset(20),
    filter_life(23), temp_unit(24), runtime_reset(28)
  - Created momentary “one-shot” maintenance toggles with auto-off automations
  - Sensors wired: humidity/temperature (scaling=1), fault code + problem binary_sensor

• Tuya/LocalTuya context seed
  - Added tuya.localtuya.context.yaml as SSoT for device inventory, DP legend,
    HA entity bindings, setup guide, troubleshooting, and sanity checks

• PS4 package
  - Command-line sensor for recent games + image/button templates
  - Scripts to route HDMI matrix & wake console, plus sync automation

• Presence/occupancy & privacy
  - (From earlier) Bedroom camera privacy package and occupancy composites

• Git push pipeline docs
  - Updated ops doc to reflect dsm-git remote, core.sshCommand, and bare repo checks

Co-authored-by: LocalTuya config flow (DP discovery)
EOF

if git -C "$CFG_DIR" diff --cached --quiet; then
  echo "No staged changes; nothing to commit."
else
  git -C "$CFG_DIR" commit -F "$TMPMSG"
fi
rm -f "$TMPMSG"

if ! git -C "$CFG_DIR" remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  echo "ERROR: remote '$REMOTE_NAME' not found. Configure it, then re-run."
  exit 2
fi

git -C "$CFG_DIR" fetch "$REMOTE_NAME" --prune

if git -C "$CFG_DIR" rev-parse --verify --quiet "$REMOTE_NAME/main" >/dev/null; then
  TAG="backup_remote_main_$(date +%Y%m%d_%H%M%S)"
  REMOTE_SHA="$(git -C "$CFG_DIR" rev-parse "$REMOTE_NAME/main")"
  echo "Creating safety tag $TAG for remote main at $REMOTE_SHA"
  git -C "$CFG_DIR" tag -f "$TAG" "$REMOTE_SHA"
  git -C "$CFG_DIR" push "$REMOTE_NAME" "refs/tags/$TAG"
else
  echo "Remote main not found; skipping backup tag."
fi

set +e
git -C "$CFG_DIR" pull --rebase --autostash "$REMOTE_NAME" main
PULL_RC=$?
set -e
if [ "$PULL_RC" -ne 0 ]; then
  echo "Rebase had conflicts or failed. Resolve manually, then re-run push."
  exit 3
fi

git -C "$CFG_DIR" push "$REMOTE_NAME" HEAD:refs/heads/main

LOCAL=$(git -C "$CFG_DIR" rev-parse --short HEAD)
if git -C "$CFG_DIR" config --get core.sshCommand >/dev/null 2>&1; then
  REMOTE=$(ssh -F "$CFG_DIR/.ssh/config" "$REMOTE_HOST_ALIAS" "git --git-dir=/volume1/HA_MIRROR for-each-ref --format='%(objectname:short)' refs/heads/main" 2>/dev/null | head -n1)
else
  REMOTE="(parity check skipped: no sshCommand configured)"
fi

echo "Parity: local=$LOCAL  remote=$REMOTE"
if [ "$REMOTE" != "(parity check skipped: no sshCommand configured)" ] && [ "$LOCAL" = "$REMOTE" ]; then
  echo "✅ Push successful; remote is in sync."
else
  echo "ℹ️  If mismatch, inspect: git -C \"$CFG_DIR\" log --oneline --decorate --graph -n 5"
fi

echo "Done."
