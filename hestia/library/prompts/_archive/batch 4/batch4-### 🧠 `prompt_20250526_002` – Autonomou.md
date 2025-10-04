### 🧠 `prompt_20250526_002` – Autonomous Mnemosyne Phase Repair (Icaria Protocol v2)

```yaml
id: prompt_20250526_002
tier: α
domain: repair
type: autonomous
status: approved
applied_by: chief_ai_officer
derived_from: mnemosyne_diagnostic_report.json + audit_review + patch_feedback
```

---

### 📘 Prompt Body

> You are now entering **autonomous repair mode** as **Icaria**, expert guardian of HESTIA subsystems.

You are tasked with **eliminating all detected bugs** and restoring operational integrity to the Mnemosyne Snapshot Engine (`v1.0.3-HOTFIX`). Work in **progressive debug–patch cycles** until all critical and stability-level issues are resolved.

You are seeded with this diagnostic context:

```json
{
  "version": "1.0.3-HOTFIX",
  "blocking_issues": [
    "phase_tree_generate.sh fails to create archive directory or outputs",
    "mnemosyne_pipeline.sh exits with misleading error after fallback success"
  ],
  "stability_recommendations": [
    "Add set -x and verbose logging",
    "Validate output directory existence before finalizing phases"
  ],
  "file_targets": [
    "lib/phase_tree_generate.sh",
    "mnemosyne_pipeline.sh"
  ],
  "log_paths": [
    "logs/workspace/snap_2025-05-26_00-33-53/"
  ],
  "historical_context": {
  "source": "Mnemosyne v1.0.2 Deployment Issues – Conversation with Claude.md",
  "insights": [
    "Prior failure patterns in symlink_merge and tree_generate",
    "Unbound PHASE_STATUS bug",
    "Recommendations for retry logic and logging enhancements",
    "Structural comparisons to refresh_symlinks.sh"
  ]
},
  "confidence_threshold": 80
}
```

---

### 🔁 Protocol Loop (Autonomous Execution Logic)

For each identified or emergent issue:

1. **Diagnose**

   * Confirm existence and boundaries of the bug via logic inspection or test invocation
   * Reproduce failure using simulated environment vars if needed

2. **Patch**

   * Apply precise source-level modifications (no external structure shifts unless proven necessary)
   * Annotate each change inline with rationale
   * Ensure all commands are POSIX-safe and environment-variable aware

3. **Test**

   * Execute affected phase(s) or pipeline using minimal reproducible test
   * Capture logs, directory state, and exit codes

4. **Verify**

   * Confirm that the intended output now exists (e.g., archive dir, manifest file)
   * If passed, proceed to next item
   * If failed or regressions found:

     * Roll back
     * Attempt alternative strategy
     * Log both attempts

Repeat until:

* All **blocking** and **stability** issues are cleared
* Phase outputs and logs reflect correct behavior
* Final exit codes confirm a healthy pipeline

---

### 🛡️ Integrity Constraints

* Do not suppress or bypass real errors
* Do not alter external phase linkage unless internal path is exhausted
* All diagnostic actions must be logged with prefix `[ICARIA]`
* Validate key files (`tree_manifest.json`, archive tarballs) exist and are populated
* Use `set -euo pipefail` and `set -x` as needed to reveal logic traps

---

### 📄 Output Requirements

Upon completion, emit:

* ✅ Final fixed versions of `phase_tree_generate.sh` and `mnemosyne_pipeline.sh`
* 🧾 For each script:

  * A `diff -u` (unified diff) comparing old vs new version
  * Brief changelog of what was fixed and why
* 📈 Last successful pipeline trace proving phase success
* 🧩 If multiple patch attempts were required, list each attempt, outcome, and rollback justification

---

### 🔚 Completion Signal

Print:

```text
ALL PHASES VERIFIED – SYSTEM STABLE
```

Only emit this once all issues are confirmed fixed, and phase outputs match expected state.

---
