---
id: ADR-0018
title: Workspace lifecycle (trash, archive, bundles) & quarantine policy
status: Proposed
related: [ADR-0008, ADR-0009, ADR-0012]
decision:
  classes:
    - trash: ".trash/ (gitignored, auto-swept)"
    - archive: "archive/ (kept, not packaged)"
    - bundles: "artifacts/ (tar/gz; packaged with manifest)"
    - quarantine: ".quarantine/ (blocked from merge)"
rules:
  - "Include-scan fail if trash/quarantine files appear outside allowed roots."
  - "Packaging step excludes trash/quarantine; archives require manifest+sha256."
acceptance:
  - "CI include-scan catches misplaced temp/binary files."
  - "Packager emits manifest; sha256 stable across reruns."
enforcement_protocols: [include_scan_v2, file_delivery_integrity_v2]
---


ADR to define and channel how to manage files flagged depreated, trash, archived, bundles, tarball, etc.

Need to define:
- Classify and canonicalize folders where specific types of files go (e.g. hestia/vault, root trash/ folder, etc)
- Define automated workspace actions based on file type / extension / location / timestamp


## Token Blocks

```
# misplaced temp/binary detector (example)
./tools/include_scan.sh --deny-ext 'log|tmp|bak|swp' --deny-path '(^|/)\.(trash|quarantine)/?'

# packaging determinism probe
old=$(sha256sum artifacts/release.tar.gz | awk '{print $1}')
# ... rerun packaging ...
new=$(sha256sum artifacts/release.tar.gz | awk '{print $1}')
test "$old" = "$new"
```

---

# ADR-0018 — Workspace hygiene, lifecycle & guardrails (v2)

**id:** ADR-0018
**title:** Workspace lifecycle (trash, archive, bundles) & quarantine policy
**status:** Proposed → Ready for adoption
**related:** ADR-0008, ADR-0009, ADR-0011, ADR-0012
**owner:** Hestia Ops
**scope:** Entire HA config workspace (incl. `hestia/*`; excludes HA-managed `.storage/`)

---

## 1) Problem & goals

The workspace accumulates in-situ backups, temp files, tarballs, and tool outputs with mixed conventions. We now generate reports (ReportKit) and maintenance artifacts (Compactor). We need a **single, simple policy** that:

* Defines **one naming scheme** for backups and generated files.
* Assigns **one home** for reports, bundles, trash, quarantine, and long-term storage.
* Gives **lightweight automation** to prevent bloat (janitor) and **guardrails** to catch drift (include-scan CI / pre-commit).
* Stays **HA-friendly** (never write into `.storage/` directly; compactor operates on copies).

---

## 2) Canonical naming

### 2.1 In‑situ backups (hand-touched files only)

* **Pattern (only allowed):** `name.ext.bak.YYYYMMDDTHHMMSSZ`

  * Example: `configuration.yaml.bak.20250926T154200Z`
* **Rules:**

  * Create **≤ 1** new `.bak.*` per file per minute.
  * **Do not** use `*.bak`, `*.perlbak`, `*.bak-<date>`, `*.bak2`, etc. (janitor normalizes then prunes).
  * Keep brief (see retention). Long-lived copies go to `hestia/vault/backups/`.

### 2.2 Programmatic reports

* Use ReportKit batch dirs: `hestia/reports/YYYYMMDD/<BATCH_ID>/…`
* Embed provenance as **commented front‑matter** (TSV/MD) or `_meta` (JSON). No sidecar meta files.
* Manifest `_index.jsonl` sits at `hestia/reports/_index.jsonl`.

### 2.3 Bundles / packages

* **Pattern:** `name.YYYYMMDDTHHMMSSZ.tar.gz` in `hestia/vault/bundles/`.
* Must include `MANIFEST.json` with SHA256 for contents.

### 2.4 Quarantine & trash

* `.quarantine/` — blocked from merge until human decision.
* `.trash/` — transient, auto-swept. Never committed.

---

## 3) Folder real estate (one purpose per root)

| Path                     | Purpose                                                        | Retention               |
| ------------------------ | -------------------------------------------------------------- | ----------------------- |
| `.trash/`                | Temp & sweep targets                                           | ≤ 7 days                |
| `.quarantine/`           | Manual review / blocked from merge                             | manual                  |
| `hestia/reports/`        | All tool-generated reports (ReportKit batches, `_index.jsonl`) | default 90 days         |
| `hestia/vault/backups/`  | Curated long-term backups (rolled up from in-situ)             | ≥ 180 days or keep-N=10 |
| `hestia/vault/bundles/`  | Deliverable tarballs with manifest                             | ≥ 180 days              |
| `hestia/vault/legacy/`   | Frozen legacy configs/docs                                     | no auto-delete          |
| `hestia/vault/receipts/` | Install/ops receipts & logs                                    | ≥ 180 days              |
| `hestia/tools/_legacy/`  | Old tooling kept for reference                                 | no auto-delete          |

> Migration: rename any `hestia/vault/deprecated/` to `hestia/vault/legacy/` at next window.

---

## 4) Lifecycle states

1. **Working/Staging** — Edits may create short‑lived `*.bak.<UTC>`; tools write only under `hestia/reports/…`.
2. **Promotion** — Important point‑in‑time copies are **copied** to `hestia/vault/backups/`.
3. **Archive/Bundle** — Shareable exports → `hestia/vault/bundles/` (with manifest + SHA).
4. **Quarantine** — Suspicious/invalid outputs → `.quarantine/` (blocks merge).
5. **Retirement** — Janitor prunes old `.bak.*`, report batches, and drains `.trash/`.

---

## 5) Guardrails & automation

### 5.1 Include-scan (CI / pre-commit)

Fail if forbidden extensions or misplaced files appear outside allowed roots.

* **Forbidden extensions (outside allowed roots):** `*.log`, `*.tmp`, `*.swp`, `*.perlbak`, `*.bak` (bare), `*.bak.*` (outside policy), editor swap files.
* **Allowed messy roots:** `.trash/`, `.quarantine/`, `hestia/reports/`, `hestia/vault/*`.

**Minimal script (POSIX):**

```bash
# hestia/tools/utils/ops/include_scan.sh
set -euo pipefail
ALLOWED='^\.(trash|quarantine)\/|^hestia\/reports\/|^hestia\/vault\/'
BAD=()
while IFS= read -r -d '' f; do
  case "$f" in
    *.log|*.tmp|*.swp|*.perlbak|*.bak)
      echo "$f" | grep -Eq "$ALLOWED" || BAD+=("$f");;
    *.bak.*)
      # tolerate only if filename matches .bak.YYYYMMDDTHHMMSSZ
      echo "$f" | grep -Eq ".*\.bak\.[0-9]{8}T[0-9]{6}Z$" || {
        echo "$f" | grep -Eq "$ALLOWED" || BAD+=("$f");
      };;
  esac
done < <(git ls-files -z)
if [ ${#BAD[@]} -gt 0 ]; then
  printf "[include-scan] FAIL\n%s\n" "${BAD[@]}"; exit 1;
fi
echo "[include-scan] OK"
```

### 5.2 Janitor (cron/manual; BusyBox-safe)

* Normalizes stray backups → `*.bak.<UTC>` then **rolls up** recent ones to `hestia/vault/backups/` and **prunes** aged ones.
* Prunes `hestia/reports` batches older than TTL.
* Empties `.trash/` older than 7 days.

**Minimal script (POSIX):**

```bash
# hestia/tools/utils/ops/workspace_janitor.sh
set -euo pipefail
ROOT="${1:-.}"; TTL_BAK_DAYS="${TTL_BAK_DAYS:-14}"; TTL_REPORT_DAYS="${TTL_REPORT_DAYS:-90}"
find "$ROOT" -path "*/.git/*" -prune -o \
  \( -name "*.bak" -o -name "*.perlbak" -o -regex ".*\\.bak[-_0-9TZ:]*$" \) -type f -print0 | \
  while IFS= read -r -d '' p; do ts=$(date -u +"%Y%m%dT%H%M%SZ"); n="${p%.bak}.bak.$ts"; [ "$p" = "$n" ] || mv -f "$p" "$n"; done
mkdir -p "$ROOT/hestia/vault/backups"
find "$ROOT" -path "*/hestia/vault/backups/*" -prune -o -name "*.bak.[0-9TZ]*" -type f -mtime -"$TTL_BAK_DAYS" -exec cp -n {} "$ROOT/hestia/vault/backups/" \;
find "$ROOT" -name "*.bak.[0-9TZ]*" -type f -mtime +"$TTL_BAK_DAYS" -delete
find "$ROOT/hestia/reports" -mindepth 2 -maxdepth 2 -type d -mtime +"$TTL_REPORT_DAYS" -exec rm -rf {} + 2>/dev/null || true
find "$ROOT/.trash" -type f -mtime +7 -delete 2>/dev/null || true; find "$ROOT/.trash" -type d -empty -delete 2>/dev/null || true
echo "[janitor] done"
```

> For manifest-aware pruning, you may use ReportKit’s `retention.py`; keep this shell version for BusyBox environments.

---

## 6) Retention defaults (configurable)

* **In‑situ backups `*.bak.*`:** keep **14 days** locally; roll copies into `hestia/vault/backups/` for **≥ 180 days** or **N=10 latest per source**.
* **Reports:** keep **90 days** (delete whole batch dirs); keep `_index.jsonl` (append‑only audit). Option: track `_index.jsonl` in Git or ignore; see §7.3.
* **Bundles:** keep **≥ 180 days**; no automatic deletion without manual decision.
* **Trash:** delete after **7 days**.
* **Legacy:** never auto-delete.

> Centralize these TTLs in `hestia/tools/utils/ops/policy.env` and source it from the scripts.

---

## 7) Implementation notes

### 7.1 HA alignment

* Never write tooling outputs to `.storage/`. Copy inputs out; write to `hestia/reports/` and `hestia/vault/*` only.
* Compactor is offline-only; registry swaps are explicit, audited operations.

### 7.2 Deterministic bundles

* Prefer Python `tarfile` with normalized metadata (name order, mtime fixed) for reproducible SHA256; BusyBox tar fallback allowed.

### 7.3 Git ignore strategy for reports

* Default: `hestia/reports/**` ignored, **but** keep `_index.jsonl` tracked via negative rule if desired.

  * Example `.gitignore` in `hestia/reports`: `*` then `!_index.jsonl`
* Alternative: ignore `_index.jsonl` too if you want zero churn in Git.

---

## 8) Acceptance

* **Naming:** All new backups use `*.bak.<UTC>`; janitor normalizes strays.
* **Structure:** Tools only write to `hestia/reports/…` (with front‑matter/manifest) or `hestia/vault/*`.
* **Guardrails:** include-scan fails on drift; merges blocked until fixed.
* **Retention:** running janitor removes aged `.bak.*` and report batches per policy.
* **Bundles:** manifest + deterministic SHA across reruns.

---

## 9) Rollout (surgical, low‑risk)

1. Create roots: `.trash/`, `.quarantine/`, `hestia/reports/`, `hestia/vault/{backups,bundles,legacy,receipts}`.
2. Drop `include_scan.sh` and `workspace_janitor.sh` into `hestia/tools/utils/ops/`; add `policy.env` for TTLs.
3. Wire pre-commit/CI to run include-scan.
4. Rename `hestia/vault/deprecated/` → `hestia/vault/legacy/`.
5. Announce backup pattern + retention; confirm ReportKit outputs land under `hestia/reports/` only.

---

## 10) Quick commands

```bash
# One-time normalize & sweep
bash hestia/tools/utils/ops/workspace_janitor.sh

# CI guard
bash hestia/tools/utils/ops/include_scan.sh

# Optional: ReportKit retention (manifest-aware)
PYTHONPATH=$(pwd) python3 -m hestia.tools.utils.reportkit.retention \
  --base hestia/reports --older-than 90d --dry-run
```

---

## Meta commentary (not part of the official ADR)

### A) Critical review — weak points & hardening

1. **Ambiguity: tracking `_index.jsonl` in Git.**
   *Risk:* churn on every run if tracked; invisibility if ignored.
   **Harden:** default to **ignored** in Git; add a separate `hestia/reports/_rollup.json` (manually refreshed) if you need a stable, committed snapshot. Update §7.3 accordingly when you choose.

2. **Janitor safety on large trees.**
   *Risk:* unintended traversal into vendor dirs or symlinks.
   **Harden:** add `-path '*/node_modules/*' -prune -o` and `-xtype l -prune` to `find` guards; add `ROOT` sanity check (must contain `.git` or `configuration.yaml`).

3. **Reproducible bundles on BusyBox.**
   *Risk:* BusyBox tar lacks `--sort=name`/`--mtime`.
   **Harden:** provide a tiny Python `mkbundle.py` (uses `tarfile` + fixed mtime/uid/gid) and prefer it in scripts.

4. **Time format collisions.**
   *Risk:* multiple backups within one second.
   **Harden:** allow optional suffix `__2`, `__3` if the exact timestamp exists; scripts should probe and increment.

5. **Policy sprawl.**
   *Risk:* TTLs hard-coded across scripts.
   **Harden:** central `policy.env` with `TTL_BAK_DAYS`, `TTL_REPORT_DAYS`, etc., sourced by both janitor and include-scan.

6. **Quarantine governance.**
   *Risk:* items sit forever.
   **Harden:** require a `REASON.txt` and auto‑open a GitHub issue/label when files appear; janitor does **not** delete quarantine.

7. **Edge formats of backups.**
   *Risk:* editors create hidden swap/backup files.
   **Harden:** extend include-scan to flag `*~`, `.#*`, `*.orig`, `.DS_Store`.

### B) Quick wins & big gains

1. **Single `policy.env`**  → instant consistency across tools; 5‑minute change.
2. **Tiny `mkbundle.py`**  → deterministic tarballs everywhere; removes SHA drift.
3. **Negative rule in `hestia/reports/.gitignore`**  → choose whether `_index.jsonl` is tracked with a one‑line change.
4. **Root sanity check in janitor**  → prevents running janitor in the wrong directory; negligible cost.
5. **Include-scan as pre-commit hook**  → stops junk before it ever enters Git.


---
id: ADR-0018
title: "Workspace hygiene, lifecycle & quarantine policy"
status: Proposed (Ready to adopt)
owners: [hestia-core]
author: 
  - "Evert Appels"
  - "Strategos"
related: [ADR-0008, ADR-0009, ADR-0012]
date: 2025-09-26
last_updated: 2025-09-26
tags: ["architecture", workspace, lifecycle, quarantine, trash, archive, bundles, guardrails, automation]
---

# 1) Purpose

Establish one simple, consistent system to name, place, retain, and clean up non-source files in the Home Assistant (Hestia) workspace. The goals are:

* Prevent repo bloat and ambiguity.
* Make provenance and retention deterministic.
* Keep runtime/state and secrets out of Git.
* Keep generated reports and bundles discoverable and easy to prune.

# 2) Scope

Covers *all* non-source artifacts in the repo: backups, temporary files, reports, diagnostics, tarballs/bundles, archives, quarantined files, and deprecated materials. Does **not** change how app code/config is structured (see ADR‑0008/0009) but constrains where and how tools write files.

# 3) Canonical directories (top-level real estate)

* `.trash/` — temporary trash (gitignored). Auto-swept by TTL.
* `.quarantine/` — blocked/suspect items not eligible to merge (gitignored). Manual review only.
* `artifacts/` — reproducible release bundles/tarballs **with** manifest & checksums (gitignored).
* `archive/` — curated, long-lived reference snapshots (kept; not auto-packaged). Must include README (+ provenance).
* `hestia/reports/` — all tool/script output batches (gitignored). Structured by date/batch.
* `hestia/vault/` — long-term human-curated materials (kept). Subfolders: `backups/`, `bundles/` (manual), `deprecated/`.

> Git policy: `.storage/`, `.venv*/`, `deps/`, caches, token stores and any runtime state are **never** tracked by Git.

# 4) File naming (simple & UTC-safe)

Times use compact UTC format `YYYYMMDDTHHMMSSZ`. Avoid spaces/colons.

**Backups (in-place, transient)**

* Pattern: `<name>.bk.<UTC>` (e.g., `core.entity_registry.bk.20250926T145011Z`).
* Permissions: `0600` if possible.
* Default TTL: 7 days (then auto-pruned or promoted).

**Backups (vault, long-lived)**

* Location: `hestia/vault/backups/`.
* Pattern: `<name>.<UTC>.bk` or `<name>.bk.<UTC>` (both acceptable here; prefer the former for lexicographic sort).
* Retention: keep N latest per base-name (default N=5) + any manually pinned ones.

**Bundles / release artifacts**

* Location: `artifacts/`.
* Pattern: `<label>__<UTC>__<tag>.tgz`.
* Must include: `MANIFEST.json` and `SHA256SUMS` (reproducible build expectation). Determinism probe runs in CI.

**Reports / diagnostics**

* Location: `hestia/reports/<YYYYMMDD>/<UTC>__<tool>__<label>/`.
* Each file includes a short frontmatter header (commented) or `_meta` alongside JSON.
* Batch is discoverable via append-only `hestia/reports/_index.jsonl`.

**Quarantine**

* Location: `.quarantine/`.
* Pattern: `<why>__<UTC>__<original_name>`.

# 5) Lifecycle states & retention

* **Staging** → *generated* (in `hestia/reports/…`) → optional **archive**/**artifacts** promotion → eventual **prune** by TTL.
* **In-place backups**: auto-prune after 7d unless promoted to vault.
* **Trash**: `.trash/` pruned after 14d.
* **Reports**: default TTL 90d under `hestia/reports/` (CLI enforces; keep latest K per prefix/label).
* **Artifacts**: no TTL; reproducible builds only (must pass determinism check).
* **Archive**/**Vault**: no TTL; human-curated, with README and provenance.

# 6) Guardrails & automation

**Pre-merge checks (CI)**

* *Include-scan*: fail if any banned paths/extensions appear tracked (`.storage/**`, `.venv/**`, `*.bk.*`, caches, `.trash/**`, `.quarantine/**`).
* *Packaging determinism*: rebuild `artifacts/…` and verify SHA256 unchanged.

**Pre-commit hooks (local, optional)**

* Deny-add for `.storage/**`, keys, tokens, and virtualenvs.
* Normalize/rename any `*.bak*` → `*.bk.<UTC>`.

**ReportKit retention**

* `hestia/tools/utils/reportkit/retention.py` enforces the TTL policy on `hestia/reports/`.

**Sweeper (workspace hygiene)**

* Nightly task (cron/automation) that:

  1. Deletes `.trash/` items older than 14d.
  2. Prunes `*.bk.<UTC>` in-place backups older than 7d.
  3. Keeps N latest vault backups per base-name; deletes older unless pinned.
  4. Runs ReportKit retention for `hestia/reports/`.

# 7) Runtime & secrets policy (non-negotiable)

* `.storage/**`, `.cloud/**`, authentication tokens, sessions, PEM/keys, and device databases are **never** committed.
* Virtualenvs (`.venv*/`), dependency `deps/`, caches (`.mypy_cache/`, `__pycache__/`, etc.) are **never** committed.
* If already tracked, untrack in place and add to `.gitignore` (see Migration).

# 8) Tooling conventions

* All scripts must accept `--out-dir hestia/reports` and write into a date/batch.
* All generated files include compact frontmatter with: tool, script, created_at (UTC), batch_id, input_path, rows/hash.
* Atomic writes (`os.replace`) and `0600` perms best-effort for sensitive outputs.

# 9) Folder standardization quick map

```
.trash/                # temp deletes, auto-swept
.quarantine/           # blocked from merge; manual review
artifacts/             # reproducible bundles + MANIFEST + checksums
archive/               # curated snapshots + README/provenance
hestia/reports/        # all generated outputs (batched)
hestia/vault/backups/  # long-lived backups (kept)
hestia/vault/bundles/  # manually stored bundles (optional)
hestia/vault/deprecated/  # human-curated deprecated materials
```

# 10) Migration plan (one-time, scripted)

1. **Ignore**: extend `.gitignore` for banned paths (`.storage/**`, `.venv*/`, `deps/`, caches, `hestia/reports/**`, `.trash/**`, `.quarantine/**`, `artifacts/**`, `*.bk.*`).
2. **Untrack**: `git rm -r --cached` the banned directories/files while keeping them on disk.
3. **Backups**: rename existing `*.bak*` to the canonical `.bk.<UTC>` (or move to `hestia/vault/backups/`).
4. **Reports**: relocate ad-hoc outputs into `hestia/reports/<date>/<batch>/` (or delete if superseded).
5. **CI**: enable include-scan + determinism checks; block merges on violations.

# 11) Acceptance criteria

* CI include-scan rejects any tracked files under banned paths.
* Packaging job verifies deterministic SHA256 for `artifacts/*` bundles.
* Sweeper and ReportKit retention reduce `hestia/reports/` and in-place backups per policy.
* No secrets or runtime state remain in Git history’s tip; new violations are blocked.

---

## Meta‑Review: Weak points / uncertainty to harden (not part of ADR)

1. **Legacy backups naming variance** — mixed `.bak`, `.bak-<localtime>`, and dotted timestamps will exist for a while. *Mitigation*: provide a small renamer script plus an allowlist in include-scan for a grace period; CI warns (not fails) for 30 days, then flips to fail.
2. **OS/filesystem semantics** — BusyBox/Alpine environments may ignore `chmod 0600` or `fsync` on some mounts. *Mitigation*: treat perms/fsync as best-effort; do not fail runs; log a warning.
3. **Append-only manifest size** — `_index.jsonl` may grow. *Mitigation*: add optional `reportkit/retention.py --compact-index` that rotates the index monthly.
4. **Human use of `archive/`** — risk of dumping, not curating. *Mitigation*: require a README and a `PROVENANCE.json` (generated via ReportKit) for any new `archive/` folder.
5. **Accidental tracking of `.storage/**`** — editors may stage files. *Mitigation*: add a pre-commit *deny* hook and CI hard-fail if `.storage/**` appears in Git.

## Meta‑Review: Quick wins / big gains (not part of ADR)

* **One-liner hygiene target**: `make hygiene` to (a) untrack banned paths, (b) move/rename legacy backups, (c) run ReportKit retention, (d) print a delta summary.
* **Deterministic bundles by default**: template a `scripts/make_bundle.sh` that always writes MANIFEST + SHA256 and runs a reproducibility probe.
* **Frontmatter verifier gate**: lightweight CI job `verify_frontmatter.py` over last batch to guarantee provenance headers are present.
* **Batch “latest” symlink**: keep `hestia/reports/latest` pointing to most recent batch for quick navigation.
