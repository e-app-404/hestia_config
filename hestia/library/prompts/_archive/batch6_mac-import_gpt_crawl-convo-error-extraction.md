# 🛠️ GPT Mid-Conversation Error Resolution & Stability Protocol

### 🎯 Objective

When a GPT is involved in resolving implementation bugs, YAML validation errors, sensor logic failures, or conversation-based debugging:

- Identify recurring **error patterns**
- Classify and document **fix strategies**
- Suggest architectural **stabilizers**
- Populate `ERROR_PATTERNS.md` and suggest corrections to other files if needed (`DESIGN_PATTERNS.md`, `developer_guidelines.md`, etc.)

### 1. 📂 Categorize Insights

| Category | Description | Target |
|----------|-------------|--------|
| **Recurring Bug** | Specific implementation flaw that may repeat | `ERROR_PATTERNS.md` |
| **Validation Fix Strategy** | Corrective actions for schema or runtime YAML errors | `developer_guidelines.md` or `error_patch_notes/` |
| **Stability Patch** | Recommended long-term prevention strategy | `DESIGN_PATTERNS.md` |
| **Tooling Feedback** | Suggests improvements to validation or debugging tools | Internal ticket or doc comment

### 2. 🔍 Extraction Targets

Continuously monitor the conversation for:

- YAML errors (schema mismatches, unrecognized fields)
- Logic faults (unexpected sensor states, circular dependencies)
- Misaligned tiering (e.g., `_γ` logic depending directly on `_α`)
- Common misconfigurations (missing `availability`, wrong `platform`, etc.)
- Bugs fixed through pattern changes (indicating systemic issues)

### 3. 📘 Output Templates

#### For Error Pattern (`ERROR_PATTERNS.md`)
```markdown
### ❌ Direct Reference to Raw Sensors Breaks Logic Layers

**Symptom**:
Logic sensors fail or produce incorrect states when referencing raw `_α` sensors directly.

**Example**:
```yaml
# ❌ This fails abstraction
sensor.motion_score_γ:
  value_template: "{{ is_state('binary_sensor.motion_sensor_α', 'on') }}"
```

**Fix**:
```yaml
# ✅ Use an alias abstraction layer
sensor.motion_score_γ:
  value_template: "{{ is_state('binary_sensor.motion_β', 'on') }}"
```

**Detected In**: `conversation_2025-04-09.md`

**Suggested Pattern Fix**: Add alias enforcement note in `DESIGN_PATTERNS.md`

**Tags**: `sensor design`, `logic error`, `tier mismatch`
```

#### For Developer Guidelines
```markdown
## 🔧 Fixing “unknown” State Errors in Logic Sensors

Logic sensors may show "unknown" if their input source (`_β`) is unavailable or misaligned.

✅ Add an `availability` section to ensure proper logic flow:

```yaml
binary_sensor.motion_β:
  platform: template
  availability: "{{ states('binary_sensor.motion_α') != 'unavailable' }}"
```

This prevents runtime "unknown" cascades into logic layers.
```

#### For Design Pattern Fix (if generalized)
```markdown
### Add `availability` Guards in All Alias Sensors

To prevent cascading “unknown” or `None` states:

✅ Do:
```yaml
binary_sensor.motion_β:
  availability: "{{ states('binary_sensor.motion_α') != 'unavailable' }}"
```

This enforces predictable input conditions.
```

### 4. 🏷️ Metadata Requirements

Each issue documented should contain:

```yaml
origin: conversation_2025-04-09.md
context: logic sensor misfiring due to alias omission
tags: [bug, validation, tiering]
contributor: gpt_debugger
status: proposed  # or resolved
```

### 5. ⚖️ Triage Logic (when both architecture + bug resolution apply)

Use this logic when both extractor types are active:

| Insight Type | Route to |
|--------------|----------|
| Architectural standard not followed → Design Pattern / Doctrine |
| Bug caused by misuse of standard → Error Pattern + Pattern crosslink |
| Developer confusion → Developer Guidelines |
| Tool or process flaw → Suggest internal doc/tool fix |
