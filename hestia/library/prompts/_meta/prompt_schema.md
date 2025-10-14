---
title: "HESTIA Promptset Schema and Usage"
authors: "Kybernetes"
source: "HESTIA / Promptset Runtime"
slug: "promptset-schema"
tags: ["hestia", "promptset", "governance", "gpt", "multi-phase", "validation"]
date: 2025-10-14
last_updated: 2025-10-14
---

# HESTIA Promptset Documentation

## 📘 Overview

The HESTIA `.promptset` schema defines **multi-phase, protocol-bound GPT prompt workflows** for governance, diagnostics, validation, and controlled generation. It supports both **legacy single-phase** prompts and **modular, future-facing** configurations.

All `.promptset` files should conform to the canonical schema and be located under: `/config/hestia/library/prompts/`

## 🧱 Promptset Structure

A valid `.promptset` contains the following root-level blocks:

| Field                  | Type   | Required | Description                                        |
|------------------------|--------|----------|----------------------------------------------------|
| `promptset`            | object | ✅        | Root container for all fields                      |
| `id`                   | string | ✅        | Unique identifier (snake_case recommended)         |
| `version`              | string | ✅        | Semantic version                                   |
| `created`              | date   | ✅        | Creation date                                      |
| `description`          | string | ✅        | Human-readable summary                             |
| `persona`              | string | ✅        | Persona expected to execute the promptset          |
| `purpose`              | string | ✅        | Operational goal or scenario coverage              |
| `legacy_compatibility` | bool   | ✅        | If true, supports older prompt systems             |
| `schema_version`       | string | ✅        | Must match current validator schema (`1.0`)        |

## 📂 Artifact Binding

```yaml
artifacts:
  required:
    - path: /config/hestia/library/docs/governance/system_instruction.yaml
    - path: /config/hestia/library/docs/governance/architecture_doctrine.yaml
  optional:
    - path: /config/.workspace/governance_index.md
    - path: /config/hestia/library/docs/governance/hades_config_index.yaml
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
  - Reference: /config/hestia/library/docs/promptset_schema.yaml
  - This file: /config/hestia/library/docs/promptset_docs.md
```

## ✅ Deployment & Validation

Place `.promptset` files into:

`/config/hestia/library/prompts/migration/incoming/`

They will activate if:

* All `required` artifacts resolve
* Persona is recognized in `persona_registry.yaml`
* Structure is valid per schema

Output artifacts and logs are placed at:

* `prompt_validation_log.json` in `/config/hestia/library/prompts/migration/`
* Markdown `.md` files in `/config/hestia/library/prompts/reports/`

## 🧪 Example Use Cases

| Scenario              | Promptset ID                              | Persona      |
| --------------------- | ----------------------------------------- | ------------ |
| Copilot enforcement   | `copilot_integrity_diagnostics.promptset` | `strategos`  |
| Prompt audits         | `test_kybernetes_001`                     | `kybernetes` |
| Configuration tracing | `config_snapshot_audit.promptset`         | `eunomia`    |

## 📎 Related Schemas & References

* `/config/hestia/library/prompts/_meta/draft_template.promptset`
* `/config/hestia/library/docs/governance/system_instruction.yaml`
* `/config/hestia/library/docs/governance/persona_registry.yaml`

## 🛡 Governance Note

All `.promptset` files are classified as governance-bound configuration. Ensure:

* Changes are committed via Git and version-controlled
* All logic is deterministic and auditable
* Output artifacts pass checksum and integrity validation
* Changes trigger revalidation via `prompt_validation_log.json`

---

End of `promptset_docs.md`
