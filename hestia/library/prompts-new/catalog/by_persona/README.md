# Persona Navigation (Hard Copies)

This directory contains **hard copies** of prompts organized by persona for specialized navigation.

## ⚠️  NAVIGATION ONLY: These are Hard Copies

Files in this directory are **hard copies** from `/catalog/by_domain/` (the primary canonical location).

**Do not edit files here directly** - always update the primary location first, then sync copies.

## Persona Classifications

Based on Greek archetypes for specialized prompt categories:

- `promachos/`: **Governance & Meta-System** - Policy, ADR, governance prompts
- `strategos/`: **Strategy & Planning** - Strategic analysis, planning prompts  
- `kybernetes/`: **Navigation & Pilot** - Guidance, routing, pilot prompts
- `icaria/`: **Repair & Fix** - Diagnostic, troubleshooting, repair prompts
- `nomia/`: **Validation & Rules** - Quality assurance, compliance, validation prompts
- `heurion/`: **Discovery & Analysis** - Research, analysis, discovery prompts

## Persona Characteristics

### Promachos (Governance)
- **Focus**: System governance and meta-control
- **Examples**: ADR creation, policy definition, governance review
- **Keywords**: governance, policy, meta, control, oversight

### Strategos (Strategy)  
- **Focus**: Strategic planning and high-level orchestration
- **Examples**: Architecture planning, strategy analysis, roadmap creation
- **Keywords**: strategy, planning, architecture, roadmap, orchestration

### Kybernetes (Navigation)
- **Focus**: Guidance and piloting through complex processes
- **Examples**: Workflow guidance, process navigation, step-by-step instructions
- **Keywords**: guidance, pilot, navigation, workflow, process

### Icaria (Repair)
- **Focus**: Diagnostic and repair operations
- **Examples**: Troubleshooting, debugging, system repair, problem resolution
- **Keywords**: repair, fix, debug, troubleshoot, diagnose

### Nomia (Validation)
- **Focus**: Rule enforcement and quality assurance  
- **Examples**: Validation, compliance checking, quality gates, rule enforcement
- **Keywords**: validation, compliance, rules, quality, standards

### Heurion (Discovery)
- **Focus**: Analysis, research, and discovery
- **Examples**: Data analysis, research, investigation, pattern discovery
- **Keywords**: analysis, research, discovery, investigation, exploration

## Copy Synchronization

Copies are maintained automatically:
- **Sync tool**: `/config/hestia/tools/catalog/sync_copies.py`
- **Validation**: `/config/hestia/tools/catalog/validate_copies.py`  
- **Source**: Primary canonical files in `/catalog/by_domain/`

## Usage

Browse by persona for specialized discovery, but always reference primary canonical paths:
```yaml
# Correct reference
bindings:
  - /config/hestia/library/prompts/catalog/by_domain/diagnostic/prompt_20251008_001_debug.md

# Incorrect - do not reference persona copies
bindings:
  - /config/hestia/library/prompts/catalog/by_persona/icaria/prompt_20251008_001_debug.md
```