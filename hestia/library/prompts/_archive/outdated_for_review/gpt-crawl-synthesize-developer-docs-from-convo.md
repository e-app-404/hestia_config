## 📘 GPT Instruction Set: Synthesizing Sensor Abstractions from Conversation History

### 🧩 1. **Input Sources**
- **Primary Source:** ChatGPT conversation history (acts as a stream-of-consciousness design narrative)
- **Attachments:** Structured data files like `sensor_registry.yaml`, `sensor_motion_score.yaml`, `device_groups.json`, etc.

---

### 🧠 2. **Purpose & Goals**
- Reverse-engineer a working abstraction system from semi-structured design dialogue
- Create formalized:
  - **Architectural principles**
  - **Naming conventions**
  - **Developer guidelines**
  - **YAML config patches**
- Enable robust, modular Home Assistant design that is transparent and easy to maintain.

---

### 📏 3. **Processing Strategy**

#### a. **Conversation Parsing**
- Identify **entities**, **abstraction layers**, and **naming conventions** as described informally.
- Track:
  - Source entities (raw hardware)
  - Aliases and abstraction logic
  - Final automation-facing signals

#### b. **Cross-Referencing Attachments**
- Validate that referenced entity IDs exist and are wired correctly in the configuration files.
- Detect:
  - Missing aliases
  - Incorrect references
  - Gaps in the abstraction chain (e.g., a motion score pointing to a non-existent motion sensor)

#### c. **Semantic Layer Classification**
- Group all sensors using a **Greek-lettered tier system**:
  - `α` = Raw input
  - `β` = Alias/abstract pointer
  - `γ` = Score derivation
  - `δ` = Aggregated or decayed value
  - `ε` = Validated logic
  - `ζ` = Final automation-facing output

#### d. **Delta Computation**
- Identify layers or sensors **expected by logic** but not yet defined in the YAML/configs.
- Create a **delta table** mapping:
  - Room
  - Sensor type
  - Missing tier
  - Suggested name
  - Recommended definition logic

---

### 🧾 4. **Output Generation Process**

#### ➕ a. YAML Patch Generation
For each Greek abstraction tier (`β` → `ζ`):
- Auto-generate Home Assistant-compliant YAML using template or sensor logic.
- Ensure:
  - Unique IDs
  - Device classes (where relevant)
  - Appropriate Jinja2 logic for scoring, decay, validation

#### 📚 b. Developer Documentation
Output a **single-source-of-truth doc** that includes:
- Naming strategy and suffix taxonomy
- Per-sensor-type abstraction stack
- Configuration locations
- Sample logic for each tier
- How-to for testing, validation, debugging

#### 🧱 c. System Integration Guide
Instructions for:
- Importing YAMLs into `/packages/` or `!include` trees
- Reloading templates safely
- Adding validation sensors or audit dashboards

---

### 🧰 5. **Tooling Hooks (Optional Enhancements)**
Suggest custom tools or helpers such as:
- `sensor.abstraction_layer_health`
- `sensor.<room>_debug_greek_stack`
- CLI patch validators
- Metadata versioning files (`metadata_abstraction_greek_layers.yaml`)

---

### ✅ 6. **Success Criteria**
- A complete set of abstracted sensors (`α` to `ζ`) per domain
- No broken or unresolved references in YAML
- Consistent naming and logic across all rooms/zones
- Final `ζ` layer sensors used in automations and UI
