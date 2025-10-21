Canonical guardrails wrappers

This directory provides canonical tool entrypoints for guardrail checks under the unified tools tree (`/config/hestia/tools`).

Each script here is a thin wrapper that delegates to the existing implementation in `/config/hestia/guardrails/`.

Rationale
- Maintain a cohesive tools namespace under `hestia/tools` per ADR-0024
- Preserve backward compatibility for CI and docs that still reference `hestia/guardrails/`
- Avoid symlinks inside the HA config tree (ADR-0015); use exec/runpy instead

Migration notes
- Consumers may begin calling `hestia/tools/guardrails/<script>` now
- CI workflows referencing `hestia/guardrails/*` continue to work unchanged
- When ready, update workflows/docs to point to the canonical path; wrappers can then remain indefinitely or be retired later
