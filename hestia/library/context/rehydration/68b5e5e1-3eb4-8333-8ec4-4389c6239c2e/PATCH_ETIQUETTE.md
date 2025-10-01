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
   - Keep file->stdout forwarder guarded by `LOG_FORWARD_STDOUT=1`.

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
