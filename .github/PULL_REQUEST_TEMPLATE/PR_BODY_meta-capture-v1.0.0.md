## Summary
Meta-Capture v1.0.0 — governed pipeline: TOML-only config, GREEN-only apply with ruamel merges, pin-lock, secrets/schema gates, limits, idempotency, broker auto-detect (rewrite/replace) with evidence, routing suggestions for ORANGE, reports+ledger evidence.

## Changes
- `meta_capture.py`: governed merges, pin-lock, secret-rules (YAML), schema, limits, idempotency, run-lock, broker auto-detect, routing suggestions, severity/skip reasons, APU objects, atomic writes + .bak.
- `hestia.toml`: `[automation.meta_capture]` + `[apply]` + `[retention]`.
- `cli.conf`: dry-run/apply, prune helpers.
- Ignore: reports, ledger, staging.
- Examples: operator-only ORANGE demo, canonical GREEN sample.

## Evidence (commands)
```bash
# Dry-run → report + severity_counts
make -C /config/hestia/tools/meta_capture dry-run verify-policy

# GREEN apply with broker (non-idempotent)
echo "# nudge $RANDOM" >> /config/hestia/workspace/staging/sample_meta_capture_green__tmp.yaml
make -C /config/hestia/tools/meta_capture apply-green
jq '.results[0] | {traffic_light,applied,skip_reason,broker}' \
  $(ls -1t /config/hestia/workspace/reports/meta_capture/*__apply.json | head -1)

# Idempotency re-apply
make -C /config/hestia/tools/meta_capture apply-green
jq '.results[0] | {traffic_light,applied,skip_reason}' \
  $(ls -1t /config/hestia/workspace/reports/meta_capture/*__apply.json | head -1)

# Secrets RED
echo 'notes: ["ghp_1234567890abcdefghijklmnopqrstuvwxyzABCDE"]' > /config/hestia/workspace/staging/secret_probe.yaml
make -C /config/hestia/tools/meta_capture dry-run || true
jq '.results[]|select(.source|endswith("secret_probe.yaml"))|{traffic_light,skip_reason}' \
  $(ls -1t /config/hestia/workspace/reports/meta_capture/*__dry_run.json | head -1)
```

## Risk & Rollback

* Risk: low; GREEN-only apply with strict gates.
* Rollback: disable `[apply].use_write_broker` or pin prior tag; revert last commit; reports/ledger remain for audit.
