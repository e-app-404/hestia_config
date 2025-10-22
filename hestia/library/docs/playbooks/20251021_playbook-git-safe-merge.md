# Playbook: Git Safe-Merge (idempotent)

Status: Accepted
Date: 2025-10-21
Related ADRs: ADR-0009 (ADR governance), ADR-0024 (Canonical /config), ADR-0027 (Write governance), ADR-0032 (Patch workflow)

## Purpose

Provide an idempotent, governance-compliant sequence to safely merge a long-lived feature branch into `main` without losing untracked documents or artifacts. This guards against “lost documents” failure modes (untracked files + branch switch).

## Canonical Paths & Adjustments (ADR-0024)

- Reports and durable notes MUST live under `/config/hestia/reports/<YYYY-MM-DD>/...` rather than ad-hoc paths.
- This playbook persists bundle notes from ignored `artifacts/` into the canonical reports tree before merge.

## Sequence (bash; idempotent)

```bash
# 0) Shell hardening
set -euo pipefail

# 1) Safety anchors (reflog + tag + backup of untracked)
BRANCH="feat/occupancy-beta-any-on-aggregate"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DATE_BUCKET="$(date -u +%Y-%m-%d)"

git rev-parse --abbrev-ref HEAD
git fetch --all --tags

git tag -a "pre-merge_${BRANCH}_${STAMP}" -m "Safety anchor before merging ${BRANCH} to main" || true
# Backup untracked/ignored working files so nothing disappears on checkout:
mkdir -p .safe/backup_${STAMP}
git ls-files --others --exclude-standard -z | xargs -0 tar -czf ".safe/backup_${STAMP}/untracked_${STAMP}.tar.gz" || true

# 2) Full diff capture for audit/rollback
mkdir -p .safe
git diff --no-ext-diff --binary origin/main...HEAD > ".safe/feature_vs_main_${STAMP}.patch"
git shortlog -sne origin/main..HEAD > ".safe/authors_${STAMP}.txt"

# 3) Make the bundle notes durable (move out of ignored path) — ADR-compliant
mkdir -p "hestia/reports/${DATE_BUCKET}"
if [ -f artifacts/bundle_update/20251022__feat-occupancy-beta-any-on-aggregate__bundle-notes.md ]; then
  cp artifacts/bundle_update/20251022__feat-occupancy-beta-any-on-aggregate__bundle-notes.md \
     "hestia/reports/${DATE_BUCKET}/bundles__${STAMP}__${BRANCH}__bundle-notes.md"
fi
if [ -f artifacts/bundle_update/20251022__feat-occupancy-beta-any-on-aggregate__commit-message.txt ]; then
  cp artifacts/bundle_update/20251022__feat-occupancy-beta-any-on-aggregate__commit-message.txt \
     "hestia/reports/${DATE_BUCKET}/bundles__${STAMP}__${BRANCH}__commit-message.txt"
fi
git add "hestia/reports/${DATE_BUCKET}" || true
git commit -m "docs(reports): persist ${BRANCH} bundle notes for governance audit [${STAMP}]" || true

# 4) Sync and linearize the feature branch atop the latest main (safer history)
git checkout "${BRANCH}"
git pull --rebase --autostash origin "${BRANCH}"
git fetch origin main
git rebase origin/main

# 5) Pre-merge validations (governed)
# YAML parse (best-effort) — HA config checks should be run via repo tools as well
if command -v python >/dev/null 2>&1; then
  git ls-files '*.yaml' '*.yml' | xargs -I{} sh -c "python - <<'PY'\nimport sys,yaml\nyaml.safe_load(open('{}'))\nprint('OK {}')\nPY" || true
fi
# Preferred: repo-native checks
/config/bin/config-health /config
/config/bin/config-validate /config

# 6) Merge into main with an explicit merge commit (keeps branch identity)
git checkout main
git pull origin main
git merge --no-ff "${BRANCH}" -m "merge(${BRANCH}): ADR normalization + media registry unique_id + occupancy/room_db updates"

# 7) Push and tag
git push origin main
git tag -a "merge-${BRANCH}-${STAMP}" -m "Merged ${BRANCH} into main on ${STAMP}" || true
git push origin --tags || true
```

## Why this works

- Creates safety anchors (tag + untracked backup) before any history changes
- Moves bundle notes out of ignored area into canonical, tracked reports
- Rebase onto latest `origin/main` to reduce conflict surface
- Uses explicit merge commit to preserve branch context
- Runs governance checks (ADR-0024 path health and YAML validation)

## Binary acceptance criteria

- Tracked files created under `hestia/reports/<YYYY-MM-DD>/bundles__<timestamp>__<branch>__*.{md,txt}`
- `git diff --name-only origin/main...main` post-merge shows only intended changes
- Repo YAML checks pass
- Tag `merge-${BRANCH}-${STAMP}` exists on origin
- Tag `pre-merge_${BRANCH}_${STAMP}` exists locally (and can be pushed)

## Rollback

- Revert the merge commit (no history rewrite):

```bash
git checkout main
git log --oneline --decorate -n 5   # copy MERGE_SHA
git revert -m 1 MERGE_SHA
git push origin main
```

- Fast reset to safety tag (requires force-with-lease):

```bash
git checkout main
git reset --hard "pre-merge_${BRANCH}_${STAMP}"
git push --force-with-lease origin main
```
