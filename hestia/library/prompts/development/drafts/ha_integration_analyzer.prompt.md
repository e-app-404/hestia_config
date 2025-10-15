---
mode: 'agent'
model: 'Claude Sonnet 4'
tools: ['search/codebase']
description: 'Streamlined Home Assistant integration configuration analyzer with prioritized patch plan generation'
---

# Home Assistant Integration Analyzer v2

<!-- 
Streamlined version v2 addressing critical issues from v1:
- Fixed JavaScript syntax and variable handling
- Simplified 5-phase to 3-step process
- Improved error handling and validation
- Clearer priority definitions with specific indicators
-->

## Objective

Analyze Home Assistant integration configurations against documentation to identify improvements and generate actionable patch plans with clear priorities.

## Input Requirements

Please provide these three inputs to begin analysis:

1. **Integration Documentation**: `${input:integration_doc_path:Full path to integration documentation file}`
2. **Configuration File**: `${input:config_yaml_path:Full path to YAML configuration file to analyze}`  
3. **Analysis Topic**: `${input:topic:Short identifier for this analysis (e.g., netgear_snmp)}`

## Pre-Flight Validation

Before starting analysis, I will verify:

1. **File Accessibility**:
   - Integration documentation exists and is readable at specified path
   - Configuration YAML file exists and is accessible
   - Output directory `/config/hestia/workspace/cache/patch_plans/` is writable

2. **Error Handling**:
   - If files are missing, I'll provide clear guidance on locating correct paths
   - If permissions are insufficient, I'll suggest resolution steps
   - If file formats are invalid, I'll explain requirements

## Streamlined Analysis Process

### Step 1: Analyze & Compare

**Load Documentation**:
- Parse integration documentation from `${input:integration_doc_path}`
- Extract configuration parameters, valid values, and best practices
- Identify required vs optional parameters and version requirements
- Build reference schema for comparison

**Load Configuration**:
- Parse YAML configuration from `${input:config_yaml_path}`
- Extract integration-specific configurations
- Map current parameters to documentation schema
- Identify discrepancies and improvement opportunities

### Step 2: Classify & Prioritize

I will categorize all issues using this refined priority framework:

#### CRITICAL Priority
**Definition**: Configuration errors preventing functionality or causing Home Assistant load failures.
**Key Indicators**: Missing required parameters, invalid values, syntax errors, security vulnerabilities
**Impact**: Integration completely broken or Home Assistant won't start

#### HIGH Priority  
**Definition**: Functional configuration that significantly underperforms or lacks important capabilities.
**Key Indicators**: Missing error handling, inefficient polling, missing security features, poor UI integration
**Impact**: Integration works but with major limitations or performance issues

#### MEDIUM Priority
**Definition**: Missing best practices that impact maintainability, monitoring, or integration completeness.
**Key Indicators**: Missing unique_id, suboptimal naming, missing derived sensors, hardcoded values
**Impact**: Technical debt that affects future maintenance or monitoring capabilities

#### LOW Priority
**Definition**: Cosmetic improvements enhancing user experience without functional impact.
**Key Indicators**: Icon assignments, comment additions, formatting consistency, UI presentation
**Impact**: Aesthetic enhancements only

**Output Format for Each Issue**:
```markdown
### [PRIORITY]: [Issue Description]

**Problem**: [Clear explanation of the issue]
**Impact**: [What doesn't work or works suboptimally]  
**Solution**: [Specific fix required]

**Before**:
```yaml
# Current configuration
```

**After**:
```yaml
# Improved configuration  
```

**Validation**: [How to verify the fix works]

### Step 3: Generate & Present

**Create Patch Plan File**:
- Generate comprehensive patch plan using current date in YYYYMMDD format
- Save to `/config/hestia/workspace/cache/patch_plans/[YYYYMMDD]_${input:topic}_patch_plan.md`
- Include all classified issues with before/after examples

**Present Executive Summary**:
- Display overview of findings and priorities
- Highlight critical and high priority issues requiring immediate attention
- Request user validation before implementation

## Patch Plan Template Structure

When generating the patch plan, I'll create a file with these sections:

<!-- Patch Plan Template Structure starts here -->
# Home Assistant Integration Patch Plan

**Date**: [Current date in YYYYMMDD format]
**Topic**: [Analysis topic from input]
**Integration**: [Integration name identified from analysis]
**Configuration File**: [Path from input parameter]
**Documentation Reference**: [Path from input parameter]

## Executive Summary
[2-3 sentence overview of findings and recommended actions]

## Analysis Results
**Issues Found**: [Total count by priority]
- CRITICAL: [count] issues
- HIGH: [count] issues  
- MEDIUM: [count] issues
- LOW: [count] issues

## Priority Issues
[All classified issues using the format above]

## Implementation Roadmap
### Immediate (Critical Issues)
- [ ] [Brief description of each critical fix]

### This Week (High Priority)  
- [ ] [Brief description of each high priority improvement]

### This Month (Medium Priority)
- [ ] [Brief description of each medium priority enhancement]

### Future (Low Priority)
- [ ] [Brief description of each low priority polish item]

## Validation Steps
1. **Configuration Check**: Run `${workspaceFolder}/bin/config-validate ${workspaceFolder}`
2. **Integration Test**: Restart Home Assistant and verify entity loading
3. **Functional Test**: [Integration-specific validation steps]

## Backup & Rollback
**Backup**: `cp [config-file] [config-file].backup.[YYYYMMDD_HHMMSS]`
**Restore**: `cp [config-file].backup.[timestamp] [config-file]`

## References
- Documentation: [Integration documentation path]
- Error Patterns: error_patterns.yml
<!-- Patch Plan Template Structure ends here -->

## Error Pattern Integration

During analysis, I will cross-reference findings against known error patterns in:
- `/config/hestia/library/error_patterns.yml`

This ensures I leverage existing knowledge of common issues and their solutions.

## Quality Assurance Standards

For every recommendation, I will ensure:

- **Accuracy**: All suggestions are validated against official Home Assistant documentation
- **Syntax**: All "After" examples use correct YAML syntax and follow best practices
- **Completeness**: Each issue includes clear problem description, impact assessment, and specific solution
- **Actionability**: Implementation steps are concrete and testable

## Usage Instructions

1. **Start Analysis**: Provide the three required input parameters
2. **Review Validation**: Confirm all files are accessible 
3. **Monitor Progress**: I'll provide status updates for each step
4. **Review Results**: Examine the generated patch plan and executive summary
5. **Approve Implementation**: Validate recommendations before applying changes

## Example Usage

To analyze a Netgear SNMP configuration:
```
/ha_integration_analyzer integration_doc_path:/config/hestia/library/ha_implementation/integration/integration.sensor-snmp.md config_yaml_path:/config/packages/package_netgear_gs724t.yaml topic:netgear_snmp
```

## Ready to Begin

I'm ready to perform your Home Assistant integration analysis. Please provide the three required input parameters:

1. Integration documentation path
2. Configuration YAML file path  
3. Analysis topic identifier

Once provided, I'll validate file access and begin the streamlined 3-step analysis process.