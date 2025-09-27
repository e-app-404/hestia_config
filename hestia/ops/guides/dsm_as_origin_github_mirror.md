# DSM-as-origin GitHub mirror
This guide helps you set up a Synology DSM NAS as the authoritative Git repository for your project, with automatic mirroring to GitHub. This setup allows you to push changes to your NAS, which then mirrors them to GitHub using a deploy key.

Below is a single, end-to-end chain of actions. Read the brief descriptions, then copy each fenced block **exactly** into the stated terminal (Mac or NAS). Only the **first** block contains placeholders; edit those once, then reuse.

## 0) Session / Environment Variables (edit placeholders, then source)

Run on **both** Mac and NAS shells before other blocks (adjust only once on each).

```bash
export REPO="omega_registry"
export NAS_HOST="ds220plus.reverse-beta.ts.net"
export NAS_HOST_LAN="192.168.0.104"
export NAS_USER="gituser"
export NAS_ADMIN="babylonrobot"
export NAS_GITROOT="/volume1/git"
export GH_ORG="e-app-404"
export GH_REPO="omega_registry"
export GH_URL="git@github.com:${GH_ORG}/${GH_REPO}.git"
export MIRROR_KEY="/var/services/homes/${NAS_USER}/.ssh/${REPO}_mirror_key"
```

> Ensure in DSM → **Git Server** UI that **Allow access** is ticked for the `${NAS_USER}` account.

## 1) Prepare repository root and create bare repo (NAS)

SSH to NAS as `${NAS_ADMIN}` (use either hostname or LAN IP) and run:

```bash
ssh ${NAS_ADMIN}@${NAS_HOST_LAN}
```

Then on the NAS shell:

```bash
sudo mkdir -p "${NAS_GITROOT}"
sudo chown -R "${NAS_USER}:users" "${NAS_GITROOT}"
sudo chmod 755 "${NAS_GITROOT}"
sudo -u "${NAS_USER}" git init --bare "${NAS_GITROOT}/${REPO}.git"
sudo -u "${NAS_USER}" git config --global init.defaultBranch main
```

## 2) Install your Mac developer SSH public key for push access (Mac → NAS)

On your **Mac** (copies your local `~/.ssh/id_ed25519.pub` to NAS /tmp):

```bash
ssh ${NAS_ADMIN}@${NAS_HOST_LAN} "cat > /tmp/dev_id_ed25519.pub" < ~/.ssh/id_ed25519.pub
```

On the **NAS** shell (still logged in as `${NAS_ADMIN}`):

```bash
GHOME=$(sudo awk -F: -v u="${NAS_USER}" '$1==u{print $6}' /etc/passwd)
sudo rm -rf "$GHOME/.ssh"
sudo install -d -m 700 -o "${NAS_USER}" -g users "$GHOME/.ssh"
sudo install -m 600 -o "${NAS_USER}" -g users /tmp/dev_id_ed25519.pub "$GHOME/.ssh/authorized_keys"
sudo chmod go-w "$GHOME"
sudo rm -f /tmp/dev_id_ed25519.pub
```

## 3) Point your local repo to DSM and push (Mac)

Run **on your Mac** from inside your local `omega_registry` repository directory:

```bash
cd /Users/evertappels/Projects/omega_registry
git remote remove origin 2>/dev/null || true
git remote add origin "ssh://${NAS_USER}@${NAS_HOST_LAN}${NAS_GITROOT}/${REPO}.git"
git ls-remote "ssh://${NAS_USER}@${NAS_HOST_LAN}${NAS_GITROOT}/${REPO}.git"
git push -u origin HEAD
```

## 4) Generate GitHub Deploy Key for mirroring (NAS)

On the **NAS** shell:

```bash
sudo -u "${NAS_USER}" mkdir -p "$(dirname "${MIRROR_KEY}")"
sudo -u "${NAS_USER}" ssh-keygen -t ed25519 -C "mirror-${REPO}@DS220plus" -N "" -f "${MIRROR_KEY}"
sudo -u "${NAS_USER}" ssh-keygen -y -f "${MIRROR_KEY}" | sudo tee "${MIRROR_KEY}.pub" >/dev/null
sudo -u "${NAS_USER}" sh -c 'ssh-keyscan -H github.com >> "$HOME/.ssh/known_hosts"'
```

Copy the **public** key to your Mac clipboard, then add it in GitHub → repo **Settings → Deploy keys** → **Add deploy key** → paste → **Allow write access** → Save.

```bash
ssh -t ${NAS_ADMIN}@${NAS_HOST_LAN} "sudo cat '${MIRROR_KEY}.pub'" | pbcopy
```

## 5) Test GitHub auth using the deploy key (NAS)

Back on the **NAS** shell:

```bash
sudo -u "${NAS_USER}" GIT_SSH_COMMAND="ssh -i ${MIRROR_KEY} -o IdentitiesOnly=yes" ssh -T git@github.com || true
```

## 6) Install post-receive mirror hook (NAS)

On the **NAS** shell (writes a static hook with your variables expanded):

```bash
HOOK_PATH="${NAS_GITROOT}/${REPO}.git/hooks/post-receive"
sudo tee "$HOOK_PATH" >/dev/null <<EOF
#!/bin/sh
set -eu
GH_URL="${GH_URL}"
KEY="${MIRROR_KEY}"
LOG="/var/log/git-mirror-${REPO}.log"
start=$(date -Iseconds)
echo "[$start] mirror start -> $GH_URL" >> "$LOG"
GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes"
if /usr/bin/env GIT_SSH_COMMAND="$GIT_SSH_COMMAND" git push --mirror "$GH_URL" >> "$LOG" 2>&1; then
  echo "[$(date -Iseconds)] mirror OK" >> "$LOG"
else
  echo "[$(date -Iseconds)] mirror FAIL" >> "$LOG"
fi
exit 0
EOF
sudo chown "${NAS_USER}:users" "$HOOK_PATH"
sudo chmod +x "$HOOK_PATH"
```

## 7) Trigger a one-off mirror and verify (NAS)

On the **NAS** shell:

```bash
sudo -u "${NAS_USER}" /usr/bin/env GIT_SSH_COMMAND="ssh -i ${MIRROR_KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes" git --git-dir="${NAS_GITROOT}/${REPO}.git" push --mirror "${GH_URL}"
sudo tail -n 50 "/var/log/git-mirror-${REPO}.log"
```

## 8) Hardening & housekeeping (NAS)

On the **NAS** shell:

```bash
sudo synoacltool -enforce-inherit "${NAS_GITROOT}"
sudo chown -R "${NAS_USER}:users" "${NAS_GITROOT}"
sudo chmod 755 "${NAS_GITROOT}"
```

## 9) Acceptance checks

Run where stated.

**Mac:**

```bash
git ls-remote "ssh://${NAS_USER}@${NAS_HOST}${NAS_GITROOT}/${REPO}.git" | head
```

**NAS:**

```bash
sudo -u "${NAS_USER}" GIT_SSH_COMMAND="ssh -i ${MIRROR_KEY} -o IdentitiesOnly=yes" ssh -T git@github.com || true
sudo tail -n 20 "/var/log/git-mirror-${REPO}.log"
```

If all checks pass, the pilot is live: pushes to DSM mirror automatically to GitHub via the deploy key.
