---
title: ADR-0007: Meta/Governance Patterns and Schema Definitions Contract
date: 2025-09-11
status: Pending Validation
---

# ADR-0007: Meta/Governance Patterns and Schema Definitions Contract

## Table of Contents
1. Context
2. Decision
3. Enforcement
4. Tokens
5. Last updated

## 1. Context
This ADR formalizes the canonical meta and governance patterns, including schema definitions, design patterns, and prompt registries. These artifacts define architectural standards, validation schemas, and governance logic for the Home Assistant configuration.

## 2. Decision
### Included Artifacts
- `architecture_doctrine.yaml`
- `design_patterns.md`
- `prompt_registry.md`
- `metadata_schema.yaml`
- `hades_config_index.yaml`
- All related markdown and YAML files in governance and meta folders

### Scope
- Architectural doctrine: standards and principles for configuration and automation
- Design patterns: reusable logic and best practices
- Schema definitions: validation and normalization of configuration artifacts
- Prompt registry: meta-instructions and governance logic

### Example Tokens
- `doctrine`, `pattern`, `schema`, `prompt`, `validation_rule`, `meta_instruction`, `index`, `governance_tag`

## 3. Enforcement
- All referenced artifacts must be validated for coverage and consistency with live configuration and governance logic.
- Changes to doctrine, patterns, or schemas require a new contract version.
- This ADR is pending validation and subject to revision after full review.

## 4. Tokens
- `doctrine`, `pattern`, `schema`, `prompt`, `validation_rule`, `meta_instruction`, `index`, `governance_tag`

---
_Last updated: 2025-09-11_
