# Hestia Workspace: Complete Proposed Structure

## Four-Pillar Architecture

```
hestia/
├── config/                           # Runtime & Machine-First (267 files)
│   ├── devices/                      # Device integrations & configs
│   │   ├── broadlink.yaml
│   │   ├── hifi.yaml
│   │   ├── lights.yaml
│   │   ├── localtuya.yaml
│   │   ├── media.yaml
│   │   ├── motion.yaml
│   │   ├── netgear.yaml
│   │   └── valetudo.yaml
│   ├── network/                      # Network, DNS, topology
│   │   ├── cloudflare.yaml
│   │   ├── dns.topology.json
│   │   ├── nas.yaml
│   │   ├── netgear.yaml
│   │   ├── network.extract.yaml
│   │   ├── network.runtime.yaml
│   │   ├── network.topology.json
│   │   ├── tailscale_machines.topology.json
│   │   └── tailscale_reverse_proxy.diagnostics.yaml
│   ├── preferences/                  # UI, styles, timeouts
│   │   ├── lovelace.yaml
│   │   ├── motion_timeout.configuration.yaml
│   │   └── styles.yaml
│   ├── storage/                      # Storage & backup configs
│   │   ├── samba.yaml
│   │   └── backup.yaml
│   ├── registry/                     # Indexes, rooms, mappings
│   │   ├── hades_config_index.yaml
│   │   ├── room_registry.yaml
│   │   └── rooms_registry.yaml
│   ├── diagnostics/                  # Monitoring & health checks
│   │   ├── alert_thresholds.yaml
│   │   ├── git_push_logger_pipeline.yaml
│   │   ├── glances.yaml
│   │   ├── network_probes.yaml
│   │   └── tailscale_reverse_proxy.diagnostics.yaml
│   ├── preview/                      # Generated config previews
│   │   ├── smb.conf
│   │   └── notes/
│   ├── system/                       # System-level configs
│   │   ├── cli.conf
│   │   ├── relationships.conf
│   │   └── transient_state.conf
│   └── index/
│       └── manifest.yaml             # Master index of all config files
│
├── library/                          # Knowledge & References (401 files)  
│   ├── docs/                         # Documentation & governance
│   │   ├── ADR/                      # Architecture Decision Records
│   │   │   ├── ADR-0001-tts-yaml.md
│   │   │   ├── ADR-0010-workspace-shape-and-autofs.md
│   │   │   ├── ADR-0012-workspace-folder-taxonomy.md
│   │   │   ├── ADR-000x-template.md
│   │   │   ├── architecture_POA.md
│   │   │   ├── area_hierarchy.yaml
│   │   │   ├── hestia_structure.md
│   │   │   └── tier_definitions.yaml
│   │   ├── playbooks/                # Operational procedures
│   │   │   ├── HA_config_workspace_vscode_git.md
│   │   │   ├── git_push_logger_pipeline.yaml
│   │   │   ├── ha_mqtt_discovery.md
│   │   │   └── ha_remote_config_export.md
│   │   ├── governance/               # System instructions & personas
│   │   │   ├── system_instruction.yaml
│   │   │   ├── persona_registry.yaml
│   │   │   ├── persona.library/
│   │   │   └── output_contracts/
│   │   └── historical/               # Legacy documentation
│   │       └── ha_remote_config_export.md
│   ├── prompts/                      # Curated prompt library
│   │   ├── _meta/                    # Prompt metadata & schemas
│   │   ├── automation/               # Automation-related prompts
│   │   ├── configuration/            # Config generation prompts  
│   │   ├── diagnostics/              # Troubleshooting prompts
│   │   └── validation/               # Validation & linting prompts
│   └── context/                      # Rehydration & session data
│       ├── rehydration/              # Session rehydration seeds
│       │   ├── 68b5e5e1-3eb4-8333-8ec4-4389c6239c2e/
│       │   ├── STRAT-HA-BB8-2025-09-03T06-50Z-001/
│       │   └── JANUS_DSM_PORTAL_SEED_v1/
│       ├── scaffolding/              # Template scaffolds
│       └── seeds/                    # Context seeds & memory vars
│
├── tools/                            # Scripts & Utilities (97 files)
│   ├── adr/                          # ADR validation & management
│   │   └── verify_frontmatter.py
│   ├── apply_strategos/              # Strategos application pipeline
│   │   ├── apply_strategos_pipeline.sh
│   │   ├── apply_strategos_00_env.sh
│   │   └── apply_strategos_*.sh
│   ├── template_patcher/             # Template patching system
│   │   ├── patch_ha_templates.sh
│   │   ├── rollback_ha_templates.sh
│   │   └── patches/
│   ├── system/                       # System-level utilities
│   │   ├── hestia_workspace_enforcer.sh
│   │   ├── hestia_neutralize.sh
│   │   └── hestia_autofs_uninstall.sh
│   ├── utils/                        # General utilities
│   │   ├── validators/               # Validation tools
│   │   ├── env/                      # Environment setup
│   │   ├── git/                      # Git utilities
│   │   └── vault_manager/            # Vault management
│   ├── doctor/                       # Diagnostic utilities
│   │   └── hestia_doctor.sh
│   ├── install/                      # Installation scripts
│   │   └── hestia_one_time_install.sh
│   ├── one_shots/                    # One-time operation scripts
│   │   └── ha_mount_one_shot.sh
│   └── legacy/                       # Legacy tooling
│       └── backup_renamer.py
│
└── workspace/                        # Operations & Transient (427 files)
    ├── operations/                   # Active operational work
    │   ├── deploy/                   # Deployment scripts & artifacts
    │   │   ├── dsm/
    │   │   └── ha_mount_strategos/
    │   ├── reports/                  # Generated reports & outputs  
    │   │   ├── diagnostics/
    │   │   ├── audits/
    │   │   └── evidence/
    │   ├── guardrails/               # Safety checks & validation
    │   │   ├── check_duplicate_keys.py
    │   │   ├── check_rest_command_guardrails.sh
    │   │   └── sql_sensor_guardrails.yaml
    │   └── guides/                   # Operational guides
    │       ├── dsm_configure-synology-nas-git-server.md
    │       ├── ha_smb_mount.md
    │       └── optimize-your-home-assistant-database.md
    ├── cache/                        # Temporary & work-in-progress
    │   ├── data/                     # Transient data files
    │   ├── staging/                  # Staging area
    │   ├── template.library/         # Template work area
    │   ├── lovelace/                 # Lovelace UI work
    │   ├── discovery/                # Device discovery outputs  
    │   ├── scratch/                  # Short-lived patches & diffs
    │   └── out/                      # Job-scoped outputs
    │       └── workspace-reorg-v1/   # This reorganization work
    └── archive/                      # Long-term storage
        ├── vault/                    # Secure storage & backups
        │   ├── backups/
        │   ├── bundles/
        │   ├── import_templates/
        │   ├── patch_archive/
        │   ├── receipts/
        │   ├── registry/
        │   ├── storage/
        │   ├── tarballs/
        │   └── templates/
        ├── deprecated/               # Deprecated files
        ├── duplicates/               # Duplicate cleanup
        └── legacy/                   # Legacy artifacts
```

## Content Allocation Logic (Machine-Friendly)

### Programmatic Rules for Content Classification

```yaml
hestia_content_allocation_rules:
  version: "2.0"
  
  config:
    purpose: "Runtime & Machine-First Configurations"
    file_patterns: ["*.yaml", "*.json", "*.conf", "*.ini"]
    content_types: ["device_integration", "network_topology", "system_preference", "runtime_config"]
    exclusions: ["documentation", "human_readable_guides", "temporary_files"]
    
    devices:
      purpose: "Hardware device integrations and configurations"
      required_attributes: ["device_type", "integration_method"]
      file_naming: "{device_name}.{yaml|conf}"
      content_validation: 
        - "must_contain: device configuration parameters"
        - "must_not_contain: documentation or guides"
      examples: ["broadlink.yaml", "hifi.yaml", "motion.yaml"]
    
    network:
      purpose: "Network infrastructure and connectivity configs"
      required_attributes: ["network_component", "topology_data"]
      file_naming: "{component}.{yaml|json|conf}"
      content_validation:
        - "must_contain: network parameters or topology"
        - "allowed_types: [runtime, extract, topology]"
      examples: ["network.runtime.yaml", "dns.topology.json"]
    
    preferences:
      purpose: "User interface and system preference configurations"
      required_attributes: ["preference_scope", "ui_component"]
      file_naming: "{component}.{yaml|conf}"
      content_validation:
        - "must_contain: preference or UI configuration"
      examples: ["lovelace.yaml", "motion_timeout.yaml"]
    
    storage:
      purpose: "Storage backend and data persistence configurations"
      required_attributes: ["storage_backend", "persistence_config"]
      file_naming: "{backend}.yaml"
      content_validation:
        - "must_contain: storage or backup configuration"
      examples: ["samba.yaml", "backup.yaml"]
    
    registry:
      purpose: "Index files and entity registries"
      required_attributes: ["registry_type", "index_scope"]
      file_naming: "{registry_name}.yaml"
      content_validation:
        - "must_contain: registry or index data"
        - "must_be: machine_parseable"
      examples: ["room_registry.yaml", "manifest.yaml"]
    
    diagnostics:
      purpose: "Monitoring, health checks, and diagnostic configurations"
      required_attributes: ["diagnostic_type", "monitoring_target"]
      file_naming: "{diagnostic_component}.yaml"
      content_validation:
        - "must_contain: diagnostic or monitoring config"
      examples: ["alert_thresholds.yaml", "network_probes.yaml"]
    
    preview:
      purpose: "Generated configuration previews (non-runtime)"
      required_attributes: ["preview_type", "generated_flag"]
      file_naming: "{component}.{conf|ini}"
      content_validation:
        - "must_be: generated_preview"
        - "must_not_be: runtime_loaded"
      examples: ["smb.conf"]
    
    system:
      purpose: "System-level and cross-component configurations"
      required_attributes: ["system_scope", "config_type"]
      file_naming: "{component}.conf"
      content_validation:
        - "must_contain: system-wide configuration"
      examples: ["cli.conf", "relationships.conf"]
    
    index:
      purpose: "Master indexes and manifests"
      required_attributes: ["index_scope", "manifest_type"]
      file_naming: "manifest.yaml"
      content_validation:
        - "must_contain: index or manifest data"
        - "must_reference: other config files"
      examples: ["manifest.yaml"]

  library:
    purpose: "Knowledge, Documentation & References"
    file_patterns: ["*.md", "*.yaml", "*.txt", "*.json"]
    content_types: ["documentation", "governance", "prompts", "context"]
    exclusions: ["runtime_config", "machine_operations"]
    
    docs:
      purpose: "Human-readable documentation and governance"
      required_attributes: ["doc_type", "human_readable"]
      subdirs:
        ADR:
          purpose: "Architecture Decision Records"
          file_naming: "ADR-{number}-{slug}.md"
          content_validation:
            - "must_contain: decision record format"
            - "must_have: front_matter"
        playbooks:
          purpose: "Operational procedures and runbooks"
          file_naming: "{procedure_name}.{md|yaml}"
          content_validation:
            - "must_contain: procedural instructions"
        governance:
          purpose: "System instructions and personas"
          file_naming: "{component}.yaml"
          content_validation:
            - "must_contain: governance or instruction data"
        historical:
          purpose: "Legacy and archived documentation"
          file_naming: "{legacy_doc}.md"
          content_validation:
            - "must_be: historical_reference"
    
    prompts:
      purpose: "Curated prompt library for AI interactions"
      required_attributes: ["prompt_category", "ai_context"]
      subdirs:
        _meta:
          purpose: "Prompt metadata and schemas"
          content_validation: ["must_contain: prompt_metadata"]
        automation:
          purpose: "Automation-related prompts"
          content_validation: ["must_contain: automation_prompt"]
        configuration:
          purpose: "Configuration generation prompts"
          content_validation: ["must_contain: config_generation_prompt"]
        diagnostics:
          purpose: "Troubleshooting and diagnostic prompts"
          content_validation: ["must_contain: diagnostic_prompt"]
        validation:
          purpose: "Validation and linting prompts"
          content_validation: ["must_contain: validation_prompt"]
    
    context:
      purpose: "Session context and rehydration data"
      required_attributes: ["context_type", "session_data"]
      subdirs:
        rehydration:
          purpose: "Session rehydration seeds"
          file_naming: "{session_id}/"
          content_validation: ["must_contain: session_context"]
        scaffolding:
          purpose: "Template scaffolds and frameworks"
          content_validation: ["must_contain: template_scaffold"]
        seeds:
          purpose: "Context seeds and memory variables"
          content_validation: ["must_contain: context_seed"]

  tools:
    purpose: "Scripts, Utilities & Automation"
    file_patterns: ["*.py", "*.sh", "*.js", "*.yaml"]
    content_types: ["executable_script", "utility", "automation", "validation"]
    exclusions: ["documentation", "configuration", "data_files"]
    
    validation_rules:
      - "must_be: executable OR utility_config"
      - "must_not_contain: runtime_configuration"
      - "must_not_contain: documentation_content"

  workspace:
    purpose: "Operations, Cache & Transient Files"
    file_patterns: ["*"]
    content_types: ["operational", "temporary", "cache", "archive"]
    exclusions: ["permanent_configuration", "documentation"]
    
    operations:
      purpose: "Active operational work and artifacts"
      subdirs:
        deploy: 
          purpose: "Deployment scripts and artifacts"
          content_validation: ["must_contain: deployment_artifact"]
        reports:
          purpose: "Generated reports and audit outputs"
          content_validation: ["must_be: generated_report"]
        guardrails:
          purpose: "Safety checks and validation scripts"
          content_validation: ["must_contain: validation_logic"]
        guides:
          purpose: "Operational guides and procedures"
          content_validation: ["must_contain: operational_procedure"]
    
    cache:
      purpose: "Temporary and work-in-progress files"
      subdirs:
        data: 
          purpose: "Transient data files"
          content_validation: ["must_be: temporary_data"]
        staging:
          purpose: "Staging area for processing"
          content_validation: ["must_be: staging_content"]
        scratch:
          purpose: "Short-lived patches and diffs"
          content_validation: ["must_be: temporary_patch"]
        out:
          purpose: "Job-scoped outputs and results"
          content_validation: ["must_be: job_output"]
    
    archive:
      purpose: "Long-term storage and historical data"
      subdirs:
        vault:
          purpose: "Secure storage and backups"
          content_validation: ["must_be: archived_backup"]
        deprecated:
          purpose: "Deprecated files awaiting removal"
          content_validation: ["must_be: deprecated_content"]
        legacy:
          purpose: "Legacy artifacts for reference"
          content_validation: ["must_be: legacy_reference"]

enforcement_commands:
  validation_script: "tools/utils/validators/hestia_structure_validator.py"
  index_checker: "tools/utils/validators/hestia_index_validator.py"
  path_scanner: "tools/utils/validators/scan_hardcoded_paths.sh"
  
validation_queries:
  content_fit: "python tools/utils/validators/validate_content_allocation.py --path {file_path}"
  structure_compliance: "tools/utils/validators/hestia_structure_validator.py --check-all"
  path_references: "tools/utils/validators/scan_hardcoded_paths.sh --scan-all"
```

## Design Principles Applied

### 1. Purpose-Driven Hierarchy
- **config/**: Machine-first runtime configurations only
- **library/**: Human knowledge, documentation, and prompts  
- **tools/**: Scripts, utilities, and automation
- **workspace/**: Operational work, temporary files, and archives

### 2. Clear Boundaries  
- No overlapping responsibilities between directories
- Each file type has exactly one logical home
- Machine vs. human content clearly separated

### 3. Scalability
- Structure supports future content additions
- Consistent naming conventions throughout
- Easy to extend without disruption

### 4. Machine-Friendly
- All config files properly indexed  
- JSON/YAML structure for automation
- Clear file type conventions (.yaml, .json, .md, .sh, .py)

### 5. Copilot-Optimized
- Generated files follow same organizational principles
- Clear output destinations (workspace/cache/out/)
- Logical artifact placement

## Migration Benefits
- **68% reduction** in top-level complexity (14 → 4 directories)
- **Zero ambiguity** in file placement
- **Future-ready** for pending action items:
  - Config consolidation → `config/` with proper indexing
  - Prompt library builds → `library/prompts/`
  - Patch system → `workspace/cache/scratch/`
  - System instruction consolidation → `library/docs/governance/`