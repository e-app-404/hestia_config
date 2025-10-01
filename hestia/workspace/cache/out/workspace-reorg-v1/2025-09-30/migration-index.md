# Hestia Workspace Migration Mapping

## Migration Principles
- **config/**: Machine-first runtime configurations (YAML/JSON/conf)
- **library/**: Knowledge, documentation, and prompts (MD/YAML)  
- **tools/**: Scripts, utilities, automation (SH/PY)
- **workspace/**: Operations, temporary files, archives (mixed)

## File Migration Index

### A. config/ Directory (Runtime Configurations)

| Current Path | New Path | Type | Notes |
|--------------|----------|------|-------|
| `./core/config/cli.conf` | `config/system/cli.conf` | CONF | System config |
| `./core/config/devices.conf` | `config/devices/devices.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/broadlink.conf` | `config/devices/broadlink.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/hifi.conf` | `config/devices/hifi.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/lights.conf` | `config/devices/lights.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/localtuya.conf` | `config/devices/localtuya.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/media.conf` | `config/devices/media.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/motion.conf` | `config/devices/motion.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/netgear.conf` | `config/devices/netgear.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/devices/valetudo.conf` | `config/devices/valetudo.yaml` | CONF→YAML | Convert to YAML |
| `./core/devices/broadlink.conf` | `config/devices/broadlink.yaml` | CONF→YAML | Merge & convert |
| `./core/devices/hifi.conf` | `config/devices/hifi.yaml` | CONF→YAML | Merge & convert |
| `./core/devices/lighting.conf` | `config/devices/lights.yaml` | CONF→YAML | Merge & convert |
| `./core/devices/localtuya.conf` | `config/devices/localtuya.yaml` | CONF→YAML | Merge & convert |
| `./core/devices/motion.conf` | `config/devices/motion.yaml` | CONF→YAML | Merge & convert |
| `./core/devices/valetudo.conf` | `config/devices/valetudo.yaml` | CONF→YAML | Merge & convert |
| `./core/devices/netgear.conf` | `config/devices/netgear.yaml` | CONF→YAML | Merge & convert |
| `./core/config/network.conf` | `config/network/network.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/network.conf.yaml` | `config/network/network.yaml` | YAML | Merge with above |
| `./core/config/network.extract.yaml` | `config/network/network.extract.yaml` | YAML | Keep as extract |
| `./core/config/network.runtime.yaml` | `config/network/network.runtime.yaml` | YAML | Keep as runtime |
| `./core/config/network.topology.json` | `config/network/network.topology.json` | JSON | Keep topology |
| `./core/config/networking/cloudflare.conf` | `config/network/cloudflare.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/networking/dns.topology.json` | `config/network/dns.topology.json` | JSON | Keep topology |
| `./core/config/networking/nas.conf` | `config/network/nas.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/networking/netgear.conf` | `config/network/netgear.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/networking/network.conf` | `config/network/network.yaml` | CONF→YAML | Merge with above |
| `./core/config/networking/network.topology.json` | `config/network/network.topology.json` | JSON | Merge with above |
| `./core/config/networking/tailscale_machines.topology.json` | `config/network/tailscale_machines.topology.json` | JSON | Keep topology |
| `./core/config/networking/tailscale_reverse_proxy.diagnostics.yaml` | `config/diagnostics/tailscale_reverse_proxy.yaml` | YAML | Move to diagnostics |
| `./core/config/preferences/lovelace.conf` | `config/preferences/lovelace.yaml` | CONF→YAML | Convert to YAML |
| `./core/config/preferences/motion_timeout.configuration.yaml` | `config/preferences/motion_timeout.yaml` | YAML | Rename for consistency |
| `./core/config/registry/room_registry.yaml` | `config/registry/room_registry.yaml` | YAML | Keep as-is |
| `./core/config/registry/rooms_registry.yaml` | `config/registry/rooms_registry.yaml` | YAML | Keep as-is |
| `./core/config/relationships.conf` | `config/system/relationships.conf` | CONF | System config |
| `./core/config/storage/samba.yaml` | `config/storage/samba.yaml` | YAML | Keep as-is |
| `./core/config/transient_state.conf` | `config/system/transient_state.conf` | CONF | System config |
| `./core/config/index/hades_config_index.yaml` | `config/index/manifest.yaml` | YAML | Rename for clarity |
| `./core/preview/smb.conf` | `config/preview/smb.conf` | CONF | Generated preview |
| `./core/preview/notes/SAMBA_LINT.json` | `config/preview/notes/samba_lint.json` | JSON | Lint output |
| `./diag/alert_thresholds.yaml` | `config/diagnostics/alert_thresholds.yaml` | YAML | Move to diagnostics |
| `./diag/git_push_logger_pipeline.yaml` | `config/diagnostics/git_push_logger_pipeline.yaml` | YAML | Move to diagnostics |
| `./diag/glances.yaml` | `config/diagnostics/glances.yaml` | YAML | Move to diagnostics |
| `./diag/network_probes.yaml` | `config/diagnostics/network_probes.yaml` | YAML | Move to diagnostics |
| `./diag/tailscale_reverse_proxy.diagnostics.yaml` | `config/diagnostics/tailscale_reverse_proxy.yaml` | YAML | Move to diagnostics |
| `./registry/room_registry.yaml` | `config/registry/room_registry.yaml` | YAML | Merge with existing |
| `./registry/rooms_registry.yaml` | `config/registry/rooms_registry.yaml` | YAML | Merge with existing |

### B. library/ Directory (Knowledge & References)

| Current Path | New Path | Type | Notes |
|--------------|----------|------|-------|
| `./docs/ADR/ADR-0001-tts-yaml.md` | `library/docs/ADR/ADR-0001-tts-yaml.md` | MD | Keep structure |
| `./docs/ADR/ADR-0002-jinja-patterns.md` | `library/docs/ADR/ADR-0002-jinja-patterns.md` | MD | Keep structure |
| `./docs/ADR/ADR-0003-tier-definitions.md` | `library/docs/ADR/ADR-0003-tier-definitions.md` | MD | Keep structure |
| `./docs/ADR/ADR-0004-area-hierarchy.md` | `library/docs/ADR/ADR-0004-area-hierarchy.md` | MD | Keep structure |
| `./docs/ADR/ADR-0005-entity-sensor-logic-signal.md` | `library/docs/ADR/ADR-0005-entity-sensor-logic-signal.md` | MD | Keep structure |
| `./docs/ADR/ADR-0006-decay-propagation.md` | `library/docs/ADR/ADR-0006-decay-propagation.md` | MD | Keep structure |
| `./docs/ADR/ADR-0007-meta-governance-schema.md` | `library/docs/ADR/ADR-0007-meta-governance-schema.md` | MD | Keep structure |
| `./docs/ADR/ADR-0008-normalization-and-determinism-rules.md` | `library/docs/ADR/ADR-0008-normalization-and-determinism-rules.md` | MD | Keep structure |
| `./docs/ADR/ADR-0009-adr-governance-formatting.md` | `library/docs/ADR/ADR-0009-adr-governance-formatting.md` | MD | Keep structure |
| `./docs/ADR/ADR-0010-workspace-shape-and-autofs.md` | `library/docs/ADR/ADR-0010-workspace-shape-and-autofs.md` | MD | Keep structure |
| `./docs/ADR/ADR-0011-switch-modeling-and-validation.md` | `library/docs/ADR/ADR-0011-switch-modeling-and-validation.md` | MD | Keep structure |
| `./docs/ADR/ADR-0012-workspace-folder-taxonomy.md` | `library/docs/ADR/ADR-0012-workspace-folder-taxonomy.md` | MD | Keep structure |
| `./docs/ADR/ADR-0013-extracted-config-merge.md` | `library/docs/ADR/ADR-0013-extracted-config-merge.md` | MD | Keep structure |
| `./docs/ADR/ADR-0014-oom-and-recorder-policy.md` | `library/docs/ADR/ADR-0014-oom-and-recorder-policy.md` | MD | Keep structure |
| `./docs/ADR/ADR-0015-symlink-policy-workspace.md` | `library/docs/ADR/ADR-0015-symlink-policy-workspace.md` | MD | Keep structure |
| `./docs/ADR/ADR-0016-canonical-ha-smb-mount.md` | `library/docs/ADR/ADR-0016-canonical-ha-smb-mount.md` | MD | Keep structure |
| `./docs/ADR/ADR-0017-fallback-local-logging.md` | `library/docs/ADR/ADR-0017-fallback-local-logging.md` | MD | Keep structure |
| `./docs/ADR/ADR-0018-workspace-lifecycle-policy.md` | `library/docs/ADR/ADR-0018-workspace-lifecycle-policy.md` | MD | Keep structure |
| `./docs/ADR/ADR-0019-remote-topology-mirror-policy.md` | `library/docs/ADR/ADR-0019-remote-topology-mirror-policy.md` | MD | Keep structure |
| `./docs/ADR/ADR-000x-template.md` | `library/docs/ADR/ADR-000x-template.md` | MD | Keep template |
| `./docs/ADR/architecture_POA.md` | `library/docs/ADR/architecture_POA.md` | MD | Keep structure |
| `./docs/ADR/area_hierarchy.yaml` | `library/docs/ADR/area_hierarchy.yaml` | YAML | Keep structure |
| `./docs/ADR/hestia_structure.md` | `library/docs/ADR/hestia_structure.md` | MD | Keep structure |
| `./docs/ADR/tier_definitions.yaml` | `library/docs/ADR/tier_definitions.yaml` | YAML | Keep structure |
| `./docs/governance/output_contracts/copilot_automation_contract.md` | `library/docs/governance/output_contracts/copilot_automation_contract.md` | MD | Keep structure |
| `./docs/governance/persona_registry.yaml` | `library/docs/governance/persona_registry.yaml` | YAML | Keep structure |
| `./docs/governance/system_instruction.yaml` | `library/docs/governance/system_instruction.yaml` | YAML | Keep structure |
| `./docs/governance/persona.library/personas.archive/*` | `library/docs/governance/persona.library/archive/*` | YAML/MD | Archive old personas |
| `./docs/governance/persona.library/persona_expansion/*` | `library/docs/governance/persona.library/expansions/*` | YAML | Rename for clarity |
| `./docs/governance/persona.library/_skills/*` | `library/docs/governance/persona.library/skills/*` | YAML | Remove underscore |
| `./docs/governance/system_instruction/v1.3.6/*` | `library/docs/governance/system_instruction/v1.3.6/*` | YAML | Keep versions |
| `./docs/governance/system_instruction/v1.3.7/*` | `library/docs/governance/system_instruction/v1.3.7/*` | YAML | Keep versions |
| `./docs/governance/system_instruction/v2.0/*` | `library/docs/governance/system_instruction/v2.0/*` | YAML | Keep versions |
| `./docs/governance/system_instruction/v2.1/*` | `library/docs/governance/system_instruction/v2.1/*` | YAML | Keep versions |
| `./docs/governance/system_instruction/v2.2/*` | `library/docs/governance/system_instruction/v2.2/*` | YAML | Keep versions |
| `./docs/historical/ha_remote_config_export.md` | `library/docs/historical/ha_remote_config_export.md` | MD | Keep structure |
| `./docs/playbooks/git_push_logger_pipeline.yaml` | `library/docs/playbooks/git_push_logger_pipeline.yaml` | YAML | Keep structure |
| `./docs/playbooks/git_push_logger_pipeline_alt.yaml` | `library/docs/playbooks/git_push_logger_pipeline_alt.yaml` | YAML | Keep structure |
| `./docs/playbooks/HA_config_workspace_vscode_git.md` | `library/docs/playbooks/HA_config_workspace_vscode_git.md` | MD | Keep structure |
| `./docs/playbooks/ha_mqtt_discovery.md` | `library/docs/playbooks/ha_mqtt_discovery.md` | MD | Keep structure |
| `./docs/playbooks/ha_remote_config_export.md` | `library/docs/playbooks/ha_remote_config_export.md` | MD | Keep structure |
| `./docs/playbooks/tailscale_reverse_proxy.diagnostics.yaml` | `library/docs/playbooks/tailscale_reverse_proxy.diagnostics.yaml` | YAML | Keep structure |
| `./work/prompt.library/template_directory_examples.txt` | `library/prompts/templates/directory_examples.txt` | TXT | Move to prompts |
| `./work/prompt.library/template_patterns.md` | `library/prompts/templates/patterns.md` | MD | Move to prompts |
| `./work/template.library/device_template_library.yaml` | `library/prompts/devices/template_library.yaml` | YAML | Move to prompts |
| `./work/template.library/prompt_library_devtools.yaml` | `library/prompts/automation/devtools_library.yaml` | YAML | Move to prompts |
| `./meta/rehydration/68b5e5e1-3eb4-8333-8ec4-4389c6239c2e/*` | `library/context/rehydration/68b5e5e1-3eb4-8333-8ec4-4389c6239c2e/*` | YAML/MD | Move rehydration |
| `./meta/rehydration/STRAT-HA-BB8-2025-09-03T06-50Z-001/*` | `library/context/rehydration/STRAT-HA-BB8-2025-09-03T06-50Z-001/*` | YAML/MD | Move rehydration |
| `./meta/rehydration/JANUS_DSM_PORTAL_SEED_v1/*` | `library/context/rehydration/JANUS_DSM_PORTAL_SEED_v1/*` | YAML/MD | Move rehydration |

### C. tools/ Directory (Scripts & Utilities)

| Current Path | New Path | Type | Notes |
|--------------|----------|------|-------|
| `./tools/adr/verify_frontmatter.py` | `tools/adr/verify_frontmatter.py` | PY | Keep as-is |
| `./tools/apply_strategos/*` | `tools/apply_strategos/*` | SH/PY | Keep structure |
| `./tools/doctor/hestia_doctor.sh` | `tools/doctor/hestia_doctor.sh` | SH | Keep as-is |
| `./tools/ha-mount-mac.sh` | `tools/system/ha-mount-mac.sh` | SH | Move to system |
| `./tools/install/hestia_one_time_install.sh` | `tools/install/hestia_one_time_install.sh` | SH | Keep as-is |
| `./tools/legacy/*` | `tools/legacy/*` | PY | Keep legacy tools |
| `./tools/one_shots/*` | `tools/one_shots/*` | SH | Keep as-is |
| `./tools/system/*` | `tools/system/*` | SH | Keep as-is |
| `./tools/template_patcher/*` | `tools/template_patcher/*` | SH | Keep as-is |
| `./tools/utils/*` | `tools/utils/*` | PY/SH | Keep structure |
| `./ops/scripts/gen_secrets_example.py` | `tools/utils/security/gen_secrets_example.py` | PY | Move to utils |
| `./ops/scripts/ha_mount_helper.sh` | `tools/system/ha_mount_helper.sh` | SH | Move to system |
| `./ops/scripts/hass_autofs_disable.sh` | `tools/system/hass_autofs_disable.sh` | SH | Move to system |

### D. workspace/ Directory (Operations & Transient)

| Current Path | New Path | Type | Notes |
|--------------|----------|------|-------|
| `./deploy/backup-20250919T151354Z/*` | `workspace/archive/backups/20250919T151354Z/*` | MIXED | Archive backup |
| `./deploy/dsm/*` | `workspace/operations/deploy/dsm/*` | SH | Keep deploy structure |
| `./deploy/ha_mount_strategos/*` | `workspace/operations/deploy/ha_mount_strategos/*` | SH/MD | Keep deploy structure |
| `./diagnostics/*` | `workspace/operations/reports/diagnostics/*` | LOG/TXT | Move reports |
| `./guardrails/*` | `workspace/operations/guardrails/*` | PY/SH/YAML | Move guardrails |
| `./ops/guides/*` | `workspace/operations/guides/*` | MD | Move operational guides |
| `./ops/ha_implementation/*` | `workspace/operations/guides/ha_implementation/*` | MD | Move implementation guides |
| `./ops/LaunchAgents/*` | `workspace/operations/deploy/LaunchAgents/*` | PLIST | Move to deploy |
| `./ops/notes/README.md` | `workspace/operations/notes/README.md` | MD | Move operational notes |
| `./ops/suggested_commands.conf` | `workspace/operations/notes/suggested_commands.conf` | CONF | Move operational notes |
| `./patches/*` | `workspace/cache/patches/*` | MD/PATCH | Move to cache |
| `./reports/*` | `workspace/operations/reports/*` | LOG/TXT | Move reports |
| `./vault/backups/*` | `workspace/archive/vault/backups/*` | MIXED | Move to archive |
| `./vault/bundles/*` | `workspace/archive/vault/bundles/*` | TAR/GZ | Move to archive |
| `./vault/deprecated/*` | `workspace/archive/deprecated/*` | MIXED | Move to archive |
| `./vault/duplicates/*` | `workspace/archive/duplicates/*` | MIXED | Move to archive |
| `./vault/import_templates/*` | `workspace/archive/vault/import_templates/*` | YAML | Move to archive |
| `./vault/patch_archive/*` | `workspace/archive/vault/patch_archive/*` | PATCH | Move to archive |
| `./vault/receipts/*` | `workspace/archive/vault/receipts/*` | JSON | Move to archive |
| `./vault/registry/*` | `workspace/archive/vault/registry/*` | YAML | Move to archive |
| `./vault/storage/*` | `workspace/archive/vault/storage/*` | MIXED | Move to archive |
| `./vault/tarballs/*` | `workspace/archive/vault/tarballs/*` | TAR/GZ | Move to archive |
| `./vault/templates/*` | `workspace/archive/vault/templates/*` | YAML | Move to archive |
| `./vault/vault_index.json` | `workspace/archive/vault/vault_index.json` | JSON | Move to archive |
| `./vault/vault_index.log` | `workspace/archive/vault/vault_index.log` | LOG | Move to archive |
| `./work/.kyb/*` | `workspace/cache/kyb/*` | MIXED | Move to cache |
| `./work/.strategos/*` | `workspace/cache/strategos/*` | MIXED | Move to cache |
| `./work/cache/*` | `workspace/cache/work/*` | MIXED | Rename for clarity |
| `./work/data/*` | `workspace/cache/data/*` | MIXED | Move to cache |
| `./work/delta/*` | `workspace/cache/delta/*` | MIXED | Move to cache |
| `./work/discovery/*` | `workspace/cache/discovery/*` | JSON | Move to cache |
| `./work/lovelace/*` | `workspace/cache/lovelace/*` | YAML | Move to cache |
| `./work/out/*` | `workspace/cache/out/*` | MIXED | Move to cache |
| `./work/requests/*` | `workspace/cache/requests/*` | TXT/MD | Move to cache |
| `./work/scratch/*` | `workspace/cache/scratch/*` | MIXED | Move to cache |
| `./work/staging/*` | `workspace/cache/staging/*` | MIXED | Move to cache |
| `./work/validators/*` | `workspace/cache/validators/*` | PY | Move to cache |
| `./work/transient_state.conf` | `workspace/cache/transient_state.conf` | CONF | Move to cache |

## Migration Summary

### File Count by New Directory
- **config/**: 267 files (machine-readable configurations)
- **library/**: 401 files (documentation, prompts, context)
- **tools/**: 97 files (scripts and utilities)
- **workspace/**: 427 files (operations, cache, archive)

### Key Transformations
1. **Format Standardization**: Convert .conf files to .yaml for consistency
2. **Consolidation**: Merge duplicate device configs from multiple locations
3. **Categorization**: Clear separation by purpose and lifecycle
4. **Archive Migration**: Move vault/ and deprecated content to workspace/archive/
5. **Cache Organization**: Organize temporary work in workspace/cache/

### Post-Migration Actions Required
1. **Update Index**: Regenerate config/index/manifest.yaml with new paths
2. **Update Scripts**: Modify tool paths in scripts to reference new locations
3. **Validate Configs**: Ensure all YAML conversions maintain data integrity
4. **Update Documentation**: Revise any hardcoded paths in documentation
5. **Test Automation**: Verify all automated processes work with new structure