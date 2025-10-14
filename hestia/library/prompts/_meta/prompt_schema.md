# HESTIA Promptset Documentation

## 📘 Overview

The HESTIA `.promptset` schema defines **multi-phase, protocol-bound GPT prompt workflows** for governance, diagnostics, validation, and controlled generation. It supports both **legacy single-phase** prompts and **modular, future-facing** configurations.

All `.promptset` files should conform to the canonical schema and be located under: `/config/hestia/library/prompts/`.

## 🧱 Promptset Structure

A valid `.promptset` contains the following root-level blocks:

| Field              | Type     | Required | Description |
|-------------------|----------|----------|-------------|
| `promptset`        | object   | ✅        | Root container for all fields |
| `id`               | string   | ✅        | Unique identifier (snake_case recommended) |
| `version`          | string   | ✅        | Semantic version |
| `created`          | date     | ✅        | Creation date |
| `description`      | string   | ✅        | Human-readable summary |
| `persona`          | string   | ✅        | Persona expected to execute the promptset |
| `purpose`          | string   | ✅        | Operational goal or scenario coverage |
| `legacy_compatibility` | bool | ✅        | If true, supports older prompt systems |
| `schema_version`   | string   | ✅        | Must match current validator schema (`1.0`) |

## 📂 Artifact Binding

```yaml
artifacts:
  required:
    - path: /mnt/data/system_instruction.yaml
    - path: /mnt/data/architecture_doctrine.yaml
  optional:
    - path: .workspace/governance_index.md
    - path: /mnt/data/hades_config_index.yaml
```

* `required`: Must be available in environment before promptset activation
* `optional`: Used if present; non-fatal if missing
* Paths may include globs (`**/*.yaml`) for auto-binding in future releases

## 🔐 Protocol Bindings

```yaml
bindings:
  protocols:
    - prompt_optimization_first
    - confidence_scoring_always
    - phase_context_memory
  persona: strategos
```

- Each promptset can bind to **enforced protocols** from `system_instruction.yaml`
- These drive formatting, scoring, and behavioral compliance
- Persona logic determines execution behavior, response authority, and context retention


## 🚦 Operational Modes

Promptsets define a primary `mode`, such as:

| Mode                     | Description                               |
| ------------------------ | ----------------------------------------- |
| `governance_review_mode` | Protocol audits, scorecards, diffs        |
| `diagnostic_mode`        | File/system/env validation                |
| `enforcement_mode`       | Output contracts, Copilot protocol checks |
| `legacy_mode`            | Single-turn legacy prompts                |

Multiple modes can be defined for phased activation.


## 🔁 Phases

Each promptset may include multiple `phases`:

```yaml
phases:
  - name: file_write_integrity
    persona: strategos
    instructions: |
      ...
    outputs:
      - name: write_integrity_report.md
        required: true
        content: |
          # Report
          ...
```

- `name`: Internal ID
- `persona`: Execution agent
- `instructions`: Prompt body (shown to GPT/Copilot)
- `outputs`: Artifact names + content emitted per phase

## 🧰 Migration Block

For adapting legacy prompts:

```yaml
migration:
  strategy: |
    - Consolidate legacy prompt formats into multi-phase blocks
    - Add compatibility flag for validator fallback
```


## 📚 Extensibility & Docs

```yaml
extensibility:
  - Add new operational modes and artifacts as required
  - Validate with promptset_schema.yaml
documentation:
  - Reference: /mnt/data/promptset_schema.yaml
  - For usage patterns: promptset_docs.md
```


## ✅ Deployment & Validation

Place finalized promptsets in:

`/config/hestia/library/prompts/migration/incoming/`

They are activated automatically if:

- All `required` artifacts resolve
- Persona constraints are met
- Phases follow correct structure

Validator feedback is issued via:

- `/config/hestia/library/prompts/migration/prompt_validation_log.json` (needs wiring)
- Phase-generated `.md` reports


## 🧪 Example Use Cases

| Scenario              | Promptset ID                              | Persona      |
| --------------------- | ----------------------------------------- | ------------ |
| Copilot enforcement   | `copilot_integrity_diagnostics.promptset` | `strategos`  |
| Prompt audits         | `test_kybernetes_001`                     | `kybernetes` |
| Configuration tracing | `config_snapshot_audit.promptset`         | `eunomia`    |


## 📎 Related Schemas

- `/config/hestia/library/prompts/_meta/draft_template.promptset`: Field type definitions + structural rules
- `/config/hestia/library/docs/governance/system_instruction.yaml`: Protocol registry and persona triggers
- `/config/hestia/library/docs/governance/persona_registry.yaml`: Role bindings and behavioral constraints


## 🛡 Governance Note

All promptsets are considered **governance artifacts** and should:

* Be version-controlled in Git
* Contain only deterministic logic
* Avoid dynamic content unless validated by checksum or content hash

Edits to `.promptset` files should trigger revalidation of associated reports.


End of `promptset_docs.md`