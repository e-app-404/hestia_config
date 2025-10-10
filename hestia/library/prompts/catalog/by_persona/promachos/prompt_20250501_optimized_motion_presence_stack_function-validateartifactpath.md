---
id: prompt_20250501_optimized_motion_presence_stack
slug: function-validateartifactpath
title: "\U0001F9E0 Function: validate_artifact_path"
date: '2025-06-06'
tier: "beta"
domain: governance
persona: promachos
status: approved
tags: []
version: '1.0'
source_path: batch5/prompt_20250501_optimized_motion_presence_stack.md
author: HESTIA Chief AI Officer
related: []
last_updated: '2025-10-09T02:33:26.748162'
redaction_log: []
---

id: prompt_20250605_sequential_refactor_executor
tier: β
domain: refactor
type: structured_execution
status: approved
applied_by: chief_ai_officer
derived_from: user_trace + refactor_advisory_plan

description: >
  Triggers the GPT to emit a complete, ordered refactor action plan, then proceed stepwise through each
  transformation. Ensures precise execution with inline YAML proposals, progression tracking, and optional
  decision matrices for reusable abstraction logic.

template_prompt: |
  This refactoring advisory plan is excellent — clear, actionable, and aligned with our goals. Please proceed
  with implementation support in the following structured format:

  1. Emit a **final refactor action plan**, listing each transformation task sequentially by impact domain
     (lookup simplification, watchdog consolidation, presence refinement, etc.), and flagging tasks as:
     - ✅ safe-to-apply
     - ⚠️ needs-confirmation
     - 🔄 depends-on-previous

  2. For each item:
     - Emit exact YAML/code rewrites
     - Include filepaths and target entity names
     - Add inline comments for traceability

  3. Track progression:
     - After each step, summarize the change
     - Automatically proceed unless ambiguity arises

  4. For abstraction-related logic (e.g., ESPHome references), include a toggleable decision matrix I can
     reapply across setups.

  Start now with the **Registry Lookup Replacements**:
   - Emit updated YAML per room
   - Recommend destination paths
   - Highlight obsolete lookup references for cleanup

  Then proceed to **Watchdog Boolean Refactor**. Follow through sequentially.

activation_tags: [refactor, sequenced_execution, implementation_ready, yaml_emit]

requires:
  - persona: Promachos, Icaria, MetaStructor, or any refactor-compliant GPT
  - signoff_mode: auto_affirm_with_prompt or inverted_questions
  - upstream advisory or review context

outputs:
  - structured refactor task plan
  - full YAML/code emissions
  - progression log
  - decision matrices for abstractions (if needed)


### ⚠️ Protocol Compliance Mandate – Executable Delivery Warning

**Context:** This document defines the formal warning issued when executable delivery protocols are violated within HESTIA pipeline environments, particularly in critical toolchains such as Mnemosyne, Daedalia, Iris, and Hephaestus.

---

### 🔒 Enforcement Trigger

This compliance mandate is triggered when the following are observed:

* Delivery of syntactically invalid or incomplete code blocks
* Placeholder constructs (`...`, `[snippet]`, `TODO`, etc.) included in runtime logic
* Functions emitted without input safety or return guarantees
* Troubleshooting commentary **instead of** directly executable code
* Phase scripts that cause uncontrolled execution behavior (e.g. fork bombs, infinite subshells)

---

### 🧾 Response Protocol (protocol\_executable\_delivery\_compliance\_v1)

All agents (human or GPT) must:

1. **Deliver full script content**, not deltas, unless explicitly operating under a patch protocol (e.g. `patch_synthesis_release_request_v1`).
2. **Embed complete function bodies**, scoped, validated, and declared explicitly.
3. Avoid placeholder or speculative syntax under all conditions.
4. Wrap all deliverables in triple-backtick code blocks and mark with appropriate language tags (`bash`, `yaml`, `json`, etc.).
5. Clearly declare intent, behavioral effect, and invocation scope.

---

### ✅ Minimum Structure Example

```bash
# 🧠 Function: validate_artifact_path
# Description: Ensures provided artifact path is safe, readable, and non-null
validate_artifact_path() {
  local path="$1"
  if [[ -z "$path" || ! -f "$path" ]]; then
    echo "[ERROR] Invalid or missing artifact path: $path" >&2
    return 1
  fi
  return 0
}
```

---

### 📌 Systems Under Governance

This protocol applies to any runtime or tooling contribution within:

* 🧠 **Mnemosyne** – phase orchestration and artifact processing
* 📂 **Daedalia** – source management, introspection, and path enumeration
* 📊 **Iris** – output rendering, diff synthesis, and visual pipeline intelligence
* 🔧 **Hephaestus** – structural validators, meta-lint, and link tracing

---

### 🛑 Noncompliance Consequences

Any violation of the above may result in:

* Rejection of GPT-inferred patches or scripts
* Downgrade to manual review mode
* Logging of the deviation to `PROMPT_DEVIATIONS.md`
* Reduction of `execution_trust_score` and suspension from automated flows

---

### 🧠 Confirming Remediation

A compliant response must:

* Acknowledge the protocol violation
* Deliver a full, patchable script replacement
* Contain no speculative or incomplete elements
* Use clear markers for function purpose and input safety

---

### 🔁 Recommended Permanent Enforcement

Embed this protocol in:

* All `validate_output_contract()` gates
* Phase loader preconditions (`bootstrap_phase.sh`)
* Iris output summarizers and visual diff scaffolds

---

Filed under: `protocol_executable_delivery_compliance_v1`
Scope: Mnemosyne, Daedalia, Iris, Hephaestus
Status: Active
Last Updated: 2025-06-06
Author: HESTIA Chief AI Officer

