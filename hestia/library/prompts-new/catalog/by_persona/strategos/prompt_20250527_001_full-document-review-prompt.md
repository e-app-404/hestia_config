---
id: prompt_20250527_001
slug: full-document-review-prompt
title: '**Full Document Review Prompt**'
date: '2025-10-01'
tier: "\u03B3"
domain: diagnostic
persona: strategos
status: candidate
tags: []
version: '1.0'
source_path: "batch 4/batch4-### \U0001F9E0 `prompt_20250527_001` \u2013 content review\
  \ and optimization.md"
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.816827'
redaction_log: []
---

**id: prompt_20250527_001**
**prompt: generic_content_review_optimization**

```markdown
#  **Full Document Review Prompt**

You are performing a structural and semantic audit of the following document block.

## Task:
- Infer the author’s intent and core purpose.
- Analyze structural clarity, naming consistency, and modular composition.
- Identify opportunities to improve alignment with tiered behavior, persona clarity, or output contracts.
- Where appropriate, generate valid, self-contained YAML or markdown fragments that:
  - Strengthen behavior
  - Resolve ambiguity
  - Expand capabilities

Do not alter the original unless instructed—emit a short review declaration and a proposed patch strategy only.

## Output:
- A brief diagnostic of current clarity and gaps
- A proposed modular improvement plan
- Wait for user validation before generating or applying any patch

---

## Concrete context-specific example:

> Begin full document review of `system_instruction.yaml` (semantic_version: "v1.3.0") provided below. Focus on improving structural clarity, isolating responsibilities, and surfacing assumptions.
```
