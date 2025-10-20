---
id: prompt_20251001_fff9f1
slug: gammatiermacrolibraryyaml
title: gamma_tier_macro_library.yaml
date: '2025-10-01'
tier: "α"
domain: operational
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch 3/batch3-prompt_meta_yaml_structure.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.339527'
redaction_log: []
---

From the provided Home Assistant YAML archives and configuration.yaml, generate an inferred **meta-structure** per unique top-level entity type (`sensor`, `binary_sensor`, `automation`, `template`, etc.). Use `!include` statements and directory merge strategies (e.g. `!include_dir_merge_list`) from configuration.yaml to determine:

1. Where entities originate from
2. Whether each YAML block should be rendered as a list or dictionary
3. The expected syntax for valid entity definitions

For each entity type, produce a **Markdown block** with:

- The filename and directory path where the sample was found
- The merge strategy (list, named dict)
- A YAML snippet with **descriptive placeholder values**, replacing data with semantic explanations or expected types

Also emit a companion **playbook section**:

**Hard Rules** – Structural invariants, schema expectations, merge behavior, required keys  
**Soft Rules** – Best practices, naming conventions, typical subsystem roles, recommended tier logic

Use the following format:

---

### sensor  
**Source:** `hestia/sensors/other/`  
**Merge Strategy:** `!include_dir_merge_list`  

```yaml
# gamma_tier_macro_library.yaml
- sensor:
  - name: Example sensor name
    unique_id: Example unique_id value
    attributes:
      tier: Structural tier of the entity. E.g., "γ", "δ", "μ"
      subsystem: Subsystem the entity belongs to. Possible values: ["theia", "aether", ...]
      ...

