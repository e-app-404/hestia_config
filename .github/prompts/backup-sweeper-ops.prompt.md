---
mode: "agent"
model: "GPT-4o"
description: "Execute complete Hestia Backup Sweeper pipeline with health reporting and compliance validation"
tools: ["runCommands", "runTasks", "edit", "search", "problems"]
---

# Hestia Backup Sweeper Operations

Execute the complete Backup Sweeper pipeline for workspace lifecycle management, backup cleanup, and compliance validation according to ADR-0018, ADR-0024, and ADR-0027.

## Mission

Run the end-to-end Backup Sweeper automation pipeline to:

1. **Scan workspace** for backup files and lifecycle violations
2. **Standardize naming** according to canonical patterns
3. **Execute cleanup** with TTL-based retention policies
4. **Manage vault** with keep-N-latest strategies
5. **Generate comprehensive reports** with health scoring and recommendations

## Scope & Preconditions

- **Configuration**: All settings sourced from `/config/hestia/config/system/hestia.toml`
- **Tool Location**: `/config/hestia/tools/backup_sweeper.py` (main orchestrator)
- **Components**: 5-component modular pipeline under `/config/hestia/tools/sweeper/`
- **Safety**: Atomic operations, backup-before-modify, dry-run validation
- **Compliance**: ADR-0024 canonical paths, ADR-0018 workspace lifecycle, ADR-0027 file governance

## Inputs

- **Mode**: `${input:mode:full}` - Operation mode (full|dry-run|validate-only)
- **Scope**: `${input:scope:workspace}` - Scan scope (workspace|specific-path)
- **Force**: `${input:force:false}` - Skip confirmation prompts
- **Report Level**: `${input:report_level:comprehensive}` - Report detail (summary|detailed|comprehensive)

## Workflow

### 1. Pre-flight Validation

- Verify `/config/hestia/config/system/hestia.toml` exists and is valid
- Check tool components under `/config/hestia/tools/sweeper/`
- Validate write permissions and canonical path compliance
- Confirm backup storage locations are accessible

### 2. Pipeline Execution

Execute the backup sweeper orchestrator with proper configuration:

```bash
cd /config
python hestia/tools/backup_sweeper.py \
  --config=/config/hestia/config/system/hestia.toml \
  ${mode == 'dry-run' ? '--dry-run' : ''} \
  ${mode == 'validate-only' ? '--validate-only' : ''} \
  --verbose
```

### 3. Component Analysis

Monitor each pipeline component:

- **index.py**: Workspace scanning and file discovery
- **naming_convention.py**: Naming standards enforcement
- **sweeper.py**: TTL-based cleanup execution
- **vault_warden.py**: Vault retention management
- **sweeper_report.py**: Health scoring and reporting

### 4. Report Review

Analyze generated reports:

- **Location**: `/config/hestia/reports/{YYYY-MM-DD}/sweeper__{timestamp}__cleanup.log`
- **Index**: `/config/hestia/reports/_index.jsonl`
- **Health Score**: Workspace health metrics (0-100)
- **Recommendations**: Actionable improvement suggestions

### 5. Validation & Monitoring

- Verify report index is updated
- Check health score trends
- Validate compliance with governance ADRs
- Confirm atomic operations completed successfully

## Output Expectations

### Success Criteria

- Pipeline completes all 5 components successfully
- Health report generated with current workspace score
- Report index updated with batch metadata
- No critical governance violations detected
- Backup operations follow atomic patterns

### Report Structure

- **Frontmatter**: Tool metadata, batch ID, compliance tracking
- **Executive Summary**: Health score, processed counts, recommendations
- **Component Results**: Per-component execution logs with metrics
- **Compliance Status**: ADR validation results and hot rule checking
- **Operational Insights**: Trend analysis and workspace improvement suggestions

### Failure Handling

If any component fails:

1. **Capture error logs** and component state
2. **Check rollback requirements** for any partial operations
3. **Generate failure report** with diagnostic information
4. **Provide recovery recommendations** for manual intervention

## Quality Assurance

- [ ] Configuration loaded successfully from `hestia.toml`
- [ ] All 5 pipeline components executed in sequence
- [ ] Report generated with proper frontmatter metadata
- [ ] Health score calculated and trended
- [ ] Compliance validation completed for hot ADRs
- [ ] Atomic operations verified (no partial states)
- [ ] Report index updated with batch entry
- [ ] Workspace health recommendations provided

## Safety Guardrails

- **Dry-run validation**: Always preview operations when `mode=dry-run`
- **Atomic operations**: Use backup-before-modify patterns per ADR-0027
- **Scope validation**: Restrict operations to approved workspace areas
- **Permission checks**: Verify write access before destructive operations
- **Rollback support**: Maintain operation reversibility via backup retention

## Integration Points

- **ADR Governance**: References `/config/.workspace/governance_index.md` for hot rules
- **Configuration**: Sources all settings from centralized `hestia.toml`
- **Reporting**: Integrates with workspace report indexing system
- **Task System**: Can be triggered via VS Code tasks or direct CLI execution
- **Health Monitoring**: Provides metrics for operational dashboard tracking

## Related Resources

- **Main Tool**: `/config/hestia/tools/backup_sweeper.py`
- **Configuration**: `/config/hestia/config/system/hestia.toml`
- **Component Directory**: `/config/hestia/tools/sweeper/`
- **Report Index**: `/config/hestia/reports/_index.jsonl`
- **ADR References**: ADR-0018 (lifecycle), ADR-0024 (paths), ADR-0027 (governance)
