---
id: ADR-0019
title: Remote Topology & Mirror Policy (GitHub ⇄ NAS ⇄ Local)
status: proposed
date: 2025-09-28
author: e-app-404
relates_to:
  - ADR-0015  # Snapshots & inventory policy
  - ADR-0017  # Branch rescue / rollback protocol
  - ADR-0018  # Workspace lifecycle & CI guardrails
---

## Context
We operate with:
- **GitHub repo**: canonical "source of truth".
- **NAS mirror** (`origin`): pull-through mirror + backup, served from Synology.
- **Local worktrees**: developer machines.

We already follow ADR-0017/0018 safety patterns (backup tags/branches, receipts, hygiene gate). This ADR consolidates the **remote topology, allowed flows, and recovery procedures**.

## Decision
1) **Source of truth** = `github/main`.  
2) **NAS mirror** is **pull-only** (no dev pushes). It is updated by **fetching from GitHub**, not by direct developer force-pushes.  
3) All risky ref moves (force updates, history surgery) **must**:
   - create **backup branch + tag** first,
   - be recorded with a **receipt** in `hestia/reports/<YYYYMMDD>/...`,
   - follow ADR-0017 commands (one-at-a-time).
4) CI gates (ADR-0018) are required on PRs into `main`:  
   - `hygiene-gate / gate`  
   - `ADR-0018 Extra Guards / guards`  
   - `ADR Frontmatter Verify / verify`

## Topology & Roles
- **GitHub remote name:** `github` (read/write for maintainers).  
- **NAS remote name:** `origin` (**read** for devs; **admin-managed write**).  
- **Local:** developers create branches, push to **GitHub**, open PRs; mirror sync is **automated or admin-run**.

## Normal Flow
- Dev → **push branch to GitHub**, open PR → CI gates pass → **merge to `main`**.
- Mirror sync (job or admin) runs:
  ```bash
  # on NAS host, in bare repo; run as repo owner (e.g., gituser)
  git -C /volume1/git-mirrors/ha-config.git \
    fetch --prune https://github.com/<org>/<repo>.git \
    +refs/heads/main:refs/heads/main
  ```
- No direct developer push to `origin/main`.

## Cutover / Force-Replace (rare)

When we must replace `github/main` with a known-good branch:

1. **Preflight (local)**:
   ```bash
   git status --porcelain
   git fetch github main && git rev-parse github/main
   ```

2. **Back up current GitHub main**:
   ```bash
   STAMP=$(date -u +%Y%m%dT%H%M%SZ)
   git push github github/main:refs/heads/backup/main-$STAMP
   git push github github/main:refs/tags/backup/main-$STAMP
   ```

3. **Publish our branch & replace main (with lease)**:
   ```bash
   git push github my/branch:my/branch
   git push --force-with-lease=main github my/branch:main
   ```

4. **Receipt**: write a short receipt under `hestia/reports/<YYYYMMDD>/cutover_receipt_<TS>.txt`.

5. **Mirror update (pull-through only)**:
   - **Preferred**: NAS fetch from GitHub (same command as Normal Flow).
   - **If fetch is blocked by perms**, NAS admin may run (in bare repo, as repo owner):
     ```bash
     GH_SHA=$(git ls-remote --heads https://github.com/<org>/<repo>.git main | awk '{print $1}')
     git -C /volume1/git-mirrors/ha-config.git update-ref refs/heads/main "$GH_SHA"
     ```
   - **Never require developers to force-push to origin**.

## Disaster Recovery
- **Roll back GitHub main to a backup**:
  ```bash
  git push --force-with-lease=main github backup/main-<STAMP>:main
  ```
- **NAS mirror then fetches from GitHub to realign**.

## Guardrails
- **NAS perms**: the bare repo is owned by the service account (e.g., `gituser:users`), directories are `g+s`, and the repo path is in `safe.directory` for admin tasks.
- **Branch Protection on GitHub main** requires:
  - `hygiene-gate / gate`
  - `ADR-0018 Extra Guards / guards`
  - `ADR Frontmatter Verify / verify`
- **Pre-commit hook** denies staging `.storage/**` and other ADR-0018 banned paths.
- **Receipts** (text, tiny) are allowed in Git to explain cutovers.

## Consequences
- **Clear ownership**: GitHub is canonical; NAS is backup/distribution.
- **Lower risk during cutovers**; easy rollbacks via backup branches/tags.
- **Auditable** via receipts & CI gates.

## Appendix — One-at-a-time Command Cards

**A) Verify triad alignment**
```bash
git rev-parse HEAD
git ls-remote --heads github main | awk '{print $1}'
git ls-remote --heads origin main | awk '{print $1}'
```

**B) Seed CI status context on main**
```bash
git switch main
git pull --ff-only github main
git commit --allow-empty -m "ci(hygiene): seed"
git push github main
```

**C) Mirror health (NAS host)**
```bash
git -C /volume1/git-mirrors/ha-config.git show-ref refs/heads/main
```