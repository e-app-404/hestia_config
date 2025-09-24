---
title: ADR-0014: OOM Mitigation & Recorder Policy
date: 2025-09-18
status: Approved
tags: ["performance", "memory", "oom", "recorder", "database", "policy"]
author:
  - "Platform / Home-Ops"
  - "GitHub Copilot (assisted)"
  - "Evert Appels"
related: 
  - ADR-0010
  - ADR-0012
---

# ADR-0014 — OOM Mitigation & Recorder Policy

## Status
Accepted

## Context
Home Assistant host experienced recurrent OOM events leading to service instability. Logs indicated heavy history/recorder growth and integration churn (e.g., diagnostics/media). Absolute path divergence also impaired tooling, but is handled by ADR-0010.

## Decision
1. Enforce conservative recorder policy:
   - , , 
   - Exclude noisy/non-essential domains; include core entity domains.
2. Add OOM guard package with:
   -  memory telemetry
   - Threshold knob (, default 90)
   - 5-minute sustained high-memory persistent notification
3. Keep a **single**  definition (guarded by CI/enforcer).
4. No automatic restarts; notify operator for targeted remediation.

## Consequences
- Smaller DB, lower memory churn, faster recorder queries.
- Clear signal when memory pressure persists.

## Rollout
- Package-based; no changes to  beyond existing package include.
- Restart Home Assistant Core to apply.

## Links
- ADR-0010 — Workspace Shape & Neutral Path (/n/ha)
