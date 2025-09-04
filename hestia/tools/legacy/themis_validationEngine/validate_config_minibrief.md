## ✅ **Option 1: `validate_config.py` CLI Scaffold**

A local tool you can run on any Home Assistant config to validate real loader behavior.

**Features**:

* Accepts root `configuration.yaml`
* Recursively resolves all `!include` directives
* Enforces `.yaml` suffix, structure shape, merge behavior
* Emits:

  * ✅ success with merged keys
  * ⚠️ warnings for invalid structures
  * ❌ errors for loader breakage

**Suggested Invocation**:

```bash
python3 validate_config.py --root /config/configuration.yaml
```

**Scaffold Includes**:

* Forked subset of `homeassistant/util/yaml/loader.py`
* Custom warnings and exceptions for merge rule violations
* Optional: Output resolved config tree as JSON

---

## 🧠 **Option 2: `protocol_loader_simulation_v1` (for `system_instruction.yaml`)**

Static GPT-enforced loader rules that simulate `loader.py` logic.

```yaml
- id: protocol_loader_simulation_v1
  description: >
    Emulates loader.py behavior statically — validates file extensions, merge rules, and structural shapes
    for all !include directives and package configurations.
  applies_to_roles: [Hestia, Promachos, MetaStructor]
  triggers:
    - config scan involving `!include` or `packages:`
    - execution_mode in [generate, validate]
    - doctrinal enforcement of include/loader semantics
  actions:
    - Validate that only `.yaml` files are scanned
    - Enforce correct directive usage (`!include_dir_merge_list` with list-shaped YAML only, etc.)
    - Simulate merge behavior (last-key-wins for named includes, sorted lists for dir merges)
    - Check `packages:` target only dict-shaped configs
  fallback_behavior: warn_on_invalid_merge_or_shape
  audit_tags:
    - mode: STATIC_LOADER_VALIDATION
    - context: CONFIG_TREE_SHAPE
```
