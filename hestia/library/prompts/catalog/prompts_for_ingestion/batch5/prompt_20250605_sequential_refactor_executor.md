id: prompt_20250605_sequential_refactor_executor
tier: β
domain: refactor
type: structured_execution
status: approved
applied_by: chief_ai_officer
derived_from: prompt_20250501_optimized_motion_presence_stack
related_prompts:
  - id: prompt_20250501_optimized_motion_presence_stack
    relationship: optimization_origin
    note: >
      This prompt continues execution of the refactor plan initiated by the optimization directive emitted in prompt_20250501.
      It assumes advisory context is already known and focuses purely on implementation.

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
