# PATCH_ETIQUETTE.md

## Scope
All changes MUST preserve Supervisor-only diagnostics and single control-plane semantics.

## Rules
1) Control-plane
   - `run.sh` is the sole supervisor of Python children.
   - `services.d/echo_responder/down` MUST remain present.

2) Observability
   - Emit DIAG to **stdout first**, append to file best-effort.
   - Maintain `HEALTH_SUMMARY` cadence at **15s** when health checks enabled.
   - Keep file→stdout forwarder guarded by `LOG_FORWARD_STDOUT=1`.

3) Safety
   - Never block container startup waiting on external resources.
   - On child exit, log `dead=<proc>(<pid>) exit_code=<code>` and respawn.
   - Respect `/tmp/bb8_restart_disabled` if present (manual halt).

4) Config + Schema
   - `config.yaml` must expose `enable_health_checks` and `log_path`.
   - Any new option MUST be reflected in docs and runtime normalization.

5) Commits + ADRs
   - Comply with ADR-0001 commit trailer requirements.
   - Update docs under `docs/` and governance under `docs/ADR/` when behavior changes.
   - Reference ADR-0011 for any ops impacting Supervisor-only flows.

6) Tests & Verification
   - Provide a **Supervisor-only** verification block (`ha addons ...`) with expected matches.
   - Evidence acceptance via DIAG/HEALTH_SUMMARY snapshots.

## Prohibited
- Adding s6 longruns for children covered by run.sh.
- Introducing docker-dependent diagnostics.
- Silencing DIAG or reducing heartbeat visibility.

---

**Token usage advisory**

* Keep prompts compact; prefer structured blocks (YAML/JSON) over prose.
* Reuse the `rehydration_seed` values; avoid restating unchanged context.

**Recommended next GPT startup configuration**

* Role: *Strategos with Copilot liaison* enabled.
* Tools: none required (no web); operate on user-supplied outputs and repo diffs.
* Mode: Supervisor-only; assume no container shell.

**Assumptions / risks to validate on resume**

* Mosquitto availability and credentials unchanged.
* BLE adapter (`/dev/hci0`) remains present after reboots.
* Supervisor logs retain last 2000 lines (rotate if needed).

**Guardrails to enforce**

* ❌ No docker exec/ps diagnostics.
* ✅ All checks via `ha addons info|options|logs`.
* ✅ DIAG lines must include: `run.sh entry`, `RUNLOOP attempt`, `Started bb8_core.*`, `Child exited`, `HEALTH_SUMMARY`.
* ✅ Heartbeats expected to tick; ages must change across ~15s snapshots.

---

**Handoff tag:** `HANDOFF::STRATEGOS::HA-BB8::2025-09-03T06:50Z-001`