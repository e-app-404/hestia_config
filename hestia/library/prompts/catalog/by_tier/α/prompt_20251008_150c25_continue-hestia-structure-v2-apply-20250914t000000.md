---
id: prompt_20251008_150c25
slug: continue-hestia-structure-v2-apply-20250914t000000
title: "\u2705 CONTINUE: Hestia Structure v2 \u2014 APPLY 20250914T000000Z (Reinforced)"
date: '2025-10-08'
tier: "\u03B1"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: 20250914_hestia_structure_cont2.txt
author: Unknown
related: []
last_updated: '2025-10-09T01:44:26.585548'
redaction_log: []
---

# ✅ CONTINUE: Hestia Structure v2 — APPLY 20250914T000000Z (Reinforced)

You are GitHub Copilot (GPT-4.1) operating on a Mac-mounted HA workspace.

- **ROOT (canonical, case-sensitive):** /Volumes/HA/config/hestia
- **JOB_ID (locked):** 20250914T000000Z
- **OUT:** /Volumes/HA/config/hestia/work/out/20250914T000000Z

Do **not** reference archives; operate only on the mounted tree. Keep workspace noise minimal (no multi-script sprawl). If any gate fails, print a **single** `BLOCKED:` line and stop.


## Guardrails (restate)
- Write only under `/Volumes/HA/config/hestia/**`.
- Idempotent: re-run yields identical tree + hashes.
- Convert `.conf → .yaml` **only if** YAML-parseable (no semantic edits).
- Samba preview stays INI (preview only; no hardening/CIDR narrowing).
- Use `/Volumes/HA/...` (uppercase **HA**) for all paths; if you encounter `/Volumes/ha`, canonicalize to `/Volumes/HA`.
- Single branch: `refactor/hestia-structure-v2`; single PR.

**Tokens**
- SUCCESS:
COMPLETED: 20250914T000000Z
BRANCH: refactor/hestia-structure-v2
PR: <url-or-#>
OUT: /Volumes/HA/config/hestia/work/out/20250914T000000Z
PROPERTY-HASH: <sha256>
SUMMARY:

files_moved: <n>
files_converted_yaml: <n>
docs_relocated: <n>
yaml_parse: PASS
samba_preview_lint: PASS|SKIP
manifest: <count> entries; verify PASS

- BLOCK:
`BLOCKED: <domain> -> <reason>`


## Target layout (authoritative)
Ensure these exist (you scaffolded already—great):

```
/Volumes/HA/config/hestia/
core/{devices,networking,templates,preferences,registry,diagnostics,preview}
docs/{ADR,Playbooks,Governance,Historical}
tools/
work/{scratch,out,cache}
patches/
vault/
```


## Action Matrix (explicit remap of known sources)

> Move/rename atomically with `git mv`. If destination exists with identical bytes → **skip**; if differs → **BLOCKED: COLLISION** (don’t auto-merge).

**Runtime configs → core/**

- `core/config/devices/*.conf`
  - `broadlink.conf`            → `core/devices/broadlink.yaml`   (if YAML-parseable)
  - `hifi.conf`                 → `core/devices/hifi.yaml`        (if YAML-parseable)
  - `lights.conf`               → `core/devices/lights.yaml`      (if YAML-parseable)
  - `localtuya.conf`            → `core/devices/localtuya.yaml`   (if YAML-parseable)
  - `motion.conf`               → `core/devices/motion.yaml`      (if YAML-parseable)
  - `valetudo.conf`             → `core/devices/valetudo.yaml`    (if YAML-parseable)
  - `devices.conf`              → `core/devices/devices.yaml`     (if YAML-parseable)

- `core/config/networking/*`
  - `cloudflare.conf.yaml`       → `core/networking/cloudflare.yaml`
  - `dns_registry.topology.json` → `core/networking/dns_registry.topology.json`
  - `dns.topology.json`          → `core/networking/dns.topology.json`
  - `nas.conf`                   → `core/networking/nas.conf`
  - `network.conf.yaml`          → `core/networking/network.yaml`
  - `network.topology.json`      → `core/networking/network.topology.json`
  - `tailscale_machines.topology.json` → `core/networking/tailscale_machines.topology.json`
  - `tailscale_reverse_proxy.diagnostics.yaml` → `core/diagnostics/tailscale_reverse_proxy.yaml`

- `core/config/index/*`
  - `hades_config_index.yaml`   → `core/registry/hades_config_index.yaml`

- `core/preferences/*`
  - `motion_timeout.configuration.yaml` → `core/preferences/motion_timeout.configuration.yaml`
  - `radio.config.yaml`                 → `core/preferences/radio.config.yaml`
  - `style_guide.md`                    → `docs/Playbooks/style_guide.md`  (doc, not runtime)

- `core/system/*`
  - `relationships.conf`         → if YAML → `core/networking/relationships.yaml`; else keep under `core/system/` (log family)

- `core/config/ha_remote_config_export.md` → `docs/Playbooks/Remote_Config_Export.md`  (historical; mark as legacy in REPORT)

**Governance / Architecture → docs/**

- core/architecture/*
  - `ADR-0008-normalization-and-determinism-rules.md` → docs/ADR/ (keep name)
  - `ADR-0009-switch-modeling-and-validation.md`         → docs/ADR/
  - `area_hierarchy.yaml`,` tier_definitions.yaml`         → docs/ADR/  (architecture data)

- `core/governance`, `core/persona_registries`, `core/system_instruction/*` → `docs/Governance/**`
- `prompt_registry/**` → `docs/Governance/PromptRegistry/**` (metadata & templates)
- `ops/**` (pipelines, how-tos) → `docs/Playbooks/**`
- `state/transient_state.conf` → `work/` (transient or delete with note in REPORT)
- `xplab_portal/**` → `docs/Historical/xplab_portal/**`

**Preview (optional)**
- If a Samba overlay exists and is renderable, write preview to: `core/preview/samba.ini` (one `[global]`, shares A→Z; no hardening).


## Apply sequence (single pass)

1) **Inventory → plan.json (refresh)**
- Build an ordered list: `[{"op":"move|convert|skip","src":"…","dst":"…","family":"yaml|json|ini|md","risk":"low|med|hi"}]`
- Save to `/Volumes/HA/config/hestia/work/out/20250914T000000Z/plan.json`.
- If any destination collision with different bytes → **BLOCKED: COLLISION -> <src> vs <dst>**.

2) **Execute moves & safe conversions**
- For `.conf` candidates: try `yaml.safe_load`; if success → write `.yaml` (sorted keys, LF, trailing newline). Else keep `.conf` and move only.
- Never alter semantics; formatting only.

3) **configuration.yaml include block (idempotent)**
- Find `/Volumes/HA/config/configuration.yaml` (root of HA config). If not found → WARN in REPORT, continue.
- Upsert this exact block (replace if markers exist):

BEGIN HESTIA-INCLUDES (managed)

```yaml
hestia_devices: !include_dir_merge_named hestia/core/devices
hestia_networking: !include_dir_merge_named hestia/core/networking
automation: !include hestia/core/templates/automations.yaml
script: !include hestia/core/templates/scripts.yaml
hestia_preferences: !include_dir_merge_named hestia/core/preferences
hestia_registry: !include_dir_merge_named hestia/core/registry
```
END HESTIA-INCLUDES


4) **QA gates**
- YAML parse over `core/**/*.y*ml` → PASS required.
- Samba preview lint (if `core/preview/samba.ini` exists): exactly one `[global]`; shares alpha; **no** `client min protocol|server min protocol|hosts allow|interfaces` keys. Else → SKIP.
- Normalize all touched text: UTF-8, LF, final newline; trim trailing spaces; stable key sort for YAML.

5) **Determinism evidence (core/** only)**
- Compute `manifest.sha256` (filename + sha256 of canonicalized bytes) and roll-up `property_hash.txt` under `/work/out/20250914T000000Z/`.
- Exclude `docs/**`, `work/**`, `tools/**`, `vault/**`, `patches/**` from property hash.

6) **Report & Commit**
- `/work/out/20250914T000000Z/REPORT.md`: mapping table, counts, any WARN, QA results, and PROPERTY-HASH.
- Commit in logical chunks:
  - Moves/conversions + include block
  - `/work/out/20250914T000000Z/*` evidence
- Open PR: **“Hestia Structure v2 — runtime/doc split + deterministic core”**. PR body must embed:
  - Executive summary
  - Mapping table (top 20 rows + link to full `plan.json`)
  - QA results
  - SUCCESS token (below)

7) **Emit SUCCESS tokens** (exact format shown above).

## Sanity checks (before you start moving)
- Use **these globs** for source discovery (case-sensitive):
  - `/Volumes/HA/config/hestia/core/config/devices/*.conf`
  - `/Volumes/HA/config/hestia/core/config/networking/*.{yaml,yml,json,conf}`
  - `/Volumes/HA/config/hestia/core/config/index/*.yaml`
  - `/Volumes/HA/config/hestia/core/preferences/*`
  - `/Volumes/HA/config/hestia/core/registry/*`
  - `/Volumes/HA/config/hestia/core/architecture/*`
  - `/Volumes/HA/config/hestia/core/governance/**`
  - `/Volumes/HA/config/hestia/core/ops/**`
  - `/Volumes/HA/config/hestia/core/state/*`
  - `/Volumes/HA/config/hestia/core/system/*`
- If any of the above roots are missing, **don’t fail**—log in REPORT.

## Proceed
You already have branch + OUT scaffold and my approval.

**Apply now** with the sequence above. If anything would force a lossy merge (e.g., content mismatch at destination), stop with a `BLOCKED: COLLISION` and list the conflicting pairs.

On success, print the SUCCESS tokens and the PR link/number.

