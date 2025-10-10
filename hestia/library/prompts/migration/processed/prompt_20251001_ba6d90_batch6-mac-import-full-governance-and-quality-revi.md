---
id: prompt_20251001_ba6d90
slug: batch6-mac-import-full-governance-and-quality-revi
title: Batch6 Mac Import Full Governance And Quality Review
date: '2025-10-01'
tier: "α"
domain: operational
persona: promachos
status: candidate
tags:
- governance
version: '1.0'
source_path: batch6_mac-import_full governance and quality review.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:24.153907'
redaction_log: []
---

I am conducting a full governance and quality review of a collection of automation scripts used in our Mnemosyne environment. I've attached a `.tar.gz` archive containing multiple scripts. Please perform a hardened code audit with the following goals:

1. **Security and Fault Tolerance**:
   - Flag any use of unsafe operations (e.g., `eval`, shell injections, unchecked subprocesses).
   - Identify missing error handling, unsafe retries, or fail-silent logic.

2. **Consistency with Mnemosyne Standards**:
   - Validate that all scripts follow architectural conventions for entity references, tier naming (α–ζ), and automation hooks.
   - Confirm suffix and naming alignment with the `system_instruction.yaml` if available.

3. **Semantic and Logical Integrity**:
   - Detect logic duplication, invalid fallbacks, improper zone blending, or missing actuator checks.
   - Highlight any scripts that misinterpret inferred vs physical sensor logic or confuse γ/η-tier boundaries.

4. **Inter-script Cohesion**:
   - Identify scripts that reference shared logic but drift in logic structure or fallback assumptions.
   - Suggest consolidation opportunities or macro extraction if reusable patterns are observed.

5. **Deployment Readiness**:
   - Emit a manifest of scripts by zone and tier.
   - Annotate which scripts are deployment-ready vs which require governance patching.
   - Suggest validation hooks (e.g., CI macros, presence_simulation_traces/) to cover inferred-only zones or fallback-critical logic paths.

Output:
- A structured audit summary by script
- A YAML or markdown reconciliation manifest
- A list of recommended next actions (refactor, validate, reject)
- Highlight any blockers to deployment or integration with HESTIA pipelines

Once this is done, confirm if:
- Each script is aligned with the POA/DOT logic for its domain
- A fallback trace manifest and error harness is needed
- Macro hooks for templating can be safely emitted

