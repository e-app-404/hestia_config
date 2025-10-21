---
id: DOCS-SWEEPER-002
title: "Hestia Backup Sweeper System README"
slug: sweeper-readme
version: 1.0
created: 2025-10-20
author: "e-app-404"
adrs: ["ADR-0018", "ADR-0024", "ADR-0027", "ADR-0008"]
installation: hestia/tools/sweeper
entrypoint: /config/hestia/tools/backup_sweeper.py
reporting: /config/hestia/reports
configuration: "/config/hestia/config/system/hestia.toml → [automation.sweeper]"
content_type: readme
last_updated: 2025-10-21
---

# Hestia Backup Sweeper System

Configuration-driven workspace lifecycle management for backup files with modular architecture and comprehensive reporting.

## Overview

The Hestia Backup Sweeper System implements ADR-0018 workspace lifecycle policies through a 5-component modular pipeline:

1. **index.py** - Workspace scanner and file discovery
2. **naming_convention.py** - Naming standards enforcement
3. **sweeper.py** - File lifecycle management with TTL cleanup
4. **vault_warden.py** - Vault retention management
5. **sweeper_report.py** - Comprehensive reporting

## Quick Start

```bash
# Run complete pipeline (production mode)
python /config/hestia/tools/backup_sweeper.py

# Preview what would be done (dry-run mode)
python /config/hestia/tools/backup_sweeper.py --dry-run

# Validate configuration and components
python /config/hestia/tools/backup_sweeper.py --validate-only
```

## Configuration

All behavior is controlled by `/config/hestia/config/system/hestia.toml`:

- **Retention Policies**: TTL rules for different file types
- **Naming Standards**: Canonical backup format enforcement
- **Scope Patterns**: File discovery and validation rules
- **Safety Settings**: Backup-before-modify, atomic operations
- **Performance**: Parallel processing, batch sizes
- **Error Handling**: Continue/stop modes, quarantine policies

## Component Usage

### Individual Components

Each component can be run independently for testing or specialized workflows:

```bash
# 1. File Discovery
python /config/hestia/tools/sweeper/index.py \
  --config=/config/hestia/config/system/hestia.toml \
  --dry-run

# 2. Naming Standardization
python /config/hestia/tools/sweeper/naming_convention.py \
  --config=/config/hestia/config/system/hestia.toml \
  --index-file=/path/to/index.log \
  --dry-run

# 3. TTL Cleanup
python /config/hestia/tools/sweeper/sweeper.py \
  --config=/config/hestia/config/system/hestia.toml \
  --index-file=/path/to/index.log \
  --dry-run

# 4. Vault Retention
python /config/hestia/tools/sweeper/vault_warden.py \
  --config=/config/hestia/config/system/hestia.toml \
  --index-file=/path/to/index.log \
  --verify-integrity \
  --dry-run

# 5. Comprehensive Reporting
python /config/hestia/tools/sweeper/sweeper_report.py \
  --config=/config/hestia/config/system/hestia.toml \
  --shared-log=/path/to/shared.log \
  --update-index
```

## Pipeline Flow

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│   index.py  │───▶│ naming_conv.py   │───▶│ sweeper.py  │
│             │    │                  │    │             │
│ Discovers   │    │ Standardizes     │    │ Applies TTL │
│ files and   │    │ backup names     │    │ cleanup     │
│ classifies  │    │ with guardrails  │    │ policies    │
└─────────────┘    └──────────────────┘    └─────────────┘
                                                   │
┌─────────────┐    ┌──────────────────┐           │
│sweeper_     │◀───│ vault_warden.py  │◀──────────┘
│report.py    │    │                  │
│             │    │ Manages vault    │
│ Generates   │    │ retention by     │
│ comprehensive│    │ basename groups  │
│ reports     │    │                  │
└─────────────┘    └──────────────────┘
```

## Key Features

### Safety & Guardrails

- **Scope Validation**: Files must be within configured paths
- **Regex Guardrails**: Prevent accidental renames outside pattern
- **Backup-Before-Modify**: Safety copies before any changes
- **Atomic Operations**: Transaction-safe file operations
- **Error Recovery**: Configurable error handling with rollback

### Performance

- **Parallel Processing**: Configurable worker count and batch sizes
- **Memory Limits**: Configurable thresholds and warnings
- **Progress Logging**: Detailed operation tracking
- **Log Rotation**: Automatic cleanup of old logs

### Reporting & Compliance

- **Frontmatter Metadata**: Structured YAML+JSON log format
- **ADR Compliance**: Built-in adherence to governance decisions
- **Health Scoring**: Workspace health metrics (0-100 scale)
- **Recommendations**: Actionable improvement suggestions
- **Report Indexing**: Searchable report catalog

## Configuration Examples

### Basic TTL Policies

```toml
[retention]
in_place_backups = { ttl_days = 7, auto_prune = true }
trash = { ttl_days = 14, auto_prune = true }
vault_backups = { keep_latest = 5, auto_prune = true }
```

### Naming Rules

```toml
[automation.sweeper.naming_rules]
scope_validation_required = true
before_patterns = ["*.bak", "*.bak-*", "*_backup*"]
after_pattern = "{basename}.bk.{utc_timestamp}Z"
guardrail_regex = "^[a-zA-Z0-9._-]+\\.(bak|backup|restore)"
```

### Safety Settings

```toml
[safety]
atomic_writes = true
backup_before_modify = true
verify_checksums = true
rollback_on_failure = true
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Check file permissions and ownership
2. **Config Not Found**: Verify hestia.toml path and syntax
3. **Component Missing**: Run `--validate-only` to check components
4. **Scope Violations**: Review `scope_patterns` configuration
5. **TTL Not Working**: Check retention policy configuration

### Debug Mode

Enable verbose logging for debugging:

```toml
[automation.sweeper]
verbose_logging = true

[debug]
verbose_logging = true
trace_file_operations = true
```

### Log Locations

- **Shared Logs**: `/config/hestia/reports/{date}/sweeper__{timestamp}__cleanup.log`
- **Report Index**: `/config/hestia/reports/_index.jsonl`
- **Debug Output**: `/config/.trash/debug/` (if enabled)

## Integration

### Cron/Scheduled Execution

```bash
# Daily at 2:00 AM UTC (from hestia.toml maintenance schedule)
0 2 * * * /config/.venv/bin/python /config/hestia/tools/backup_sweeper.py
```

### CI/CD Integration

The sweeper integrates with CI/CD workflows for backup governance enforcement.

### Pre-commit Hooks

Individual components can be used in pre-commit hooks for validation.

## Architecture Decision Records

This system implements:

- **ADR-0018**: Workspace lifecycle policies with backup patterns and hygiene
- **ADR-0024**: Canonical config path (`/config` only, no dual SMB mounts)
- **ADR-0027**: File writing governance with atomic operations and safety

## Support

For issues or questions:

1. Check the comprehensive report for recommendations
2. Run with `--dry-run` to preview operations
3. Review configuration in `hestia.toml`
4. Check error logs in report location
5. Validate components with `--validate-only`
