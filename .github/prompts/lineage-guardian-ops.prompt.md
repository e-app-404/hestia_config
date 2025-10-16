---
mode: "agent"
model: "Claude Sonnet 4"
description: "Execute Hestia Lineage Guardian pipeline for entity relationship validation and correction"
tools: ["runCommands", "runTasks", "edit", "search", "problems", "files"]
---

# Hestia Lineage Guardian Operations

Execute the complete Lineage Guardian pipeline for Home Assistant template entity relationship validation, lineage correction, and graph integrity management.

## Mission

Run the end-to-end Lineage Guardian automation pipeline to:
1. **Scan templates** for entity relationships and lineage metadata
2. **Validate lineage** against declared vs actual entity references
3. **Generate correction plans** for lineage violations (non-destructive)
4. **Check graph integrity** with bidirectional consistency validation
5. **Produce comprehensive reports** with actionable recommendations

## Scope & Preconditions

- **Configuration**: All settings sourced from `/config/hestia/config/system/hestia.toml`
- **Tool Location**: `/config/hestia/tools/lineage_guardian/` (modular components)
- **Scope**: Template files under `/config/domain/templates/` only
- **Safety**: Dry-run by default, backup-before-modify, scope validation
- **Compliance**: ADR-0024 canonical paths, ADR-0018 workspace lifecycle, entity lineage patterns

## Inputs

- **Mode**: `${input:mode:full-pipeline}` - Operation mode (full-pipeline|scan-only|validate-only|correct-plan)
- **Template Dir**: `${input:template_dir:/config/domain/templates/}` - Template directory to scan
- **Apply Changes**: `${input:apply:false}` - Apply correction plans (requires explicit confirmation)
- **Report Detail**: `${input:report_level:comprehensive}` - Report detail level (summary|detailed|comprehensive)

## Workflow

### 1. Environment Setup
- Verify tool installation at `/config/hestia/tools/lineage_guardian/`
- Check configuration in `hestia.toml` under `[automation.lineage_guardian]`
- Validate Python environment and dependencies
- Confirm template directory accessibility and scope

### 2. Graph Scanning Phase
Execute entity relationship discovery:

```bash
cd /config/hestia/tools/lineage_guardian
python lineage_guardian/graph_scanner.py \
  --output ./.artifacts/graph.json \
  --template-dir ${template_dir} \
  --verbose \
  --recursive
```

**Expected Output**: Entity relationship graph with source→target mappings

### 3. Lineage Validation Phase  
Validate declared vs actual entity relationships:

```bash
python lineage_guardian/lineage_validator.py \
  --graph-file ./.artifacts/graph.json \
  --output ./.artifacts/violations.json \
  --verbose \
  --check-bidirectional
```

**Expected Output**: Lineage violations and metadata inconsistencies

### 4. Correction Planning Phase
Generate non-destructive correction plans:

```bash
python lineage_guardian/lineage_corrector.py \
  --violations-file ./.artifacts/violations.json \
  --plan-dir ./.artifacts/_plan \
  --dry-run \
  --backup-before-modify
```

**Expected Output**: Correction plan files (no actual modifications)

### 5. Graph Integrity Check
Perform bidirectional consistency validation:

```bash
python lineage_guardian/graph_integrity_checker.py \
  --graph-file ./.artifacts/graph.json \
  --output ./.artifacts/integrity.json \
  --check-circular \
  --check-orphaned \
  --check-duplicates
```

**Expected Output**: Graph integrity analysis with health scores

### 6. Comprehensive Reporting
Generate actionable reports:

```bash
python lineage_guardian/lineage_report.py \
  --graph ./.artifacts/graph.json \
  --violations ./.artifacts/violations.json \
  --integrity ./.artifacts/integrity.json \
  --outdir ./.artifacts/report \
  --format markdown \
  --include-recommendations
```

**Expected Output**: Markdown reports with executive summaries and action items

### 7. Optional: Apply Corrections
If `apply=true` and corrections are approved:

```bash
# Re-run corrector without --dry-run flag
python lineage_guardian/lineage_corrector.py \
  --violations-file ./.artifacts/violations.json \
  --plan-dir ./.artifacts/_plan \
  --apply \
  --atomic-writes \
  --backup-before-modify
```

**Safety**: Only executes with explicit confirmation and backup creation

## Output Expectations

### Success Criteria
- All 5 pipeline components execute successfully
- Entity relationship graph generated with complete mappings  
- Lineage violations identified and categorized
- Correction plans generated (non-destructive by default)
- Graph integrity score calculated with recommendations
- Comprehensive report produced with actionable insights

### Report Structure
- **Executive Summary**: Health score, violation count, critical issues
- **Graph Analysis**: Entity relationship mappings and dependency chains
- **Violation Details**: Specific lineage inconsistencies with file locations
- **Integrity Assessment**: Circular dependencies, orphaned entities, duplicates
- **Action Plan**: Prioritized recommendations for lineage improvements
- **Technical Details**: File-level analysis and correction specifications

### Artifact Organization
```
.artifacts/
├── graph.json              # Entity relationship graph
├── violations.json         # Lineage validation violations  
├── integrity.json          # Graph integrity analysis
├── _plan/                 # Correction plan files (dry-run)
│   ├── {template_file}.plan.yaml
│   └── {template_file}.backup.yaml
└── report/                # Comprehensive reports
    ├── executive_summary.md
    ├── lineage_analysis.md
    ├── violations_detail.md
    └── action_plan.md
```

### Error Handling
If any component fails:
1. **Preserve artifacts** from successful components
2. **Generate partial report** with available data
3. **Identify failure point** and provide troubleshooting guidance
4. **Ensure no partial modifications** were applied to templates

## Quality Assurance

- [ ] Configuration loaded from `hestia.toml` successfully
- [ ] Template directory scanning completed without errors
- [ ] Entity relationship graph generated with proper mappings
- [ ] Lineage validation identified all inconsistencies
- [ ] Correction plans generated without modifying source files
- [ ] Graph integrity analysis completed with health scoring
- [ ] Comprehensive report generated with actionable recommendations
- [ ] All artifacts preserved under `.artifacts/` directory
- [ ] Safety guardrails prevented unintended modifications

## Safety Guardrails

- **Dry-run default**: All correction operations are non-destructive by default
- **Scope validation**: Operations restricted to `/config/domain/templates/` only
- **Backup creation**: Automatic backup before any file modifications
- **Atomic operations**: All file writes use atomic replace patterns
- **Rollback support**: Complete operation reversibility via backup restoration
- **Permission checks**: Verify write access before attempting corrections

## Integration Points

- **Configuration**: Sources settings from `[automation.lineage_guardian]` in `hestia.toml`
- **Template System**: Integrates with Home Assistant template structure
- **Entity Registry**: Validates against actual entity availability
- **Workspace Reports**: Generates reports compatible with workspace indexing
- **VS Code Tasks**: Can be triggered via task system or direct CLI execution
- **Health Monitoring**: Provides lineage health metrics for operational tracking

## Advanced Options

### CLI Wrapper Usage
For simplified execution:

```bash
cd /config/hestia/tools/lineage_guardian  
python lineage_guardian_cli.py \
  --mode ${mode} \
  --template-dir ${template_dir} \
  --verbose \
  ${apply == 'true' ? '--apply' : '--dry-run'}
```

### VS Code Task Integration
Use workspace tasks for integrated execution:
- **"Lineage Guardian: Full Pipeline (dry-run)"**
- **"Lineage Guardian: Scanner Only"**
- **"Lineage Guardian: Open Documentation"**

### Component-Specific Execution
Run individual components for targeted analysis:
- **Scanner**: Entity relationship discovery only
- **Validator**: Lineage violation identification only  
- **Corrector**: Correction plan generation only
- **Integrity**: Graph consistency analysis only
- **Reporter**: Report generation from existing artifacts

## Related Resources

- **Tool Directory**: `/config/hestia/tools/lineage_guardian/`
- **Configuration**: `/config/hestia/config/system/hestia.toml` → `[automation.lineage_guardian]`
- **CLI Wrapper**: `lineage_guardian_cli.py`
- **Documentation**: `/config/hestia/library/docs/guides/development/lineage_guardian_copilot_guide.md`
- **VS Code Tasks**: Integrated workspace task definitions
- **Template Directory**: `/config/domain/templates/` (scan target)