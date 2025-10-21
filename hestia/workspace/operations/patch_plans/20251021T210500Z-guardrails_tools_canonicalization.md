---
title: Guardrails tool canonicalization (wrappers-first)
author: copilot
timestamp_utc: 2025-10-21T21:05:00Z
adr_refs:
  - ADR-0024: Canonical config path
  - ADR-0015: Symlink policy
  - ADR-0032: Patch operation workflow
scope_guards:
  - No deletion of existing hestia/guardrails scripts
  - No symlinks inside /config
  - Only additive wrappers under hestia/tools/guardrails
validation:
  - Run path lint (ADR-0024)
  - Ensure wrappers exec/runpy to backing scripts
---

Plan
1) Add wrappers under /config/hestia/tools/guardrails delegating to /config/hestia/guardrails/*
2) Keep CI workflows pointing to hestia/guardrails for now; document canonical path in README
3) Later phase (separate PR/patch): update workflows/docs to point to hestia/tools/guardrails

Risk & rollback
- Low risk: wrappers are additive and do not change CI references
- Rollback: remove the new wrapper files
