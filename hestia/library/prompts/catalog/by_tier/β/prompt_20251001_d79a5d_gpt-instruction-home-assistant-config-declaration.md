---
id: prompt_20251001_d79a5d
slug: gpt-instruction-home-assistant-config-declaration
title: Gpt Instruction Home Assistant Config Declaration Mapper
date: '2025-10-01'
tier: "beta"
domain: extraction
persona: generic
status: candidate
tags: []
version: '1.0'
source_path: gpt-validate-config/gpt-instruction-home-assistant-config-declaration-mapper.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.595749'
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

