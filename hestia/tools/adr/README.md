ADR Governance Tools
====================

This directory contains the canonical ADR front‑matter verifier and a complementary normalizer.

- frontmatter_verify.py — Validates ADR files against rules in `hestia/config/meta/adr.toml`.
- frontmatter-normalize.py — Applies safe, config‑driven normalizations (dry‑run by default).

Both tools emit timestamped reports under `/config/hestia/reports/YYYYMMDD/` and maintain a stable latest copy and JSONL index for dashboards.

Verifier
--------

Usage:

- python3 hestia/tools/adr/frontmatter_verify.py [--config PATH] [--adr-dir PATH] [--level basic|standard|strict] [--report] [--report-dir DIR]

Notes:
- Default level is basic (CI‑friendly): only missing front‑matter is ERROR; most issues are WARN.
- Strict level is available for developers via a VS Code task (“ADR: Frontmatter Verify (strict)”).
- Stable latest report: `/config/hestia/reports/frontmatter-adr.latest.log`.

Normalizer
----------

Purpose: Apply low‑risk, schema‑informed cleanups so ADRs conform to governance without manual editing.

Usage:
- python3 hestia/tools/adr/frontmatter-normalize.py [--config PATH] [--adr-dir PATH] [--level basic|standard|strict] [--apply] [--report] [--report-dir DIR]

Behavior by level:
- basic: normalize status aliases (via adr.toml), coerce related/supersedes to ADR‑#### arrays, add TOKEN_BLOCK if missing. No other content rewrites.
- standard: includes basic + regenerate slug from title (kebab‑case) if invalid, ensure TOKEN_BLOCK present.
- strict: includes standard + prefix ADR ID to title if missing, bump `last_updated` when changes applied.

Safety:
- Dry‑run by default. Use `--apply` to write changes. Writes use atomic replace per ADR‑0027.
- Stable latest report: `/config/hestia/reports/adr-frontmatter-normalize.latest.log`.

Reports & Index
---------------

Both tools write:
- Timestamped report: `/config/hestia/reports/YYYYMMDD/<tool>__<UTC>__report.log`
- Stable latest: `/config/hestia/reports/<tool>.latest.log`
- Index line: `/config/hestia/reports/_index.jsonl`

Quick‑win workflow
------------------

1) Run the normalizer in dry‑run with report.
2) Review `adr-frontmatter-normalize.latest.log` for proposed actions.
3) If acceptable, re‑run with `--apply` (optionally limit to a subset via `--adr-dir`).
4) Run the verifier in strict mode with report and review `frontmatter-adr.latest.log`.

Common quick wins:
- Status aliases: e.g., “Approved” → “Accepted”.
- related/supersedes arrays: convert mixed entries to pure ADR ID lists.
- TOKEN_BLOCK: insert a minimal section if missing.
- Slug regeneration from title if invalid or drifted.

Governance & ADRs
-----------------

- ADR‑0009: ADR governance and formatting policy.
- ADR‑0024: Path standards — tools read/write under `/config` only.
- ADR‑0027: File writing governance — atomic replaces and audit trails.

CI Integration
--------------

- CI runs the verifier at `--level basic` to avoid blocking on non‑critical issues.
- Developers can run strict verification locally and apply normalizations as needed.
