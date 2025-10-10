---
id: prompt_20251001_b5671e
slug: mnemosyne-phase-4-full-rebuild-safety-contract
title: "\U0001F510 Mnemosyne Phase 4 \u2013 Full Rebuild + Safety Contract"
date: '2025-10-01'
tier: "α"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: "batch 4/batch4-# \U0001F510 Mnemosyne Phase 4 \u2013 Full Rebuild +\
  \ .md"
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.786358'
redaction_log: []
---

# 🔐 Mnemosyne Phase 4 – Full Rebuild + Safety Contract

## 🧭 Project Scope

This is **Phase 4** of the Mnemosyne Orchestrator – a critical Home Assistant orchestration tool. You are responsible for delivering a single, production-ready `mnemosyne.sh` script that integrates all safety, fallback, and diagnostic mechanisms from previous phases and completes the Phase 4 execution integrity requirements.

---

## 🔢 Historical Integration Summary

**Included from Phase 1–3:**

* Full logging system with fallback functions
* JSON modes: `--status --json`, `--diagnose --json`
* Config fallback and environment variable cascade
* `create_fallback_metadata()` for failed phase recovery
* `execute_phase()` hardened with trap handling
* Legacy command mapping and CLI flags

---

## ❌ Current Phase 4 Failures

| Symptom             | Root Cause                                               |
| ------------------- | -------------------------------------------------------- |
| Segfault on dry-run | Variables used before initialization                     |
| Logging fails early | `logging.sh` sourced before paths validated              |
| Metadata missing    | `METADATA_FILE` computed before `PHASE_WORKSPACE` exists |
| Unsafe path usage   | Hardcoded `/tmp/` usage, no persistent fallback          |

---

## 🔁 Policy Change: No More `/tmp/`

Use:

* `${DEFAULT_LOG_DIR}/fallback/` → fallback metadata
* `${DEFAULT_LOG_DIR}/workspace/` → dry-run sandbox
* `${WORKSPACE_DIR}/phase.d/` → status tracking

---

## ✅ Claude Must Deliver

A **single, atomic `mnemosyne.sh` script** that:

### ✅ Embeds all Phase 3 Capabilities:

* `create_fallback_metadata()` function
* Trap-safe `execute_phase()`
* JSON output diagnostics
* Full CLI flag compatibility
* Legacy command mapping

### ✅ Enforces Phase 4 Guarantees:

* Early variable initialization
* Directory guards and path validation
* Fallback-safe logging if `logging.sh` is unavailable
* No `/tmp/` usage at any point

---

## 🧠 🧪 Phase 4 Sanity Contract (Self-Validation Logic)

Claude must implement and return a `check_sanity_contract()` function that validates these conditions at runtime:

```bash
check_sanity_contract() {
  local contract_failures=0

  [[ -n "$PHASE_WORKSPACE" && -d "$PHASE_WORKSPACE" ]] || { echo "[FAIL] PHASE_WORKSPACE invalid"; ((contract_failures++)); }
  [[ -n "$WORKSPACE_DIR" && -d "$WORKSPACE_DIR" ]]     || { echo "[FAIL] WORKSPACE_DIR invalid"; ((contract_failures++)); }
  [[ -n "$SNAPSHOT_ID" ]]                              || { echo "[FAIL] SNAPSHOT_ID not set"; ((contract_failures++)); }
  [[ "${PHASE4_SANITY_MODE:-false}" == "true" ]]       || { echo "[FAIL] PHASE4_SANITY_MODE not enabled"; ((contract_failures++)); }
  [[ -f "$PHASE_WORKSPACE/metadata.json" ]]            || { echo "[FAIL] metadata.json missing in workspace"; ((contract_failures++)); }

  if (( contract_failures > 0 )); then
    echo "[ERROR] Phase 4 contract integrity check failed: $contract_failures issues detected"
    return 1
  else
    echo "[OK] Phase 4 contract integrity verified"
    return 0
  fi
}
```

This function must be executed at the end of every dry-run or snapshot invocation.

---

## 🚦 Output Contract

Claude must return:

* Fully integrated, self-validating `mnemosyne.sh`
* `check_sanity_contract()` included and used
* Fallback-safe and POSIX-compatible logic throughout
* Dry-run exits cleanly, logs success, and writes metadata

---
