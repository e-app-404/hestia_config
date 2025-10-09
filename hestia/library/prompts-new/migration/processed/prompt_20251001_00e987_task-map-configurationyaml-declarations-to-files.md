---
id: prompt_20251001_00e987
slug: task-map-configurationyaml-declarations-to-files
title: "\U0001F50D Task: Map `configuration.yaml` Declarations to Files"
date: '2025-10-01'
tier: "\u03B3"
domain: extraction
persona: nomia
status: candidate
tags: []
version: '1.0'
source_path: tasks/gpt-task-map-configuration-declarations-to-files.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:24.927011'
redaction_log: []
---

# 🔍 Task: Map `configuration.yaml` Declarations to Files

You are analyzing a Home Assistant `configuration.yaml` file alongside a full directory structure.

## 🎯 Your Goal

Produce a table mapping **every line** of `configuration.yaml` to its corresponding file(s), directory, or declaration — even if the target is invalid. This allows complete visibility of what the Home Assistant instance is trying to load.

## 📄 Output Format

Your output must be a table with the following columns:

| Column Name | Description |
|-------------|-------------|
| `unique_id` | A unique row hash (e.g., MD5 of line number + value) |
| `configuration_line_number` | Line number in the configuration.yaml |
| `configuration_value` | The raw line string |
| `configuration_target` | The full file or folder being targeted (as seen by Home Assistant) |
| `declaration_type` | One of: `include`, `include_dir_list`, `include_dir_merge_list`, `include_dir_named`, `include_dir_merge_named`, `none` |
| `is_valid` | `true/false` — whether the target exists in the config |
| `target_type` | `file`, `folder`, `none` |
| `target_value` | Filename or folder name (basename of the path) |
| `target_content` | Detected config role: `sensor`, `template`, `package`, `script`, etc. |
| `content_valid` | `true/false` — whether the file(s) are valid YAML and suitable for inclusion |

## ⚠️ Rules & Notes

- For directory includes, list each YAML file separately.
- Use heuristic detection for `target_content` based on filename or path.
- Parse includes even when invalid, and reflect this in `is_valid = false`.
- Use `/config/` as the base path to match Home Assistant logic.

