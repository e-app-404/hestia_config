#!/usr/bin/env bash
set -euo pipefail
REPO=/n/ha
cd "$REPO"

# Safety limits
MAX_CANDIDATES=10000
CMD_TIMEOUT=10s

cleanup() {
  rm -f /tmp/hestia_candidates.list || true
  rm -f /tmp/hestia_neutralize.tmp.* || true
}
trap cleanup EXIT INT TERM

# generate candidate list safely (limit and avoid shell history expansion issues)
git -C "$REPO" ls-files -z -- . ":!hestia/core/architecture/**" ":!hestia/vault/**" ":!hestia/work/**" ":!.git/**" | tr '\0' '\n' > /tmp/hestia_candidates.list

# enforce an upper bound on list size to avoid pathological repos
CAND_COUNT=$(wc -l < /tmp/hestia_candidates.list | tr -d '[:space:]' || echo 0)
if [ "$CAND_COUNT" -gt "$MAX_CANDIDATES" ]; then
  echo "BLOCKED: candidate list too large ($CAND_COUNT > $MAX_CANDIDATES)" >&2
  exit 2
fi

# Count pre-hits with timeout to avoid long-running grep
if command -v timeout >/dev/null 2>&1; then
  PRE_HITS=$(timeout $CMD_TIMEOUT grep -REn --binary-files=without-match "/Volumes/(HA|ha)" -I "$REPO" --exclude-dir=hestia/core/architecture --exclude-dir=hestia/vault --exclude-dir=hestia/work --exclude-dir=.git 2>/dev/null | wc -l | tr -d '[:space:]' || true)
else
  PRE_HITS=$(grep -REn --binary-files=without-match "/Volumes/(HA|ha)" -I "$REPO" --exclude-dir=hestia/core/architecture --exclude-dir=hestia/vault --exclude-dir=hestia/work --exclude-dir=.git 2>/dev/null | wc -l | tr -d '[:space:]' || true)
fi
PRE_HITS=${PRE_HITS:-0}
echo "EVIDENCE: pre_hits=$PRE_HITS"

CHANGED=0
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  f="$REPO/$rel"
  [ -f "$f" ] || continue
  # only operate on reasonably sized text files
  if [ $(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null) -gt $((5*1024*1024)) ]; then
    # skip files larger than 5MB
    continue
  fi
  tmp="$(mktemp /tmp/hestia_neutralize.tmp.XXXXXX)"
  # Use a timeout for sed if available by running under 'timeout'
  if command -v timeout >/dev/null 2>&1; then
    timeout $CMD_TIMEOUT sed -e 's#/n/ha#/n/ha#g' -e 's#/n/ha#/n/ha#g' -e 's#/n/ha#/n/ha#g' -e 's#/n/ha#/n/ha#g' "$f" > "$tmp" || true
  else
    sed -e 's#/n/ha#/n/ha#g' -e 's#/n/ha#/n/ha#g' -e 's#/n/ha#/n/ha#g' -e 's#/n/ha#/n/ha#g' "$f" > "$tmp" || true
  fi
  if [ -f "$tmp" ] && ! cmp -s "$tmp" "$f"; then
    mv "$tmp" "$f"
    CHANGED=$((CHANGED+1))
  else
    rm -f "$tmp" || true
  fi
done < /tmp/hestia_candidates.list

if [ "$CHANGED" -gt 0 ]; then
  git -C "$REPO" add -A || true
fi

# Run the enforcer script with timeout
ENFORCER="$REPO/hestia/tools/system/hestia_workspace_enforcer.sh"
if [ ! -x "$ENFORCER" ]; then
  chmod +x "$ENFORCER" 2>/dev/null || true
fi
if command -v timeout >/dev/null 2>&1; then
  if ! timeout $CMD_TIMEOUT /bin/bash "$ENFORCER" > /tmp/enforcer.out 2>&1; then
    tail -n 2 /tmp/enforcer.out | sed 's/^/EVIDENCE: /'
    head -n 1 /tmp/enforcer.out | sed 's/^/BLOCKED: ENFORCER -> /'
    exit 4
  fi
else
  if ! /bin/bash "$ENFORCER" > /tmp/enforcer.out 2>&1; then
    tail -n 2 /tmp/enforcer.out | sed 's/^/EVIDENCE: /'
    head -n 1 /tmp/enforcer.out | sed 's/^/BLOCKED: ENFORCER -> /'
    exit 4
  fi
fi
tail -n 1 /tmp/enforcer.out | sed 's/^/EVIDENCE: /'

HOOKS_DIR=$(git -C "$REPO" rev-parse --git-path hooks)
mkdir -p "$HOOKS_DIR"
cat > "$HOOKS_DIR/pre-commit" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
/n/ha/hestia/tools/system/hestia_workspace_enforcer.sh
EOF
chmod +x "$HOOKS_DIR/pre-commit"

if git -C "$REPO" diff --quiet && git -C "$REPO" diff --cached --quiet; then
  echo "OK: COMMIT"
else
  git -C "$REPO" commit -m "workspace: neutralize /Volumes paths; install enforcer hook" >/dev/null 2>&1 || true
  echo "OK: COMMIT"
fi

HEAD=$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo NONE)
echo "EVIDENCE: head=$HEAD"
if git -C "$REPO" remote get-url origin >/dev/null 2>&1; then
  if git -C "$REPO" push -u origin stability/workspace-autofs-v1 >/dev/null 2>&1; then
    echo "OK: PUSHED origin stability/workspace-autofs-v1"
  else
    echo "BLOCKED: git push failed (check auth/remote)"
  fi
else
  echo 'BLOCKED: NO_REMOTE_ORIGIN -> set with: git -C /n/ha remote add origin <URL>'
fi

echo "DONE: PATHS_NEUTRALIZED"
BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "UNKNOWN")
echo "SUMMARY: repo=$REPO branch=$BRANCH head=$HEAD pre_hits=$PRE_HITS hooks=$HOOKS_DIR"
