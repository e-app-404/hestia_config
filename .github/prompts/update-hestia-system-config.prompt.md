---
mode: "agent"
model: "gpt-4"
description: "Update Hestia system configuration files with recent changes and ensure information accuracy"
tools: ["edit", "search", "readFiles", "writeFiles"]
---

# Update Hestia System Configuration Files

Systematically update configuration files in `/config/hestia/config/system/` with recent changes and validate information accuracy across the workspace.

## Mission

Maintain accurate and current documentation in Hestia system configuration files by:
1. **Identifying recent changes** requiring documentation updates
2. **Updating appropriate system config files** with relevant information
3. **Scanning workspace for inconsistencies** and proposing corrections
4. **Presenting patch plans** for validation before applying changes

## Scope & Preconditions

**Target Configuration Files:**
- `maintenance_log.conf` - Session-based maintenance tracking
- `cli.conf` - CLI command documentation and usage patterns
- `addons.conf` - Home Assistant addon configuration and changes
- `hestia.toml` - Central workspace configuration
- `homeassistant.conf` - HA-specific settings and integration notes
- `suggested_commands.conf` - Operational command patterns
- `transient_state.conf` - Current system state documentation

**Required Context:**
- Recent git commits and changes
- New tools or scripts added to workspace
- Home Assistant configuration modifications
- System maintenance actions performed
- ADR compliance requirements

## Workflow

### Phase 1: Change Detection & Analysis

1. **Scan Recent Activity:**
   - Review git log for recent commits and file changes
   - Identify new tools, scripts, or configuration additions
   - Detect Home Assistant addon changes or updates
   - Analyze maintenance actions from logs or evidence

2. **Categorize Changes:**
   - **Maintenance Actions**: Document in `maintenance_log.conf`
   - **CLI Tools**: Add to `cli.conf` with usage patterns
   - **Addon Changes**: Update `addons.conf` with versions/configurations
   - **System Settings**: Modify `hestia.toml` or `homeassistant.conf`
   - **Operational Patterns**: Add to `suggested_commands.conf`

### Phase 2: Configuration File Updates

#### For `maintenance_log.conf`:
```yaml
session_YYYY_MM_DD_description:
  date: "YYYY-MM-DD"
  duration: "~X hours"
  focus: "Brief description of maintenance focus"
  
  actions_completed:
    action_name:
      description: "What was accomplished"
      files_modified: ["list", "of", "files"]
      tools_used: ["command", "patterns"]
      
  metrics:
    errors_before: X
    errors_after: X
    success_rate: "XX%"
    
  knowledge_captured:
    topic_name:
      description: "Key insights or learnings"
      
  confidence_level:
    technical: 0.XX
    operational: 0.XX
    documentation: 0.XX
```

#### For `cli.conf`:
```yaml
new_tool_name:
  command: "/path/to/tool"
  description: "Tool purpose and functionality"
  usage_patterns:
    - "common usage example"
    - "advanced usage with flags"
  dependencies: ["required", "packages"]
  related_adrs: ["ADR-XXXX"]
```

#### For `addons.conf`:
```yaml
addon_name:
  version: "X.X.X"
  installation_date: "YYYY-MM-DD"
  configuration_notes: "Key settings or customizations"
  dependencies: ["other", "addons"]
  maintenance_notes: "Important operational information"
```

### Phase 3: Workspace Validation Scan

1. **Cross-Reference Validation:**
   - Verify tool documentation matches actual implementation
   - Check addon versions against installed versions
   - Validate maintenance log entries against file timestamps
   - Ensure ADR compliance references are current

2. **Content Accuracy Review:**
   - Scan for outdated version numbers or references
   - Identify missing documentation for new tools
   - Check for broken file paths or references
   - Validate configuration examples against current syntax

3. **Consistency Checks:**
   - Ensure naming conventions match across files
   - Verify cross-references between configuration files
   - Check for duplicate or conflicting information
   - Validate timestamp formats and standards

### Phase 4: Patch Plan Generation

For each identified issue, generate structured patch proposals:

```markdown
## Patch Plan: [Brief Description]

**Target File:** `/config/hestia/config/system/[filename]`
**Issue Type:** [Missing Documentation | Outdated Information | Inconsistency]
**Priority:** [High | Medium | Low]

**Current State:**
```yaml
# Current configuration or missing section
```

**Proposed Change:**
```yaml
# Recommended configuration or addition
```

**Rationale:** 
- Why this change is needed
- What problem it solves
- ADR compliance or governance requirement

**Impact Assessment:**
- Files affected: [list]
- Breaking changes: [Yes/No]
- Validation required: [commands to verify]

**Dependencies:**
- Prerequisites for this change
- Related changes that must be made together
```

## Output Expectations

### Update Summary Report

```markdown
# Hestia System Configuration Update Summary

## Changes Applied
- [X] maintenance_log.conf: Added session_YYYY_MM_DD_description
- [X] cli.conf: Added [tool_name] documentation  
- [X] addons.conf: Updated [addon_name] version information

## Patch Plans for Review
1. **[filename]**: [brief description] - [Priority]
2. **[filename]**: [brief description] - [Priority]

## Validation Commands
- `command to verify change 1`
- `command to verify change 2`

## Next Actions Required
- [ ] Review and approve patch plans
- [ ] Execute validation commands
- [ ] Update related documentation if needed
```

### Patch Plan Presentation

Present each patch plan with:
- **Clear before/after comparison**
- **Specific rationale for the change**
- **Impact assessment and risk analysis**
- **Validation steps to confirm success**
- **Priority ranking for implementation order**

## Quality Assurance

### Pre-Update Validation
- [ ] Backup existing configuration files
- [ ] Verify file write permissions
- [ ] Check for file locks or concurrent edits
- [ ] Validate YAML/TOML syntax before applying changes

### Post-Update Verification
- [ ] Confirm file syntax remains valid
- [ ] Verify cross-references resolve correctly
- [ ] Test any documented commands or tools
- [ ] Validate ADR compliance is maintained

### Error Handling
- **Syntax Errors**: Validate all YAML/TOML before saving
- **Missing References**: Flag broken links or file paths
- **Permission Issues**: Document access requirements
- **Concurrent Edits**: Detect and handle file conflicts

## Security & Compliance

- **No Secrets**: Never include passwords, tokens, or sensitive data
- **ADR Compliance**: Ensure changes align with governance requirements
- **Path Standards**: Follow ADR-0024 canonical path conventions
- **File Governance**: Use ADR-0027 write-broker patterns when available

## Success Criteria

- [ ] All recent changes documented in appropriate system config files
- [ ] No outdated or incorrect information remains
- [ ] All cross-references and file paths are valid
- [ ] Patch plans are clear, actionable, and prioritized
- [ ] Configuration files maintain valid syntax and structure
- [ ] Changes support operational workflows and maintenance

Execute this prompt to maintain accurate, current documentation in Hestia system configuration files while identifying and proposing corrections for any inconsistencies found during workspace scanning.