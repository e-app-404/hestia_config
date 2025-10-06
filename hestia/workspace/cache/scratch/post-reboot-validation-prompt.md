# Post-Reboot ADR-0024 Validation Request

## Context Recovery Prompt

**Copy and paste this prompt after reboot to restore full context:**

---

I just rebooted my macOS system after implementing ADR-0024 canonical /config path hardening. Before the reboot, we completed a comprehensive firmlink hardening process and all pre-reboot validations passed.

**Please restore context and perform a complete post-reboot validation by:**

1. **Reading the full session context** from:
   - `hestia/workspace/cache/scratch/session-context-export-2025-10-05.md`
   - `hestia/library/docs/ADR/ADR-0024-canonical-config-path.md` 
   - `hestia/workspace/cache/scratch/firmlink-hardening-reboot-status.md`

2. **Running comprehensive post-reboot validation** including:
   - Firmlink materialization check (`stat -f %HT /config`)
   - Path resolution verification (`python3 -c "import os; print(os.path.realpath('/config'))"`)
   - Mount status analysis (`mount | grep homeassistant`)
   - Health check suite (`bin/config-health`, guard scripts, linters)
   - Development workflow testing (template patcher, VS Code tasks)
   - Environment variable validation

3. **Implementing any remaining ADR-0024 compliance items**:
   - Apply `.env.adr0024` if environment needs updating
   - Update VS Code workspace settings if needed
   - Clean up any legacy path references

4. **Providing a final implementation status report** with:
   - Success/failure of firmlink materialization
   - Complete validation results
   - Any issues found and fixes applied
   - Updated ADR-0024 documentation if needed

**Expected outcome**: Confirmation that ADR-0024 is fully implemented with a native APFS firmlink at `/config` and all development workflows operational.

**Key success indicator**: `/config` should show as a directory (not symlink) with `stat -f %HT /config` returning "Directory".

---

## Quick Reference Commands

If you need to run the validation suite quickly:

```bash
# Firmlink status
echo -n "node type: "; stat -f %HT /config
[[ -L /config ]] && echo "→ symlink" || echo "→ directory/firmlink"

# Path resolution  
python3 -c "import os; print('Config realpath:', os.path.realpath('/config'))"

# Health checks
bin/config-health /config
REQUIRE_CONFIG_WRITABLE=0 tools/lib/require-config-root.sh
tools/lint_paths.sh

# Development workflow
bash /config/hestia/tools/template_patcher/patch_jinja_templates.sh

# Mount verification
mount | grep -E '/config|homeassistant'
```

## Context Files Locations

All session context preserved in these files:
- `hestia/workspace/cache/scratch/session-context-export-2025-10-05.md`
- `hestia/workspace/cache/scratch/firmlink-hardening-reboot-status.md`  
- `hestia/workspace/cache/scratch/vscode-terminal-adr0024-analysis.md`
- `hestia/library/docs/ADR/ADR-0024-canonical-config-path.md`

Ready-to-apply configuration files:
- `.env.adr0024` (ADR-0024 compliant environment)
- `.vscode/hass-live.code-workspace.adr0024` (terminal settings)