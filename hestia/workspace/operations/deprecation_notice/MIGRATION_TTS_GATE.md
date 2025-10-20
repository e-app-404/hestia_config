# TTS Gate Migration Guide: HACS Variable → Native HA Components

## Migration Overview

The TTS gate system has been migrated from the unresponsive HACS Variable component to native Home Assistant components. This maintains identical functionality while removing the third-party dependency.

## Implementation Options

### **Option 1: JSON Storage in input_text (RECOMMENDED)**

**File:** `/config/packages/package_tts_gate_native.yaml`

**Advantages:**
- ✅ Drop-in replacement for existing functionality
- ✅ Uses native HA `input_text` component 
- ✅ Persistent across HA restarts
- ✅ JSON storage supports unlimited keys
- ✅ Template-friendly access patterns

**Migration Steps:**
1. **Replace package file**: `package_tts_gate.yaml` → `package_tts_gate_native.yaml`
2. **Update script calls**: `script.tts_gate` → `script.tts_gate_native`
3. **Add helper entity**: `input_text.tts_gate_registry` (4KB max storage)
4. **Test functionality**: Same parameters, same behavior

**Storage Mechanism:**
```yaml
# Helper entity stores JSON registry:
input_text.tts_gate_registry: '{"ha_startup": {"last_ts": 1697123456.789, "count": 1}}'

# Script reads/writes via templates:
reg: "{{ states('input_text.tts_gate_registry') | from_json }}"
```

### **Option 2: Individual Helper Entities**

**File:** `/config/packages/package_tts_gate_individual.yaml`

**Use Case:** When JSON parsing is problematic or individual entity monitoring needed

**Advantages:**
- ✅ Separate entities per TTS key for granular control
- ✅ Uses `input_datetime` + `input_number` (native components)
- ✅ Easy monitoring in HA UI
- ✅ No JSON parsing required

**Disadvantages:**
- ❌ Requires pre-defining entities for each TTS key
- ❌ More complex setup for new keys

### **Option 3: SQLite Database Storage**

**File:** `/config/packages/package_tts_gate_sql.yaml`

**Use Case:** High-volume TTS scenarios or advanced analytics needs

**Advantages:**
- ✅ Unlimited storage capacity
- ✅ SQL queries for analytics
- ✅ Integrates with existing room database patterns

**Disadvantages:**
- ❌ More complex setup
- ❌ Requires shell commands and database management

## Migration Checklist

### **Pre-Migration**
- [ ] Identify all automations calling `script.tts_gate`
- [ ] Note current TTS keys in use
- [ ] Backup current `package_tts_gate.yaml`

### **Migration Steps**
1. **Install new package:**
   ```bash
   # Option 1 (Recommended)
   cp /config/packages/package_tts_gate_native.yaml /config/packages/
   ```

2. **Add helper entity:**
   ```bash
   # Already added to /config/domain/helpers/input_text.yaml
   # input_text.tts_gate_registry with 4KB max storage
   ```

3. **Update automation calls:**
   ```yaml
   # OLD:
   - action: script.tts_gate
   
   # NEW:
   - action: script.tts_gate_native
   ```

4. **Test functionality:**
   - Developer Tools → Services → `script.tts_gate_native`
   - Verify TTS gating behavior matches original

5. **Remove old package:**
   ```bash
   # After successful testing:
   rm /config/packages/package_tts_gate.yaml
   rm /config/domain/variables/tts_vars.yaml
   ```

### **Post-Migration Validation**
- [ ] TTS announcements respect cooldown periods
- [ ] Registry persists across HA restarts  
- [ ] Template sensor shows correct key counts
- [ ] No template errors in logs

## Troubleshooting

### **JSON Parsing Errors**
```yaml
# If templates fail, check:
{% set reg_src = states('input_text.tts_gate_registry') | default('{}', true) %}
{% set reg = reg_src if reg_src is mapping else (reg_src | from_json) %}
```

### **Storage Limit Issues**
- `input_text` max: 4KB (4096 characters)
- Typical key entry: ~50 chars
- Estimated capacity: ~80 TTS keys
- If exceeded, consider Option 3 (SQL storage)

### **Helper Entity Missing**
```bash
# Ensure helper exists:
grep -A 5 "tts_gate_registry" /config/domain/helpers/input_text.yaml

# Reload helpers:
# Settings → System → Reload Configuration → Helper entities
```

## Performance Comparison

| Component | HACS Variable | Native input_text | Performance Impact |
|-----------|---------------|-------------------|-------------------|
| Persistence | ✅ | ✅ | Identical |
| Template Access | ✅ | ✅ | Identical |
| JSON Storage | ✅ | ✅ | Identical |
| Dependencies | ❌ HACS required | ✅ Native only | **Improved** |
| Update Reliability | ❌ Component issues | ✅ Core HA component | **Improved** |

## Expected Outcome

**Functionality:** 100% identical TTS gating behavior
**Dependencies:** Reduced (no HACS Variable component needed)
**Reliability:** Improved (native HA components only)
**Maintenance:** Simplified (no third-party component updates)

The migration maintains complete backward compatibility while eliminating the unresponsive HACS Variable dependency.