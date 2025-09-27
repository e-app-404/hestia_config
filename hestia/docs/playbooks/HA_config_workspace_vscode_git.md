# Home Assistant Config Workspace – Git & VS Code Layout

This README documents how the **/Volumes/HA/config** workspace is wired for Git and VS Code. It explains the split Git directory ("gitdir pointer"), the VS Code file layout, what is ignored, and the safe maintenance tasks you can run.

> **TL;DR**
>
> * **Repo root (work tree):** `/Volumes/HA/config`
> * **Actual git directory:** `/Volumes/HA/config/hestia/core/meta/.git`
> * **Pointer file:** `/Volumes/HA/config/.git` containing exactly: `gitdir: hestia/core/meta/.git`
> * **VS Code settings (canonical):** `/Volumes/HA/config/hestia/core/meta/.vscode/` (root `.vscode` is a symlink to this)
> * **Lean workspace file:** `/Volumes/HA/config/config-lean.code-workspace` (Git off, YAML ergonomics kept)
> * **Trash/archive:** `/Volumes/HA/config/.trash/` (ignored)
> * **NAS mirror (bare):** `nas = babylonrobot@dsm-git-host:/volume1/git-mirrors/ha-config.git`
> * **NAS working tree (auto-updated by hook):** `/volume1/git-mirrors/ha-config-live` (on DSM)

---


## 1) Git Layout (split gitdir)

### What you have

* **Work tree (your files):** `/Volumes/HA/config`
* **Git metadata:** `/Volumes/HA/config/hestia/core/meta/.git`
* **Pointer file at repo root:** `/Volumes/HA/config/.git`

  Content:

  ```
  gitdir: hestia/core/meta/.git
  ```

Git follows the relative `gitdir:` pointer to find the real `.git` directory. This is portable and keeps the repo root clean.

### Why this helps

* Keeps the root tidy and reduces noisy watchers.
* Lets you **see** `hestia/core/meta/.git` in Explorer while we exclude it from heavy indexing.
* Works with standard Git commands as long as the pointer exists.

### Key commands (explicit paths)

Use `--git-dir` and `--work-tree` when you want to be explicit and avoid CWD issues:

```bash
# Show branch & toplevel
GITDIR="/Volumes/HA/config/hestia/core/meta/.git"
ROOT="/Volumes/HA/config"

(cd /; git --git-dir="$GITDIR" --work-tree="$ROOT" rev-parse --abbrev-ref HEAD)
(cd /; git --git-dir="$GITDIR" --work-tree="$ROOT" rev-parse --show-toplevel)

# Status (fast, no untracked scan)
(cd /; GIT_OPTIONAL_LOCKS=0 git --git-dir="$GITDIR" --work-tree="$ROOT" status -uno)
```

> **Migration helper (only if you’ve not split yet):**
>
> ```bash
> # Move the existing .git to meta and write the pointer file (run once)
> cd /Volumes/HA/config
> mv .git hestia/core/meta/.git
> printf 'gitdir: hestia/core/meta/.git\n' > .git
> git rev-parse --git-dir   # should print: hestia/core/meta/.git
> ```

---

## 2) Remotes, SSH, and NAS mirror

* **Remote name:** `nas`
* **Bare repo on DSM:** `/volume1/git-mirrors/ha-config.git`
* **DSM working tree:** `/volume1/git-mirrors/ha-config-live` (auto-updated when `main` is pushed)
* **SSH selection:** the repo pins your Mac’s SSH config so Git never tries `/config/.ssh`.

### Pin SSH to your Mac keys (already done)

```bash
cd /Volumes/HA/config
# Always use macOS ~/.ssh/config and the right key
MAC_HOME="$((/usr/bin/dscl . -read "/Users/$(id -un)" NFSHomeDirectory 2>/dev/null | awk -F': ' '{print $2}') || true)"
[ -n "$MAC_HOME" ] || MAC_HOME="$HOME"
SSH_CONFIG="$MAC_HOME/.ssh/config"

git config --local core.sshCommand "ssh -F $SSH_CONFIG -o IdentitiesOnly=yes"
```

### Verify remotes

```bash
cd /Volumes/HA/config
git remote -v        # should show: nas  babylonrobot@dsm-git-host:/volume1/git-mirrors/ha-config.git
```

### Sync (manual)

```bash
BRANCH="$(git symbolic-ref --quiet --short HEAD || echo main)"
git push -u nas "$BRANCH:main"
```

### Sync (scripted QoL)

A small helper lives at `hestia/utils/ha_sync_nas.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
BRANCH="$(git symbolic-ref --quiet --short HEAD || echo main)"
git push -u nas "$BRANCH"
```

### DSM post-receive hook (installed)

* **Location:** `/volume1/git-mirrors/ha-config.git/hooks/post-receive`
* **Effect:** whenever `refs/heads/main` is updated, the hook hard-updates `/volume1/git-mirrors/ha-config-live` to that commit.

> If you ever relocate the DSM working tree, edit the hook’s `WT="…"` path accordingly.

---


---


## 3) VS Code Layout

### Canonical settings folder

* `/Volumes/HA/config/hestia/core/meta/.vscode/`

  * `settings.json`
  * optional `_bak/` for backups

### Root symlink for compatibility

* `/Volumes/HA/config/.vscode -> hestia/core/meta/.vscode`

This keeps all editor config co-located with meta while preserving VS Code’s default discovery of a root `.vscode` folder.

### Lean workspace (recommended for daily editing)

* **File:** `/Volumes/HA/config/config-lean.code-workspace`
* **Goals:** Git disabled (no churn), YAML ergonomics enabled, watchers/search exclude heavy runtime paths, still **visible** meta git.

Key settings (abbrev.):

```json
{
  "folders": [
    { "path": "/Volumes/HA/config" },
    { "path": "/Users/evertappels/.ssh" }
  ],
  "settings": {
    "git.enabled": false,
    "python.defaultInterpreterPath": "/Volumes/HA/config/.venv/bin/python",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": { "source.fixAll.ruff": "explicit" },

    "yaml.schemaStore.enable": true,
    "yaml.validate": true,
    "yaml.format.enable": true,
    "yaml.customTags": [
      "!include", "!include_dir_merge_named", "!include_dir_merge_list",
      "!include_dir_list", "!include_dir_named", "!secret", "!env_var"
    ],

    "files.exclude": {
      "**/.DS_Store": true,
      "**/__pycache__": true,
      "**/*.pyc": true
    },
    "files.watcherExclude": {
      "hestia/core/meta/.git/**": true,
      "**/.storage/**": true,
      "www/**": true,
      "tts/**": true,
      "reports/**": true,
      "hestia/diagnostics/**": true,
      "hestia/work/**": true,
      "tmp/**": true
    },
    "search.exclude": {
      "hestia/core/meta/.git/**": true,
      "**/.storage/**": true,
      "www/**": true,
      "tts/**": true,
      "reports/**": true,
      "hestia/diagnostics/**": true,
      "hestia/work/**": true,
      "tmp/**": true
    }
  }
}
```

> **Visibility vs. performance:** we do **not** hide `hestia/core/meta/.git` in `files.exclude`, so you can inspect it. We exclude it from **watchers** and **search** to avoid heavy scanning.

---


---


## 4) Ignore hygiene (root .gitignore)

Minimal additive patterns to keep noise out (your project `.gitignore` remains authoritative):

```gitignore
# Strategos maintenance assets
/.trash/
/.strategos/

# VS Code root symlink (we keep settings under meta/.vscode)
/.vscode

# HA runtime, caches, logs, archives (sample)
/.storage/
/www/
/tts/
/reports/
/tmp/
*.tar.gz
*.backup
```

---

## 5) Health checks (binary, no side-effects)

```bash
ROOT="/Volumes/HA/config"
GITDIR="/Volumes/HA/config/hestia/core/meta/.git"

# Pointer correctness
sed -n '1p' "$ROOT/.git"           # expect: gitdir: hestia/core/meta/.git

# Resolve toplevel and gitdir actually used
(cd /; git --git-dir="$GITDIR" --work-tree="$ROOT" rev-parse --show-toplevel)
(cd /; git --git-dir="$GITDIR" --work-tree="$ROOT" rev-parse --git-dir)

# Quick status sample (fast)
(cd /; GIT_OPTIONAL_LOCKS=0 git --git-dir="$GITDIR" --work-tree="$ROOT" status -uno)

# Remotes
(cd /; git --git-dir="$GITDIR" --work-tree="$ROOT" remote -v)

# SSH pinning
(cd /; git --git-dir="$GITDIR" --work-tree="$ROOT" config --get core.sshCommand)
```

**DSM sanity:**

```bash
# Bare repo HEAD
ssh -F ~/.ssh/config babylonrobot@dsm-git-host 'git --git-dir=/volume1/git-mirrors/ha-config.git symbolic-ref HEAD'

# Bare repo tip of main
ssh -F ~/.ssh/config babylonrobot@dsm-git-host 'git --git-dir=/volume1/git-mirrors/ha-config.git rev-parse --verify refs/heads/main'

# Working tree tip
ssh -F ~/.ssh/config babylonrobot@dsm-git-host 'git -C /volume1/git-mirrors/ha-config-live rev-parse --abbrev-ref HEAD; git -C /volume1/git-mirrors/ha-config-live log -1 --oneline || true'
```

---

## 6) Maintenance tasks

### Archive & prune legacy git backups

Directories such as `.git.DISABLED.bak.*` can be archived then removed. `/.trash/` is ignored by Git.

```bash
ROOT="/Volumes/HA/config"; TRASH="$ROOT/.trash"; mkdir -p "$TRASH"
for d in "$ROOT"/.git.DISABLED.bak.*; do
  [ -d "$d" ] || continue
  base="$(basename "$d")"
  tar -C "$(dirname "$d")" -czf "$TRASH/${base}.tar.gz" "$base"
  rm -rf "$d"
  echo "archived $base -> $TRASH/${base}.tar.gz"
done
# Ensure ignored
grep -qxF "/.trash/" "$ROOT/.gitignore" || echo "/.trash/" >> "$ROOT/.gitignore"
```

---

## 7) Guardrails & Best Practices

* **Never** move `hestia/core/meta/.git` without updating the root pointer file.
* Prefer `git -C /Volumes/HA/config …` or explicit `--git-dir/--work-tree` to avoid cwd edge cases.
* Keep `/.trash/` in `.gitignore`; clear it periodically.
* In VS Code, keep watchers/search exclusions for `meta/.git` and HA runtime churn for speed.
* Keep your **lean** workspace as the default for day‑to‑day editing; open the full workspace only when needed.

---

## 8) Quick Facts

* Repo branch currently: **main** (as last verified)
* Git remotes: local/NAS only; public origin intentionally absent
* Pointer file syntax is standard and supported by Git across platforms

---

*Last updated:* 2025-09-10
