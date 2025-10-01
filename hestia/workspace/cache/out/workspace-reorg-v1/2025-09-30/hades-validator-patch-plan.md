# Hades Index Validator - Patch Plan

## Executive Summary
The hades index validator is **non-functional** due to path misalignment with the four-pillar architecture and ADR-0016 violations. This patch plan provides a systematic approach to restore functionality while ensuring compliance.

## Phase 1: Critical Path Fixes (HIGH PRIORITY)

### 1.1 Update Index File Location Constants
**Issue**: Validator looks for non-existent index files in wrong locations
**Fix**: Update paths to match four-pillar architecture

```python
# BEFORE (BROKEN):
PREFERRED_INDEXS = [
    Path('~/hass/hestia/index/hades_index.conf'),      # Wrong location
    Path('~/hass/hestia/index/hades.indx'),            # Wrong location
]
FALLBACK_INDEX = Path('/Volumes/config/hestia/index/hades_index.conf')  # ADR-0016 violation

# AFTER (FIXED):
PREFERRED_INDEXS = [
    Path('~/hass/hestia/config/index/manifest.yaml').expanduser(),        # Correct location
    Path('~/hass/hestia/config/index/hades_config_index.yaml').expanduser(), # Alternative name
]
# Use environment variable per ADR-0016
FALLBACK_INDEX = Path(os.getenv('HA_MOUNT', os.path.expanduser('~/hass'))) / 'config/hestia/config/index/manifest.yaml'
```

### 1.2 Fix Path Expansion Logic
**Issue**: `Path('~/hass')` doesn't expand tilde
**Fix**: Add proper path expansion

```python
# BEFORE (BROKEN):
def map_path(p: str):
    if p.startswith('/config/'):
        return Path('~/hass') / p[len('/config/'):]  # Tilde not expanded
    return Path(p)

# AFTER (FIXED):
def map_path(p: str):
    """Map /config/ paths to local filesystem with proper expansion"""
    if p.startswith('/config/'):
        ha_mount = os.getenv('HA_MOUNT', os.path.expanduser('~/hass'))
        return Path(ha_mount) / p[len('/config/'):]
    return Path(p).expanduser()
```

### 1.3 Remove ADR-0016 Violations
**Issue**: Hardcoded `/Volumes/config/` paths
**Fix**: Use environment variables and parameterized paths

```python
import os  # Add missing import

# Replace hardcoded paths with environment-aware logic
def get_fallback_paths():
    """Get fallback index paths respecting ADR-0016"""
    ha_mount = os.getenv('HA_MOUNT', os.path.expanduser('~/hass'))
    return [
        Path(ha_mount) / 'config/hestia/config/index/manifest.yaml',
        Path(ha_mount) / 'config/hestia/config/index/hades_config_index.yaml',
    ]
```

## Phase 2: Index Structure Compatibility (MEDIUM PRIORITY)

### 2.1 Support Current YAML Format
**Issue**: Validator expects `.conf`/`.indx` but actual file is `.yaml`
**Fix**: Update to handle actual manifest.yaml format

```python
def load_index(path: Path):
    """Load index file supporting both legacy and current formats"""
    try:
        import yaml
        content = yaml.safe_load(path.read_text(encoding='utf-8'))
        
        # Handle current manifest.yaml structure
        if 'hades_config_index' in content:
            return content
            
        # Handle legacy structure (if needed)
        if 'artifacts' in content and 'hades_config_index' not in content:
            return {'hades_config_index': content}
            
        return content
        
    except Exception as e:
        # Fallback parser for .conf format (legacy support)
        return _parse_legacy_format(path)
```

### 2.2 Update Artifact Path Validation
**Issue**: Index contains obsolete `hestia/core/config/` paths
**Fix**: Handle both old and new path formats during transition

```python
def normalize_artifact_path(path_str: str):
    """Normalize artifact paths to new structure"""
    if not path_str:
        return path_str
        
    # Convert old structure to new structure
    if '/hestia/core/config/' in path_str:
        return path_str.replace('/hestia/core/config/', '/hestia/config/')
    
    return path_str

def check():
    # ... existing code ...
    for cat, items in art.items():
        for it in items:
            raw = it.get('path')
            normalized_path = normalize_artifact_path(raw)  # Normalize path
            p = map_path(normalized_path)
            # ... rest of validation logic ...
```

## Phase 3: Enhanced Error Handling (LOW PRIORITY)

### 3.1 Improve Exception Handling
**Issue**: Broad `Exception` catching hides specific errors
**Fix**: Use specific exception types

```python
def check_yaml_load(p: Path):
    try:
        import yaml
        yaml.safe_load(p.read_text(encoding='utf-8'))
        return True, None
    except yaml.YAMLError as e:
        return False, f'yaml_error: {e}'
    except FileNotFoundError:
        return False, 'file_not_found'
    except PermissionError:
        return False, 'permission_denied'
    except Exception as e:
        return False, f'unexpected_error: {e}'
```

### 3.2 Add Input Validation
**Issue**: No validation of parser state
**Fix**: Add safety checks

```python
def _parse_legacy_format(path: Path):
    # ... existing parsing logic with added validation ...
    if stripped.startswith('- '):
        if cur_category is None:
            raise ValueError(f"Item found without category context at: {line}")
        # ... rest of logic ...
```

## Phase 4: Configuration Updates (IMMEDIATE)

### 4.1 Update Index File Content
**Issue**: `manifest.yaml` contains obsolete paths
**Fix**: Update all artifact paths to new structure

```bash
# Script to update manifest.yaml paths
sed -i 's|/config/hestia/core/config/|/config/hestia/config/|g' hestia/config/index/manifest.yaml

# Update root_hint as well
sed -i 's|/config/hestia/core/config/|/config/hestia/config/|g' hestia/config/index/manifest.yaml
```

### 4.2 Validate Tag Policy
**Issue**: Tags may be outdated for new structure
**Fix**: Review and update allowed tags

```python
# Current tags - review for completeness
ALLOWED_TAGS = set([
    'tailscale', 'mullvad', 'samba', 'glances', 'hades',
    'layer3', 'healthcheck', 'home_assistant', 'synology_dsm',
    # Consider adding new tags for four-pillar architecture:
    'config', 'library', 'tools', 'workspace',  # pillar tags
    'devices', 'network', 'storage', 'diagnostics',  # config subtypes
])
```

## Implementation Schedule

### ⚡ IMMEDIATE (Day 1)
1. **Fix critical path constants** (1.1)
2. **Update manifest.yaml paths** (4.1) 
3. **Remove ADR-0016 violations** (1.3)

### 🔧 URGENT (Day 2-3)  
1. **Fix path expansion logic** (1.2)
2. **Support YAML format** (2.1)
3. **Add path normalization** (2.2)

### 🛡️ IMPORTANT (Week 1)
1. **Enhance error handling** (3.1, 3.2)
2. **Update tag policy** (4.2)
3. **Add comprehensive tests**

## Testing Strategy

### Unit Tests Required
```python
def test_path_mapping():
    # Test /config/ mapping to local paths
    assert map_path('/config/hestia/config/test.yaml').name == 'test.yaml'

def test_index_location():
    # Test index file discovery
    assert locate_index().exists()

def test_path_normalization():
    # Test old -> new path conversion
    old = '/config/hestia/core/config/network/test.yaml'
    new = '/config/hestia/config/network/test.yaml'
    assert normalize_artifact_path(old) == new

def test_yaml_format_support():
    # Test current manifest.yaml format
    result = load_index(Path('hestia/config/index/manifest.yaml'))
    assert 'hades_config_index' in result
```

### Integration Tests
1. **End-to-end validation** with actual manifest.yaml
2. **Path resolution** with environment variables
3. **Cross-platform compatibility** (macOS/Linux)

## Risk Assessment

### 🚨 HIGH RISK
- **Breaking existing workflows** if validator is used in CI/CD
- **Path resolution failures** on different environments

### ⚠️ MEDIUM RISK  
- **Performance impact** from path normalization
- **Compatibility issues** with legacy index formats

### ✅ LOW RISK
- **Enhanced error messages** (improvement only)
- **Tag policy updates** (additive changes)

## Success Criteria

1. ✅ **Validator finds index file** at correct location
2. ✅ **All artifact paths resolve** to existing files  
3. ✅ **ADR-0016 compliance** (no hardcoded paths)
4. ✅ **Four-pillar architecture support** 
5. ✅ **Zero regression** in existing functionality
6. ✅ **Comprehensive test coverage** (>90%)

## Rollback Plan

If issues arise:
1. **Keep backup** of original validator
2. **Revert manifest.yaml** to previous state
3. **Disable validator** in CI until fixed
4. **Use git bisect** to identify problematic changes

---

**Estimated Implementation Time**: 2-3 days  
**Priority Level**: **CRITICAL** - required for workspace validation  
**Dependencies**: Four-pillar architecture completion  