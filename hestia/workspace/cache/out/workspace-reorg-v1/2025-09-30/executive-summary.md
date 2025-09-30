# Hestia Workspace Reorganization: Executive Summary

## Current State Analysis
- **14 top-level directories** with overlapping purposes and unclear boundaries
- **1,192 total files** distributed across inconsistent hierarchy
- **Core issue**: Fragmented structure with duplicated functions (e.g., `diag/`, `diagnostics/`, `ops/guides/`, `docs/playbooks/`)

## Proposed Solution: Four-Pillar Architecture

### 1. **config/** (Runtime & Machine-First) - 267 files
- Consolidates `core/` → `config/`
- Machine-readable YAML/JSON configs for HA runtime
- Structured subdirs: `devices/`, `network/`, `preferences/`, `storage/`, `registry/`
- All files indexed in `config/index/manifest.yaml`

### 2. **library/** (Knowledge & References) - 401 files  
- Merges `docs/` + `meta/rehydration/` + `work/prompt.library/`
- Three streams: `docs/` (ADRs, playbooks), `prompts/` (curated), `context/` (rehydration)
- Operational knowledge separated from transient work

### 3. **tools/** (Scripts & Utilities) - 97 files
- Keeps current `tools/` structure (already well-organized)
- Adds `ops/scripts/` content for consolidation
- Maintainable CLI utilities and automation

### 4. **workspace/** (Operations & Transient) - 427 files
- Replaces `work/`, `vault/`, scattered operational files
- Subdirs: `operations/` (deploy, reports), `cache/` (temp), `archive/` (vault)
- Clear separation of active vs. archived content

## Key Improvements
- **Reduced cognitive load**: 14 → 4 top-level directories  
- **Clear ownership**: Each file type has obvious home
- **Machine-friendly**: Config files properly indexed and structured
- **Future-proof**: Scales for incoming migrations (patches, libraries)
- **Copilot-optimized**: Generated files follow same structure principles

## Impact Metrics
- 68% reduction in top-level complexity
- 100% of files have clear categorical homes  
- Eliminates 4 duplicate/overlapping directories
- Supports all pending action items (config consolidation, library builds, patch system)