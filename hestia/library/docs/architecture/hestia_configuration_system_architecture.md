---
id: hestia-configuration-system-architecture
title: Hestia Configuration System Architecture & Implementation Plan
slug: hestia-configuration-system-architecture-implementation-plan
status: Draft
date: 2025-10-15
last_updated: 2025-10-15
author: hestia-core
tags:
  - architecture
  - configuration
  - implementation
  - governance
compliance_adrs:
  - ADR-0018
  - ADR-0024
  - ADR-0027
implementation_priority: high
estimated_effort: 3-5 days
dependencies:
  - ADR system architecture
  - Backup sweeper automation
  - CI/CD guardrails
---

# Hestia Configuration System Architecture & Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for the Hestia Configuration System, a centralized configuration-driven approach to workspace lifecycle management, backup retention, and automation governance. The system implements ADR-0018 workspace lifecycle policies through a single source of truth configuration file.

## System Architecture

### Core Principles

1. **Single Source of Truth**: All system parameters defined in `/config/hestia/config/system/hestia.toml`
2. **Separation of Concerns**: Configuration vs. Logic vs. Implementation
3. **Configuration-Driven Automation**: All automation tools read from central config
4. **ADR Compliance**: Built-in adherence to governance decisions
5. **Environment Awareness**: Production, development, and CI/CD specific overrides

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hestia Configuration System                  │
├─────────────────────────────────────────────────────────────────┤
│ Configuration Layer (hestia.toml)                              │
│ ├─ System Parameters & Constants                               │
│ ├─ Path Definitions & Directory Structure                      │
│ ├─ Retention Policies & TTL Rules                             │
│ ├─ Automation Schedules & Triggers                            │
│ ├─ Validation Rules & Guardrails                              │
│ ├─ Security & Permission Settings                             │
│ └─ Environment & Feature Flags                                │
├─────────────────────────────────────────────────────────────────┤
│ Implementation Layer                                            │
│ ├─ Backup Sweeper Automation                                  │
│ ├─ CI/CD Enforcement Scripts                                  │
│ ├─ ADR System Integration                                     │
│ ├─ Report Generation & Cleanup                               │
│ ├─ Vault Management & Retention                              │
│ └─ Legacy Migration Tools                                     │
├─────────────────────────────────────────────────────────────────┤
│ Integration Layer                                               │
│ ├─ Git Hooks & Pre-commit Validation                         │
│ ├─ Cron Jobs & Scheduled Tasks                               │
│ ├─ CI/CD Pipeline Integration                                │
│ └─ Monitoring & Health Checks                                │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Structure

### Key Configuration Sections

#### 1. Meta Information (`[meta]`)

- **Purpose**: Version tracking, compliance documentation
- **Usage**: Tool compatibility checks, migration tracking
- **Key Fields**: `version`, `compliance_adrs`, `last_updated`

#### 2. Path Definitions (`[paths]`)

- **Purpose**: Canonical path definitions (ADR-0024)
- **Usage**: All tools use these paths, no hardcoding
- **Subsections**: `workspace`, `vault`, `gitignored`

#### 3. Backup Management (`[backup]`)

- **Purpose**: Backup file format, retention, locations
- **Usage**: Backup creation, migration, cleanup automation
- **Key Rules**: Canonical format, TTL policies, legacy detection

#### 4. File Naming (`[naming]`)

- **Purpose**: Consistent naming conventions across all tools
- **Usage**: Report generation, backup creation, bundle naming
- **Standards**: UTC timestamps, structured naming patterns

#### 5. Retention Policies (`[retention]`)

- **Purpose**: TTL rules for different file types
- **Usage**: Automated cleanup, storage management
- **Categories**: Backups, trash, vault, reports, quarantine, artifacts

#### 6. Automation Configuration (`[automation]`)

- **Purpose**: Sweeper scheduling, performance settings
- **Usage**: Cron job configuration, parallel processing
- **Features**: Error handling, logging, batch processing

#### 7. Validation Rules (`[validation]`)

- **Purpose**: File validation, CI/CD enforcement
- **Usage**: Pre-commit hooks, include-scan, guardrails
- **Rules**: Banned prefixes, file extensions, grace periods

#### 8. Security Settings (`[security]`)

- **Purpose**: File permissions, sensitive path protection
- **Usage**: File creation, vault management, quarantine
- **Controls**: Permission sets, access restrictions

#### 9. ADR Integration (`[adr]`)

- **Purpose**: ADR system configuration
- **Usage**: Frontmatter processing, index generation
- **Components**: Processors, validation rules, backup formats

#### 10. Performance & Monitoring (`[performance]`)

- **Purpose**: Resource limits, monitoring thresholds
- **Usage**: Performance optimization, health checks
- **Metrics**: File sizes, batch limits, processing times

## Implementation Plan

### Phase 1: Core Infrastructure (Days 1-2)

#### 1.1 Backup Sweeper Implementation

**File**: `/config/hestia/tools/backup_sweeper.py`

**Responsibilities**:

- Read configuration from `hestia.toml`
- Standardize legacy backup naming (`*.bak*` → `*.bk.YYYYMMDDTHHMMSSZ`)
- Implement TTL-based cleanup (7 days in-place, 14 days trash)
- Manage vault retention (keep latest N per basename)
- Generate cleanup reports with frontmatter metadata

**Key Functions**:

```python
class BackupSweeper:
    def __init__(self, config_path: str)
    def load_configuration(self) -> Dict
    def standardize_backup_names(self) -> None
    def cleanup_expired_backups(self) -> None
    def manage_vault_retention(self) -> None
    def generate_cleanup_report(self) -> None
```

#### 1.2 Configuration Validation Library

**File**: `/config/hestia/tools/lib/config_validator.py`

**Responsibilities**:

- Validate `hestia.toml` structure and values
- Ensure path existence and permissions
- Verify TTL configurations and date formats
- Check ADR compliance settings

#### 1.3 Fix ADR System Compliance

**Target**: `/config/hestia/tools/adr/frontmatter_update.py`

**Changes**:

- Update backup naming from `.bak-YYYYMMDD-HHMMSS` to `.bk.YYYYMMDDTHHMMSSZ`
- Read backup format from `hestia.toml`
- Add `--no-backup` option for CI usage

### Phase 2: CI/CD Integration (Day 2)

#### 2.1 Enhanced Include-Scan

**File**: `/config/.github/workflows/adr-0018-include-scan.yml`

**Enhancements**:

- Read banned prefixes from `hestia.toml`
- Dynamic grace period calculation
- Configuration-driven validation rules

#### 2.2 Pre-commit Hook System

**File**: `/config/.github/hooks/pre-commit`

**Features**:

- Configuration-driven validation
- Backup name standardization
- Sensitive file detection

### Phase 3: Automation & Scheduling (Day 3)

#### 3.1 Cron Integration

**File**: `/config/hestia/tools/cron/maintenance_scheduler.py`

**Responsibilities**:

- Read maintenance schedules from `hestia.toml`
- Execute daily/weekly/monthly tasks
- Log execution results

#### 3.2 Report Generation System

**File**: `/config/hestia/tools/reporting/report_manager.py`

**Features**:

- Configuration-driven report structure
- Metadata standardization
- TTL-based report cleanup

### Phase 4: Legacy Migration (Day 4)

#### 4.1 One-time Migration Tool

**File**: `/config/hestia/tools/migration/legacy_backup_migrator.py`

**Responsibilities**:

- Identify all legacy backup patterns
- Rename to canonical format
- Move vault backups to proper location
- Generate migration report

#### 4.2 Grace Period Management

**File**: `/config/hestia/tools/governance/grace_period_manager.py`

**Features**:

- Extend/manage grace periods
- Update allowlist configurations
- Generate compliance reports

### Phase 5: Monitoring & Health (Day 5)

#### 5.1 Health Check System

**File**: `/config/hestia/tools/monitoring/health_checker.py`

**Capabilities**:

- Configuration validation
- Disk usage monitoring
- Backup integrity checks
- Performance metrics

#### 5.2 Dashboard & Reporting

**File**: `/config/hestia/tools/dashboard/workspace_dashboard.py`

**Features**:

- Workspace health overview
- Retention policy compliance
- Automation execution status

## Configuration Usage Patterns

### Tool Implementation Pattern

```python
#!/usr/bin/env python3
import toml
from pathlib import Path

class ConfigurableTool:
    def __init__(self):
        self.config = self.load_config()
        self.paths = self.config['paths']
        self.retention = self.config['retention']
        # ... other config sections

    def load_config(self):
        config_path = Path('/config/hestia/config/system/hestia.toml')
        return toml.load(config_path)

    def get_backup_format(self):
        return self.config['backup']['canonical_format']

    def get_ttl_days(self, file_type):
        return self.config['retention'][file_type]['ttl_days']
```

### Separation of Concerns

#### ✅ Configuration Layer Responsibilities

- Define system constants and parameters
- Specify retention policies and TTL rules
- Set path definitions and directory structure
- Configure automation schedules and triggers
- Define validation rules and guardrails

#### ✅ Implementation Layer Responsibilities

- Read configuration from `hestia.toml`
- Implement business logic for specific functions
- Execute file operations based on config rules
- Generate reports with configured metadata
- Handle errors according to config policies

#### ❌ Anti-patterns (What NOT to do)

- **No hardcoded paths** in implementation scripts
- **No hardcoded TTL values** or retention policies
- **No duplicate configuration** across multiple files
- **No inline configuration** within implementation logic
- **No mixed concerns** (config + logic in same component)

## Implementation Dependencies

### Required Tools & Libraries

- **Python 3.10+**: For implementation scripts
- **toml library**: Configuration parsing
- **pathlib**: Path manipulation
- **datetime**: Timestamp handling
- **concurrent.futures**: Parallel processing
- **logging**: Structured logging

### Configuration Dependencies

1. **ADR System**: Must be updated for canonical backup format
2. **CI/CD Workflows**: Must read from configuration
3. **Git Hooks**: Must be configuration-driven
4. **Cron Jobs**: Must use maintenance schedules

## Migration Strategy

### Pre-Implementation Checklist

- [ ] Validate `hestia.toml` structure and syntax
- [ ] Test configuration loading in Python
- [ ] Verify all required directories exist
- [ ] Check current backup file count and patterns
- [ ] Identify CI/CD integration points

### Implementation Sequence

1. **Configuration Validation**: Ensure `hestia.toml` is correct
2. **Backup Sweeper**: Core cleanup automation
3. **ADR System Fix**: Update backup naming compliance
4. **CI/CD Integration**: Update workflows and hooks
5. **Legacy Migration**: One-time cleanup of existing backups
6. **Monitoring Setup**: Health checks and reporting

### Post-Implementation Validation

- [ ] All backup files use canonical naming
- [ ] TTL cleanup is functioning correctly
- [ ] CI/CD enforcement is active
- [ ] Vault retention is working
- [ ] Reports are being generated correctly

## Risk Assessment & Mitigation

### High Risk Items

1. **Data Loss**: Backup deletion automation
   - **Mitigation**: Extensive testing, staged rollout, backup-before-delete
2. **CI/CD Breakage**: Enforcement rule changes
   - **Mitigation**: Grace period, phased enforcement, rollback plan
3. **Performance Impact**: Large file operations
   - **Mitigation**: Parallel processing, batch limits, monitoring

### Medium Risk Items

1. **Configuration Errors**: Invalid `hestia.toml` syntax
   - **Mitigation**: Validation tools, CI checks, schema validation
2. **Permission Issues**: File access problems
   - **Mitigation**: Permission checks, error handling, logging

## Success Criteria

### Functional Requirements

- [ ] All 230+ backup files standardized to canonical format
- [ ] TTL-based cleanup removes expired files automatically
- [ ] CI/CD enforcement prevents non-compliant files
- [ ] Vault retention keeps latest N backups per basename
- [ ] Reports generated with proper frontmatter metadata

### Performance Requirements

- [ ] Backup sweeper completes in < 2 minutes
- [ ] CI/CD checks complete in < 30 seconds
- [ ] Memory usage stays under 512MB
- [ ] Parallel processing improves performance by 3x

### Compliance Requirements

- [ ] ADR-0018 workspace lifecycle policy fully implemented
- [ ] ADR-0024 canonical paths used throughout
- [ ] ADR-0027 file writing governance enforced
- [ ] Grace period management functional until 2025-10-27
- [ ] Legacy migration completed before enforcement

## Future Enhancements

### Planned Features (Q1 2026)

- **API Endpoints**: REST API for configuration management
- **Web Dashboard**: Visual workspace health monitoring
- **Advanced Deduplication**: Intelligent backup consolidation
- **Encrypted Vault**: Secure storage for sensitive backups

### Experimental Features

- **Compressed Backups**: Space optimization
- **Notification System**: Alert integration
- **Git Hook Automation**: Automatic configuration updates
- **Machine Learning**: Predictive cleanup optimization

---

**Implementation Status**: Draft  
**Next Review**: 2025-10-20  
**Implementation Target**: 2025-10-25  
**Compliance Deadline**: 2025-10-27 (Grace Period Expiry)
