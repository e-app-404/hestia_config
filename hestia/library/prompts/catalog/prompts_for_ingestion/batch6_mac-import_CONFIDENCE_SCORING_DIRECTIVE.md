# 📏 Confidence Scoring Directive

## Purpose

To enforce consistent and auditable evaluation of all new prompts, instruction sets, personas, validation protocols, or governance patches.

## Mandate

All proposals (e.g., protocol additions, system behavior modifications, persona deployments) must include a structured confidence scoring block based on the following domains:

1. **Structural Confidence**: How complete and well-formed is the structure (YAML, Markdown, JSON)?
2. **Operational Confidence**: Can the artifact be executed or followed as-is with current context or capabilities?
3. **Semantic Confidence**: Does the behavior or instruction align with HESTIA doctrine, prompt design standards, and tier integrity principles?

## Format

Each artifact will include the following block:

```yaml
confidence_metrics:
  structural: {score: 85, rationale: "YAML schema complete and parseable"}
  operational: {score: 78, rationale: "Supports tier validation but may need integration hooks"}
  semantic: {score: 90, rationale: "Aligns with GPT_INSTRUCTION_DOCTRINE.md and prompt role logic"}
  adoption_recommendation: true
```

## Thresholds

| Field         | Minimum Adoption Score |
|---------------|------------------------|
| Structural     | 70                     |
| Operational    | 75                     |
| Semantic       | 80                     |
| Average        | ≥ 78                   |