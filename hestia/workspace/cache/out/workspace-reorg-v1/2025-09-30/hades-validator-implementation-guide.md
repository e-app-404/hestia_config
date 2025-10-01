# Hades Index Validator - Implementation Guide

## Step-by-Step Patch Application

### PHASE 1: IMMEDIATE FIXES (5 minutes)

#### Step 1: Update manifest.yaml paths
```bash
# Fix obsolete paths in the index file
cd /Users/evertappels/hass

# Update artifact paths from old to new structure
sed -i.bak 's|/config/hestia/core/config/|/config/hestia/config/|g' hestia/config/index/manifest.yaml

# Update root_hint as well  
sed -i 's|root_hint: "/config/hestia/core/config/"|root_hint: "/config/hestia/config/"|g' hestia/config/index/manifest.yaml

# Verify changes
echo "=== CHANGES MADE ==="
diff hestia/config/index/manifest.yaml.bak hestia/config/index/manifest.yaml || echo "No backup found"
```

#### Step 2: Replace the validator with fixed version
```bash
# Backup original validator
cp hestia/tools/utils/validators/hades_index_validator.py hestia/tools/utils/validators/hades_index_validator.py.backup

# Copy the fixed version
cp hestia/workspace/cache/out/workspace-reorg-v1/2025-09-30/hades_index_validator_fixed.py hestia/tools/utils/validators/hades_index_validator.py

# Make executable (if needed)
chmod +x hestia/tools/utils/validators/hades_index_validator.py
```

### PHASE 2: TESTING (10 minutes)

#### Step 3: Basic functionality test
```bash
# Test if validator can locate index file
cd /Users/evertappels/hass
python3 hestia/tools/utils/validators/hades_index_validator.py

# Expected output: Either "✅ OK: hades index checks passed" or specific failure messages
```

#### Step 4: Individual component testing
```bash
# Test path mapping
python3 -c "
import sys
sys.path.insert(0, 'hestia/tools/utils/validators')
from hades_index_validator import map_path, locate_index

# Test path mapping
test_path = '/config/hestia/config/network/topology.yaml'
mapped = map_path(test_path)
print(f'Path mapping: {test_path} -> {mapped}')
print(f'Exists: {mapped.exists() if mapped else \"None\"}')

# Test index location
try:
    idx_path = locate_index()
    print(f'Found index: {idx_path}')
except Exception as e:
    print(f'Index location error: {e}')
"
```

### PHASE 3: VERIFICATION (15 minutes)

#### Step 5: Full validation run
```bash
# Run with verbose output to see what's being checked
python3 -c "
import sys
sys.path.insert(0, 'hestia/tools/utils/validators')
from hades_index_validator import check, locate_index, load_index

print('=== VALIDATOR TEST REPORT ===')
try:
    idx_path = locate_index()
    print(f'✅ Index file found: {idx_path}')
    
    idx = load_index(idx_path)
    artifacts = idx.get('hades_config_index', {}).get('artifacts', {})
    print(f'✅ Loaded {len(artifacts)} artifact categories')
    
    total_items = sum(len(items) for items in artifacts.values())
    print(f'✅ Total artifacts: {total_items}')
    
    failures = check()
    if failures:
        print(f'⚠️  Found {len(failures)} validation issues:')
        for f in failures[:5]:  # Show first 5
            print(f'   {f[0]} | {f[1]} | {f[2]}')
        if len(failures) > 5:
            print(f'   ... and {len(failures) - 5} more')
    else:
        print('✅ All validations passed!')
        
except Exception as e:
    print(f'❌ Critical error: {e}')
    import traceback
    traceback.print_exc()
"
```

#### Step 6: Check specific artifact validation
```bash
# Test validation of a specific file that should exist
python3 -c "
import sys
sys.path.insert(0, 'hestia/tools/utils/validators')
from hades_index_validator import map_path, check_yaml_load
from pathlib import Path

# Test a file we know should exist after reorganization
test_files = [
    '/config/hestia/config/network/network.runtime.yaml',
    '/config/hestia/config/storage/samba.yaml', 
    '/config/hestia/config/diagnostics/glances.yaml'
]

for test_file in test_files:
    mapped_path = map_path(test_file)
    if mapped_path and mapped_path.exists():
        ok, err = check_yaml_load(mapped_path)
        status = '✅' if ok else f'❌ {err}'
        print(f'{status} {test_file} -> {mapped_path}')
    else:
        print(f'❌ Missing: {test_file} -> {mapped_path}')
"
```

### PHASE 4: INTEGRATION (5 minutes)

#### Step 7: Update any CI/CD references
```bash
# Check if validator is used in workflows
grep -r "hades_index_validator" .github/ || echo "Not used in GitHub workflows"

# Check pre-commit hooks
grep -r "hades_index_validator" .pre-commit-config.yaml || echo "Not in pre-commit hooks"

# Check if referenced in other scripts
find . -name "*.sh" -exec grep -l "hades_index_validator" {} \; || echo "Not referenced in shell scripts"
```

#### Step 8: Commit the changes
```bash
# Add the changes
git add hestia/config/index/manifest.yaml
git add hestia/tools/utils/validators/hades_index_validator.py
git add hestia/workspace/cache/out/workspace-reorg-v1/2025-09-30/

# Commit with descriptive message
git commit -m "fix: Update hades index validator for four-pillar architecture

- Updated validator paths to match new hestia/config/ structure
- Fixed ADR-0016 violations (removed hardcoded /Volumes paths)  
- Added proper path expansion with .expanduser()
- Enhanced error handling and validation logic
- Updated manifest.yaml paths from old hestia/core/config/ to new hestia/config/
- Added path normalization for transition period
- Improved tag policy for four-pillar architecture

Fixes: Non-functional validator due to path misalignment
Resolves: #workspace-reorg validation requirements"
```

## Rollback Procedure (if needed)

```bash
# If something goes wrong, rollback is simple:

# 1. Restore original validator
cp hestia/tools/utils/validators/hades_index_validator.py.backup hestia/tools/utils/validators/hades_index_validator.py

# 2. Restore original manifest  
cp hestia/config/index/manifest.yaml.bak hestia/config/index/manifest.yaml

# 3. Commit rollback
git add -A
git commit -m "rollback: Revert hades validator changes due to issues"
```

## Success Indicators

After applying the patch, you should see:

✅ **Validator locates index file** at `hestia/config/index/manifest.yaml`  
✅ **No ADR-0016 violations** (no hardcoded /Volumes paths)  
✅ **Path resolution works** for /config/ -> ~/hass mapping  
✅ **YAML validation succeeds** for existing config files  
✅ **Enhanced error messages** provide clear debugging info  
✅ **No regressions** in existing functionality  

## Troubleshooting Common Issues

### Issue: "No hades index found"
**Solution**: Check if `hestia/config/index/manifest.yaml` exists and is readable

### Issue: "path_missing" errors  
**Solution**: Verify files were moved to new locations during reorganization

### Issue: "yaml_load_fail" errors
**Solution**: Check individual YAML files for syntax errors

### Issue: "bad_tags" errors  
**Solution**: Update ALLOWED_TAGS in validator if new tags are needed

---

**Estimated Total Time**: 35 minutes  
**Risk Level**: Low (changes are reversible)  
**Testing Required**: Basic validation run  
**Dependencies**: Four-pillar architecture completion