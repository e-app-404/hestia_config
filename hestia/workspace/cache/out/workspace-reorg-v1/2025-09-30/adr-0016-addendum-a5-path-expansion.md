# ADR-0016 Addendum A5: Python Path Expansion Compliance

**Status**: Accepted  
**Date**: 2025-09-30  
**Addendum to**: ADR-0016 (Canonical HA edit root & non‑interactive SMB mount)

## Decision

All Python code using `pathlib.Path()` with tilde (`~`) paths **MUST** call `.expanduser()` to ensure proper path resolution.

## Rationale

Without `.expanduser()`, `Path('~/hass/...')` treats the tilde as literal text, creating incorrect paths like `./~/hass/...` instead of the intended `/Users/username/hass/...`.

## Requirements

### Mandatory Pattern
```python
# ✅ REQUIRED
vault_root = Path('~/hass/hestia/workspace/archive/vault').expanduser()
config_path = Path('~/hass/configuration.yaml').expanduser()

# ✅ ALSO ACCEPTABLE  
vault_root = Path(os.path.expanduser('~/hass/hestia/workspace/archive/vault'))
```

### Prohibited Pattern
```python
# ❌ FORBIDDEN - tilde remains literal
vault_root = Path('~/hass/hestia/workspace/archive/vault')  # Wrong!
```

## Enforcement

### 1. Validation Command
```bash
make adr-0016-validate
```

### 2. Pre-commit Hook
Automatically prevents commits with non-expanded tilde paths in Python files.

### 3. Manual Check
```bash
find hestia -name "*.py" -exec grep -H "Path('~" {} \; | grep -v ".expanduser()"
# Should return no results
```

## Scope

- **Applies to**: All Python files in the `hestia/` directory tree
- **Shell scripts**: Continue using `$HOME` or proper shell expansion
- **Documentation**: May reference patterns for illustration

## Validation Results (Initial)

✅ **Current Status**: All Python files compliant (5 correct examples found)  
✅ **Guardrails**: Validator script and pre-commit hook implemented  
✅ **Integration**: Added to `make adr-0016-validate` target

## Implementation

Implemented in commit workspace-reorg-implementation-20250930 with:
- Validator script: `hestia/tools/utils/validators/adr_0016_path_expansion.sh`  
- Make target: `make adr-0016-validate`
- Pre-commit hook: `.githooks/pre-commit-adr-0016`
- Integration: Main pre-commit hook calls ADR-0016 validator

This addendum ensures path consistency and prevents runtime errors from incorrect path resolution.