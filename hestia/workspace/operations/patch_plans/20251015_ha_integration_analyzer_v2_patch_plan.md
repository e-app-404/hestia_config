# Home Assistant Integration Analyzer Patch Plan

**Date**: 20251015
**Topic**: ha_integration_analyzer_v2
**Integration**: VS Code Prompt Template
**Configuration File**: `/config/hestia/library/prompts/development/drafts/ha_integration_analyzer.prompt.md`
**Documentation Reference**: VS Code Prompt Files Documentation

## Executive Summary

The current ha_integration_analyzer prompt template has solid conceptual foundations but contains critical technical issues that prevent practical use. Key problems include invalid JavaScript syntax in YAML context, inconsistent variable handling, and overly complex structure. This patch plan addresses these issues while streamlining the user experience and improving reliability.

## Analysis Results

**Total Issues Found**: 11 issues identified across priority levels

- CRITICAL: 3 issues (JavaScript syntax, variable inconsistency, recursive templates)
- HIGH: 3 issues (missing error handling, overly complex structure, ambiguous priorities)
- MEDIUM: 3 issues (hard-coded paths, missing error pattern integration, limited tool use)
- LOW: 2 issues (verbose documentation, limited examples)

## Detailed Findings

### CRITICAL: Invalid JavaScript Syntax in YAML Context

**Problem**: Template contains JavaScript expressions like `${new Date().toISOString().split('T')[0].replace(/-/g, '')}` that won't execute in VS Code prompt context.

**Impact**: Date calculations appear as literal strings, breaking file naming and timestamps.

**Before**:

```markdown
**Date**: ${new Date().toISOString().split('T')[0].replace(/-/g, '')}

- Create file at: `/config/hestia/workspace/cache/patch_plans/${new Date().toISOString().split('T')[0].replace(/-/g, '')}_${topic}_patch_plan.md`
```

**After**:

```markdown
**Date**: [Generate current date in YYYYMMDD format]

- Create file at: `/config/hestia/workspace/cache/patch_plans/[YYYYMMDD]_${input:topic}_patch_plan.md`
```

**Validation**: Verify template variables resolve correctly when prompt is executed.

### CRITICAL: Inconsistent Variable Reference Format

**Problem**: Mixes VS Code prompt variables (`${input:var}`) with custom variables (`${var}`) inconsistently throughout template.

**Impact**: Variable resolution failures and execution errors.

**Before**:

```markdown
- Parse the integration knowledge page at `${integration_doc_path}`
- Parse the YAML configuration file at `${config_yaml_path}`
  **Topic**: ${topic}
```

**After**:

```markdown
- Parse the integration knowledge page at `${input:integration_doc_path}`
- Parse the YAML configuration file at `${input:config_yaml_path}`
  **Topic**: ${input:topic}
```

**Validation**: All variables use consistent VS Code input format with proper placeholders.

### CRITICAL: Recursive Template Structure

**Problem**: Patch plan template contains variables that reference themselves, creating circular dependencies.

**Impact**: Template generation fails or produces malformed output.

**Before**:

````markdown
#### Patch Plan Template

```markdown
**Configuration File**: `${config_yaml_path}`
```
````

````

**After**:
```markdown
#### Patch Plan Template Structure
When generating the patch plan, include these sections with actual values substituted:
- Configuration File: [Path from input parameter]
- Documentation Reference: [Path from input parameter]
````

**Validation**: Template generates clean patch plans without circular references.

### HIGH: Missing Error Handling Guidance

**Problem**: No validation steps for input file existence or accessibility.

**Impact**: Silent failures with unclear error messages when files don't exist.

**Before**:

```markdown
## Execution Instructions

1. **Validate Inputs**: Confirm both file paths exist and are accessible
```

**After**:

```markdown
## Pre-Flight Validation

Before starting analysis, verify:

1. **File Accessibility**:
   - Check integration documentation exists at specified path
   - Verify configuration YAML file is readable
   - Confirm write access to patch plan output directory
2. **Error Handling**: If files are missing, provide clear guidance to user on locating correct paths
```

**Validation**: Prompt provides helpful error messages when inputs are invalid.

### HIGH: Overly Complex Phase Structure

**Problem**: 5-phase process with nested steps is overwhelming and difficult to follow.

**Impact**: Users may skip important steps or abandon the process.

**Before**:

```markdown
### Phase 1: Documentation Ingestion & Parsing

### Phase 2: Configuration Analysis

### Phase 3: Priority-Based Issue Classification

### Phase 4: Patch Plan Generation

### Phase 5: File Operations & Output
```

**After**:

```markdown
### Step 1: Analyze & Compare

- Load and parse both documentation and configuration files
- Identify discrepancies and improvement opportunities

### Step 2: Classify & Prioritize

- Categorize issues by impact level (Critical → Low)
- Generate specific recommendations with before/after examples

### Step 3: Generate & Present

- Create timestamped patch plan file
- Present executive summary for user validation
```

**Validation**: Streamlined process is easier to follow and complete.

### HIGH: Ambiguous Priority Definitions

**Problem**: MEDIUM and LOW priority definitions have unclear boundaries and potential overlap.

**Impact**: Inconsistent issue classification across different analyses.

**Before**:

```markdown
#### MEDIUM Priority

**Definition**: Configuration works correctly but has gaps that could negatively impact related functionalities, monitoring, or future maintenance without immediate runtime effects.

#### LOW Priority

**Definition**: Aesthetic or organizational improvements that enhance code maintainability, UI presentation, or documentation without affecting functionality.
```

**After**:

```markdown
#### MEDIUM Priority

**Definition**: Missing best practices that impact maintainability, monitoring, or integration completeness but don't affect core functionality.
**Key Indicators**: Missing unique_id, suboptimal naming, missing derived sensors, hardcoded values

#### LOW Priority

**Definition**: Cosmetic improvements that enhance user experience or code organization without functional impact.
**Key Indicators**: Icon assignments, comment additions, formatting consistency, UI presentation tweaks
```

**Validation**: Clear distinction between MEDIUM (technical debt) and LOW (cosmetic) priorities.

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)

- [ ] Replace all JavaScript expressions with clear placeholder instructions
- [ ] Standardize variable references to VS Code input format throughout
- [ ] Restructure patch plan template to avoid circular references
- [ ] Add comprehensive input validation requirements

### Phase 2: High Priority (Within 1 week)

- [ ] Simplify 5-phase structure to 3-step process
- [ ] Clarify priority definitions with specific indicators
- [ ] Add error handling and fallback procedures
- [ ] Create decision gates between major steps

### Phase 3: Medium Priority (Within 1 month)

- [ ] Replace hard-coded paths with workspace-relative references
- [ ] Integrate with existing error pattern knowledge base
- [ ] Add support for additional VS Code tools
- [ ] Create modular sections for different integration types

### Phase 4: Low Priority (As time permits)

- [ ] Condense verbose documentation sections
- [ ] Add multiple usage scenario examples
- [ ] Create quick-start guide for common use cases
- [ ] Add confidence scoring for recommendations

## Testing & Validation

1. **Syntax Validation**

   - Test prompt template with VS Code prompt file parser
   - Verify all input variables resolve correctly
   - Confirm no JavaScript expressions remain

2. **Execution Testing**

   - Run prompt with sample SNMP documentation and configuration
   - Verify patch plan file creation with proper naming
   - Test error handling with invalid file paths

3. **Usability Testing**
   - Time how long it takes to complete analysis
   - Verify output quality and actionability
   - Test with different integration types

## Rollback Plan

**Backup Commands**:

```bash
cp /config/hestia/library/prompts/development/drafts/ha_integration_analyzer.prompt.md /config/hestia/library/prompts/development/drafts/ha_integration_analyzer.prompt.md.backup.20251015
```

**Restore Commands**:

```bash
cp /config/hestia/library/prompts/development/drafts/ha_integration_analyzer.prompt.md.backup.20251015 /config/hestia/library/prompts/development/drafts/ha_integration_analyzer.prompt.md
```

## Implementation Files

### Primary Implementation

- `/config/hestia/library/prompts/development/drafts/ha_integration_analyzer_v2.prompt.md` (new streamlined version)

### Supporting Documentation

- `/config/hestia/library/prompts/development/README.md` (usage guide)
- `/config/hestia/library/prompts/development/examples/` (sample analyses)

## Success Criteria

1. **Technical**: Template executes without syntax errors or variable resolution issues
2. **Usability**: Complete analysis can be performed in under 10 minutes
3. **Quality**: Generated patch plans are actionable and well-structured
4. **Reliability**: Error handling provides clear guidance for common issues

## References

- VS Code Prompt Files Documentation
- Original template: `/config/hestia/library/prompts/development/drafts/ha_integration_analyzer.prompt.md`
- Error Patterns: `/config/hestia/library/error_patterns.yml`
- Promptset Template: `/config/hestia/library/prompts/_meta/draft_template.promptset`

---

_Generated by Home Assistant Integration Analyzer Patch Plan v1.0_
