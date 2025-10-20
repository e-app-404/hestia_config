# Meta-Capture Examples (Operator Use Only)

- `orange_shape_example.yaml` demonstrates an ORANGE result and a `routing_suggestion`
  only when schema validation is not active (e.g., running with a Python that lacks
  `jsonschema` or when `[automation.meta_capture.schemas.intake]` is intentionally
  unset for drills).
- CI always runs with schema validation on; shape mismatches are RED by design.
- Operators may use this example to demo routing suggestions outside CI.
