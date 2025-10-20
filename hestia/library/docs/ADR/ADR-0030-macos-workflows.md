---
id: GUIDE-0001
title: ADR-0030 macOS Finder Workflows - Implementation Guide
slug: adr-0030-macos-finder-workflows-implementation-guide
status: Reference
related:
- ADR-0030
- ADR-0009
supersedes: []
date: 2025-10-20
decision: Workspace maintenance, ops and procedures will go accompanied by the implementation of compliant macOS Finder workflows including architecture, logic patterns, modification procedures, and maintenance guidelines.
author: GitHub Copilot (Claude Sonnet 4)
tags: ["implementation", "workflows", "macos", "finder", "adr-0030", "automation", "governance", "documentation"]
last_updated: 2025-10-20
---

# ADR-0030 macOS Finder Workflows - Implementation Guide

## Table of Contents

1. [Overview](#1-overview)
2. [Workflow Architecture](#2-workflow-architecture)
3. [Implementation Logic](#3-implementation-logic)
4. [Individual Workflow Details](#4-individual-workflow-details)
5. [Modification Guide](#5-modification-guide)
6. [Testing & Debugging](#6-testing--debugging)
7. [Best Practices](#7-best-practices)
8. [Future Enhancements](#8-future-enhancements)
9. [References](#9-references)
10. [Token Block](#10-token-block)

## 1. Overview

This document explains how six macOS Automator workflows were created to enforce ADR-0030 workspace lifecycle policies directly from Finder. These workflows provide right-click context menu actions for proper file management according to the architectural decision record.

## 2. Workflow Architecture

### Core Structure
Each workflow follows the same basic pattern:

```
<WorkflowName>.workflow/
├── Contents/
│   ├── Info.plist          # Service registration & metadata
│   └── document.wflow      # Automator workflow definition
```

### Common Components

**1. Service Registration (Info.plist)**
- Registers workflow as Finder service
- Defines menu item name and context requirements
- Specifies input file types (`public.item`)

**2. Shell Script Action (document.wflow)**
- Single "Run Shell Script" action with bash scripts
- Input method: command line arguments (`inputMethod: 1`)
- Shell: `/bin/bash`
- Processes selected Finder items as `"$@"`

## 3. Implementation Logic

### Project Root Detection
All workflows use this pattern to find the project context:

```bash
current_dir="$PWD"
project_root=""

while [[ "$current_dir" != "/" ]]; do
    if [[ -d "$current_dir/.git" ]] || [[ -d "$current_dir/hestia" ]]; then
        project_root="$current_dir"
        break
    fi
    current_dir="$(dirname "$current_dir")"
done

if [[ -z "$project_root" ]]; then
    project_root="$PWD"
fi
```

**Logic:** Walks up directory tree looking for `.git` or `hestia` folders to establish workspace context.

### UTC Timestamp Generation
Consistent across all workflows:

```bash
utc_timestamp="$(date -u '+%Y%m%dT%H%M%SZ')"
```

**Format:** `YYYYMMDDTHHMMSSZ` (e.g., `20251020T143022Z`)

### User Interaction Patterns

**Simple Notifications:**
```bash
osascript -e "display notification \"Message\" with title \"Title\""
```

**User Input Dialogs:**
```bash
value=$(osascript -e 'display dialog "Prompt:" default answer "default"' 2>/dev/null | cut -d: -f3)
```

**Confirmation Dialogs:**
```bash
response=$(osascript -e 'display dialog "Question?" buttons {"No", "Yes"} default button "Yes"' 2>/dev/null)
if [[ "$response" == *"Yes"* ]]; then
    # proceed
fi
```

### macOS Metadata Exclusion
Standard tar exclusion pattern used in compression workflows:

```bash
tar -czf "$output" -C "$source_dir" \
    --exclude=".DS_Store" \
    --exclude=".__MACOSX" \
    --exclude=".Spotlight-V100" \
    --exclude=".Trashes" \
    --exclude=".fseventsd" \
    --exclude=".TemporaryItems" \
    --exclude=".VolumeIcon.icns" \
    --exclude="._*" \
    --exclude=".localized" \
    --exclude="desktop.ini" \
    --exclude="Thumbs.db" \
    "$item_name" 2>/dev/null
```

## 4. Individual Workflow Details

### 1. ADR Archive (`ADR Archive.workflow`)

**Purpose:** Smart archiving to correct ADR locations with user choice

**Key Logic:**
- Presents dialog with 4 destination options
- Maps choices to ADR directory structure
- Handles different naming conventions per destination
- Creates metadata for reports, updates indexes

**Destinations:**
- **Vault Backup:** `hestia/workspace/archive/vault/backups/` → `name.TIMESTAMP.bk`
- **Artifacts:** `artifacts/` → `name__TIMESTAMP__tag.tgz`
- **Reports:** `hestia/reports/YYYYMMDD/` → `TIMESTAMP__tool__name`
- **Quarantine:** `.quarantine/` → `reason__TIMESTAMP__name`

**Special Features:**
- Permission setting for backups (`chmod 0600`)
- Report metadata generation with frontmatter
- Index updates for reports (`_index.jsonl`)

### 2. ADR Backup (`ADR Backup.workflow`)

**Purpose:** In-place backups with proper ADR naming and TTL

**Key Logic:**
- Handles files and directories differently
- Files: direct copy with `.bk.TIMESTAMP` suffix
- Directories: tar.gz compression with metadata exclusion
- Sets secure permissions (0600) best-effort
- 7-day TTL notification

**Naming Pattern:**
```bash
# Files
backup_name="${name}.bk.${utc_timestamp}"

# Directories  
backup_name="${name}.bk.${utc_timestamp}.tar.gz"
```

### 3. ADR Bundle (`ADR Bundle.workflow`)

**Purpose:** Create reproducible release bundles with manifests

**Key Logic:**
- User prompts for bundle label and version tag
- Creates temporary staging directory
- Generates MANIFEST.json with metadata
- Creates SHA256SUMS for verification
- Uses metadata-free tar compression

**Bundle Structure:**
```
bundle/
├── MANIFEST.json
├── <selected-files>
└── ...
```

**MANIFEST.json Format:**
```json
{
    "bundle": "label__TIMESTAMP__tag.tgz",
    "created": "TIMESTAMP",
    "label": "label",
    "tag": "tag",
    "adr": "0030",
    "contents": ["file1", "file2"]
}
```

### 4. ADR Trash (`ADR Trash.workflow`)

**Purpose:** Safe deletion to `.trash/` with tracking

**Key Logic:**
- Confirmation dialog before deletion
- Timestamped naming for chronological order
- Creates trash log for tracking
- 14-day TTL notification

**Naming Pattern:**
```bash
trash_name="${utc_timestamp}__${name}"
```

**Tracking:**
- Creates `.trash_log` with entry metadata
- Handles naming conflicts with counters

### 5. ADR Report (`ADR Report.workflow`)

**Purpose:** Structured report generation with full metadata

**Key Logic:**
- User prompts for tool name and label
- Creates date-based directory structure
- Generates metadata files for each item
- Updates global report index
- Creates/updates "latest" symlink

**Directory Structure:**
```
hestia/reports/YYYYMMDD/TIMESTAMP__tool__label/
├── _batch.json
├── _meta_file1.txt
├── _meta_file2.txt
├── file1
└── file2
```

**Metadata Format:**
```bash
# Tool: tool_name
# Created: TIMESTAMP
# Batch: batch_id
# Source: /path/to/source
# ADR: 0030
# Type: file|directory
# Size: bytes
```

### 6. ADR Check (`ADR Check.workflow`)

**Purpose:** Policy compliance validation

**Key Logic:**
- Pattern matching against banned/warning lists
- Relative path calculation from project root
- Categorizes violations, warnings, and compliant files
- Optional detailed report generation

**Banned Patterns:**
```bash
banned_patterns=(
    "\.storage/"
    "\.venv"
    "deps/"
    "__pycache__"
    "\.mypy_cache"
    "\.DS_Store"
    "\.pytest_cache"
    "node_modules/"
    "\.env"
    "\.pem$"
    "\.key$"
    "\.token"
    "session"
)
```

**Warning Patterns:**
```bash
warning_patterns=(
    "\.bak$"
    "\.backup$"
    "\.old$"
)
```

## 5. Modification Guide

### Adding New Workflow

1. **Create Directory Structure:**
   ```bash
   mkdir -p "/Users/evertappels/Library/Services/New Workflow.workflow/Contents"
   ```

2. **Create Info.plist:**
   ```xml
   <!-- Copy from existing workflow and modify NSMenuItem/default -->
   ```

3. **Create document.wflow:**
   ```xml
   <!-- Copy from existing workflow and modify COMMAND_STRING -->
   ```

4. **Restart Services:**
   ```bash
   /System/Library/CoreServices/pbs -flush
   ```

### Modifying Existing Workflows

**Common Modifications:**

1. **Change Menu Name:**
   - Edit `Info.plist` → `NSServices[0].NSMenuItem.default`

2. **Modify Script Logic:**
   - Edit `document.wflow` → `actions[0].action.ActionParameters.COMMAND_STRING`

3. **Add New Destination:**
   - Add case to choice handling in archive workflow
   - Define new directory pattern and naming convention

4. **Modify Exclusion Patterns:**
   - Update `--exclude` flags in tar commands
   - Add new patterns to hygiene checker arrays

## 6. Testing & Debugging

### Testing Workflows

1. **Create Test Files:**
   ```bash
   touch /tmp/test1.txt /tmp/test2.log
   mkdir /tmp/test_dir
   ```

2. **Test in Finder:**
   - Select files
   - Right-click → Services → ADR [Workflow]
   - Verify output and notifications

3. **Check Output:**
   - Verify files appear in correct locations
   - Check naming conventions
   - Validate metadata files

### Debugging

**Common Issues:**
- **Services not appearing:** Run `pbs -flush` and restart Finder
- **Permission errors:** Check script permissions and target directories
- **Dialog failures:** Test osascript commands in Terminal
- **Path issues:** Verify project root detection logic

**Debug Script:**
```bash
# Add to beginning of workflow script
exec 2>/tmp/workflow_debug.log
set -x
```

## 7. Best Practices

1. **Error Handling:** Always check command return codes
2. **User Feedback:** Provide notifications for all operations
3. **Path Safety:** Use absolute paths and proper quoting
4. **Atomic Operations:** Use temporary files and `mv` for final placement
5. **Metadata:** Include comprehensive provenance information
6. **TTL Communication:** Always inform users of retention policies

## 8. Future Enhancements

**Potential Additions:**
- Bulk operations workflow for multiple directories
- Cleanup workflow for expired TTL items
- Migration workflow for legacy naming
- Integration with git hooks for pre-commit validation
- Compression level options for bundles
- Encryption options for sensitive backups

## 9. References

### File Locations

- **Workflows:** `~/Library/Services/`
- **Documentation:** `~/Library/Services/ADR-0030-Workflows-Documentation.md`
- **ADR Reference:** `/config/hestia/library/docs/ADR/ADR-0030-workspace-lifecycle-policy.md`

### Related Documents

- ADR-0030: Workspace hygiene, lifecycle & quarantine policy
- ADR-0009: ADR Governance, Redaction, and Formatting Policy

## 10. Token Block

```yaml
TOKEN_BLOCK:
  accepted:
    - WORKFLOW_IMPLEMENTATION_OK
    - ADR_0030_COMPLIANT
    - MACOS_FINDER_INTEGRATION
    - AUTOMATION_DOCUMENTED
    - MODIFICATION_GUIDE_COMPLETE
  produces:
    - FINDER_SERVICE_WORKFLOWS
    - ADR_COMPLIANT_FILE_OPERATIONS
    - WORKSPACE_HYGIENE_AUTOMATION
  requires:
    - ADR_0030_POLICY
    - MACOS_AUTOMATOR
    - BASH_SHELL_SUPPORT
  drift:
    - DRIFT: workflow_non_compliant
    - DRIFT: missing_metadata_generation
    - DRIFT: invalid_naming_convention
    - DRIFT: incomplete_error_handling
```
