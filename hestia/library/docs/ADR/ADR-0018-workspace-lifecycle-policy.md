---
id: ADR-0018
title: "ADR-0018: Workspace hygiene, lifecycle & quarantine policy"
slug: workspace-hygiene-lifecycle-quarantine-policy
status: "Accepted"
related:
- ADR-0008
- ADR-0009
- ADR-0024
- ADR-0027
supersedes: []
last_updated: '2025-10-15'
date: '2025-09-26'
decision: Architectural decision documented in this ADR.
owners:
- hestia-core
references:
- .github/workflows/adr-0018-include-scan.yml
author: "e-app-404"
tags:
- architecture
- workspace
- lifecycle
- quarantine
- trash
- archive
- bundles
- guardrails
- automation
---

## ADR-0018 — Workspace hygiene, lifecycle & quarantine policy

# 1) Purpose

Establish one simple, consistent system to name, place, retain, and clean up non-source files in the Home Assistant (Hestia) workspace. The goals are:

- Prevent repo bloat and ambiguity.
- Make provenance and retention deterministic.
- Keep runtime/state and secrets out of Git.
- Keep generated reports and bundles discoverable and easy to prune.

# 2) Scope

Covers *all* non-source artifacts in the repo: backups, temporary files, reports, diagnostics, tarballs/bundles, archives, quarantined files, and deprecated materials. Does **not** change how app code/config is structured (see ADR‑0008/0009) but constrains where and how tools write files.

# 3) Canonical directories (top-level real estate)

- `.trash/` — temporary trash (gitignored). Auto-swept by TTL.
- `.quarantine/` — blocked/suspect items not eligible to merge (gitignored). Manual review only.
- `artifacts/` — reproducible release bundles/tarballs **with** manifest & checksums (gitignored).
- `archive/` — curated, long-lived reference snapshots (kept; not auto-packaged). Must include README (+ provenance).
- `hestia/reports/` — all tool/script output batches (gitignored). Structured by date/batch.
- `hestia/workspace/archive/vault/` — long-term human-curated materials (kept). Subfolders: `backups/`, `bundles/` (manual), `deprecated/`.

> Git policy: `.storage/`, `.venv*/`, `deps/`, caches, token stores and any runtime state are **never** tracked by Git.

# 4) File naming (simple & UTC-safe)

Times use compact UTC format `YYYYMMDDTHHMMSSZ`. Avoid spaces/colons.

**Backups (in-place, transient)**

- Pattern: `<name>.bk.<UTC>` (e.g., `core.entity_registry.bk.20250926T145011Z`).
- Permissions: `0600` if possible.
- Default TTL: 7 days (then auto-pruned or promoted).

**Backups (vault, long-lived)**

- Location: `hestia/workspace/archive/vault/backups/`.
- Pattern: `<name>.<UTC>.bk` or `<name>.bk.<UTC>` (both acceptable here; prefer the former for lexicographic sort).
- Retention: keep N latest per base-name (default N=5) + any manually pinned ones.

**Bundles / release artifacts**

- Location: `artifacts/`.
- Pattern: `<label>__<UTC>__<tag>.tgz`.
- Must include: `MANIFEST.json` and `SHA256SUMS` (reproducible build expectation). Determinism probe runs in CI.

**Reports / diagnostics**

- Location: `hestia/reports/<YYYYMMDD>/<UTC>__<tool>__<label>/`.
- Each file includes a short frontmatter header (commented) or `_meta` alongside JSON.
- Batch is discoverable via append-only `hestia/reports/_index.jsonl`.

**Quarantine**

- Location: `.quarantine/`.
- Pattern: `<why>__<UTC>__<original_name>`.

# 5) Lifecycle states & retention

- **Staging** → *generated* (in `hestia/reports/…`) → optional **archive**/**artifacts** promotion → eventual **prune** by TTL.
- **In-place backups**: auto-prune after 7d unless promoted to vault.
- **Trash**: `.trash/` pruned after 14d.
- **Reports**: default TTL 90d under `hestia/reports/` (CLI enforces; keep latest K per prefix/label).
- **Artifacts**: no TTL; reproducible builds only (must pass determinism check).
- **Archive**/**Vault**: no TTL; human-curated, with README and provenance.

# 6) Guardrails & automation

**Pre-merge checks (CI)**

- *Include-scan*: fail if any banned paths/extensions appear tracked (`.storage/**`, `.venv/**`, `*.bk.*`, caches, `.trash/**`, `.quarantine/**`).
- *Packaging determinism*: rebuild `artifacts/…` and verify SHA256 unchanged.

**Pre-commit hooks (local, optional)**

- Deny-add for `.storage/**`, keys, tokens, and virtualenvs.
- Normalize/rename any `*.bak*` → `*.bk.<UTC>`.

**ReportKit retention**

- `hestia/tools/utils/reportkit/retention.py` enforces the TTL policy on `hestia/reports/`.

**Sweeper (workspace hygiene)**

- Nightly task (cron/automation) that:

  1. Deletes `.trash/` items older than 14d.
  2. Prunes `*.bk.<UTC>` in-place backups older than 7d.
  3. Keeps N latest vault backups per base-name; deletes older unless pinned.
  4. Runs ReportKit retention for `hestia/reports/`.

# 7) Runtime & secrets policy (non-negotiable)

- `.storage/**`, `.cloud/**`, authentication tokens, sessions, PEM/keys, and device databases are **never** committed.
- Virtualenvs (`.venv*/`), dependency `deps/`, caches (`.mypy_cache/`, `__pycache__/`, etc.) are **never** committed.
- If already tracked, untrack in place and add to `.gitignore` (see Migration).

# 8) Tooling conventions

- All scripts must accept `--out-dir hestia/reports` and write into a date/batch.
- All generated files include compact frontmatter with: tool, script, created_at (UTC), batch_id, input_path, rows/hash.
- Atomic writes (`os.replace`) and `0600` perms best-effort for sensitive outputs.

# 9) Folder standardization quick map

```
.trash/                   # temp deletes, auto-swept
.quarantine/              # blocked from merge; manual review
artifacts/                # reproducible bundles + MANIFEST + checksums
archive/                  # curated snapshots + README/provenance
hestia/reports/           # all generated outputs (batched)
hestia/workspace/archive/vault/backups/     # long-lived backups (kept)
hestia/workspace/archive/vault/bundles/     # manually stored bundles (optional)
hestia/workspace/archive/vault/deprecated/  # human-curated deprecated materials
```

# 10) Migration plan (one-time, scripted)

1. **Ignore**: extend `.gitignore` for banned paths (`.storage/**`, `.venv*/`, `deps/`, caches, `hestia/reports/**`, `.trash/**`, `.quarantine/**`, `artifacts/**`, `*.bk.*`).
2. **Untrack**: `git rm -r --cached` the banned directories/files while keeping them on disk.
3. **Backups**: rename existing `*.bak*` to the canonical `.bk.<UTC>` (or move to `hestia/workspace/archive/vault/backups/`).
4. **Reports**: relocate ad-hoc outputs into `hestia/reports/<date>/<batch>/` (or delete if superseded).
5. **CI**: enable include-scan + determinism checks; block merges on violations.

# 11) Acceptance criteria

- CI include-scan rejects any tracked files under banned paths.
- Packaging job verifies deterministic SHA256 for `artifacts/*` bundles.
- Sweeper and ReportKit retention reduce `hestia/reports/` and in-place backups per policy.
- No secrets or runtime state remain in Git history’s tip; new violations are blocked.

---

## Meta‑Review: Weak points / uncertainty to harden (not part of ADR)

1. **Legacy backups naming variance** — mixed `.bak`, `.bak-<localtime>`, and dotted timestamps will exist for a while. *Mitigation*: provide a small renamer script plus an allowlist in include-scan for a grace period; CI warns (not fails) for 30 days, then flips to fail.
2. **OS/filesystem semantics** — BusyBox/Alpine environments may ignore `chmod 0600` or `fsync` on some mounts. *Mitigation*: treat perms/fsync as best-effort; do not fail runs; log a warning.
3. **Append-only manifest size** — `_index.jsonl` may grow. *Mitigation*: add optional `reportkit/retention.py --compact-index` that rotates the index monthly.
4. **Human use of `archive/`** — risk of dumping, not curating. *Mitigation*: require a README and a `PROVENANCE.json` (generated via ReportKit) for any new `archive/` folder.
5. **Accidental tracking of `.storage/**`** — editors may stage files. *Mitigation*: add a pre-commit *deny* hook and CI hard-fail if `.storage/**` appears in Git.

## Meta‑Review: Quick wins / big gains (not part of ADR)

- **One-liner hygiene target**: `make hygiene` to (a) untrack banned paths, (b) move/rename legacy backups, (c) run ReportKit retention, (d) print a delta summary.
- **Deterministic bundles by default**: template a `scripts/make_bundle.sh` that always writes MANIFEST + SHA256 and runs a reproducibility probe.
- **Frontmatter verifier gate**: lightweight CI job `frontmatter_verify.py` over last batch to guarantee provenance headers are present.
- **Batch “latest” symlink**: keep `hestia/reports/latest` pointing to most recent batch for quick navigation.

## Token Blocks

```yaml
TOKEN_BLOCK:
  notes: lifecycle policy validation checks
  checks:
    - name: reports-structure
      cmd: "test -d /config/hestia/reports || echo 'reports dir missing'"
    - name: backups-pattern
      cmd: "ls /config/**/*.bk.* >/dev/null 2>&1 || true"
    - name: index-jsonl-exists
      cmd: "test -f /config/hestia/reports/_index.jsonl || true"
```
