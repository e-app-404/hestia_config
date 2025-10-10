---
id: prompt_20250401_931d51
slug: gpt-instructions-hestia-conversation-analysis-for
title: 'GPT Instructions: HESTIA Conversation Analysis for Architectural Knowledge'
date: '2025-04-01'
tier: "α"
domain: instructional
persona: nomia
status: candidate
tags: []
version: '1.0'
source_path: outdated_for_review/gpt-crawl-chat-architecture.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:25.706427'
redaction_log: []
---

# GPT Instructions: HESTIA Conversation Analysis for Architectural Knowledge

## Purpose
Extract architectural principles, design patterns, and system rules from development conversations to enrich HESTIA's architectural knowledge base.

## Input Sources
Analyze:
- Developer conversation threads
- Code review discussions
- Design decision explanations
- Problem-solving sessions

## Analysis Process

### 1. First Pass: Identify Key Segments
- Scan the entire conversation
- Mark segments where architectural decisions are being discussed
- Flag explanations of "why" something is designed a certain way
- Identify discussions around problems and their solutions

### 2. Second Pass: Extract Core Concepts
For each identified segment, extract:
- The problem being addressed
- The proposed solution or pattern
- The rationale behind the decision
- Any constraints or requirements mentioned
- Whether it's presented as a flexible pattern or strict rule

### 3. Third Pass: Categorize and Formalize
Categorize each extracted concept as either:
- **Design Pattern** - A recommended approach based on experience
- **Architectural Doctrine** - A foundational rule that must be followed

## Output Format

For each extracted principle, create:

### 1. Structured Principle Entry
```yaml
id: "<auto_generated_id>"
title: "<concise_title>"
principle: "<clear_statement>"
rationale: "<why_this_matters>"
example:
  good: "<code_or_approach_to_follow>"
  avoid: "<anti_pattern_to_avoid>"
tier: "<architectural_layer>" # α, β, γ, δ, ε, ζ or "all"
domain: "<relevant_subsystem>" # motion, lighting, etc.
type: "pattern" # or "doctrine" 
source: 
  conversation_id: "<this_conversation_id>"
  participants: ["<participant1>", "<participant2>"]
  date: "<extraction_date>"
status: "proposed"
tags: ["<relevant_tag1>", "<relevant_tag2>"]
```

### 2. Human-Readable Explanation
```markdown
### <Title>

**Type**: [Pattern|Doctrine]
**Domain**: <domain>
**Tier**: <tier>

**Principle**: <One-sentence summary>

**Why**: <Explanation of rationale>

✅ **Do**:
```yaml
<good example>
```

❌ **Don't**:
```yaml
<problematic example>
```

**Context**: Extracted from discussion about <topic> between <participants> on <date>.
```

## Tips for Quality Extraction

### Recognizing Design Patterns
- Look for phrases like "we typically...", "it's better to...", "in my experience..."
- Solutions to recurring problems
- Approaches that improve code quality but have alternatives
- May include words like "recommended", "preferred", "usually"

### Recognizing Architectural Doctrines
- Look for phrases like "must always...", "never...", "critical to..."
- Fundamental architectural decisions
- Rules that maintain system integrity
- May include words like "required", "mandatory", "essential"

### General Guidelines
- Focus on principles that apply beyond the specific context discussed
- Prioritize extracting the "why" behind decisions, not just the "what"
- Include enough context that someone unfamiliar with the conversation can understand
- Use the exact language from the conversation when possible for examples
- If unclear whether something is a pattern or doctrine, default to pattern

## Integration Process
1. Generate a JSON representation of each principle
2. Submit to approval queue for review by the architecture team
3. Upon approval, create a PR to update:
   - `architecture_principles.yaml` with the structured entry
   - `docs/developer_guidelines.md` with the human-readable explanation
   - Tag principles with the conversation they were extracted from

## Example Extraction

**Conversation Segment**:
> "When working with motion sensors, we've found that having an explicit alias layer between the physical sensor and the logic prevents a lot of headaches when hardware changes. All logic should point to these aliases rather than directly to device entities."

**Extracted Principle**:
```yaml
id: "sensor_aliasing_001"
title: "Sensor Aliasing Before Logic"
principle: "Always create aliased entities for physical sensors before referencing them in logic"
rationale: "Decouples logic from physical implementation, enabling hardware changes without breaking automations"
example:
  good: |
    # Create alias first
    binary_sensor.kitchen_motion_β:
      value_template: "{{ is_state('binary_sensor.kitchen_motion_device', 'on') }}"
    
    # Reference alias in logic
    sensor.kitchen_motion_score_γ:
      value_template: "{{ 100 if is_state('binary_sensor.kitchen_motion_β', 'on') else 0 }}"
  avoid: |
    # Directly referencing physical device in logic
    sensor.kitchen_motion_score_γ:
      value_template: "{{ 100 if is_state('binary_sensor.kitchen_motion_device', 'on') else 0 }}"
tier: "β"
domain: "sensors"
type: "doctrine" 
source:
  conversation_id: "conv_20250401_arch_review"
  participants: ["developer1", "architect2"]
  date: "2025-04-01"
status: "proposed"
tags: ["aliasing", "sensors", "abstraction"]
```
