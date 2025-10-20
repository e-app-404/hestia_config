# Optimized prompt (copy-paste to Strategos / Copilot)

> You are Strategos (γ). Produce an **exhaustive patch plan proposal** for our AppDaemon + room-db stack that drives us to pixel-perfect delivery with no further edits. Scope includes: `room_db_updater`, `activity_tracker`, `valetudo_default_activity`, `room_db_exporter`, the v3.1 `area_mapping.yaml`, and any glue/ops scripts.
>
> **Deliverables required** (no omissions):
>
> 1. Executive summary and goals; explicit in/out of scope; assumptions.
> 2. Precise change list per component (JFDI patches, QoL, code hygiene), with short rationale.
> 3. Concrete code patches (AppDaemon-style Python snippets/diffs) for: robust HTTP endpoints (return `(payload, 200)`), write limiter harmonization, retry/backoff with jitter, idempotent upserts, capability-based admission control (mapping → allowed domain/room), mapping reload endpoint, exporter write-after-update hook, bulk reseed endpoint, and defensive parsing in `activity_tracker`.
> 4. Ops runbooks: preflight/backup, rollout, validation, rollback. Commands must be **HA Terminal safe** (no `\;`), with the correct paths (`/addon_configs/a0d7b954_appdaemon/...` on host; `/config/...` in container).
> 5. Test plan: unit, integration (AppDaemon harness), black-box curl checks, and binary acceptance criteria.
> 6. Observability: structured logging, minimal metrics, and error taxonomy.
> 7. Risk register + mitigations.
> 8. Final **delta-contract** (YAML) and a compact **checklist**.
>
> Assume current env and evidence shared (v3.1 mapping, DB path realities, limiter collisions, exporter 500, etc.). Prefer small, surgical changes over rewrites. Output must be crisp and immediately actionable by Copilot.
