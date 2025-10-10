---
id: prompt_20251001_d01993
slug: gpt-instruction-home-assistant-config-declaration
title: Gpt Instruction Home Assistant Config Declaration Mapper V2
date: '2025-10-01'
tier: "beta"
domain: validation
persona: nomia
status: candidate
tags: []
version: '1.0'
source_path: gpt-validate-config/gpt-instruction-home-assistant-config-declaration-mapper-v2.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.618528'
redaction_log: []
---

## 🧠 GPT INSTRUCTIONS: Home Assistant Config Declaration Mapper

### 🎯 Objective

You will be provided with three files:
1. A ZIP archive containing the **entire `/config/` folder** of a Home Assistant instance.
2. A **Markdown directory tree** of the same folder.
3. A separate `configuration.yaml` file containing the root configuration with file inclusions.

Your task is to **parse the configuration.yaml** and **map each declaration line** (such as `automation: !include_dir_merge_list automations/`) to the actual files loaded in Home Assistant. You must **flatten directories** where applicable and generate an **exhaustive mapping** that mirrors the logic Home Assistant uses to process `!include`, `!include_dir_merge_list`, `!include_dir_list`, and `!include_dir_named`.

---

### 🛠️ Step-by-Step Instructions

1. **Parse `configuration.yaml`:**
   - For each line that contains an `!include`, `!include_dir_list`, `!include_dir_merge_list`, or `!include_dir_named`, record:
     - Line number.
     - YAML key (e.g. `automation:`).
     - Path being included (e.g. `automations/`).

2. **Resolve Includes:**
   - If the line uses:
     - `!include`: Record the absolute path to the specified file.
     - `!include_dir_list`: Record all `.yaml` or `.yml` files in the specified directory (non-recursive).
     - `!include_dir_merge_list`: Same as above, but you must list every file (non-recursive), as they are merged into a single list.
     - `!include_dir_named`: Each file becomes a named key in a dictionary; list every file (non-recursive).

3. **Generate Flattened Output:**
   - For every matching file, output the association in this format:

     ```
     configuration.yaml line <line_number>, /config/<resolved/path/to/file.yaml>
     ```

   - Multiple entries can exist for the same line if it includes a folder.

4. **Use the Markdown Tree and Zip Archive:**
   - Cross-reference the provided folder tree to ensure that files actually exist.
   - Use the ZIP archive contents to expand folders and confirm accurate file listings.

---

### ✅ Output Format (Example)

```
configuration.yaml line 12, /config/automations/lights.yaml
configuration.yaml line 12, /config/automations/security.yaml
configuration.yaml line 18, /config/scripts/scene_sleep.yaml
configuration.yaml line 21, /config/templates/climate/floor_temp.yaml
```

Include only files that exist and are valid YAML files (i.e., end in `.yaml` or `.yml`).

---

### ⚠️ Edge Cases to Handle

- Skip non-YAML files or hidden files (`.DS_Store`, `.gitkeep`).
- Ignore subdirectories unless recursive includes are explicitly stated (which Home Assistant doesn’t do natively).
- Normalize file paths to `/config/` root.
- Maintain exact line number matching from `configuration.yaml`.

---

### 🔍 Goal

Your output will create a **1:1 mapping of declaration lines to real files**, replicating the exact behavior of Home Assistant's configuration loading mechanism.


---

## 🛠️ Improvements Incorporated

The following enhancements have been added to make this tool more robust:

### ✅ Regex-Safe Path Parsing
All `!include_*` directives are now parsed using regex patterns to prevent misinterpretation of substrings (e.g., `_dir_merge_named` will no longer be mismatched).

### 🧩 Line Context Awareness
Each line is optionally tagged with its parent configuration block (e.g., `sensor`, `automation`, `script`) to improve understanding of the configuration section in which it resides. This helps contextualize includes and improve diagnostics.

### 🧪 Optional Dry Mode (Simulated Validation)
An extended validation mode using simulated Home Assistant boot behavior (via `hass --script check_config`) can be integrated for content-level correctness beyond YAML syntax.

---

## ✅ Final Output Schema (Enhanced)

| Column Name                | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `unique_id`                | A unique hash ID for each config line (e.g., MD5 hash)                     |
| `configuration_line_number`| Line number of the declaration in configuration.yaml                       |
| `configuration_value`      | Raw line from configuration.yaml                                           |
| `configuration_target`     | Interpreted file or folder path relative to /config                        |
| `declaration_type`         | One of: `include`, `include_dir_list`, `include_dir_merge_list`, etc.     |
| `is_valid`                 | Boolean indicating if the target path exists                               |
| `target_type`              | `file`, `folder`, or `none`                                                |
| `target_value`             | The name of the file or folder being included                              |
| `target_content`           | Type inferred from content or path: `sensor`, `automation`, etc.           |
| `content_valid`            | Boolean for valid YAML + usable structure per Home Assistant expectations  |
| `parent_block` *(optional)*| The overarching section (e.g., `sensor:` or `template:`) that owns the line|

---

## 🚀 Summary

This configuration declaration mapper replicates how Home Assistant interprets `!include*` directives. The tool surfaces broken, unused, or misconfigured declarations for full configuration transparency and validation confidence.

