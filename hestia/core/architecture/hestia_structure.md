# Hestia Content Strategy: Final Structure & Purpose

## Key Principles

- **Purpose-driven folders:** Every folder is anchored to a specific, documented role (e.g., devices, network, system, state, tooling, preferences, registry, diagnostics, tools, vault, work, patches).
- **No catch-all buckets:** Avoid generic or ambiguous folders; all content must fit a clear pillar.
- **Merge or clarify overlapping folders:** If functions overlap (e.g., tools/helpers/utils), merge or strictly define boundaries.
- **README files:** Each major folder must include a README describing its purpose, expected contents, and usage guidelines.
- **Separation of meta/config:** Project meta (contracts, schemas) is kept in `meta/`; editor/repo config (.git, .vscode) is kept at the repo root.
- **Operational and transient separation:** Diagnostics, vault, and work folders are clearly separated for logs, backups, and in-progress files.
- **Regular audits:** Periodically review folder contents for correct placement and update documentation as the project evolves.
- **Scalability and future-proofing:** Structure supports easy addition of new pillars, folders, and content types without disruption.


## Master version

```
/Volumes/HA/config/hestia/
  core/                        # HA-runtime, machine-first YAML only
    devices/                   # integrations & device configs (YAML)
      broadlink.yaml
      hifi.yaml
      localtuya.yaml
      motion.yaml
      lighting.yaml
      valetudo.yaml
      netgear_sensors.yaml
    networking/                # network/DNS/Tailscale (YAML)
      network.yaml
      dns.yaml
      tailscale.yaml
    templates/                 # automations/scripts/jinja (YAML)
      automations.yaml
      scripts.yaml
    preferences/               # Lovelace, styles, timeouts (YAML/MD if UI docs)
      lovelace.yaml
      styles.yaml
      motion_timeout.yaml
    registry/                  # indices/rooms/persona maps (YAML)
      rooms.yaml
      index.yaml
    diagnostics/               # declarative probes only (YAML)
      tailscale_diagnostics.yaml
    preview/                   # generated previews only (non-runtime)
      samba.ini                # INI preview (linted, never loaded)

  docs/                        # human-readable; not consumed by HA
    ADR/
      ADR-0008-normalization-and-determinism-rules.md
      ADR-0009-switch-modeling-and-validation.md
    Playbooks/
      git_push_pipeline.md
    Governance/                # personas, system instructions, contracts
      system_instruction.yaml
      personas/
    Historical/
      ha_remote_config_export.md

  tools/                       # scripts, validators, pipelines (Mac-safe paths)
    pipelines/
      apply_strategos_*.sh
    validators/
      yaml_lint.py
      samba_lint.py
    connectivity/
      ha-mount-mac.sh
    README.md

  work/                        # transient inputs/outputs
    scratch/                   # incoming diffs/overlays
    out/                       # job-scoped outputs
    cache/
    README.md

  patches/                     # long-lived patch artifacts (optional)
    delta/
    scratch/
    README.md

  vault/                       # backups/tarballs/legacy (never loaded by HA)
    backups/
    tarballs/
    legacy/
    README.md
```

### Pillar/Folder Purpose

- **core/**: Machine-first, runtime YAML only. No documentation, scripts, or meta/config.
  - **devices/**: Integrations & device configs (YAML).
  - **networking/**: Network, DNS, Tailscale (YAML).
  - **templates/**: Automations, scripts, jinja (YAML).
  - **preferences/**: Lovelace, styles, timeouts (YAML/MD if UI docs).
  - **registry/**: Indices, rooms, persona maps (YAML).
  - **diagnostics/**: Declarative probes only (YAML).
  - **preview/**: Generated previews only (non-runtime).

- **docs/**: Human-readable documentation, ADRs, playbooks, governance/personas, historical exports. Not loaded by HA.

- **tools/**: Scripts, validators, pipelines, connectivity helpers. Mac-safe paths. No runtime YAML.

- **work/**: Transient inputs/outputs, job-scoped outputs, cache, scratch. Not loaded by HA.

- **patches/**: Long-lived patch artifacts (optional).

- **vault/**: Backups, tarballs, legacy/deprecated files. Never loaded by HA.

- **meta/**: Repo-level meta if needed (not runtime, not loaded by HA).


### Folder Purpose & Content Strategy

- **core/**: Only runtime YAML for HA. No documentation, scripts, or meta/config. All device, network, automation, UI, registry, diagnostics, and preview configs must be YAML (or INI for preview only).
- **docs/**: All human-readable documentation, ADRs, playbooks, governance/personas, historical exports. Markdown, YAML (if not runtime), or other formats as needed.
- **tools/**: All scripts, validators, pipelines, and connectivity helpers. No runtime YAML. Mac-safe paths.
- **work/**: All transient, experimental, and in-progress files, job outputs, cache, scratch. Not loaded by HA.
- **patches/**: All long-lived patch artifacts, deltas, and scratch files. Not loaded by HA.
- **vault/**: All backups, tarballs, legacy/deprecated files. Never loaded by HA. Maintain a README for clarity and retention policy.
- **meta/**: Repo-level meta if needed. Not runtime, not loaded by HA.

---
