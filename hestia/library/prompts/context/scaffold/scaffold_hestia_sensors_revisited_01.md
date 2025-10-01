project_id: hestia_sensors_revisited_01
parent_stack: HESTIA
initiative_type: maintenance
domain: sensor_catalog_governance

project_id: hestia_sensor_refactor_execution_2025q2
parent_stack: HESTIA
initiative_type: structured_maintenance_execution
domain: sensor_logic_rewrite

semantic_focus:
  - motion/occupancy/presence pipeline refactor
  - entity reference unification
  - abstraction-to-direct signal migration
  - macro and registry simplification
  - eta-tier inference logic upgrade
  - watchdog to decay-template conversion

primary_objective: >
  Execute a staged, dependency-aware refactor of the HESTIA sensor stack, implementing a previously audited
  and confirmed optimization plan. This includes rewriting motion and presence pipelines, removing unneeded
  abstractions, modernizing timeout behavior, and reinforcing tier clarity. Claude is expected to think proactively,
  sequence transformations logically, and reason through ambiguities with minimal prompts.

context_background:
  - Phase 1 and advisory design completed (by Promachos)
  - Claude is handed a greenlit refactor plan
  - Refactor spans registry cleanup, watchdog logic, tier annotation, and template refinements

execution_phases:

  - phase: 1_refactor_plan_confirmation
    description: >
      Interpret and optionally restructure the refactor plan to optimize task ordering, detect latent conflicts,
      or merge closely related tasks. Emit a canonical execution queue.
    output_expectations:
      - Refactor plan table with: task_id, action_group, impact_area, status, depends_on, escalation_needed

  - phase: 2_structured_yaml_emission
    description: >
      For each task, emit precise YAML or Jinja templates reflecting the transformed logic. Annotate every change
      with tier, origin, rationale, and migration notes. Use attribute_templates to clarify semantic shifts.
    constraints:
      - Use file-scoped comments to indicate change zones
      - Do not assume auto-imports; emit self-contained sensor blocks
      - Use `origin:` and `note:` fields to track transformation

  - phase: 3_progression_and_summary_logging
    description: >
      After each completed rewrite, emit a short summary and queue the next task automatically. Request confirmation
      only if ambiguity or domain conflict arises. Emit a final checklist of completed vs pending actions.

  - phase: 4_optional_macro_guidance_matrix
    description: >
      For sections with abstraction-vs-direct signal choices, emit a toggleable logic matrix so future developers
      can apply the same reasoning. Mark where abstraction was preserved intentionally and why.

trigger_points:
  - Prior prompt includes advisory refactor or optimization response
  - Claude is invoked mid-chain after Promachos or MetaStructor emits a task plan
  - Snapshot YAML shows legacy abstraction patterns marked for upgrade

semantic_contract:
  - All refactor outputs must preserve behavioral equivalence or improve it
  - Comments must explicitly trace rationale and transformation path
  - All outputs must be tiered and validator-ready with no guessable logic

output_contracts:
  format: yaml
  must_include:
    - entity_id
    - platform
    - state or value_template
    - tier
    - origin
    - note (change justification)
  if_abstracted:
    - include matrix or toggle rule explaining abstraction retention

persona_roles:
  Promachos: upstream governance and plan validation
  MetaStructor: naming enforcement and structural coherence
  Claude: primary executor (YAML rewrite, refactor tracking, decision matrices)
  Icaria: integration test patching
  Iris: anomaly surface for unresolved abstraction mismatches

