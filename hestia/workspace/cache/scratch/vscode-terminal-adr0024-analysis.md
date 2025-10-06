# VS Code Terminal Settings Recommendations for ADR-0024 Compliance

## Current Status Analysis

### ✅ COMPLIANT SETTINGS
- `terminal.integrated.env.osx.PATH`: Only modifies PATH, no HA path conflicts
- Python integration uses `${workspaceFolder}` correctly
- No conflicting terminal.integrated.cwd overrides

### ⚠️ NEEDS ALIGNMENT
- `.env` file contains legacy `$HOME/hass` references
- Environment variables loaded via `python.terminal.useEnvFile` propagate non-canonical paths

## Recommended Settings Updates

### 1. VS Code Workspace Settings (.vscode/hass-live.code-workspace)

Add these terminal-specific settings:

```json
{
  "settings": {
    // Ensure terminal starts in canonical workspace root
    "terminal.integrated.cwd": "${workspaceFolder}",
    
    // Environment variables that enforce ADR-0024 compliance  
    "terminal.integrated.env.osx": {
      "PATH": "/opt/homebrew/bin:${env:PATH}",
      // Override any legacy env vars with canonical paths
      "CONFIG_ROOT": "/config",
      "HA_CANONICAL_ROOT": "/config",
      // Ensure Python tools use canonical path
      "PYTHONPATH": "/config:${env:PYTHONPATH}"
    },
    
    // Automation profile for tasks - ensure they use canonical paths
    "terminal.integrated.automationProfile.osx": {
      "path": "/bin/zsh",
      "env": {
        "CONFIG_ROOT": "/config",
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### 2. Updated .env File

Replace legacy path variables:

```bash
# ADR-0024 COMPLIANT PATHS
export CONFIG_ROOT="/config"
export HA_CANONICAL_ROOT="/config"

# Legacy compatibility (marked for deprecation)
# export HA_MOUNT="$HOME/hass"  # DEPRECATED - use CONFIG_ROOT

# Update derived paths to use canonical root
export DIR_HESTIA="/config/hestia"
export DIR_PACKAGES="/config/packages"
export DIR_DOMAINS="/config/domains"
export TEMPLATE_CANONICAL="/config/custom_templates/template.library.jinja"
```

### 3. Additional Terminal Behavior Controls

```json
{
  "settings": {
    // Prevent terminals from inheriting conflicting environment
    "terminal.integrated.inheritEnv": false,
    
    // Split terminals should start in workspace root (canonical path)
    "terminal.integrated.splitCwd": "workspaceRoot",
    
    // For tasks and automation, use clean environment
    "terminal.integrated.automationProfile.osx": {
      "path": "/bin/zsh",
      "args": ["-l"],
      "env": {
        "CONFIG_MOUNT": "/config",
        "WORKSPACE_ROOT": "/config"
      }
    }
  }
}
```

## Implementation Priority

### HIGH PRIORITY
1. **Update .env file** to use `/config` instead of `$HOME/hass`
2. **Add terminal.integrated.env.osx.CONFIG_ROOT** override
3. **Set terminal.integrated.cwd** to ensure canonical workspace root

### MEDIUM PRIORITY  
4. **Configure automation profile** for tasks
5. **Add PYTHONPATH** override for Python tools
6. **Set inheritEnv: false** for clean environment

### LOW PRIORITY
7. **Configure split terminal behavior**
8. **Add workspace-specific shell profiles**

## Validation Commands

After implementing changes:

```bash
# Test terminal environment
echo $CONFIG_ROOT  # Should show: /config
echo $PWD          # Should show: /System/Volumes/Data/homeassistant
python3 -c "import os; print(os.path.realpath('/config'))"  # Should work

# Test task execution
# Run any VS Code task - should use canonical paths
```

## Risk Assessment

**LOW RISK**: These changes only affect terminal environment, not filesystem operations
**COMPATIBILITY**: Maintains backward compatibility while promoting canonical paths
**VALIDATION**: Can be tested immediately without system changes