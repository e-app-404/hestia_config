# HA Diagnostics — Operator Notes

This tool generates a structured diagnostic report and session metadata for Home Assistant configuration issues.

- Config: TOML-first via `/config/hestia/config/system/hestia.toml` under `[automation.ha_diagnostics]`.
- Modes: triage (default), analysis, remediation, documentation.
- Outputs:
  - Report: `/config/hestia/reports/ha-diagnostics-copilot_{timestamp}.yaml`
  - Meta: `/config/hestia/library/context/meta/copilot_meta_{timestamp}.json`
  - Optional: `patch.diff` (remediation mode only; no live edits)

Usage:

```
python3 /config/hestia/tools/ha_diagnostics/run_diagnostics.py --mode triage
```

CLI Contract

```
python3 /config/hestia/tools/ha_diagnostics/run_diagnostics.py \
  --mode {triage|analysis|remediation|documentation} \
  [--selection-path /path/to/snippet.yaml] \
  [--active-file /path/to/current/file] \
  [--report-dir /override/report/dir] \
  [--meta-dir /override/meta/dir]
```

Acceptance Checks
- AC1 Presence: Missing required artifacts produce a report with `missing_required` and non‑zero exit.
- AC2 Paths: Report `/config/hestia/reports/ha-diagnostics-copilot_{UTCZ}.yaml` and meta `/config/hestia/library/context/meta/copilot_meta_{UTCZ}.json` created.
- AC3 Triaged evidence: `evidence`, `classification`, `followup`, and `CONFIDENCE ASSESSMENT: N%` present.
- AC4 Modes: `analysis`, `remediation`, `documentation` emit their specified sections and confidence.
- AC5 Safety: No writes outside reports/meta; remediation emits `patch.diff` only (no live edits).
