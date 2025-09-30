# Optimized Workspace Reorganization Request for Claude Sonnet 4

## Executive Context
The Hestia workspace contains 1,192 files across 14 top-level directories with overlapping purposes. Current structure lacks clear boundaries between runtime configs, documentation, tools, and transient work, hindering maintainability and automated processing.

## Optimization Objective
Redesign the hestia/ subdirectory into an intuitive, machine-friendly four-pillar architecture that:
1. **Eliminates ambiguity** in file placement (68% reduction in top-level complexity)
2. **Supports future migrations** (config consolidation, library builds, patch system)
3. **Follows workspace flow** (generated files land in logical locations)
4. **Maintains ADR compliance** (per ADR-0012 workspace taxonomy)

## Proposed Four-Pillar Structure

### 1. **config/** - Runtime Configurations (267 files)
```
config/
├── devices/           # Device integrations (YAML)
├── network/           # Network, DNS, topology (YAML/JSON)
├── preferences/       # UI, styles, timeouts (YAML)
├── storage/           # Storage & backup configs (YAML)
├── registry/          # Indexes, rooms, mappings (YAML) 
├── diagnostics/       # Monitoring & health (YAML)
├── preview/           # Generated previews (INI/CONF)
├── system/            # System-level configs (CONF)
└── index/             # Master manifest (YAML)
```

### 2. **library/** - Knowledge & References (401 files)
```
library/
├── docs/              # Documentation & governance
│   ├── ADR/           # Architecture Decision Records
│   ├── playbooks/     # Operational procedures
│   ├── governance/    # System instructions, personas
│   └── historical/    # Legacy documentation
├── prompts/           # Curated prompt library
│   ├── _meta/         # Schemas & examples
│   ├── automation/    # Automation prompts
│   ├── configuration/ # Config generation prompts
│   ├── diagnostics/   # Troubleshooting prompts
│   └── validation/    # Linting prompts
└── context/           # Rehydration & session data
    ├── rehydration/   # Session seeds
    ├── scaffolding/   # Template scaffolds
    └── seeds/         # Context & memory vars
```

### 3. **tools/** - Scripts & Utilities (97 files)
```
tools/                 # Keep existing structure
├── adr/               # ADR validation tools
├── apply_strategos/   # Strategos pipeline
├── template_patcher/  # Template patching
├── system/            # System utilities
├── utils/             # General utilities
├── doctor/            # Diagnostics
├── install/           # Installation scripts
├── one_shots/         # One-time operations
└── legacy/            # Legacy tools
```

### 4. **workspace/** - Operations & Transient (427 files)
```
workspace/
├── operations/        # Active operational work
│   ├── deploy/        # Deployment artifacts
│   ├── reports/       # Generated reports
│   ├── guardrails/    # Safety checks
│   └── guides/        # Operational guides
├── cache/             # Temporary & work-in-progress
│   ├── data/          # Transient data
│   ├── staging/       # Staging area
│   ├── scratch/       # Patches & diffs
│   └── out/           # Job outputs (including this work)
└── archive/           # Long-term storage
    ├── vault/         # Secure backups
    ├── deprecated/    # Deprecated files
    ├── duplicates/    # Duplicate cleanup
    └── legacy/        # Legacy artifacts
```

## Key Migration Actions
1. **Format Standardization**: Convert .conf → .yaml for consistency
2. **Consolidation**: Merge duplicate configs (devices/, networking/)
3. **Index Generation**: Create config/index/manifest.yaml
4. **Archive Organization**: Vault → workspace/archive/vault/
5. **Library Build**: prompt.library → library/prompts/

## Compliance & Benefits
- ✅ **ADR-0012 Compliant**: Follows canonical workspace taxonomy
- ✅ **Machine-Friendly**: Indexed configs, consistent naming
- ✅ **Future-Ready**: Supports all pending action items
- ✅ **Copilot-Optimized**: Generated files follow same principles
- ✅ **Zero Ambiguity**: Every file has exactly one logical home

## Expected Deliverables
1. **Executive Summary** with key improvements
2. **Complete Structure Tree** showing all 4 pillars  
3. **Migration Index** mapping 1,192 current → new file paths
4. **Implementation Guide** with post-migration actions

This optimization transforms a fragmented 14-directory structure into a coherent 4-pillar architecture, reducing complexity while maintaining all functionality and supporting future growth.