---
title: "Stage: Guardrails wrappers under canonical tools path"
actor: copilot
timestamp_utc: 2025-10-21T21:00:00Z
adr_refs:
  - ADR-0024
  - ADR-0015
  - ADR-0032
status: staged
---

Summary
- Create wrappers under /config/hestia/tools/guardrails that delegate to /config/hestia/guardrails/*.
- Establish canonical tools namespace while preserving existing CI references.

Files added
- hestia/tools/guardrails/README.md
- hestia/tools/guardrails/check_duplicate_keys.py
- hestia/tools/guardrails/check_unique_automation_ids.py
- hestia/tools/guardrails/check_unique_unique_ids.py
- hestia/tools/guardrails/check_no_symlinks.sh
- hestia/tools/guardrails/check_recorder_uniqueness.sh
- hestia/tools/guardrails/check_rest_command_guardrails.sh

Validation
- Run workspace path linter (ADR-0024) and basic shell/python execution sanity.

Next
- Optionally update internal tasks/docs to prefer hestia/tools paths.
- Defer CI workflow updates to a later approved change.
