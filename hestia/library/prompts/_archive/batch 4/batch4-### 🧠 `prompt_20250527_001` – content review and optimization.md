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