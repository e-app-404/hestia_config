---
id: prompt_20250530_001
slug: batch2-prompt-20250530-001-prompts-for-synthesis
title: Batch2 Prompt 20250530 001 Prompts For Synthesis
date: '2025-10-01'
tier: "beta"
domain: extraction
persona: generic
status: candidate
tags: []
version: '1.0'
source_path: batch 2/batch2-prompt_20250530_001 prompts for synthesis.yml
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.898176'
redaction_log: []
---

### prompt_20250530_001
**Tier:** β
**Domain:** diagnostics  
**Title:** Audit Hallucinated Configuration Entities  
**Intent:** Force GPT to tag any config items not grounded in prior conversation  

**Prompt:**

```markdown
Please isolate any configuration elements in your last output that were **not explicitly discussed in our conversation**.  
Tag each one as `[NEW:UNVERIFIED]` so I can audit them quickly.  
Do not remove them—just annotate for review.
````

---

### prompt_20250530_002

**Tier:** β
**Domain:** reconciliation
**Title:** Extract Verified Config Source Inventory
**Intent:** Force a line-by-line enumeration of only discussed entities

**Prompt:**

```markdown
I want a strictly grounded enumeration of every configuration entity (sensor, binary_sensor, automation, script, shell_command, etc.) that we discussed in our conversation.

For each, include:
- where it was mentioned (paraphrase or quote)
- its purpose or function
- its configuration type (e.g., shell_command, sensor)

Do not infer or invent anything. If it's not in the conversation, omit it. This is a reconciliation step.
```

---

### prompt_20250530_003

**Tier:** β
**Domain:** regeneration
**Title:** Rebuild YAML from Verified Source List
**Intent:** Regenerate config exclusively from audited inputs

**Prompt:**

```markdown
Based on this verified source inventory, regenerate the YAML and **only include entities confirmed in the source list**.  
Tag each section with its purpose and corresponding conversation line if useful.  
Do not introduce any new tools, services, or IPs unless verified.
```
