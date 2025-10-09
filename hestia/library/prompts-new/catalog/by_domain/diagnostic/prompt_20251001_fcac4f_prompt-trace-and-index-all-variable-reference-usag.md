---
id: prompt_20251001_fcac4f
slug: prompt-trace-and-index-all-variable-reference-usag
title: "\U0001F9E0 Prompt: Trace and Index All Variable & Reference Usage per Mnemosyne\
  \ Phase"
date: '2025-10-01'
tier: "\u03B1"
domain: diagnostic
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch 4/batch4-prompt_mnemosyne_variable_index_20250528.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:27.323707'
redaction_log: []
---

`id: prompt_mnemosyne_variable_index_20250528`

# 🧠 Prompt: Trace and Index All Variable & Reference Usage per Mnemosyne Phase

## 🧭 Context

```markdown
You’ve completed a diagnostic audit of HESTIA’s `mnemosyne` shell orchestration system. Your next goal is **deep introspection**: creating a complete index of **all variables**, **env flags**, and **script-local definitions** used in each declared phase (e.g., `snapshot`, `mirror`, `diagnose`, `tree`, etc.).

The following directory structure is available:

```plaintext
/config/hestia/tools/mnemosyne/
├── mnemosyne.sh
├── lib/
│   ├── phase\_\*.sh
│   ├── utils/
│   └── \*.sh
├── mnemosyne\_diagnostics/
│   └── \*.sh

```

Each phase follows modular conventions (`phase_<name>.sh`), sometimes loaded dynamically. Diagnostic, utility, and logging components supplement this behavior.

## 🎯 Objective

Index all declared **bash variables**, **exported env vars**, **temporary scoped vars**, and **constants** per phase and module, including:

- `readonly`, `declare`, `local`, `export`
- All referenced inputs, flags (`DRY_RUN`, `PHASE`, `JSON_OUTPUT`, etc.)
- Parameter dependencies (e.g. `SNAPSHOT_ID`, `FORCE`)
- Output artifacts (e.g., logs, JSON stubs, phase outputs)

## 📋 Output Specification

For each phase and helper file:

```bash
## 🔹 Phase: snapshot (lib/phase\_tar\_pack.sh)

### Input Variables

* `SNAPSHOT_ID` (global, may be overridden)
* `CONFIG_FILE` (optional, for tar exclusions)
* `FORCE` (bool, bypass checks)

### Local/Declared

* `archive_file`
* `tar_args`
* `temp_manifest`

### Exported Outputs

* None

---

## 🔹 File: lib/utils/git\_utils.sh

### Input Variables

* `REPO_THIN_PATH`
* `DRY_RUN`

### Local/Declared

* `git_mirror_command`
* `branch`

### Exported Outputs

* `GIT_REFRESHED=true`
```

## 📌 Crosscut Tags to Track

- Phase ID variables (`PHASE`, `PHASE_WORKSPACE`)
- Boolean toggles (`FORCE`, `DRY_RUN`, `DEBUG`, `JSON_OUTPUT`)
- Snapshot metadata (`SNAPSHOT_ID`, `manifest_file`, `fallback_file`)
- Logging control (`LOG_DIR`, `FALLBACK_DIR`)
- Output modifiers (`MODULAR_PHASES_FOUND`, etc.)

## ✅ Result

Produce a tabular summary or nested dictionary of variable flow per script. This will aid debugging, consistency tracking, and modular refactor planning
```
