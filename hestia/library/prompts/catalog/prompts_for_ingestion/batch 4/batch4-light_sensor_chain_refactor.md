## Title: Refactoring Light Sensor Generation Chain for HESTIA

### 🧭 Business Context

HESTIA relies on a robust semantic generation framework to produce stateful and reactive Home Assistant configurations. One of the most complex subsystems involves the rendering of light-related sensors: the light entity templates themselves, availability sensors indicating protocol/device state, and circadian sensors driving behavior based on time-of-day dynamics. All of these are generated from a `template_engine.py` framework leveraging layered Jinja macro libraries.

### 🎯 Objective

Clarify and formalize required enhancements to the current generation pipeline for light-related sensors, with the goal of:

* Improving maintainability and traceability across generated artifacts.
* Explicitly structuring macro roles (e.g., `beta_light`, `availability`, `circadian`) into a coherent, callable chain.
* Embedding richer metadata to support downstream querying, analytics, or diagnostics.
* Ensuring semantic contracts are respected through deterministic rendering flows.

### 🔧 Technical Problem Definition

* The current `template_engine.py` invokes a fragmented set of macros.
* Output YAMLs lack consistency in attribute schemas across sensor types.
* Circadian sensors sometimes mirror rather than source from canonical IDs.
* `light_availability` sensors use `derived_from` inconsistently.
* Component-level ownership (e.g., `theia`, `hephaestus`) is implicit or absent.
* There is ambiguity and inconsistency in how `entity_id`, `unique_id`, and `canonical_id` are defined and used across the system.

### 📘 Canonical ID Standards

Clarify expectations for `canonical_id`, `entity_id`, and `unique_id`:

* `canonical_id`: A semantic identifier used as the primary reference in metadata and generation logic. Format: `<room>_<function>_<α>`.
* `entity_id`: The resulting Home Assistant entity ID (e.g., `sensor.living_room_ceiling_light_status`).
* `unique_id`: A globally unique string required for HA to avoid duplicates—should be hash-derived or deterministically generated from `canonical_id`.

All components must map their `entity_id` and `unique_id` from the `canonical_id` to ensure consistency.

### 🔄 Phased Improvement Strategy

#### Phase 1: Template Contract Finalization

* Define required inputs and output guarantees for each macro.
* Validate and document macro execution flow.
* Standardize macro annotations to ensure traceability.

#### Phase 2: Engine Integration

* Integrate contract validation into `template_engine.py`.
* Implement fail-fast logic for missing context variables (`canonical_id`, `tier`, `role`).
* Support dry-run execution to test all generation logic without writing files.

#### Phase 3: Output Contract Compliance

* Ensure all generated YAML outputs:

  * Contain required metadata headers
  * Are ordered using the `format_contract`
  * Are line-attributed with `origin_macro`, `engine_version`, and `subsystem`

### 🧰 Deterministic Context Resolution

Rendering logic must resolve context in this strict priority:

1. Parsed registry definitions (JSON)
2. Macro default values
3. CLI or override context provided to `template_engine.py`

### 📚 Glossary of Subsystem Responsibilities

* `theia`: Light circadian and environment state modeling
* `hephaestus`: Availability and failover logic
* `hermes`: Role resolution and semantic metadata assignment
* `hestia_beta`: Light control interface macros (tier β)

### 🛠 Configuration Impacts

* Affects `config/hestia/core/template/subsystem_macros_theia/light_availability_template.yaml`
* Affects `gen_beta_light_templates_*.yaml`, `gen_circadian_room_sensors_*.yaml`
* Requires re-validation of light role resolution in `alpha_light_registry.json`
* Interfaces with service scripts: `set_room_lighting`, `validate_lighting_configuration`

### ✅ Desired Output Behavior

* Generated YAML files should be line-attributed with macro, engine, and canonical lineage.
* Template engine should support dry-run validation mode with explicit pass/fail and JSON error output.
* Every output sensor must adhere to a contract with explicit `type`, `tier`, and `role` metadata fields.
* All sensors should be referenceable by canonical ID, with derived `entity_id` and `unique_id` values properly aligned.
* Each YAML should declare its `format_contract`, defining field order.

### 📋 Reference Artifacts: Validation Blueprint & Output Structure

#### 🧩 Validation Blueprint (YAML Schema Example)

```yaml
# format_contract: canonical_light_v1
# engine_version: hestia_template_engine_v3.0.4
# generated_at: 2025-05-28
# generated_by: beta_light_template_macro
# phase_executed: phase_3
# context_lineage: tier_beta > beta_light > hephaestus_availability

sensor:
  - name: "Living Room Light Status"
    unique_id: "58fa2b7e7c34f0a1"
    state: "{{ states('light.living_room_main') }}"
    attributes:
      canonical_id: "living_room_ceiling_light_α"
      tier: "beta"
      role: "primary_light"
      subsystem: "hestia_beta"
      type: "status"
      derived_from: "light.living_room_main"
      validated_by: "validator.hestia_v7_macro_chain"
      origin_macro: "beta_light_template_macro"
      engine_version: "hestia_template_engine_v3.0.4"
      phase_executed: "phase_3"
      context_lineage: "tier_beta > beta_light > hephaestus_availability"
      format_contract: "canonical_light_v1"
```

#### 🧪 Dry-Run JSON Output Stub (Best-in-Class Example)

```json
{
  "execution_metadata": {
    "engine_version": "hestia_template_engine_v3.0.4",
    "phase": "phase_3",
    "macro": "beta_light_template_macro",
    "timestamp": "2025-05-28T14:22:00Z"
  },
  "validation_result": "pass",
  "sensor_artifact": {
    "canonical_id": "living_room_ceiling_light_α",
    "entity_id": "sensor.living_room_ceiling_light.status",
    "unique_id": "58fa2b7e7c34f0a1",
    "tier": "beta",
    "role": "primary_light",
    "subsystem": "hestia_beta",
    "type": "status",
    "origin_macro": "beta_light_template_macro",
    "derived_from": "light.living_room_main",
    "format_contract": "canonical_light_v1"
  },
  "compliance": {
    "missing_fields": [],
    "extraneous_fields": [],
    "field_order_valid": true,
    "format_contract_match": true
  },
  "confidence_metrics": {
    "structural": { "score": 98, "rationale": "All keys present and schema-validated" },
    "operational": { "score": 95, "rationale": "Can be loaded and interpreted by HA directly" },
    "semantic": { "score": 94, "rationale": "ID logic matches canonical role structure and usage intent" },
    "adoption_recommendation": true
  }
}
```

---

## ✅ Engineered Prompt

You are the semantic compiler for HESTIA’s Home Assistant configuration layer. Please update the `template_engine.py` system to implement the following structured changes:

### Task

Enhance the generation chain for light-related sensors, including:

1. **Light Entity Templates** (from `beta_light_template_macro.jinja`)
2. **Light Availability Sensors** (from `light_availability_macro.jinja`)
3. **Circadian Modulators** (from `theia_circadian_room_sensors_*.jinja`)

### Requirements

* All generated sensors must include `canonical_id`, `tier`, `role`, `subsystem`, `type`, `origin_macro`, `engine_version`, `derived_from`, and `validated_by` as metadata attributes.
* Canonical ID must serve as the source of truth for both `entity_id` and `unique_id`.
* Macro execution should be logged and its result traceable.
* Adjust `template_engine.py` to perform field uniqueness checks before YAML rendering.
* All tiers must resolve via the corresponding macro libraries (`tier_beta`, `tier_gamma`, etc.)
* Support dry-run validation mode returning structured output (pass/fail + issues).
* Output YAML must follow strict format ordering and include `format_contract` metadata.
* All macro outputs must be annotated with `origin_macro`, `phase_executed`, and `context_lineage`.

### Output

* Regenerated YAMLs that replace `gen_beta_light_templates`, `light_availability_output`, and `gen_circadian_room_sensors`.
* Each entry should contain inline comments where generated and metadata headers.

### Target Files

* `template_engine.py`
* `macro_abstraction_templates.jinja`
* `beta_light_template_macro.jinja`
* `light_availability_macro.jinja`
* `theia_circadian_room_sensors*.jinja`
* consult the remaining documents in project knowledge as supporting context. 

Execute with full semantic integrity and structured metadata compliance. Prioritize robust scripting and conservative code for flawless and bug-free runtime execution.
