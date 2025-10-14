# HESTIA Promptset Documentation

## 📘 Overview

The HESTIA `.promptset` schema defines **multi-phase, protocol-bound GPT prompt workflows** for governance, diagnostics, validation, and controlled generation. It supports both **legacy single-phase** prompts and **modular, future-facing** configurations.

All `.promptset` files must conform to the canonical schema and live under: `/config/hestia/library/prompts/`

## 🧱 Promptset Structure (all fields under `promptset:`)

A valid `.promptset` contains the following root-level blocks:

| Field                  | Type   | Req | Description                                        |
|------------------------|--------|-----|----------------------------------------------------|  
| `promptset`            | object | ✅ | Root container                                     |
| `promptset.id`        | string | ✅ | Unique identifier (e.g., `example_promptset_v1`)   |
| `promptset.version`   | string | ✅ | Semantic version (e.g., `1.0.0`)                   |
| `promptset.created`   | date   | ✅ | Creation date                                      |
| `promptset.description`| string| ✅ | Human-readable summary                             |
| `promptset.persona`   | string | ✅ | Persona that executes                              |
| `promptset.purpose`   | string | ✅ | Operational goal                                   |
| `promptset.legacy_compatibility` | bool | ✅ | Legacy support switch                              |
| `promptset.schema_version` | string | ✅ | Must be `"1.0"` (see JSON schema)                  |
| `promptset.artifacts` | object | ✅ | Required/optional artifact lists                   |
| `promptset.bindings`  | object | ✅ | Protocols/persona bindings                         |
| `promptset.prompts`   | array  | ✅ | Prompt or phase definitions                        |## 📂 Artifact Binding (canonical paths)

```yaml
artifacts:
  required:
    - path: /config/hestia/library/docs/governance/system_instruction.yaml
  optional:
    - path: /config/.workspace/governance_index.md
    - path: /config/hestia/library/docs/governance/persona_registry.yaml
    - path: /config/hestia/library/docs/architecture/promptset_docs.md
````

* `required`: Must be present before promptset is activated
* `optional`: Loaded if present; non-blocking
* Paths may use globs (`**/*.yaml`) in future versions for expanded matching

## 🔐 Protocol Bindings

```yaml
bindings:
  protocols:
    - prompt_optimization_first
    - confidence_scoring_always
    - phase_context_memory
  persona: strategos
```

* Protocols drive behavior enforcement, response format, and scoring
* Persona constrains execution behavior, context memory, and access tier

## 🚦 Operational Modes

Promptsets define one or more `mode` values:

| Mode                     | Description                                      |
| ------------------------ | ------------------------------------------------ |
| `governance_review_mode` | Score GPT outputs, emit diffs, optimize behavior |
| `diagnostic_mode`        | Validate file access, workspace state            |
| `enforcement_mode`       | Require strict output formats or logic           |
| `legacy_mode`            | Support flat, non-phased prompt workflows        |

## 🔁 Phases

Each `.promptset` can define one or more `phases` to break down workflows:

```yaml
phases:
  - name: config_verification
    persona: strategos
    instructions: |
      Check configuration presence and patch consistency.
    outputs:
      - name: config_report.md
        required: true
        content: |
          # Config Validation Results
          ...
```

* `name`: ID of the phase block
* `persona`: Who executes it
* `instructions`: Copilot or GPT-readable directives
* `outputs`: Filename and required flag with preview content

## 🔄 Prompt Composition from Mono-Prompts

Promptsets can be created by composing existing mono-prompt IDs defined elsewhere:

```yaml
phases:
  - name: include_existing
    use_prompt_id: diagnostics.copilot.file_check.v1
  - name: include_git_tracking
    use_prompt_id: diagnostics.copilot.git_visibility.v1
```

* `use_prompt_id`: References an existing mono-prompt stored in a prompt registry or promptset fragment
* This supports prompt chaining and avoids duplication

## 🧰 Migration Block

For converting legacy prompts:

```yaml
migration:
  strategy: |
    - Merge single-phase .prompt files into structured multi-phase promptsets
    - Annotate fallback compatibility using legacy_compatibility: true
```

## 📚 Extensibility & Docs

```yaml
extensibility:
  - Add support for chained promptsets or conditional execution phases
  - Integrate validation schema from promptset_schema.yaml

documentation:
  - Reference: /config/hestia/library/prompts/_meta/promptset_schema.yaml
  - This file: /config/hestia/library/docs/architecture/promptset_docs.md
```

## ✅ Deployment & Validation

**Activation rules**
- Only promptsets under `/config/hestia/library/prompts/active/{category}/` are activation candidates.
- **Nothing** under `migration/*` is executable.
- Activation requires:
  - All `required` artifacts resolve
  - Persona exists in `/config/hestia/library/docs/governance/persona_registry.yaml`
  - Structure validates against `/config/hestia/library/prompts/_meta/promptset_schema.yaml`

**Outputs**
- **Automation logs** → `/config/hestia/library/prompts/logs/` (machine-readable, e.g., `prompt_validation_log.json`)
- **Analytical reports** → `/config/hestia/library/prompts/reports/` (human-readable audits/reviews)

## 🧪 Example Use Cases

| Scenario              | Promptset ID                              | Persona      |
| --------------------- | ----------------------------------------- | ------------ |
| Copilot enforcement   | `copilot_integrity_diagnostics.promptset` | `strategos`  |
| Prompt audits         | `test_kybernetes_001`                     | `kybernetes` |
| Configuration tracing | `config_snapshot_audit.promptset`         | `eunomia`    |

## 📎 Related Schemas & References

* `/config/hestia/library/prompts/_meta/promptset_schema.yaml`
* `/config/hestia/library/docs/governance/system_instruction.yaml`
* `/config/hestia/library/docs/governance/persona_registry.yaml`
* **COPIES**: STANDBY — `catalog/by_domain/` is the single canonical source.

## 🛡 Governance Note

All `.promptset` files are classified as governance-bound configuration. Ensure:

* Changes are committed via Git and version-controlled
* All logic is deterministic and auditable
* Output artifacts pass checksum and integrity validation
* Changes trigger revalidation via `prompt_validation_log.json`

---

End of `promptset_docs.md`