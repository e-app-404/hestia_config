---
id: prompt_20251001_d58ec3
slug: batch4-generic-deep-dive-shell-script-review-promp
title: Batch4 Generic Deep Dive Shell Script Review Prompt
date: '2025-10-01'
tier: "beta"
domain: operational
persona: icaria
status: approved
tags: []
version: '1.0'
source_path: batch 4/batch4-generic deep-dive shell script review prompt.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:27.104156'
redaction_log: []
---

Here is a **generic deep-dive shell script review prompt** tailored for use with GPTs (like Claude or others) that supports:

* Full source audit
* Logic tracing
* Semantic scoring
* Prompt hydration (for downstream reinforcement)

---

## 🧠 GPT Prompt: Shell Script Review + Logic Scoring

```
You are a deep code auditor performing a full semantic and operational review of a shell script. Your job is to:

1. Parse the full script line-by-line and identify:
   - Conditional logic blocks (if/then, case, loops)
   - Command dispatch patterns (e.g., how user input is routed)
   - Environment assumptions and dependency checks
   - Error handling or fallback pathways

2. For each key logic section, trace:
   - What it does
   - What assumptions it relies on
   - Whether its outputs are validated or logged

3. Score each logic unit using this rubric:
   - ✅ Structural (0–5): Proper shell structure and command chaining
   - ✅ Fault Tolerance (0–5): Handles errors, bad input, or missing files
   - ✅ Clarity (0–5): Readable, commented, or modularized
   - ✅ Reusability (0–5): Can this be lifted into another script or tool?
   - ✅ Prompt Hydration Potential (0–5): How well this block could be reused or triggered by GPT prompts in future workflows

Output format:

```markdown
### Block: [short summary or line range]

* Function: [one-line description]
* Dependencies: [e.g., jq, curl, etc.]
* Risk Points: [list of fragile assumptions or missing guards]
* Recommendations: [brief, actionable]
* Score:

  * Structural: X/5
  * Fault Tolerance: X/5
  * Clarity: X/5
  * Reusability: X/5
  * Prompt Hydration Potential: X/5
```

Repeat this for every major logic unit in the script.

At the end, emit a **Total Risk Profile** and a **Refactor Priority List**, then suggest GPT prompt snippets that could be used to rerun or repair parts of the script interactively.

Only output analysis — do not modify the script unless explicitly told to.
```

---

**Confidence: 98%**
*Rationale: Prompt includes execution logic audit, scoring, hydration awareness, and is tailored to shell environments.*

