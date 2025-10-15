---
description: 'Consolidate and optimize Copilot custom instructions for Hestia workspace'
mode: 'agent'
model: 'GPT-4o'
tools: ['codebase']
---

# Consolidate Copilot Custom Instructions for Hestia Workspace

You are tasked with reviewing and consolidating the custom Copilot instructions implementation in the Hestia workspace. Your goal is to create a unified, comprehensive, and fully functional custom instructions setup that follows VS Code best practices.

## Phase 1: Current Implementation Review

Analyze the existing custom instructions files:

1. **Primary instructions file**: `/config/.github/copilot-instructions.md`
2. **Core instructions**: `/config/hestia/library/docs/governance/copilot_instruction/20250930_copilot_instruction.ha_config-core.md`
3. **Hestia-specific instructions**: `/config/hestia/library/docs/governance/copilot_instruction/20250930_copilot_instruction.ha_config-hestia.md`
4. **VS Code settings**: `/config/.vscode/settings.json` (check for Copilot-related configurations)

For each file, document:
- Current content and structure
- Intended scope and application
- Formatting and organization quality
- Overlap with other instruction files

## Phase 2: VS Code Guidelines Compliance

Review the workspace implementation against official VS Code guidelines from:
- `custom-instructions.md` - Official VS Code custom instructions documentation
- `prompt-files.md` - Official VS Code prompt files documentation

Evaluate compliance with:
- File naming conventions (`.github/copilot-instructions.md`)
- YAML frontmatter structure
- Markdown formatting standards
- Integration with VS Code Copilot Chat settings
- Automatic application to all chat requests

## Phase 3: Content Analysis and Consolidation Strategy

### Content Categorization
Organize existing instructions into logical categories:
- **Workspace Structure & Navigation** (canonical paths, directory structure)
- **Code Quality Standards** (Python, YAML, Jinja2, formatting)
- **Security & Safety Guidelines** (secrets handling, vault management)
- **Development Workflows** (CLI tools, deployment scripts, testing)
- **Home Assistant Specific** (configuration patterns, integration best practices)
- **Architecture Decision Records** (ADR formatting, governance)

### Consistency Analysis
Identify and document:
- **Contradictions**: Conflicting guidance between files
- **Redundancy**: Duplicate information across files
- **Gaps**: Missing coverage areas
- **Outdated Information**: References to deprecated paths, tools, or practices
- **Inconsistent Terminology**: Different terms for same concepts

## Phase 4: Unified Architecture Proposal

Design a consolidated custom instructions architecture:

### Primary Structure
```
/config/.github/copilot-instructions.md (main file)
├── Workspace Overview & Context
├── Canonical Path Standards (ADR-0024)
├── Code Quality & Formatting Standards
├── Security & Vault Management
├── Development Workflows & CLI Tools
├── Home Assistant Integration Patterns
├── Architecture Decision Records (ADR) Guidelines
└── AI Assistant Safety Guidelines
```

### Supporting Files (if needed)
- Task-specific `.instructions.md` files for specialized workflows
- Reference to governance documents via Markdown links

## Phase 5: Implementation Plan

Provide a detailed patch plan including:

### Step 1: Backup Current Setup
- Create timestamped backups of existing instruction files
- Document current VS Code settings configuration

### Step 2: Create Consolidated Instructions
- Merge content from all three instruction files
- Resolve contradictions and remove redundancy
- Apply consistent formatting and structure
- Ensure compliance with VS Code guidelines

### Step 3: Update VS Code Configuration
- Remove invalid Copilot settings from `.vscode/settings.json`
- Configure proper file references if needed
- Test automatic application to chat requests

### Step 4: Validation Testing
- Test instructions apply automatically to new chat sessions
- Verify no conflicts with existing workspace functionality
- Confirm all key guidance is preserved and accessible

## Phase 6: Quality Assurance Checklist

Ensure the final implementation:
- ✅ Follows official VS Code custom instructions format
- ✅ Applies automatically to all Copilot chat requests
- ✅ Contains no contradictory guidance
- ✅ Uses consistent terminology throughout
- ✅ References current (not deprecated) paths and tools
- ✅ Maintains all critical safety and security guidelines
- ✅ Preserves Hestia-specific context and workflows
- ✅ Uses proper Markdown formatting and structure
- ✅ Includes appropriate cross-references to related documents

## Expected Deliverables

1. **Analysis Report**: Detailed findings from current implementation review
2. **Consolidated Instructions File**: Complete `/config/.github/copilot-instructions.md`
3. **Configuration Updates**: Modified VS Code settings if needed
4. **Migration Guide**: Step-by-step instructions for implementing changes
5. **Validation Plan**: Testing procedures to confirm functionality
6. **Maintenance Guidelines**: How to keep instructions current going forward

## Context Variables Available

Use these variables to reference workspace-specific information:
- `${workspaceFolder}` - Workspace root path  
- Reference current files: `[governance](/config/hestia/library/docs/governance/)`
- Link to specific tools: `[ADR linter](/config/hestia/tools/utils/validators/adr_lint)`

## Success Criteria

The final implementation should:
- Provide comprehensive guidance for AI assistants working in the Hestia workspace
- Eliminate confusion from multiple overlapping instruction files
- Follow VS Code best practices for maximum compatibility
- Maintain all critical workspace-specific knowledge
- Enable consistent, high-quality AI assistance across all development tasks

Begin the analysis and provide your findings and recommendations.