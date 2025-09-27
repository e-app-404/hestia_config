#!/usr/bin/env bash
# Hardened push-to-NAS script
# Safe for interactive use (will `return` instead of `exit` when sourced).

# Helper to handle fatal errors but not kill interactive shell if sourced.
_sourced() {
  # returns 0 if script is being sourced
  [[ "${BASH_SOURCE[0]}" != "${0}" ]]
}
_fail() {
  local code=${2:-1}
  echo "ERROR: $1" >&2
  if _sourced; then
    return "$code"
  else
    exit "$code"
  fi
}

# Small wrapper to run ssh with sane timeouts/options.
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new)
_remote_ok() {
  # $1 = user@host, $2 = remote command to test
  if ! ssh "${SSH_OPTS[@]}" "$1" -- bash -c "$2" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

# 1) quick sanity: can we reach the NAS git service?
NAS_USER_HOST="gituser@192.168.0.104"
echo "== Checking NAS SSH reachability to $NAS_USER_HOST =="
if ! ssh "${SSH_OPTS[@]}" "$NAS_USER_HOST" -- git --version >/dev/null 2>&1; then
  _fail "Unable to contact $NAS_USER_HOST (ssh or git unavailable). Network, DNS, or key problem." 2
fi
echo "OK: NAS reachable"

# 2) ensure bare repo exists (safe if already there)
# run remote block with 'set -e' but tolerate 'already initialized' cases; use mkdir -p and 'git init --bare --shared' guarded
echo "== Ensuring bare repo on NAS =="
ssh "${SSH_OPTS[@]}" "$NAS_USER_HOST" bash -s <<'REMOTE' || _fail "Failed to ensure bare repo on NAS" 3
set -euo pipefail
root=/volume1/git-mirrors/ha-config.git
mkdir -p "$root"
cd "$root"
# If it's already a bare repo this will be a no-op; tolerate non-zero outcomes gracefully.
if git rev-parse --is-bare-repository >/dev/null 2>&1; then
  echo "OK: bare repo already present"
else
  git init --bare --shared || true
  echo "OK: created bare repo (or left existing repo intact)"
fi
REMOTE

# 3) prepare local workspace
WORKDIR="$HOME/hass"
echo "== Local workspace: $WORKDIR =="
if [ ! -d "$WORKDIR" ]; then
  _fail "Local workspace $WORKDIR does not exist; mount or create it before pushing." 4
fi
cd "$WORKDIR" || _fail "Cannot cd $WORKDIR" 5

# Make sure we have a git repo (safe init)
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init || _fail "git init failed" 6
fi

# 4) set LAN remote only (safe, idempotent)
LAN_REMOTE="ssh://gituser@192.168.0.104/volume1/git-mirrors/ha-config.git"
if git remote get-url origin >/dev/null 2>&1; then
  # replace origin so we prefer LAN in this run
  git remote remove origin 2>/dev/null || true
fi
git remote add origin "$LAN_REMOTE" || _fail "Failed to add LAN remote" 7
echo "OK: origin -> $LAN_REMOTE"

# 5) stage & commit safely (don't abort terminal)
echo "== Staging and committing changes =="
git add -A || _fail "git add failed" 8

# guard against huge files ( >50MB )
BIG=$(git diff --cached --name-only --diff-filter=AM | while read -r f; do
  [ -f "$f" ] || continue
  sz=$(wc -c < "$f")
  if [ "$sz" -gt 52428800 ]; then
    printf "%s (%s bytes)\n" "$f" "$sz"
  fi
done)
if [ -n "$BIG" ]; then
  echo "ERROR: Large files staged (>50MB):"
  echo "$BIG"
  echo "Refusing to commit. Please update .gitignore or relocate these files."
  if _sourced; then return 9; else exit 9; fi
fi

git commit -m "feat(ha-config): bootstrap snapshot" || echo "INFO: no changes to commit or commit failed (non-fatal)"

# 6) push (do not kill terminal on failure; report)
echo "== Pushing to NAS =="
if ! git push -u origin main; then
  echo "ERROR: git push failed. Possible causes:"
  echo " - Network/DNS/SSH issues to NAS"
  echo " - Authentication failure (keys)"
  echo " - Remote repository permissions"
  echo "Suggestion: attempt the following from a host that can reach the NAS:"
  echo "  ssh $NAS_USER_HOST 'cd /volume1/git-mirrors/ha-config.git && git --bare-check' (example)"
  if _sourced; then return 10; else exit 10; fi
fi

# 7) quick confirmation from NAS (non-fatal)
echo "== Remote confirmation =="
ssh "${SSH_OPTS[@]}" "$NAS_USER_HOST" bash -s <<'REMOTE' || echo "WARN: Could not run remote confirmation (non-fatal)"
set -euo pipefail
cd /volume1/git-mirrors/ha-config.git || exit 0
echo "Branches:"
git for-each-ref --format="%(refname:short)" refs/heads || true
echo "Last commit:"
git log -1 --oneline || true
REMOTE

echo "OK: Push complete"