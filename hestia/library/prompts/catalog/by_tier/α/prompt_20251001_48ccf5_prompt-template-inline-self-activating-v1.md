---
id: prompt_20251001_48ccf5
slug: prompt-template-inline-self-activating-v1
title: Prompt Template Inline Self Activating V1
date: '2025-10-01'
tier: "\u03B1"
domain: validation
persona: promachos
status: approved
tags: []
version: '1.0'
source_path: batch5/prompt_template_inline_self_activating_v1.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.721127'
redaction_log: []
---

id: prompt_template_inline_self_activating_v1
tier: α
domain: prompt_engineering
type: template
status: canonical
applied_by: chief_ai_officer
derived_from: prompt_20250501_optimized_motion_presence_stack

description: >
  A reusable pattern enabling GPTs to emit an optimized prompt inline and immediately interpret it. This supports
  proactive configuration analysis, validation, or refactoring across any domain. The assistant infers user intent,
  emits a copyable markdown-formatted prompt, and continues as if the user had issued that prompt directly.

template_prompt: |
  Based on the artifact(s) I provide and your understanding of my intent, generate an optimized version of a prompt
  that activates you as a proactive assistant. This assistant should operate within your configured behavior and knowledge,
  optimize the system or configuration as appropriate, and follow any best practices. Include this optimized prompt
  as a markdown snippet at the start of your next response, and then act as if I had issued it directly.

inline_response_behavior: |
  ```prompt
  [Optimized user-facing directive tailored to the input domain and goal]
````

[Begin execution of the above directive, including review, analysis, or transformation.]

activation_tags: [inline_prompt, self_activating, auto_optimize, inferred_intent, reusable_pattern]

requires:

* `protocol_prompt_auto_optimization_v1` (to support auto-refinement and execution)
* persona capable of inline self-activation (e.g., Promachos, MetaStructor)
* signoff mode: inverted_questions or auto_affirm_with_prompt (for chainable execution)

outputs:

* optimized prompt snippet
* interpreted execution of that prompt
* structured review or output
* chainable follow-up path

