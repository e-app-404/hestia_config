---
mode: "agent"
model: "Claude Sonnet 4"
tools: ["search/codebase"]
description: "Analyze Home Assistant integration configurations against documentation and generate prioritized patch plans"
---

# Home Assistant Integration Configuration Analyzer

<!--
Promptset Metadata (for compatibility with draft_template.promptset):
- Version: 1.0
- Created: 2025-10-15
- Persona: ha_integration_analyst
- Protocols: [prompt_optimization_first, confidence_scoring_always, phase_context_memory]
- Bindings: Integration documentation, YAML configuration files
-->

## Objective

Systematically analyze Home Assistant integration configurations by comparing them against canonical documentation to identify improvements across priority levels and generate actionable patch plans.

## Input Requirements

Before proceeding, ensure you have access to:

1. **Integration Knowledge Page**: `${input:integration_doc_path:Path to integration documentation (e.g., integration.sensor-snmp.md)}`
2. **Configuration YAML File**: `${input:config_yaml_path:Path to configuration file (e.g., package_netgear_gs724t.yaml)}`
3. **Topic Identifier**: `${input:topic:Topic name for patch plan file naming (e.g., netgear_gs724t)}`

## Analysis Framework

### Phase 1: Documentation Ingestion & Parsing

1. **Load Integration Documentation**

   - Parse the integration knowledge page at `${integration_doc_path}`
   - Extract configuration parameters, valid values, examples, and best practices
   - Identify required vs optional parameters
   - Note version-specific requirements and deprecated features
   - Catalog error handling patterns and security recommendations

2. **Build Reference Schema**
   - Create internal mapping of valid configuration options
   - Document parameter relationships and dependencies
   - Establish baseline for comparison analysis

### Phase 2: Configuration Analysis

1. **Load Current Configuration**

   - Parse the YAML configuration file at `${config_yaml_path}`
   - Extract all integration-specific configurations
   - Map current parameters to documentation schema

2. **Systematic Comparison**
   - Validate each parameter against documentation
   - Check for missing required parameters
   - Identify deprecated or invalid syntax
   - Assess security and performance implications

### Phase 3: Priority-Based Issue Classification

Classify all identified issues using this priority framework:

#### CRITICAL Priority

**Definition**: Configuration errors that prevent the integration from functioning or cause Home Assistant to fail loading the configuration.

**Examples to identify**:

- Missing required parameters
- Invalid parameter values that cause validation errors
- Syntax errors in YAML structure
- Version incompatibility issues
- Security vulnerabilities (plaintext secrets, etc.)

**Output Format**:

````markdown
### CRITICAL: [Issue Description]

**Problem**: [Specific issue explanation]

**Impact**: [What breaks/fails to work]

**Before**:

```yaml
# Current problematic configuration
```
````

**After**:

```yaml
# Fixed configuration
```

**Validation**: [How to verify the fix works]

````

#### HIGH Priority
**Definition**: Configuration is functional but significantly suboptimal, preventing Home Assistant from fully deploying capabilities or causing performance/reliability issues.

**Examples to identify**:
- Missing optional parameters that significantly improve functionality
- Inefficient polling intervals or resource usage
- Incomplete error handling (missing `accept_errors`, `default_value`)
- Security improvements (SNMP v2c → v3 upgrades)
- Missing state classes or device classes for proper UI integration

**Output Format**: [Same structure as CRITICAL]

#### MEDIUM Priority
**Definition**: Configuration works correctly but has gaps that could negatively impact related functionalities, monitoring, or future maintenance without immediate runtime effects.

**Examples to identify**:
- Missing unique_id parameters preventing UI customization
- Suboptimal sensor naming or organization
- Missing template sensors for derived values
- Incomplete group definitions for logical organization
- Missing device_class assignments affecting UI presentation
- Hardcoded values that should use secrets or variables

**Output Format**: [Same structure as CRITICAL]

#### LOW Priority
**Definition**: Aesthetic or organizational improvements that enhance code maintainability, UI presentation, or documentation without affecting functionality.

**Examples to identify**:
- Inconsistent naming conventions
- Missing friendly_name attributes
- Suboptimal icon assignments
- Missing comments or documentation
- Code organization and formatting improvements
- UI presentation enhancements (better units, descriptions)

**Output Format**: [Same structure as CRITICAL]

### Phase 4: Patch Plan Generation

Generate comprehensive remediation plan using this structure:

#### Patch Plan Template
```markdown
# Home Assistant Integration Patch Plan

**Date**: ${new Date().toISOString().split('T')[0].replace(/-/g, '')}
**Topic**: ${topic}
**Integration**: [Integration name from analysis]
**Configuration File**: `${config_yaml_path}`
**Documentation Reference**: `${integration_doc_path}`

## Executive Summary

[2-3 sentence summary of findings and impact]

## Analysis Results

**Total Issues Found**: [Count by priority]
- CRITICAL: [count] issues
- HIGH: [count] issues
- MEDIUM: [count] issues
- LOW: [count] issues

## Detailed Findings

[Insert all classified issues using the priority format above]

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)
- [ ] [Issue 1 - brief description]
- [ ] [Issue 2 - brief description]

### Phase 2: High Priority (Within 1 week)
- [ ] [Issue 1 - brief description]
- [ ] [Issue 2 - brief description]

### Phase 3: Medium Priority (Within 1 month)
- [ ] [Issue 1 - brief description]
- [ ] [Issue 2 - brief description]

### Phase 4: Low Priority (As time permits)
- [ ] [Issue 1 - brief description]
- [ ] [Issue 2 - brief description]

## Testing & Validation

1. **Configuration Validation**
   - Run: `/config/bin/config-validate /config`
   - Verify: No configuration errors reported

2. **Integration Testing**
   - Restart Home Assistant
   - Verify: All entities load correctly
   - Check: Entity states update as expected

3. **Functional Testing**
   - [Integration-specific tests based on analysis]

## Rollback Plan

**Backup Commands**:
```bash
cp ${config_yaml_path} ${config_yaml_path}.backup.$(date +%Y%m%d_%H%M%S)
````

**Restore Commands**:

```bash
cp ${config_yaml_path}.backup.[timestamp] ${config_yaml_path}
```

## References

- Integration Documentation: `${integration_doc_path}`
- Home Assistant Configuration Reference: [relevant links]
- Error Patterns: `/config/hestia/library/error_patterns.yml`

---

_Generated by Home Assistant Integration Analyzer v1.0_

```

### Phase 5: File Operations & Output

1. **Generate Patch Plan File**
   - Create file at: `/config/hestia/workspace/cache/patch_plans/${new Date().toISOString().split('T')[0].replace(/-/g, '')}_${topic}_patch_plan.md`
   - Use the patch plan template above with all analysis results

2. **Present for Review**
   - Display executive summary
   - Highlight critical and high priority issues
   - Request validation before implementation

## Execution Instructions

1. **Validate Inputs**: Confirm both file paths exist and are accessible
2. **Run Analysis**: Execute all phases systematically
3. **Generate Output**: Create patch plan file with timestamp
4. **Present Results**: Show summary and request approval

## Quality Assurance

- Cross-reference all findings against official Home Assistant documentation
- Ensure all "After" examples are syntactically correct and follow best practices
- Validate that patch plan is actionable with specific steps
- Include proper backup and rollback procedures

## Usage Example

```

/ha_integration_analyzer integration_doc_path:/config/hestia/library/ha_implementation/integration/integration.sensor-snmp.md config_yaml_path:/config/packages/package_netgear_gs724t.yaml topic:netgear_gs724t_snmp

```

Ready to begin analysis. Please provide the required input parameters or run the command above with your specific file paths and topic identifier.
```
