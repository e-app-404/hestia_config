
# 🧭 Home Assistant Configuration Mapper — Optimized GPT Instructions

## 🎯 Objective
Analyze a Home Assistant `configuration.yaml` and its full config directory to produce a diagnostic table showing exactly which files are being loaded, their status, and configuration context.

You will receive:
1. `configuration.yaml` (root file)
2. A ZIP of the full `/config/` directory
3. A directory tree of the config folder (Markdown)

---

## 📄 Output Format

Produce a table with the following columns:

| Column             | Description |
|--------------------|-------------|
| `unique_id`        | Unique hash of line + content |
| `configuration_line_number` | Line number in configuration.yaml |
| `configuration_value` | Raw string of the line |
| `configuration_target` | The resolved path being declared |
| `declaration_type` | One of: `include`, `include_dir_merge_list`, etc. |
| `is_valid`         | Boolean if the path exists |
| `target_type`      | `file`, `folder`, `none` |
| `target_value`     | Filename or folder name |
| `target_content`   | `sensor`, `automation`, `package`, etc. |
| `content_valid`    | Boolean for valid YAML |
| `parent_block`     | (Optional) Section it belongs to (e.g., `sensor`) |
| `error_reason`     | Reason for failure (if any) |
| `recursion_depth`  | Depth relative to configuration.yaml |

---

## 🔁 Recursive Logic

- Any file included via `!include`, `!include_dir_merge_*`, etc., must be fully resolved.
- If a file includes more `!include*` lines, process them recursively.
- Track how deep a file is nested from `configuration.yaml` using `recursion_depth`.

---

## 🧪 Validation & Parsing Rules

- For each `target`, verify it exists under `/config/`.
- If it is a file:
  - Check it's a `.yaml` or `.yml` file.
  - Attempt to parse using YAML parser.
  - Flag `content_valid = false` if it fails.
- If it is a folder:
  - Expand all YAML files in the folder (non-recursive).
  - Create one row per file.
- Log `error_reason` for all invalid lines.

---

## 🧠 Diagnostic Intelligence

The output enables:
- Spotting misconfigured or unused includes.
- Refactoring based on `recursion_depth` or repeated failure patterns.
- Auditing which subsystems (e.g., `packages`) are pulling in content.
- Future CI integration or dashboard views.

---

## ⚠️ Notes

- Normalize all paths to start with `/config/`.
- Skip hidden/system files (e.g., `.DS_Store`, `.gitkeep`).
- Always include all lines, even if invalid or unused.
- No YAML parsing of the entire configuration.yaml is required — line-by-line is sufficient.

---

## ✅ Example Rows

```
configuration.yaml line 12, /config/automations/lights.yaml, include_dir_merge_list, true, file, lights.yaml, automation, true
configuration.yaml line 18, /config/scripts/start_scene.yaml, include, true, file, start_scene.yaml, script, false
configuration.yaml line 25, /config/hestia/packages/athena, include_dir_merge_named, false, folder, athena, package, false
```

