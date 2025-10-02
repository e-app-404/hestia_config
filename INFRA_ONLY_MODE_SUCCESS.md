# Infra-Only Mode Soft-Success Implementation

## Summary

Successfully implemented soft-success behavior for infra-only restoration mode when `/config/.storage` is missing, eliminating false-positive workflow failures.

## Problem Statement

**Before:** Workflow runs in CI/infra-only mode would exit with code `1` when encountering missing `.storage` directory, even though this is the expected state for:
- Fresh HA installations
- Infrastructure-only restoration scenarios
- CI validation runs

**Error Log:**
```
📋 Phase 2: Complete Current System Backup
🔄 Creating comprehensive backup of current .storage directory...
❌ Current .storage directory not found
exit 1
```

## Root Cause

The script's Phase 2 backup logic treated missing `.storage` as a hard failure regardless of restoration mode:

```bash
if [[ ! -d "$STORAGE_DIR" ]]; then
    echo "❌ Current .storage directory not found"
    exit 1
fi
```

This was correct for registry-restoration scenarios (protect against data loss) but wrong for infra-only mode where `.storage` absence is expected.

## Solution

Added conditional soft-fail logic that checks `SKIP_REGISTRY` flag before exiting:

### Phase 2: Backup Logic Enhancement

```bash
if [[ ! -d "$STORAGE_DIR" ]]; then
    if [[ "${SKIP_REGISTRY:-}" = "1" ]]; then
        echo "🟨 No /config/.storage present and SKIP_REGISTRY=1 → infra-only mode; skipping backup (no-op)."
        INFRA_ONLY=1
    else
        echo "❌ Current .storage directory not found (and registry restore is enabled)."
        echo "ℹ️  Create it or run with --skip-registry/CI to do infra-only."
        exit 1
    fi
fi
```

### Phase 5: Early Exit for Infra-Only

```bash
# Early exit for infra-only mode when .storage is missing
if [[ "${INFRA_ONLY:-}" = "1" ]]; then
    echo "✅ Infra-only mode complete (no .storage to restore to)."
    echo "ℹ️  When /config/.storage exists, re-run without --skip-registry (or with --write-registry) to restore registry files."
    exit 0
fi
```

## Behavior Matrix

| Scenario | .storage Exists | SKIP_REGISTRY | Result |
|----------|----------------|---------------|---------|
| Full restoration | ✅ Yes | 0 (disabled) | Backs up, restores all files |
| Full restoration | ❌ No | 0 (disabled) | **Exit 1** (fail fast - protect data) |
| Infra-only (CI) | ✅ Yes | 1 (enabled) | Backs up, skips registry files |
| Infra-only (CI) | ❌ No | 1 (enabled) | **Exit 0** ✅ (soft-success) |

## Validation

### Workflow Run: 18181117565

**Status:** ✅ Success (green checkmark)

**Phase 2 Output:**
```
📋 Phase 2: Complete Current System Backup
🔄 Creating comprehensive backup of current .storage directory...
🟨 No /config/.storage present and SKIP_REGISTRY=1 → infra-only mode; skipping backup (no-op).
```

**Phase 5 Output:**
```
📋 Phase 5: Complete System Restoration Execution
🛡️  Registry writes skipped (SKIP_REGISTRY=1). Infra-only restoration in effect.
✅ Infra-only mode complete (no .storage to restore to).
ℹ️  When /config/.storage exists, re-run without --skip-registry (or with --write-registry) to restore registry files.
```

**Exit Code:** 0 (success)

## CI Auto-Skip Logic

The v2.6 safety header automatically enables `SKIP_REGISTRY` in CI environments:

```bash
# If in CI and no explicit write requested, default to skip
if [ "${CI:-}" = "true" ] && [ "$WRITE_REGISTRY" -ne 1 ]; then
  SKIP_REGISTRY=1
fi
```

Workflow passes `CI=true` explicitly:
```bash
ssh hass "cd /tmp/${BUNDLE_DIR} && CI=true ./deploy_complete_restoration.sh --backup-source ${HA_DST} --skip-matter"
```

## Safety Guarantees Preserved

1. **Full restoration still protected:**
   - Without `--skip-registry` or `CI=true`, missing `.storage` is still a hard failure
   - Prevents accidental data loss in manual restoration scenarios

2. **Explicit opt-in for registry writes:**
   - `--write-registry` flag overrides CI auto-skip
   - Use when you actually want to restore registry files

3. **Clear user guidance:**
   - Error messages explain what's happening
   - Exit messages provide next steps

## Files Modified

### hestia/workspace/operations/deploy/ha_complete_restoration_v2.0/deploy_complete_restoration.sh

**Phase 2 (lines ~374-388):**
- Added `INFRA_ONLY=1` flag when `.storage` missing in skip mode
- Preserved fail-fast for non-skip scenarios

**Phase 5 (lines ~577-583):**
- Added early exit check for `INFRA_ONLY=1`
- Provides clear completion message

### home_assistant_complete_restoration_v2.6_PRODUCTION.tar.gz
- Rebuilt bundle with updated script
- Size: 87KB (unchanged)

## Commit Details

```
commit d60b7b0
fix(v2.6): infra-only soft-success when .storage missing

- Phase 2: Check SKIP_REGISTRY=1 before failing on missing .storage
- Set INFRA_ONLY=1 flag when missing .storage in registry-skip mode
- Phase 5: Early exit with success (exit 0) for INFRA_ONLY=1
- Net effect: CI/infra-only runs exit green even when .storage absent
- Registry restore still fails fast if .storage missing without skip flag
```

## Usage Examples

### CI/Automation (Default Safe Behavior)
```bash
# CI=true automatically enables SKIP_REGISTRY=1
CI=true ./deploy_complete_restoration.sh --backup-source /tmp/_backup_source/.storage
# Result: Exit 0 even if .storage missing
```

### Manual Infra-Only
```bash
./deploy_complete_restoration.sh --backup-source /path/to/backup --skip-registry
# Result: Exit 0 if .storage missing, skip registry files if present
```

### Full Restoration (Protected)
```bash
./deploy_complete_restoration.sh --backup-source /path/to/backup
# Result: Exit 1 if .storage missing (fail fast - protect data)
```

### Force Registry Write in CI
```bash
CI=true ./deploy_complete_restoration.sh --backup-source /path --write-registry
# Result: Exit 1 if .storage missing (explicit opt-in overrides auto-skip)
```

## Future Enhancements (Optional)

1. **Workflow Input for Registry Control:**
   ```yaml
   inputs:
     write_registry:
       description: 'Force registry writes (override CI auto-skip)'
       type: boolean
       default: false
   ```

2. **HA CLI Noise Suppression:**
   ```bash
   ssh hass "ha core stop && ha core info | grep state" 2>&1 | grep -v "401 Unauthorized" || true
   ```

3. **Pre-create .storage for Testing:**
   ```bash
   ssh hass "mkdir -p /config/.storage && chown $(id -un) /config/.storage" || true
   ```

## Testing Checklist

- ✅ CI run with missing .storage → Exit 0 (green)
- ✅ Manual run with `--skip-registry` and missing .storage → Exit 0
- ✅ Manual run WITHOUT `--skip-registry` and missing .storage → Exit 1 (fail fast)
- ✅ CI run with existing .storage → Backs up, skips registry files
- ✅ v2.6 safety features active (CI detection, tmp operations)
- ✅ Post-run troubleshooting shows correct flags

## Success Metrics

**Before Fix:**
- Workflow Status: ❌ Failed (exit code 1)
- User Experience: False-positive failure requiring manual investigation
- CI Reliability: Inconsistent (depends on .storage presence)

**After Fix:**
- Workflow Status: ✅ Success (exit code 0)
- User Experience: Clear messaging about infra-only mode
- CI Reliability: Deterministic (always succeeds in expected scenarios)

---

**Date:** 2 October 2025  
**Bundle Version:** v2.6 with infra-only soft-success  
**Workflow Run:** 18181117565 (✅ Success)  
**Commits:** bd11f81 (bundle extraction) → 447064d (docs) → d60b7b0 (infra-only fix)
