Canonical guardrails (canonical path)

This directory hosts the canonical implementations and entrypoints for guardrail checks under the unified tools tree (`/config/hestia/tools`).

Status
- Live implementations are here under `hestia/tools/guardrails/*`
- Legacy `hestia/guardrails/*` paths have been decommissioned and replaced with deprecation stubs (non‑executable) to prevent drift

Rationale
- Maintain a cohesive tools namespace under `hestia/tools` per ADR-0024
- Avoid symlinks inside the HA config tree (ADR-0015); prefer direct invocation
- Align documentation and CI to a single canonical location

Migration notes
- Consumers should call `hestia/tools/guardrails/<script>`
- Any remaining references to `hestia/guardrails/*` should be updated; stubs exit non‑zero to surface misuse

