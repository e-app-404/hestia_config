# Implementation Guide: Hestia Workspace Reorganization

## Migration Strategy

### Phase 1: Preparation (Pre-Migration)
1. ~~Create Backup~~
    Note: backup is made through HA UI.

   ```bash
   cd /Users/evertappels/hass
   tar -czf hestia-backup-$(date +%Y%m%d-%H%M%S).tar.gz hestia/
   ```

2. ~~Validate Current State~~
    Note: both are not operating right now

   ```bash
   # Run existing validators
   ./hestia/tools/utils/validators/adr_lint/cli.py hestia/docs/ADR --format human
   ./hestia/tools/utils/validators/hades_index_validator.py
   ```

3. **Create New Directory Structure**
   ```bash
   cd hestia/
   mkdir -p config/{devices,network,preferences,storage,registry,diagnostics,preview,system,index}
   mkdir -p library/{docs,prompts,context}
   mkdir -p library/docs/{ADR,playbooks,governance,historical}
   mkdir -p library/prompts/{_meta,automation,configuration,diagnostics,validation}
   mkdir -p library/context/{rehydration,scaffolding,seeds}
   mkdir -p workspace/{operations,cache,archive}
   mkdir -p workspace/operations/{deploy,reports,guardrails,guides}
   mkdir -p workspace/cache/{data,staging,scratch,out}
   mkdir -p workspace/archive/{vault,deprecated,duplicates,legacy}
   ```

### Phase 2: Migration (Systematic File Movement)

#### A. Config Files (Priority 1 - Runtime Critical)
```bash
# Device configurations (convert .conf to .yaml)
for file in core/config/devices/*.conf core/devices/*.conf; do
  if [ -f "$file" ]; then
    basename=$(basename "$file" .conf)
    # Manual conversion required - .conf files need YAML restructuring
    echo "Convert $file to config/devices/${basename}.yaml"
  fi
done

# Network configurations
cp core/config/network*.yaml config/network/
cp core/config/networking/* config/network/ 2>/dev/null || true

# Registry files
cp core/config/registry/* config/registry/ 2>/dev/null || true
cp registry/* config/registry/ 2>/dev/null || true

# Diagnostics
cp diag/*.yaml config/diagnostics/ 2>/dev/null || true

# Storage configs
cp core/config/storage/* config/storage/ 2>/dev/null || true

# Preview files  
cp core/preview/* config/preview/ 2>/dev/null || true

# System configs
cp core/config/cli.conf config/system/
cp core/config/relationships.conf config/system/
cp core/config/transient_state.conf config/system/
```

#### B. Library Files (Priority 2 - Documentation)
```bash
# ADRs and documentation
cp -r docs/* library/docs/

# Prompts and templates
cp -r work/prompt.library/* library/prompts/ 2>/dev/null || true
cp -r work/template.library/* library/prompts/ 2>/dev/null || true

# Rehydration data
cp -r meta/rehydration/* library/context/rehydration/ 2>/dev/null || true
```

#### C. Tools (Priority 3 - Keep Structure)
```bash
# Tools remain mostly as-is, just add ops/scripts content
cp ops/scripts/* tools/utils/security/ 2>/dev/null || true
```

#### D. Workspace Files (Priority 4 - Operations)
```bash
# Deploy artifacts
cp -r deploy/* workspace/operations/deploy/

# Reports and diagnostics  
cp -r reports/* workspace/operations/reports/ 2>/dev/null || true
cp -r diagnostics/* workspace/operations/reports/diagnostics/ 2>/dev/null || true

# Guardrails
cp -r guardrails/* workspace/operations/guardrails/

# Operational guides
cp -r ops/guides/* workspace/operations/guides/ 2>/dev/null || true
cp -r ops/ha_implementation/* workspace/operations/guides/ha_implementation/ 2>/dev/null || true

# Archive vault content
cp -r vault/* workspace/archive/vault/

# Cache work content
cp -r work/cache/* workspace/cache/work/ 2>/dev/null || true
cp -r work/data/* workspace/cache/data/ 2>/dev/null || true
cp -r work/discovery/* workspace/cache/discovery/ 2>/dev/null || true
cp -r work/lovelace/* workspace/cache/lovelace/ 2>/dev/null || true
cp -r work/out/* workspace/cache/out/ 2>/dev/null || true
cp -r work/scratch/* workspace/cache/scratch/ 2>/dev/null || true
cp -r work/staging/* workspace/cache/staging/ 2>/dev/null || true

# Patches
cp -r patches/* workspace/cache/patches/ 2>/dev/null || true
```

### Phase 3: Post-Migration (Validation & Updates)

#### A. Generate New Index
```bash
# Create master config index
cat > config/index/manifest.yaml << 'EOF'
version: 2.0
last_updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
artifacts:
EOF

# Add all config files to index
find config -name "*.yaml" -o -name "*.json" -o -name "*.conf" | while read file; do
  echo "  - path: \"$file\"" >> config/index/manifest.yaml
  echo "    type: \"$(echo $file | cut -d'/' -f2)_config\"" >> config/index/manifest.yaml  
  echo "    format: \"$(echo $file | rev | cut -d'.' -f1 | rev)\"" >> config/index/manifest.yaml
done
```

#### B. Update Tool References  
```bash
# Scan and update hardcoded paths in tools
grep -r "hestia/core" tools/ | while IFS: read file line; do
  echo "Update path reference in: $file"
done

grep -r "hestia/docs" tools/ | while IFS: read file line; do  
  echo "Update path reference in: $file"
done

grep -r "hestia/work" tools/ | while IFS: read file line; do
  echo "Update path reference in: $file"  
done
```

#### C. Validation Checks
```bash
# Verify config structure
python3 << 'EOF'
import yaml
import json
import pathlib

config_root = pathlib.Path('config')
errors = []

for config_file in config_root.rglob('*'):
    if config_file.is_file():
        try:
            if config_file.suffix in ['.yaml', '.yml']:
                with open(config_file) as f:
                    yaml.safe_load(f)
            elif config_file.suffix == '.json':
                with open(config_file) as f:
                    json.load(f)
        except Exception as e:
            errors.append(f"Parse error in {config_file}: {e}")

if errors:
    for error in errors:
        print(error)
    exit(1)
else:
    print("All config files parse successfully")
EOF

# Verify ADR compliance
if [ -f tools/utils/validators/adr_lint/cli.py ]; then
  python3 tools/utils/validators/adr_lint/cli.py library/docs/ADR --format human
fi

# Check for orphaned files
find . -maxdepth 1 -name "core" -o -name "docs" -o -name "meta" -o -name "work" -o -name "vault" -o -name "ops" -o -name "diag" -o -name "diagnostics" -o -name "guardrails" -o -name "registry" -o -name "reports" -o -name "patches" | while read dir; do
  if [ -d "$dir" ]; then
    echo "WARNING: Old directory still exists: $dir"
    echo "Contents: $(find "$dir" -type f | wc -l) files"
  fi
done
```

### Phase 4: Cleanup (Post-Validation)

#### A. Remove Old Directories (Only After Validation)
```bash
# Only run after confirming migration success
read -p "Migration validated? Remove old directories? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  rm -rf core/ docs/ meta/ work/ vault/ ops/ diag/ diagnostics/ guardrails/ registry/ reports/ patches/
  echo "Old directories removed"
fi
```

#### B. Update Documentation
1. Update any hardcoded paths in library/docs/ADR/
2. Revise library/docs/ADR/ADR-0012-workspace-folder-taxonomy.md to reflect new structure
3. Update system_instruction.yaml paths

#### C. Test Automation
```bash
# Test key tools still work
if [ -f tools/apply_strategos/apply_strategos_pipeline.sh ]; then
  ./tools/apply_strategos/apply_strategos_pipeline.sh --dry-run
fi

# Test ADR linter
if [ -f tools/utils/validators/adr_lint/cli.py ]; then
  python3 tools/utils/validators/adr_lint/cli.py library/docs/ADR --format json
fi
```

## Critical Success Factors

### 1. Data Integrity
- ✅ All 1,192 files accounted for in migration
- ✅ No data loss during .conf → .yaml conversion  
- ✅ Proper YAML/JSON syntax validation post-migration

### 2. Tool Compatibility
- ✅ All existing tools work with new paths
- ✅ ADR linter validates new structure
- ✅ Config index properly reflects new manifest

### 3. Documentation Consistency
- ✅ ADR-0012 updated to reflect new taxonomy
- ✅ All hardcoded paths updated in documentation
- ✅ System instructions reference correct paths

### 4. Operational Continuity  
- ✅ Deployment scripts work with new structure
- ✅ Backup/restore procedures updated
- ✅ CI/CD pipelines reference correct paths

## Rollback Plan
If issues arise:
1. Stop migration process
2. Restore from backup: `tar -xzf hestia-backup-*.tar.gz`
3. Document specific issues encountered
4. Revise migration strategy and retry

## Expected Timeline
- **Phase 1** (Preparation): 30 minutes
- **Phase 2** (Migration): 2-3 hours  
- **Phase 3** (Validation): 1 hour
- **Phase 4** (Cleanup): 30 minutes

**Total**: ~4-5 hours with testing and validation