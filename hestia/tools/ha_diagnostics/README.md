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
