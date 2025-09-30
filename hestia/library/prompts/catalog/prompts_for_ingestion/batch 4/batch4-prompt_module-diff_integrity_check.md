phase: diff_integrity_check
action: audit_refactor_information_integrity
validation_status: pending
goals:
  - Ensure that all semantically meaningful components from the original YAML are accounted for in the refactor
  - Detect and flag information loss or silent omission of operational logic
  - Confirm that each retained or modified block adds clarity, abstraction, or structural improvement
evaluation_criteria:
  - Any removed entity must be justified with a design rationale
  - Any renamed or refactored element must preserve functional equivalence or improve role expressiveness
  - New elements must be additive or consolidative, not duplicative
required_inputs:
  - source_file: ha-networking-configuration.yaml
  - refactored_file: <refactored_output>.yaml
next_steps:
  - Run semantic diff between source and refactored sensor blocks
  - Identify tier shifts, role migrations, or deleted logic
  - Emit lineage map: source_id → refactored_id with change reason
affirmation_template:
  proceed: Proceed to source-to-refactor lineage mapping and data flow traceability audit.
  pause: Pause and surface justification for removed or transformed components.
