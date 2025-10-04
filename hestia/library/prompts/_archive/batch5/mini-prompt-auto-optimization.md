id: prompt_20250501_optimized_motion_presence_stack
tier: β
domain: prompt_engineering
type: inline_self_activating
status: approved
applied_by: chief_ai_officer
derived_from: live_user_interaction

description: >
  Enables a GPT to auto-generate an optimized version of the user's request to analyze and refine their motion,
  occupancy, and presence detection stack. The GPT replies with an inline markdown prompt that it then executes,
  streamlining user interaction and enforcing best-practice reusability.

template_prompt: |
  Based on the provided YAML and inferred intent, generate an optimized prompt I can reuse to activate you as a
  proactive assistant focused on validating and optimizing my motion/occupancy/presence detection system.
  Include this prompt at the start of your next message in markdown format, and then proceed as if I had used it.

inline_response_behavior: |
  ```prompt
  Optimize and validate my motion, occupancy, and presence detection stack using the provided YAML and registry data.
  Ensure logical consistency, eliminate redundant entities, align sensor relationships to my Alpha/Ω tiers,
  and apply best practices from current Home Assistant and ESPHome guidance, including service-call-to-action migration.
  Focus on reliability, clarity, and extensibility.
  ```

[Analysis and evaluation continues here...]

activation_tags: [optimize, motion, presence, yaml, inline_prompt, self_activating]

requires:

* system_instruction.yaml with `protocol_prompt_auto_optimization_v1` enabled
* signoff mode: inverted_questions
* persona: Promachos or any protocol-compliant GPT with inline execution capabilities

outputs:

* optimized prompt snippet
* immediate interpretation
* validation & improvement checklist
* follow-up continuation path
