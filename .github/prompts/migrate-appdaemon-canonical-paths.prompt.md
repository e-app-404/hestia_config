---
description: "Migrate AppDaemon configurations to canonical /addon_configs paths and deprecate legacy /config/appdaemon directory"
mode: "agent"
tools: ["file_system", "workspace"]
model: "gpt-4"
---

# Migrate AppDaemon to Canonical /addon_configs Paths

## Mission

Execute a comprehensive migration of AppDaemon configurations from legacy `/config/appdaemon/` paths to the canonical `/Volumes/addon_configs/a0d7b954_appdaemon/` location, ensuring all references are updated and the legacy directory is properly deprecated.

## Context & Discovery

### Current State Analysis
- **Canonical Location**: `/Volumes/addon_configs/a0d7b954_appdaemon/` (AppDaemon add-on configuration)
- **Legacy Location**: `/config/appdaemon/` (deprecated workspace copy)
- **File Conflicts Discovered**:
  - `apps.yaml`: Legacy version (3 lines) vs Canonical version (full configuration)
  - `room_db_updater.py`: Legacy version (5,459 bytes, Oct 16) vs Canonical version (7,779 bytes, Oct 9)

### Workspace References
Internal references use: `/addon_configs/a0d7b954_appdaemon/` (relative to addon mount)
External references use: `/Volumes/addon_configs/a0d7b954_appdaemon/` (full macOS path)

## Scope & Preconditions

### Required Analysis
1. **File Version Comparison**: Compare all files between legacy and canonical locations
2. **Reference Audit**: Find all internal references to `/config/appdaemon/` paths
3. **Configuration Validation**: Ensure canonical versions are complete and functional
4. **ADR Compliance**: Update relevant ADRs to include addon_configs governance

### Prerequisites
- AppDaemon add-on must be stopped during file operations
- Backup existing configurations before migration
- Validate area_mapping.yaml accessibility from canonical location

## Inputs

Use these canonical path patterns:
- **Internal AppDaemon references**: `/config/` (container view)
- **Host system references**: `/Volumes/addon_configs/a0d7b954_appdaemon/`
- **Workspace documentation**: `/addon_configs/a0d7b954_appdaemon/` (relative)

## Workflow

### Phase 1: Discovery and Comparison
1. **Inventory Files**: List all files in both locations with sizes and timestamps
2. **Content Comparison**: Compare file contents to identify latest/complete versions
3. **Reference Audit**: Search entire workspace for `/config/appdaemon/` references
4. **Dependency Mapping**: Identify which files reference AppDaemon configurations

### Phase 2: File Migration and Synchronization
1. **Backup Creation**: Create timestamped backups of both locations
2. **Version Resolution**: For each conflicting file, determine authoritative version:
   - `apps.yaml`: Use canonical version (has full configuration)
   - `room_db_updater.py`: Use canonical version (larger, more recent maintenance)
3. **File Synchronization**: Ensure canonical location has latest complete versions
4. **Validation**: Verify all required files present in canonical location

### Phase 3: Reference Updates
1. **Configuration Files**: Update all references to use canonical paths
2. **Documentation**: Update appdaemon_index.yaml with correct path structure
3. **Package Files**: Update any package references to AppDaemon files
4. **Script References**: Update shell commands and automation scripts

### Phase 4: Legacy Directory Deprecation
1. **Deprecation Notice**: Create clear deprecation notice in legacy directory
2. **Symlink Creation**: Consider creating informational symlinks (if appropriate)
3. **Cleanup Schedule**: Set 2-week deprecation period as requested
4. **Documentation Updates**: Update all guides to reference canonical paths

### Phase 5: ADR Updates
1. **ADR-0028 Enhancement**: Add addon_configs volume governance to AppDaemon ADR
2. **Workspace ADR Update**: Document addon_configs integration in appropriate ADR
3. **Path Standards**: Define canonical path patterns for addon configurations
4. **Validation Tokens**: Establish guardrails for addon_configs interactions

## Output Expectations

### File Operations
- Canonical location contains all latest file versions
- Legacy directory contains clear deprecation notice
- All workspace references point to canonical paths
- Backup artifacts created with timestamps

### Documentation Updates
- `appdaemon_index.yaml` reflects correct path structure
- ADR-0028 includes addon_configs governance section
- Relevant workspace ADR updated with volume management
- Clear migration documentation for operators

### Validation Artifacts
- Comparison report showing file version decisions
- Reference audit report with all updates made
- Path validation checklist for future operations
- Rollback procedures documented

## Quality Assurance

### Pre-Migration Validation
- [ ] AppDaemon add-on status confirmed (should be stopped)
- [ ] Backup creation verified for both locations
- [ ] File comparison analysis completed
- [ ] Reference audit completed with update plan

### Migration Validation
- [ ] All files present in canonical location
- [ ] File permissions and ownership correct
- [ ] Configuration syntax validation passed
- [ ] No broken references remain in workspace

### Post-Migration Validation
- [ ] AppDaemon add-on starts successfully
- [ ] All API endpoints accessible
- [ ] Database connectivity confirmed
- [ ] room_db_updater app initializes properly

### Documentation Validation
- [ ] appdaemon_index.yaml paths updated and accurate
- [ ] ADR updates follow governance standards
- [ ] Deprecation notices clear and informative
- [ ] Migration artifacts properly archived

## Security & Risk Mitigation

### File Operation Safety
- Create comprehensive backups before any modifications
- Use atomic operations for file replacements
- Validate file integrity after operations
- Maintain rollback capability throughout process

### Configuration Integrity
- Validate YAML syntax after any configuration changes
- Test AppDaemon startup after file operations
- Verify API endpoint accessibility
- Confirm database connectivity

### Path Governance
- Establish clear validation tokens for addon_configs operations
- Document constraints and limitations for addon volume access
- Define approval requirements for addon configuration changes
- Create guardrails against unauthorized modifications

## Success Criteria

### Technical Success
- All AppDaemon files located in canonical `/Volumes/addon_configs/a0d7b954_appdaemon/`
- Zero broken references to `/config/appdaemon/` paths
- AppDaemon add-on starts and functions normally
- All API endpoints respond correctly

### Documentation Success
- appdaemon_index.yaml accurately reflects canonical structure
- ADR-0028 includes comprehensive addon_configs governance
- Clear deprecation path documented for legacy directory
- Migration artifacts properly catalogued

### Operational Success
- 2-week deprecation notice clearly communicated
- Rollback procedures tested and documented
- Future path standards established and documented
- Validation tokens defined for ongoing governance

## Failure Recovery

### Rollback Triggers
- AppDaemon fails to start after migration
- Critical configuration corruption detected
- Database connectivity lost
- API endpoints become inaccessible

### Recovery Procedures
- Restore from timestamped backups
- Revert reference updates systematically
- Validate system functionality after rollback
- Document lessons learned for future attempts

### Validation Commands
- `curl http://localhost:5050/api/appdaemon/room_db/health`
- Check AppDaemon logs for startup errors
- Verify database file accessibility
- Test room_db_updater functionality

This prompt ensures comprehensive migration while maintaining system stability and providing clear documentation of the canonical path structure going forward.