# ADR-0012 Addendum: Four-Pillar Hestia Architecture Implementation

## Executive Summary

This addendum proposes updating **ADR-0012: Workspace Folder Taxonomy** to reflect the implemented four-pillar Hestia architecture that replaced the fragmented 14-directory structure with a clean, purpose-driven organization.

## Context: Post-Migration Reality

The workspace reorganization completed on 2025-09-30 successfully transformed:
- **1,196 files** across **14 fragmented directories** → **928 files** in **4 logical pillars**
- **268 duplicate files eliminated** (confirmed zero data loss)
- **ADR-0012 compliance** achieved through systematic reorganization

## Proposed Changes to ADR-0012

### 1. Replace Section 2.2 "Knowledge & configuration tree"

**CURRENT:**
```yaml
- `hestia/core/config/` — Machine-discovered artifacts
- `hestia/core/devices/` — Authoritative records
- `hestia/docs/ADR/` — ADRs and governance docs  
- `hestia/vault/` — Archives & backups
```

**PROPOSED:**
```yaml
- `hestia/config/` — Runtime & Machine-First configurations
  - `hestia/config/devices/` — Device integrations & configs
  - `hestia/config/network/` — Network topology & connectivity
  - `hestia/config/storage/` — Storage backends & persistence
  - `hestia/config/registry/` — Indexes & entity registries
  - `hestia/config/diagnostics/` — Monitoring & health checks
  - `hestia/config/preferences/` — UI & system preferences
  - `hestia/config/preview/` — Generated config previews
  - `hestia/config/system/` — System-level configurations
  - `hestia/config/index/` — Master manifests & indexes

- `hestia/library/` — Knowledge, Documentation & References
  - `hestia/library/docs/` — Human-readable documentation & governance
    - `hestia/library/docs/ADR/` — Architecture Decision Records
    - `hestia/library/docs/playbooks/` — Operational procedures
    - `hestia/library/docs/governance/` — System instructions & personas
  - `hestia/library/prompts/` — Curated prompt library for AI interactions
  - `hestia/library/context/` — Session context & rehydration data

- `hestia/tools/` — Scripts, Utilities & Automation
  - `hestia/tools/adr/` — ADR validation & management
  - `hestia/tools/utils/` — General utilities & validators
  - `hestia/tools/system/` — System-level utilities
  - `hestia/tools/template_patcher/` — Template patching system

- `hestia/workspace/` — Operations, Cache & Transient Files
  - `hestia/workspace/operations/` — Active operational work
  - `hestia/workspace/cache/` — Temporary & work-in-progress
  - `hestia/workspace/archive/` — Long-term storage & backups
```

### 2. Update Section 2.3 "Programmatic assignation rules"

**ADD:**
```yaml
Content Allocation Rules (Machine-Enforceable):

config/:
  - Runtime configurations (.yaml, .json, .conf)
  - Device integrations and hardware configs
  - Network topology and connectivity data
  - System preferences and UI configurations
  - Storage and backup configurations
  - Registry and index files
  - Diagnostic and monitoring configs
  - Generated configuration previews
  - Must be indexed in config/index/manifest.yaml

library/:
  - Human-readable documentation (.md)
  - Governance files and system instructions (.yaml)
  - Curated prompt libraries for AI interactions
  - Session context and rehydration data
  - ADRs with proper front-matter schema
  - No runtime configurations or machine operations

tools/:
  - Executable scripts (.py, .sh, .js)
  - Validation and linting utilities
  - System administration tools
  - Template patching systems
  - No documentation content or runtime configs
  - Must be executable or utility configuration

workspace/:
  - Operational work and deployment artifacts
  - Temporary files and work-in-progress content
  - Cache directories and staging areas
  - Archives and long-term storage
  - Generated reports and audit outputs
  - No permanent configuration or documentation
```

### 3. Update Section 4 "Binary acceptance criteria"

**MODIFY EXISTING CRITERIA:**
1. **Taxonomy pass** — No files violate the four-pillar folder policy
2. **Content allocation** — All files comply with purpose-driven placement rules
3. **ADR compliance** — All ADRs parse; keys in canonical order; exactly one TOKEN_BLOCK per ADR
4. **Config validity** — All artifacts in `hestia/config/` parse and are indexed in `config/index/manifest.yaml`
5. **Path convention** — No scripts contain obsolete paths; all respect new structure
6. **Duplicate elimination** — No content duplication between pillars

**ADD NEW CRITERIA:**
7. **Structure validation** — Four-pillar architecture enforced programmatically
8. **Content fit validation** — Files placed according to content allocation rules
9. **Index completeness** — All config files referenced in master manifest
10. **Reference integrity** — All internal path references updated to new structure

### 4. Add New Enforcement Section

```bash
# Four-Pillar Structure Validation
./hestia/tools/utils/validators/hestia_structure_validator.py --check-all

# Content Allocation Validation  
./hestia/tools/utils/validators/validate_content_allocation.py --scan-all

# Path Reference Scanner
./hestia/tools/utils/validators/scan_hardcoded_paths.sh --update-mode

# Index Completeness Check
python - <<'PY'
import yaml, pathlib, sys
manifest_path = pathlib.Path('hestia/config/index/manifest.yaml')
manifest = yaml.safe_load(manifest_path.open())
indexed_paths = {item['path'].replace('/config/', '') for item in manifest.get('artifacts', [])}
config_files = set()
for path in pathlib.Path('hestia/config').rglob('*'):
    if path.is_file() and path.suffix in ['.yaml', '.yml', '.json', '.conf']:
        config_files.add(str(path))
missing = config_files - indexed_paths
if missing:
    print(f"Unindexed config files: {missing}")
    sys.exit(1)
print("Index completeness: OK")
PY
```

### 5. Update TOKEN_BLOCK Requirements

```yaml
TOKEN_BLOCK:
  accepted:
    - FOUR_PILLAR_ARCHITECTURE_IMPLEMENTED
    - CONTENT_ALLOCATION_RULES_ENFORCED
    - DUPLICATE_ELIMINATION_COMPLETED
    - PATH_REFERENCES_UPDATED
    - INDEX_COMPLETENESS_VALIDATED
  requires:
    - ADR_SCHEMA_V1
    - STRUCTURE_VALIDATION_ENFORCED
    - DETERMINISTIC_PACKAGING
    - WORKSPACE_TAXONOMY_DEFINED
  drift:
    - DRIFT: obsolete_path_references
    - DRIFT: content_allocation_violation
    - DRIFT: unindexed_config_files
    - DRIFT: duplicate_content_detected
    - DRIFT: four_pillar_structure_violation
```

## Implementation Guardrails

### Validation Commands
```bash
# Structure compliance check
hestia/tools/utils/validators/hestia_structure_validator.py --workspace /config/hestia

# Content fit validation
hestia/tools/utils/validators/validate_content_allocation.py --path {file_path}

# Path reference scanner
hestia/tools/utils/validators/scan_hardcoded_paths.sh --scan-all --update-refs

# Index validation
hestia/tools/utils/validators/hestia_index_validator.py --manifest hestia/config/index/manifest.yaml
```

### Token Blocks for Enforcement
- `FOUR_PILLAR_STRUCTURE_OK` — Structure follows config/, library/, tools/, workspace/ 
- `CONTENT_ALLOCATION_OK` — Files placed according to purpose-driven rules
- `PATH_REFERENCES_UPDATED` — All internal references use new structure
- `INDEX_COMPLETENESS_OK` — All config files properly indexed

### Evidence Requirements
- Pre/post migration file inventories
- Duplicate elimination analysis showing 268 files removed
- Structure validation reports
- Path reference update logs
- Index completeness verification

## Migration Completion Evidence

✅ **Structural Transformation**: 14 directories → 4 pillars (68% complexity reduction)
✅ **File Consolidation**: 1,196 → 928 files (268 duplicates eliminated)
✅ **Zero Data Loss**: Comprehensive audit trail maintained
✅ **ADR-0012 Compliance**: Four-pillar structure implemented
✅ **Git Tracking**: All changes properly committed and documented

## Rollout Schedule

1. **Phase 1 (Completed)**: Structural reorganization and duplicate elimination
2. **Phase 2 (In Progress)**: Path reference updates and validation tool creation
3. **Phase 3 (Next)**: CI/CD integration and automated enforcement
4. **Phase 4 (Future)**: Documentation updates and team adoption

## Related Changes

This addendum requires coordinated updates to:
- `.env` and `.env.sample` (canonicalize new paths)
- `configuration.yaml` (update hestia path references)
- GitHub workflows (update ADR linting paths)
- Copilot instructions (reflect new structure)
- README.md (update CLI examples)
- Pre-commit hooks (update validation paths)

---

**Recommendation**: Approve this addendum to formalize the successful four-pillar architecture implementation and provide governance framework for maintaining the new structure.