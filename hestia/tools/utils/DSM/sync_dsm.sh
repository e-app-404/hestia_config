#!/bin/bash
set -euo pipefail


HOST="dsm-git-host"
USER="babylonrobot"
REMOTE_NAME="nas"
BARE_PATH="/volume1/git-mirrors/ha-config.git"


if [ ! -f ~/.ssh/id_ed25519 ]; then
  echo "ERROR: SSH key ~/.ssh/id_ed25519 not found. Generate with: ssh-keygen -t ed25519 -N \"\" -f ~/.ssh/id_ed25519"
  exit 1
fi


cd /Volumes/HA/config
git remote rename dsm-git "${REMOTE_NAME}" 2>/dev/null || true
if git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
  git remote set-url "${REMOTE_NAME}" "${USER}@${HOST}:${BARE_PATH}"
else
  git remote add "${REMOTE_NAME}" "${USER}@${HOST}:${BARE_PATH}"
fi
git remote -v

BRANCH="$(git symbolic-ref --quiet --short HEAD || echo main)"
env HOME="$HOME" git push -u "${REMOTE_NAME}" "${BRANCH}" || { echo "ERROR: Git push failed. Check SSH access and remote repo existence."; exit 3; }


git config --local core.filemode false
git config --local core.untrackedCache true
git config --local gc.writeCommitGraph true
git config --local index.threads true
git config --local fetch.prune true

python3 <<'PY'
import json, subprocess
def run(*a):
    p = subprocess.run(a, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return dict(rc=p.returncode, out=p.stdout.strip(), err=p.stderr.strip())
out = {
  "repo": run("git","rev-parse","--show-toplevel")["out"],
  "branch": run("git","rev-parse","--abbrev-ref","HEAD")["out"],
  "remotes": run("git","remote","-v")["out"]
}
print(json.dumps(out, indent=2))
PY