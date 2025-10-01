# 🧠 GPT Assistant Instructions for Maintaining and Evolving the `hestia/architecture/` Documentation

These instructions guide GPT assistants in reviewing, grooming, updating, and expanding the Hestia system architecture documentation. Your task is to ensure architectural clarity, integrity, and evolution as the system grows.

## 🗂️ Understanding the Documentation Structure

You will work primarily with four core files inside the `hestia/architecture/` directory:

| File Name | Purpose |
|----------|---------|
| `README_HESTIA_ARCHITECTURE_DESIGN.md` | Conceptual overview and onboarding guide to Hestia’s architecture |
| `ARCHITECTURE_DOCTRINE.yaml` | Structured declaration of architectural principles and values |
| `DESIGN_PATTERNS.md` | Implementation-level guidance on patterns and practices aligned with doctrine |
| `entity_map.json` | Machine-readable system map of services, modules, and their relationships |

## 🛠️ Responsibilities for GPT Assistants

### 1. **Review and Validate Consistency**

- Ensure **consistency** between high-level doctrine, patterns, and actual implementation practices.
- If newer modules or practices deviate from the doctrine or patterns, suggest:
  - Updates to the doctrine if the evolution is intentional.
  - Amendments to code or patterns if they diverge unintentionally.

### 2. **Update for Accuracy**
- When design changes are introduced (e.g., new event buses, service boundaries, or infrastructure upgrades), update:
  - `entity_map.json` to reflect current module structures.
  - `DESIGN_PATTERNS.md` to explain new architectural patterns.
  - `ARCHITECTURE_DOCTRINE.yaml` if foundational principles are expanded or refined.
  - `README_HESTIA_ARCHITECTURE_DESIGN.md` to ensure onboarding remains accurate.

### 3. **Grow with Contextual Awareness**

- If asked to add documentation for a new service, component, or pattern:
  - Infer **relevant architectural principles** from existing doctrine.
  - Position the addition within Hestia’s **modular, event-driven, and resilient** philosophy.
  - Maintain the **bounded context** approach, ensuring all additions are decoupled and coherent.

### 4. **Resolve Conflicts Between Old and New**
- When encountering contradictions:
  - Prefer newer guidance **only if explicitly versioned or referenced**.
  - If not, recommend a reconciliation update that explains the divergence and transitions the documentation accordingly.

### 5. **Document with Clarity and Purpose**
- Prioritize clarity, modularity, and audience alignment:
  - Use simple, declarative prose for doctrine.
  - Use detailed, example-driven Markdown for patterns.
  - Use structured YAML or JSON for machine-parsable artifacts.


## 🤖 When to Act

You should proactively offer updates or questions to the user when:
- The entity map is out of sync with a described component.
- Patterns being used are undocumented.
- Conflicting principles exist between files.
- There’s an opportunity to **consolidate** overlapping concepts.


## 🔍 When to Infer or Consolidate

You're expected to:
- **Infer principles** from emerging practices if not yet documented.
- **Consolidate** redundant or fragmented documentation across files.
- For example: if multiple patterns suggest “event sourcing” but use different terms, unify them under one clear pattern name and description.