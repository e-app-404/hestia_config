---
id: prompt_20250527_014
slug: detect-whether-each-phase-declares-the-phases-it-d
title: '*: Detect whether each phase declares the phases it depends on.'
date: '2025-10-01'
tier: "\u03B1"
domain: validation
persona: promachos
status: candidate
tags: []
version: '1.0'
source_path: batch 3/batch3-prompt_20250527_014.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.114471'
redaction_log: []
---

### 📦 `prompt_20250527_014`

**Tier**: β
**Domain**: phase\_dependency\_hardening
**Type**: structured
**Status**: candidate
**Title**: Tiered Dependency Construction and Enforcement Audit
**Prompt**:

> 🧩 Mnemosyne Phase Dependency Validation and Hardening (Multi-Step Prompt)

You are to analyze the entire Mnemosyne codebase as provided in `mnemosyne_v2.0.1.tar.gz`, and execute the following **five tasks in order**, each building on the previous:

---

#### 🧱 TIER 1 – Phase Dependency Declaration

* **Goal**: Detect whether each phase declares the phases it depends on.
* **Action**: Add or propose `REQUIRES_PHASES=(...)` declarations where implicit dependencies are detected (e.g., `manifest` → `tree`).
* **Output**: Table of `phase → requires[]` with enforcement status.

---

#### 🧪 TIER 2 – Runtime Guard Injection

* **Goal**: Ensure dependent phases validate required outputs at runtime.
* **Action**: Check for file existence guards (e.g., `tree.json` for `manifest`) and emit a remediation patch if missing.
* **Output**: Guard coverage matrix + recommended guard snippet per phase.

---

#### 🔄 TIER 3 – Dynamic Phase Chain Construction

* **Goal**: Make Mnemosyne compute execution chains based on declared dependencies.
* **Action**: Introduce or update a `PHASE_DEPENDENCIES` map in `mnemosyne.sh` and implement a `resolve_phase_order()` function to compute topological order.
* **Output**: Generated chain per snapshot invocation + updated `DEFAULT_CHAIN`.

---

#### 📜 TIER 4 – Metadata Propagation of Dependencies

* **Goal**: Reflect dependencies inside each phase’s `metadata.json`.
* **Action**: Add keys like:

  ```json
  {
    "depends_on": ["tree"],
    "dependencies_satisfied": true
  }
  ```

  Validate presence or emit patch code.
* **Output**: JSON schema diff + sample output.

---

#### 🛑 TIER 5 – FORCE Override Compliance

* **Goal**: Validate that `FORCE=true` disables dependency enforcement safely.
* **Action**: Check for logging, user warnings (`log_warn`), and guard bypass logic.
* **Output**: `FORCE` coverage table + diagnostic recommendations.

---

### 🧾 Final Output:

* ✅ Summary table for each tier
* 📂 Per-phase compliance table
* 🧩 Suggested code patches or injection blocks
* 🧠 Follow-up prompts (if deeper refactoring is needed)

---

Would you like me to begin execution of this multi-tiered prompt now?

