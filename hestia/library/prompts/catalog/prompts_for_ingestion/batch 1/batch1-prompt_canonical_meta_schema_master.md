**Directive Prompt: Self-Contained Meta Schema + Artifact Conformance Evaluation**

For each artifact declared in the `core_artifacts:` block of `system_instruction.yaml`, carry out the following two-phase protocol:

---

### 🧩 Phase 1: Generate Self-Contained Meta Schemas

For each artifact:

* Use its `schema_reference` as the file name (e.g., `tool_manifest_schema.json`)
* Extract its actual structure by parsing the artifact source document directly
* Model all required fields, nested structures, object types, and content expectations
* For `.json` artifacts: enforce key presence, types, object schemas, and constraints
* For `.md` artifacts: validate Markdown sections by heading structure, required blocks, keyword anchors, and presence of pattern/resolution logic
* Ensure the schema can be used for:

  * Validator enforcement
  * GPT output conformance
  * Auto-fix engines (e.g., Olympus, Nomia)
* Output each schema in a valid, self-contained `.json` schema file under `/meta-schema/`, with clearly annotated property roles

---

### 🔍 Phase 2: Conformance Evaluation + Scoring

For each artifact:

* Load the artifact content and its associated schema
* Validate the artifact **against its schema**
* Detect:

  * Structural mismatches
  * Optional fields missing
  * Deprecated or unexpected fields
  * Ambiguous section boundaries (for `.md`)
* Assign a **conformance confidence score** from `0.0` to `1.0`:

  * `1.0` = Fully conformant
  * `0.8–0.99` = Minor violations (e.g., missing optional metadata)
  * `0.5–0.79` = Structural misalignments (e.g., misplaced sections, schema drift)
  * `< 0.5` = Unusable or invalid structure
* Output a per-artifact evaluation summary table with:

  * Artifact name
  * Schema reference
  * Score
  * Summary of deviations
  * Recommendations

---

🧠 All schemas and validation output must be suitable for long-term automation, documentation governance, and integration with GPT-controlled changelogs. Schema design should anticipate forward compatibility, controlled vocabulary enforcement, and validator plug-in constraints.
