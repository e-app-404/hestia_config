diff --git a/docs/ADR/ADR-0019-remote-topology-and-mirror-policy.md b/docs/ADR/ADR-0019-remote-topology-and-mirror-policy.md
--- a/docs/ADR/ADR-0019-remote-topology-and-mirror-policy.md
+++ b/docs/ADR/ADR-0019-remote-topology-and-mirror-policy.md
@@
+## Addendum — 2025-09-21T00:00Z — Clarifications, Guardrails, and Operational Cards
+
+### Why this addendum
+This addendum clarifies intent and guardrails surfaced during implementation and merge-workflow reviews, without modifying ADR-0019’s canonical sections. It encodes: (a) **local `main` must be fast-forward only**, (b) **NAS mirror remains pull-only**, (c) **admin-only force replaces** with receipts, and (d) **ADR linter** requirements per ADR-0009/0018.
+
+### Clarifications (no change to the decision intent)
+1. **Local `main` is FF-only from `github/main`.** If a fast-forward is not possible, **do not create a merge commit** on local `main`; instead hard-reset local `main` to `github/main` and continue work on a feature branch (e.g., `wip/<topic>`), cherry-picking as needed.
+2. **NAS mirror (`origin`) is pull-only for developers.** The mirror updates via **fetch from GitHub**; developers must not push (or force-push) to `origin/main`.
+3. **Force-replace of `github/main` is admin-only.** Before any history surgery, create **backup branch + tag** and write a **receipt** under `hestia/reports/<YYYYMMDD>/...` (see Command Cards below).
+4. **ADR Lint is mandatory for ADR PRs.** ADRs must pass `hestia/tools/adr_lint` and conform to ADR-0009 (front-matter schema/order, machine-parseable blocks).
+
+### Front-matter normalization (errata; metadata only)
+These are **non-substantive** metadata normalizations to align with ADR-0009. They are recorded here as guidance and **do not alter** ADR-0019’s decision text:
+- `status` should use a canonical value casing (e.g., `Proposed`/`Accepted`).
+- Use `related:` (not `relates_to:`) for cross-references.
+- Include `last_updated:` (ISO-8601) and update it on edits.
+- Ensure `author:` is a YAML list of names.
+
+### Operational Card A — Keep local `main` aligned (FF-only)
+```bash
+git fetch github
+git switch main || git switch -c main github/main
+git merge --ff-only github/main || git reset --hard github/main
+```
+*Rationale:* prevents accidental merge commits on `main` and keeps local verification aligned with the canonical branch.
+
+### Operational Card B — Abort a stuck merge & realign safely
+```bash
+STAMP=$(date -u +%Y%m%dT%H%M%SZ); CUR=$(git rev-parse --short HEAD)
+git branch backup/merge-state-$CUR-$STAMP
+git diff > /tmp/backup_merge_state_$CUR_$STAMP.patch
+git status --porcelain > /tmp/backup_merge_state_$CUR_$STAMP.status
+git merge --abort || git reset --merge || true
+git fetch github
+git switch main
+git reset --hard github/main
+```
+*Rationale:* guarantees a recoverable path with backups, then restores `main` to the canonical GitHub state.
+
+### Operational Card C — Admin-only cutover with receipts
+```bash
+# Preflight (read-only)
+git fetch github main && git rev-parse github/main
+
+# Backup GitHub main (branch + tag)
+STAMP=$(date -u +%Y%m%dT%H%M%SZ)
+git push github github/main:refs/heads/backup/main-$STAMP
+git push github github/main:refs/tags/backup/main-$STAMP
+
+# Publish candidate and force-replace main (admins only; with lease)
+git push github my/branch:my/branch
+git push --force-with-lease=main github my/branch:main
+
+# Receipt (text note in repo, tiny)
+mkdir -p hestia/reports/$(date +%Y%m%d)
+printf "cutover: %s\nsrc: %s\nby: %s\n" "$STAMP" "my/branch" "$(git config user.name)" \
+  > "hestia/reports/$(date +%Y%m%d)/cutover_receipt_${STAMP}.txt"
+git add hestia/reports/$(date +%Y%m%d)/cutover_receipt_${STAMP}.txt
+git commit -m "docs(receipt): cutover $STAMP my/branch -> main"
+git push github main
+```
+
+### Enforcement Signals (Addendum scope)
+```yaml
+TOKEN_BLOCK:
+  accepted:
+    - REMOTE_TOPOLOGY_OK
+    - MAIN_FF_ONLY
+    - MIRROR_PULL_ONLY
+    - RECEIPT_REQUIRED
+    - ADR_LINT_REQUIRED
+  requires:
+    - ADR_SCHEMA_V1
+  drift:
+    - DRIFT: local_main_non_ff
+    - DRIFT: pushed_to_origin
+    - DRIFT: missing_receipt
+    - DRIFT: adr_frontmatter_invalid
+```
+
+### Notes
+- This addendum is **non-breaking** and may be folded into ADR-0019 in a future **Amended** revision per ADR-0009 lifecycle rules.
+- If ADR-0015’s title has changed (e.g., Symlink/Template Policy), ensure ADR-0019’s `related` entry matches the final title when front-matter normalization is performed.
