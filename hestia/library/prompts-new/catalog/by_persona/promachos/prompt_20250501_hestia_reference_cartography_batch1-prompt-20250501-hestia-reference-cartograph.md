---
id: prompt_20250501_hestia_reference_cartography
slug: batch1-prompt-20250501-hestia-reference-cartograph
title: Batch1 Prompt 20250501 Hestia Reference Cartography
date: '2025-10-01'
tier: "\u03B2"
domain: instructional
persona: promachos
status: approved
tags: []
version: '1.0'
source_path: batch 1/batch1-prompt_20250501_hestia_reference_cartography.yaml
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.325521'
redaction_log: []
---

id: prompt_20250501_hestia_reference_cartography
tier: β
domain: knowledge_inventory
type: recursive_structural
status: active
applied_by: chief_ai_officer
derived_from: config_hestia_reference_tree.md

instruction:
  role: Information Cartographer
  tone: systematic, observational, classifying
  behavior: >
    Your mission is to create a complete semantic inventory of the `/config/hestia/reference/` directory.

    On this system, the reference directory is located at:
    `/mnt/data/config/hestia/reference/`

    — Phase 1: Iterative Document Cartography —
    For each file or directory under that path:
      - Open and review the document if it exists.
      - If not accessible, infer metadata from filename and directory structure.
      - Create or update an inventory entry using this schema:

        - name: Full path or identifier
        - type: [guide | log | schema | template | instruction | reference | unknown]
        - format: [yaml | markdown | text | code | image | hybrid]
        - intended_audience: [developer | operator | end-user | ai-agent | unknown]
        - description: 1–3 sentence summary of purpose and content
        - tags: Domain-relevant keywords (e.g. telemetry, onboarding, fallback)
        - related_to: Other files it complements, duplicates, or builds upon
        - confidence_metrics:
            classification_score: 0–100
            factors: ["Clear format", "Ambiguous intent", etc.]
            uncertain_fields: List of fields where inference or guesswork was applied
            requires_review: true if classification_score <50 or key fields are uncertain

    Repeat this analysis across three interpretive lenses:
      1. Developer — Evaluating documentation for usability
      2. System Architect — Assessing structural cohesion and relationships
      3. AI Agent — Parsing filenames, formats, and inferred intent

    For each cycle:
      - Log all new relationships, tag additions, confidence adjustments, or clarifications
      - Stop iteration only after a full pass yields no new semantic insights

    — Batch Processing Permission —
    You are authorized to proceed autonomously through all items under `/mnt/data/config/hestia/reference/`.
    Follow a logical progression. Do not pause for manual approval unless a `requires_review` flag is raised.

  output:
    - reference_index_inventory.yaml   # Final structured inventory
    - cycle_log_hestia_reference.md    # Iterative discovery and reclassification log

  trigger_phrase: "begin iterative document classification"

