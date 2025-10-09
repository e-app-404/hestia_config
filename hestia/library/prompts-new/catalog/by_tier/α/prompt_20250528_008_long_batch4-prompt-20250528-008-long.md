---
id: prompt_20250528_008_long
slug: batch4-prompt-20250528-008-long
title: "Batch4 ## \U0001F4E6 `Prompt 20250528 008 Long`"
date: '2025-10-01'
tier: "\u03B1"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: "batch 4/batch4-## \U0001F4E6 `prompt_20250528_008_long`.md"
author: Unknown
related: []
last_updated: '2025-10-09T02:33:27.272149'
redaction_log: []
---

## 📦 `prompt_20250528_008_long`

**Tier**: β
**Domain**: phase_dependency_hardening
**Type**: structured
**Status**: candidate
**Title**: Tiered Dependency Construction and Enforcement Audit
**Prompt**: >

You are continuing refinement on the **Mnemosyne Declarative Orchestrator v4** (Phase 5-compliant). Your task is to finalize the logging layer, apply a critical remediation to `logging.sh`, and align remaining code hygiene tasks with the project blueprint.

---

## 🔧 PART 1: CRITICAL HOTFIX (LOGGING.SH – UNBOUND VARIABLE, LINE 63)

Please integrate the following hardened fix into `lib/utils/logging.sh`, replacing any older logging array declarations or level-access logic:

### ✔️ Patch Specification

**Safe Declaration:**

```bash
declare -gA LOG_LEVELS=(
  [TRACE]=0
  [DEBUG]=1
  [INFO]=2
  [WARN]=3
  [ERROR]=4
  [FATAL]=5
)
```

**Safe Access Guard:**

```bash
get_log_level_number() {
  local level="${1:-}"
  if [[ -z "$level" ]]; then
    echo "2"
    return
  fi
  if [[ "${LOG_LEVELS[$level]+exists}" ]]; then
    echo "${LOG_LEVELS[$level]}"
  else
    echo "2"
  fi
}
```

**Runtime Flag:**

```bash
export LOGGING_INITIALIZED=true
log_debug "LOGGING_INITIALIZED set"
```

This hardens against `set -euo pipefail` failures and ensures strict-mode sourcing compatibility (confirmed on Home Assistant OS CLI).

---

## 📋 PART 2: REMAINING TASK COMPLETION

* Confirm `SCRIPT_DIR`, `PHASE_D_DIR`, and phase discovery diagnostics now resolve correctly.
* Ensure all `phase.d/phase_*.sh` scripts are picked up and executed when modular architecture is selected.
* Normalize logging punctuation and emoji usage across all messages (`log_*` functions).
* Integrate static sanity checks for `PHASE_SCRIPTS` consistency (existence + executable).
* Review `mnemosyne.sh` for residual assumptions around `.conf` vs `.yaml`, fallback-only logic, and hybrid phase loading logic.

---

## 🧭 PROJECT PLAN STATUS (🟢 = Delivered, 🟡 = Pending)

| Phase                          | Status | Notes                                                |
| ------------------------------ | ------ | ---------------------------------------------------- |
| Phase 0: Bootstrap Init        | 🟢     | Completed via `main()` baseline                      |
| Phase 1: Trap-Safe Core        | 🟢     | All exits managed with fallback metadata             |
| Phase 2: Dry-Run Simulation    | 🟢     | Simulation logged in metadata JSON                   |
| Phase 3: Metadata Scaffolding  | 🟢     | `logs/{workspace,fallback}/metadata_*.json` present  |
| Phase 4: Bulletproof CLI       | 🟢     | CLI diagnostics complete                             |
| Phase 5a: Static Sanity Checks | 🟡     | Add missing validation for `PHASE_SCRIPTS[*]`        |
| Phase 5b: Cosmetic Polish      | 🟡     | Unify logging punctuation, emoji, capitalization     |
| Phase 5c: Zsh/Bash Harmony     | 🟢     | PATH resolution and invocation robust across shells  |
| Phase 6: Fully Modular Mode    | 🟡     | `phase.d/` loading functional but needs confirmation |

---

## 📦 BLUEPRINT CONTRACT ARTIFACTS (v4.0)

* [`mnemosyne_blueprint_v4.0.yaml`](attached)
* [`prompt_contract_claude_mnemosyne_v4.0.md`](attached)
* Launch behavior previously submitted via: `claude_launch_prompt_mnemosyne_v4.md`

---

### 🧠 Constraints

* Do **not** alter fallback logic, trap behavior, or dry-run simulation engine.
* Apply **only** logging refactors and safe guards—no execution logic changes unless part of sanity checks or diagnostics.
* Return **only the updated segments** of affected files.

---

## 📨 Submission Format

* Updated segments only (not full scripts)
* Markdown code blocks
* Confirm success or highlight any ambiguity

---

## 📦 `prompt_20250528_short` 📝 Abbreviated Follow-Up Prompt (Fast Mode)

**Tier**: β
**Domain**: phase_dependency_hardening
**Type**: structured
**Status**: candidate
**Title**: Tiered Dependency Construction and Enforcement Audit
**Prompt**: >

```markdown
Please integrate the safe-guard fix for `logging.sh` (unbound variable on line 63 under `set -u`) using `declare -gA LOG_LEVELS` and a conditional key check.

Also:
- Normalize log message punctuation/emoji.
- Add static sanity check for `PHASE_SCRIPTS` existence/executable.
- Confirm modular loading (`phase.d/phase_*.sh`) works post `SCRIPT_DIR` fix.

Return only updated segments. v4 blueprint and previous launch prompt attached.
```
