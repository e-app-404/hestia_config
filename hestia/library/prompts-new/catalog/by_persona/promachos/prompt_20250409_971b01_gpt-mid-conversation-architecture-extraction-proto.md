---
id: prompt_20250409_971b01
slug: gpt-mid-conversation-architecture-extraction-proto
title: "\u2705 GPT Mid-Conversation Architecture Extraction Protocol"
date: '2025-04-09'
tier: "\u03B1"
domain: extraction
persona: promachos
status: deprecated
tags:
- extraction
version: '1.0'
source_path: batch6_mac-import_gpt_crawl-convo-architecture-extraction.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:23.017397'
redaction_log: []
---

# ✅ GPT Mid-Conversation Architecture Extraction Protocol

### 🧠 Objective

During an ongoing conversation, continuously scan for **underlying principles**, **inferred logic**, **implementation patterns**, and **naming conventions** that reflect architectural design thinking. Synthesize and document findings into the correct HESTIA architecture files, ensuring all outputs are:

- Categorized correctly (Doctrine 🔒 vs Design Pattern vs Developer Guidance)
- Consistent with the Greek Tier Naming system
- Traceable via metadata (source, tags, contributor)

### 1. 📘 Categorize Extracted Insights

| Category | Criteria | Target File |
|----------|----------|-------------|
| **🔒 Doctrine** | Non-negotiable architectural principle or constraint | `ARCHITECTURE_DOCTRINE.yaml` |
| **Design Pattern** | Common, reusable implementation strategy | `DESIGN_PATTERNS.md` |
| **Naming Convention** | Standardized entity or file naming | `nomenclature.md` |
| **Developer Guidance** | Human-readable best practices or examples | `developer_guidelines.md` |

### 2. 📐 Core Extraction Targets

Scan the conversation for:

- **Sensor tiering logic** using Greek suffixes (`_α`, `_β`, `_γ`, etc.)
- **Pattern of abstraction** (e.g., alias use, composition)
- **Architecture rationale** (why a design decision was made)
- **Entity relationships** (ownership, references)
- **Naming conflicts or violations**
- **Potential inconsistencies** between described and implemented systems

### 3. ⚙️ Output Formats

#### For Doctrine (`ARCHITECTURE_DOCTRINE.yaml`)
```yaml
- id: "alias_first_001"
  title: "Use Canonical Aliases Before Logic"
  principle: "All logic sensors must reference β-tier abstractions, not raw α-tier sensors."
  rationale: "This decouples logic from hardware, enabling substitution and stability."
  example:
    good: |
      sensor.motion_score_γ:
        source: binary_sensor.kitchen_motion_β
    avoid: |
      source: binary_sensor.kitchen_pir_α
  tier: "β"
  domain: "abstraction"
  derived_from: "conversation_2025-04-09.md"
  status: "proposed"
  created: "2025-04-09"
  contributors: ["gpt_architect"]
  tags: ["abstraction", "aliasing", "sensors"]
```

#### For Design Pattern (`DESIGN_PATTERNS.md`)
```markdown
### Use β-tier Aliases for Sensor Inputs

**Principle**: Always use `_β` alias abstractions when feeding into logic or scoring sensors.

✅ **Do**:
```yaml
sensor.motion_score_γ:
  value_template: "{{ is_state('binary_sensor.motion_β', 'on') }}"
```

❌ **Don't**:
```yaml
sensor.motion_score_γ:
  value_template: "{{ is_state('binary_sensor.motion_pir1', 'on') }}"
```

**Context**: Encourages modularity and hardware-independence.
```

#### For Developer Guidelines (`developer_guidelines.md`)
```markdown
## 3. Always Use Abstraction Aliases Before Logic

Avoid wiring logic directly to hardware (`_α`) sensors. Instead, route through `_β` tier.

💡 Use:
```yaml
binary_sensor.kitchen_motion_β
```

🚫 Avoid:
```yaml
binary_sensor.kitchen_motion_sensor_α
```
```

#### For Entity Mapping (`entity_map.json`)
```json
"sensor.kitchen_motion_β": {
  "owned_by": "abstractions/motion_aliases.yaml",
  "referenced_in": ["logic/motion_score.yaml", "dashboard/activity.yaml"]
}
```

### 4. 🧪 Cross-check Consistency

Ensure:
- Doctrines are enforced in patterns
- Patterns align with real examples
- Naming matches `nomenclature.md` rules
- All new entities are tracked in `entity_map.json`

### 5. 🏷️ Metadata Requirements

Each contribution must include:
- `origin`: source file or conversation
- `context`: what prompted the insight
- `tags`: architectural domain, e.g., `[abstraction, motion, presence]`
- `contributor`: who generated it
- `status`: proposed / approved / deprecated

