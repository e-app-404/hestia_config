# ADR-0016 Path Expansion Compliance Patch

## Summary
Add explicit requirement for `.expanduser()` with tilde paths in Python code to ADR-0016.

## Proposed Addition to ADR-0016

Add new section under "Canonicalization rules":

### 4. Python Path Expansion Requirements

**MANDATORY**: All Python code using `pathlib.Path()` with tilde (`~`) paths MUST call `.expanduser()`:

```python
# ✅ CORRECT
vault_root = Path('~/hass/hestia/workspace/archive/vault').expanduser()
ha_mount = Path('~/hass').expanduser() 
config_path = Path('~/hass/configuration.yaml').expanduser()

# ❌ INCORRECT - tilde remains literal
vault_root = Path('~/hass/hestia/workspace/archive/vault')  # becomes ./~/hass/...
```

**Rationale**: Without `.expanduser()`, `Path('~/...')` treats tilde as literal text, creating paths like `./~/hass/...` instead of `/Users/username/hass/...`.

**Alternative**: Use `os.path.expanduser('~/hass')` with `Path()` constructor:
```python
# Also acceptable
vault_root = Path(os.path.expanduser('~/hass/hestia/workspace/archive/vault'))
```

**Shell Scripts**: Use `$HOME` or command substitution instead of tilde in scripts:
```bash
# ✅ CORRECT
VAULT_DIR="$HOME/hass/hestia/workspace/archive/vault"
TARBALL_DIR="$(eval echo ~$USER)/hass/hestia/workspace/archive/vault/tarballs"

# ⚠️ CAUTION - works only in some contexts
VAULT_DIR="~/hass/hestia/workspace/archive/vault"  # May not expand
```

### Validation Commands

```bash
# Check Python files for non-expanded tilde paths
find hestia -name "*.py" -exec grep -H "Path('~" {} \; | grep -v ".expanduser()"
find hestia -name "*.py" -exec grep -H 'Path("~' {} \; | grep -v ".expanduser()"

# Should return empty (no matches)
```