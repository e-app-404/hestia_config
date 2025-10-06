# ADR-0024 Firmlink Hardening - Reboot Required

## Current State (Pre-Reboot)
- **Date**: October 5, 2025
- **Status**: Ready for reboot to materialize firmlink

## Validation Results ✅

### 1. Node Type Analysis
```
node type: Symbolic Link
→ it's a symlink
exists: True is_dir: True realpath: /System/Volumes/Data/homeassistant
```
**Status**: Currently symlink, will become firmlink after reboot

### 2. Synthetic Configuration
```
homeassistant   System/Volumes/Data/homeassistant
config  homeassistant
```
**Status**: ✅ `synthetic.conf` properly configured

### 3. Data Path Readiness
```
drwx------@ 1 evertappels  staff  16384 Oct  5 20:33 /System/Volumes/Data/homeassistant
```
**Status**: ✅ Data path exists, writable, user-owned

### 4. LaunchAgent Configuration
```
MNT="/System/Volumes/Data/homeassistant"
ProgramArguments: ["/Users/evertappels/bin/ha-mount.sh"]
```
**Status**: ✅ Targets correct Data path

### 5. Health Checks
- ✅ Guard script: `tools/lib/require-config-root.sh` functional
- ✅ Health check: `bin/config-health /config` working
- ✅ Path linter: `tools/lint_paths.sh` passing

## Root Filesystem Constraints

```
/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)
rm: /config: Read-only file system
```

**Key Finding**: macOS Sealed System Volume prevents runtime removal of `/config` symlink. This is expected behavior - synthetic entries can only be materialized during boot process.

## Reboot Requirements

### What Will Happen During Reboot:
1. APFS synthetic entry system reads `/etc/synthetic.conf`
2. Creates firmlink: `/config` → `/System/Volumes/Data/homeassistant`
3. Replaces existing symlink with native firmlink directory
4. LaunchAgent mounts SMB share to Data path as usual

### Expected Post-Reboot State:
```bash
# /config will be a directory (firmlink), not symlink
ls -ld /config
# Expected: drwxr-xr-x (directory) instead of lrwxr-xr-x (symlink)

# Realpath resolution unchanged
python3 -c "import os; print(os.path.realpath('/config'))"
# Expected: /System/Volumes/Data/homeassistant

# Mount point check
mount | grep '/config'
# Expected: No output (/config is firmlink, not mount point)

mount | grep '/System/Volumes/Data/homeassistant'  
# Expected: SMB mount active
```

## Post-Reboot Validation Commands

```bash
# 1. Confirm firmlink materialization
echo -n "node type: "; stat -f %HT /config
[[ -L /config ]] && echo "→ still symlink (ERROR)" || echo "→ firmlink success"

# 2. Test functionality
bin/config-health /config
REQUIRE_CONFIG_WRITABLE=0 tools/lib/require-config-root.sh

# 3. Development workflow test
bash /config/hestia/tools/template_patcher/patch_jinja_templates.sh

# 4. Mount verification
mount | grep -E '/config|homeassistant'
```

## Rollback Plan (If Needed)

If firmlink causes issues:
```bash
# Emergency: restore symlink (requires Recovery Mode)
sudo rm -rf /config  # (in Recovery Mode only)
sudo ln -sf System/Volumes/Data/homeassistant /config
```

## Ready State Confirmation

🎯 **ALL SYSTEMS GO FOR REBOOT**

- ✅ synthetic.conf configured correctly
- ✅ Data path prepared and mounted
- ✅ LaunchAgent targeting correct path  
- ✅ All health checks passing
- ✅ Development workflows functional

**Next Step**: `sudo reboot` to materialize firmlink