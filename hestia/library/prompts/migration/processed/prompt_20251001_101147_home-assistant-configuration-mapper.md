---
id: prompt_20251001_101147
slug: home-assistant-configuration-mapper
title: "\U0001F9ED Home Assistant Configuration Mapper"
date: '2025-10-01'
tier: "\u03B2"
domain: validation
persona: generic
status: candidate
tags: []
version: '1.0'
source_path: gpt-validate-config/gpt-instruction-home-assistant-config-declaration-mapper-v5-claude.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.472796'
redaction_log: []
---

# 🧭 Home Assistant Configuration Mapper

## 🎯 Objective
Analyze a Home Assistant `configuration.yaml` and related files to produce a diagnostic table showing which files are loaded, their status, and configuration context.

Input:
1. `configuration.yaml` (root file)
2. Config directory files (optional)
3. Directory tree (optional)

## 📄 Output Format

| Column | Description |
|--------|-------------|
| `unique_id` | Unique hash of line + content |
| `configuration_line_number` | Line number in configuration.yaml |
| `configuration_value` | Raw string of the line |
| `configuration_target` | Resolved path being declared |
| `declaration_type` | One of: `include`, `include_dir_merge_list`, etc. |
| `is_valid` | Boolean if path exists |
| `target_type` | `file`, `folder`, `none` |
| `target_value` | Filename or folder name |
| `target_content` | `sensor`, `automation`, `package`, etc. |
| `content_valid` | Boolean for valid YAML |
| `parent_block` | Section it belongs to (e.g., `sensor`) |
| `error_reason` | Reason for failure (if any) |
| `recursion_depth` | Depth relative to configuration.yaml |

## 🔁 Processing Logic

- Process all `!include`, `!include_dir_merge_*` declarations recursively
- Track nesting depth with `recursion_depth`
- For each target:
  - Verify it exists under `/config/`
  - For files: Check YAML validity
  - For folders: Expand all YAML files (non-recursive)
- Log detailed error reasons for invalid content

## 🧠 Error Classification

Standardized error codes:
- `not_found` - Path doesn't exist
- `invalid_yaml` - File can't be parsed
- `not_yaml_file` - Not a YAML file
- `empty_directory` - Directory contains no YAML
- `type_mismatch` - Declaration type doesn't match target

## 📊 Summary Metrics

Include in response:
- Total declarations processed
- Percentage of valid vs. invalid includes
- Count of broken YAMLs
- Most frequent error reasons
- Top folders by include count

## 🧩 Advanced Diagnostics

- **Orphaned declarations**: Includes that point to missing targets
- **Redundant files**: YAML files never referenced
- **Suggested organization**: Based on file naming/structure
- **System insights**: Configuration patterns, optimization opportunities

## 🧱 Additional Columns (if space allows)

| Column | Description |
|--------|-------------|
| `suggested_key` | Best-guess YAML key for ambiguous files |
| `likely_subsystem` | Module or domain the file relates to |
| `orphaned` | Boolean for includes with no matching file |
| `redundant` | Boolean for files not included anywhere |

## ⚠️ Notes

- Normalize all paths to start with `/config/`
- Skip hidden files (e.g., `.DS_Store`)
- Analyze line-by-line rather than full YAML parsing
- Always report all lines regardless of validity

## 📦 Fallback Behavior

If configuration files are incomplete:
1. Notify the user
2. Offer to proceed with limited information
3. Clearly label output as "Knowledge-Based Mapping (Fallback Mode)"

## ✅ Example Output Row

```
unique_id: "abc123", configuration_line_number: 12, configuration_value: "script: !include scripts/lights.yaml", configuration_target: "/config/scripts/lights.yaml", declaration_type: "include", is_valid: true, target_type: "file", target_value: "lights.yaml", target_content: "script", content_valid: true, parent_block: "script", error_reason: null, recursion_depth: 1
```

This process creates a complete configuration intelligence system ideal for complex Home Assistant setups.
