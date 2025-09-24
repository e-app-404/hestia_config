---
title: "ADR-0013: Source→Core Config Merge via extracted_config (Meta-Capture Pipeline)"
date: 2025-09-20
status: Proposed
author:
  - "Platform / Home-Ops"
  - "GitHub Copilot (assisted)"
  - "Strategos"
related:
  - ADR-0007
  - ADR-0009
  - ADR-0010
supersedes: []
last_updated: 2025-09-20
tags: ["meta-capture", "configuration", "merge", "governance", "secrets"]
---

# ADR-0013 — Source→Core Config Merge via `extracted_config` (Meta-Capture Pipeline)

## Table of Contents
1. Context  
2. Decision  
3. Scope  
4. Methodology  
5. Functional & Non-Functional Requirements  
6. Emitted Tokens (Governance Annotations)  
7. Expected I/O  
8. Merge Rules (Deterministic)  
9. Tooling & Runtime Behavior (incl. Copilot)  
10. Security & Compliance  
11. Rollout Plan  
12. Consequences  
13. Examples  
14. Acceptance Criteria  
15. Enforcement & Compliance with ADR-0009  
16. Open Questions  
17. TOKEN_BLOCK

## 1) Context

We routinely capture small, source-of-truth snippets (Home Assistant, Zigbee2MQTT, MQTT, device metadata) as normalized YAML under a common schema (`extracted_config`, `transient_state`, `relationships`, `suggested_commands`, `notes`). These must be merged into canonical **core configuration** while preserving idempotency, auditability, and safety (secrets handling, stable device paths).

Past merges were ad-hoc, risking drift, clobbering, or ephemeral state leaking into canonical files.

## 2) Decision

Adopt a **deterministic, token-guided merge pipeline**:

- Stage incoming snippets in `/config/hestia/staging/`.
- Validate schema; **route by domain**; perform **keyed upsert** into `/config/hestia/core/config/`.
- Enforce **non-clobber** rules and governance annotations (tokens).
- Extract secrets to `secrets.yaml`; rewrite references via `!secret`.
- Prefer stable device paths (`/dev/serial/by-id/...`) over ephemeral (`/dev/ttyUSB*`).
- Emit diffs + human summaries to `/config/hestia/audits/`.
- Gate write-backs via CI with lint/schema/secret guards.
- This ADR defines methodology, requirements, emitted tokens, expected I/O, and permitted GitHub Copilot influence.

## 3) Scope

**Inputs:** Any file conforming to meta-capture schema (minimum: `extracted_config` map).  
**Domains:** `homeassistant`, `mqtt`, `zigbee2mqtt`, `addons`, `devices`, `repo`.  
**Out of scope:** Live service orchestration (handled by HA/Supervisor flows).

## 4) Methodology

### 4.1 Repository Layout

```text
/config/hestia/
core/config/          # canonical merged configs (per-domain YAML)
staging/              # intake of captured snippets
procedures/           # human SOPs (markdown)
tools/                # merge routers, validators, guards
audits/               # before/after snapshots, diffs, changelogs
```

### 4.2 Pipeline Phases

1) **Intake & Sanity**
- Drop `*.yaml` in `staging/` as `{ISO8601}-{source}.yaml`.
- Validate minimal schema:
  - MUST contain `.extracted_config` (map).
  - `.transient_state`, `.relationships`, `.suggested_commands`, `.notes` optional.
- Normalize quoting and map ordering for stable diffs.

2) **Routing**
- Split `extracted_config` into **domain files**:
  - `.home_assistant` → `core/config/homeassistant.yaml`
  - `.mqtt` → `core/config/mqtt.yaml`
  - `.zigbee2mqtt` → `core/config/zigbee2mqtt.yaml`
  - `.addons[]` (keyed by `slug`) → `core/config/addons.yaml`
  - `.devices` → `core/config/devices.yaml`
  - `.repo` → `core/config/repo.yaml`

3) **Merge (Keyed Upsert)**
- **Maps:** Shallow merge; incoming **non-empty** wins unless target key is **pinned**.
- **Sequences of objects:** Treat as maps keyed by stable field (`slug`, `id`, `device_ieee`), then upsert.
- **Ephemeral** fields (timestamps, RSSI, last_seen) **ignored** unless whitelisted.

4) **Stability & Safety Guards**
- Serial ports: rewrite `/dev/ttyUSB*` → `/dev/serial/by-id/...` when known.
- Secrets: values matching `/password|token|key|secret/i` or `x-governance.secret: true` are moved to `secrets.yaml` and referenced via `!secret`.
- Respect governance tokens (see §6).

5) **Audit & Gate**
- Emit unified diff + human summary into `audits/`.
- CI checks: YAML validity, schema, secrets leakage, pinned-key integrity, shellcheck for scripts.

6) **Write-Back (Optional)**
- If canonical files are deployment sources, copy to service paths and restart via existing HA commands under an explicit `DEPLOY_WRITEBACK=1` flag.

## 5) Functional & Non-Functional Requirements

### Functional
- **R-F1**: Accept any compliant meta-capture YAML; reject otherwise with actionable error.
- **R-F2**: Deterministic routing and merge per domain.
- **R-F3**: Keyed upsert for lists using stable identifiers.
- **R-F4**: Secrets extraction + reference rewrite.
- **R-F5**: Diff + summary artifacts per merge.
- **R-F6**: Honor governance tokens (§6).

### Non-Functional
- **R-NF1**: Idempotent merges (re-running yields no change).
- **R-NF2**: Stable, minimal diffs.
- **R-NF3**: No plaintext secrets post-merge (CI enforced).
- **R-NF4**: Tooling version pinning for reproducibility.
- **R-NF5**: Runtime-safe; no auto restarts without explicit flag.

## 6) Emitted Tokens (Governance Annotations)

| Token / Field                         | Type        | Meaning / Effect                                                                 |
|--------------------------------------|-------------|----------------------------------------------------------------------------------|
| `# @pin`                              | comment     | Do not overwrite this key during merge.                                          |
| `# @temp`                             | comment     | Temporary value; auto-replace when stable source available.                      |
| `x-governance.managed: true`          | boolean     | Section is tool-managed (automated merges allowed).                              |
| `x-governance.secret: true`           | boolean     | Extract to `secrets.yaml`; replace with `!secret` reference.                     |
| `x-merge.key: <field>`                | string      | For list items: key field to index object (e.g., `slug`).                        |
| `x-merge.strategy: prefer-nonempty`   | string      | Incoming non-empty overrides; empty values ignored.                              |
| `x-merge.strategy: replace`           | string      | Replace entire map/array at this node.                                           |
| `x-origin.source: <name>`             | string      | Provenance (e.g., `ha-cli`, `z2m-scan`).                                         |
| `x-origin.timestamp: <ISO8601>`       | string      | Capture time; ignored in diffs but kept for audit.                               |
| `x-stability.device-path: stable`     | string      | Enforce `/dev/serial/by-id` rewrite.                                             |

> We prefer `x-*` vendor extensions over YAML tags to avoid tooling friction.

## 7) Expected I/O

### Inputs
- One or more `staging/*.yaml` files conforming to meta-capture schema, minimally:
  ```yaml
  extracted_config:
    zigbee2mqtt:
      mqtt:
        server: mqtt://192.168.0.129:1883
      serial:
        port: /dev/serial/by-id/usb-ITead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_dceb7d67ec6aef11a2e599adc169b110-if00-port0
        adapter: zstack
  ```

### Outputs

* Updated canonical domain files under `core/config/` (e.g., `zigbee2mqtt.yaml`, `mqtt.yaml`, `devices.yaml`).
* `audits/{timestamp}-changes.diff` and human summary.
* Optional: updated `secrets.yaml` with newly extracted entries.
* CI logs for validation, lints, guard results.
* (When enabled) write-backs to runtime paths and service restart logs.

### Standardized Errors

* `E-SCHEMA-001`: missing `.extracted_config`
* `E-ROUTE-404`: no routable domains found
* `E-GOV-009`: attempted overwrite of `@pin`
* `E-SECRET-013`: plaintext secret detected post-merge
* `E-STAB-021`: unstable device path unresolved

## 8) Merge Rules (Deterministic)

1. **Map merge**: `target = target * incoming` with **field-level guards**:

   * Skip if `@pin` on target key.
   * Skip if incoming is `null`/empty **and** strategy is `prefer-nonempty`.
2. **Array of objects**: convert to map by `x-merge.key` (heuristics fallback: `slug`, `id`, `ieee`, `name`), upsert, then re-emit as array sorted by key.
3. **Secrets**: move to `secrets.yaml` with key path normalized (`<domain>_<key>`); replace with `!secret <name>`.
4. **Device paths**: normalize to `/dev/serial/by-id/...` when resolvable; else mark with `# @temp`.

## 9) Tooling & Runtime Behavior (incl. GitHub Copilot)

**Pinned tools:**

* `yq` v4.x
* `jq`
* `shellcheck`

**Scripts:**

* `tools/route.sh` — domain splitting
* `tools/merge_*.yq` — domain merges
* `tools/validate.sh` — schema + yaml + guards
* `tools/secrets_guard.sh` — extraction + references

**CI:**

* Runs validate/merge in **dry-run**; posts diff artifact and status checks.
* Blocks merge on any `E-*` error.

**GitHub Copilot — Impact & Guardrails**

* **Allowed:** scaffolding shell/YQ snippets, router templates, test fixtures.
* **Not Allowed:** auto-committing generated changes, inventing secret names/values, bypassing guards.
* **Runtime Impact:** None. Copilot suggestions are reviewed and become static scripts; only pinned tools execute. CI enforces compliance.

## 10) Security & Compliance

* Secrets never stored in canonical domain files; enforced by `E-SECRET-013`.
* Diffs scrub `!secret` values; only keys are shown.
* Optional SARIF export for secret-scan results.
* Provenance retained via `x-origin.*`.

## 11) Rollout Plan

1. Land `tools/` scripts and baseline domain files.
2. Enable CI dry-run on PRs touching `staging/` or `core/config/`.
3. Migrate existing configs by running pipeline once; review diffs; tag pins where needed.
4. Enable optional write-backs behind `DEPLOY_WRITEBACK=1`.

## 12) Consequences

**Pros:** Deterministic merges, stable diffs, safer secrets, fewer footguns, clearer audits.
**Cons:** Overhead for routing scripts/annotations; initial pinning work; token learning curve.

## 13) Examples

**Stable serial rewrite (Z2M):**

```yaml
zigbee2mqtt:
  serial:
    port: /dev/serial/by-id/usb-ITead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_dceb7d67ec6aef11a2e599adc169b110-if00-port0
    adapter: zstack
  x-stability:
    device-path: stable
```

**Pinned broker host (do not overwrite):**

```yaml
mqtt:
  server: mqtt://192.168.0.129:1883  # @pin
```

**Add-on keyed upsert:**

```yaml
addons:
  - slug: core_mosquitto
    enabled: true
    x-merge.key: slug
```

## 14) Acceptance Criteria

* Re-running merge on unchanged staging yields empty diff.
* Attempting to overwrite a `# @pin` field fails with `E-GOV-009`.
* Any detected plaintext secret post-merge fails CI (`E-SECRET-013`).
* Serial device paths in canonical Z2M config use `/dev/serial/by-id/*` (unless explicitly `# @temp`).

## 15) Enforcement & Compliance with ADR-0009

* This ADR complies with ADR-0009 formatting and governance: required front-matter keys, section headers, ToC, fenced machine-parseable blocks.
* CI/githooks validate ADR structure, token block presence, and cross-links (`related`, `supersedes`).
* `last_updated` MUST increment on edits; status changes follow ADR-0009 lifecycle rules.

## 16) Open Questions

* Should per-domain JSON Schemas be enforced in CI for stricter typing?
* Should `transient_state` persist to a telemetry ledger instead of being ignored at merge?

## 17) TOKEN_BLOCK

```yaml
TOKEN_BLOCK:
  accepted:
    - META_CAPTURE_MERGE_PIPELINE
    - KEYED_UPSERT_ARRAYS
    - GOVERNANCE_TOKENS_X_EXT
    - SECRET_EXTRACTION_ENFORCED
    - STABLE_DEVICE_PATHS
    - CI_GUARDS_REQUIRED
    - DIFF_AUDIT_REQUIRED
    - COPILOT_SCAFFOLD_ALLOWED
  requires:
    - ADR_SCHEMA_V1
    - ADR_0009_COMPLIANCE
    - PINNED_TOOLING_VERSIONS
  produces:
    - MERGE_DIFF_ARTIFACT
    - AUDIT_SUMMARY
    - UPDATED_CORE_CONFIG
  drift:
    - DRIFT: plaintext_secret_in_core
    - DRIFT: missing_x_merge_key
    - DRIFT: overwrite_pinned_field
    - DRIFT: unstable_device_path
    - DRIFT: missing_diff_artifact
    - DRIFT: adr0009_noncompliant
```

```
::contentReference[oaicite:0]{index=0}
```
