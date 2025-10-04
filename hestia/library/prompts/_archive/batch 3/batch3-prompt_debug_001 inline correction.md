## [id: prompt_debug_001] Inline Correction Prompt

You are acting as an expert code repair agent.

### Task

- Detect and diagnose structural or logical issues in the following source snippet.
- Identify scope: Is the issue local (e.g., a typo), functional (e.g., misbehavior), or systemic (e.g., incorrect pattern)?
- Apply intelligent and elegant corrections within the *nearest complete structural unit* (e.g., full function, method, or block).
- Output the corrected version **in full**, retaining alignment with naming conventions, spacing, and logical flow.
- Do **not** output only a patch or diff — embed corrections inline within context-preserving frames.

### Output Format

```yaml
# Modified from original — [short reason here, e.g., fixed off-by-one error]
def function_name(...):
    ...
    # Corrected logic
    ...
```

### Review Criteria

- Code must compile or lint cleanly (assume Python 3 unless otherwise stated).
- Avoid temporary hacks; prefer idiomatic and future-proof solutions.
- If uncertain about intent, annotate your correction briefly in a comment.

### Code to Debug

[Insert user’s broken or questionable code here]

---

## [id: prompt_debug_002] HAOS Shell Hardening + Inline Refactor

You are performing a precision debugging and hardening pass on a production-critical HAOS orchestration script. This script already includes dry-run simulation logic, structured logging, fallback metadata, and phase sequencing.

### Objective

- Detect and resolve segmentation faults or premature exits due to misordered declarations, unsafe sourcing, or unguarded environment reads.
- Inject environment-safe guards *before* dry-run evaluation to ensure dry-run logic can be reached.
- Harden fallback logic so that local variable declarations only occur inside functions.
- Safely refactor top-level constants and logging infrastructure so execution does not break in Alpine/busybox HA containers.

### Instructions

- Analyze the provided script context holistically — not just the failing line.
- If a sourced file or variable causes failure before `if [[ "${DRY_RUN_MODE:-false}" == "true" ]]` is hit, wrap it with checks.
- Use POSIX-compliant fallback logic for `date`, `uname`, and `whoami` reads.
- Return the corrected version inline — do **not** strip it to only changed lines.
- Ensure `log_info`, `log_error`, etc., always resolve safely.
- Confirm dry-run logic exits cleanly with metadata preserved.

### Output Format

```bash
# 💡 Phase Tar Pack Script — Hardened Inline Fix
#!/bin/bash
# Full script with early-failure prevention and safe sourcing
...
```

### Application Context

Use this prompt in Phase 4 debug pipelines, especially during triage of segmentation faults in snapshot orchestration environments using HAOS containers.
