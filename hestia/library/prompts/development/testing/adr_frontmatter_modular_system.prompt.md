---
mode: "agent"
model: "Claude Sonnet 4"
tools: ["edit", "search", "new", "runCommands", "usages", "problems", "changes"]
description: "Create a modular, field-specific ADR frontmatter management system with canonical validation and individual field processors"
---

# ADR Frontmatter Modular Management System

## Objective

Create a modular, maintainable system for ADR frontmatter management that separates concerns by field, provides canonical validation, and enables fine-grained control over frontmatter processing.

## System Architecture

### 1. Canonical Meta-Structure Definition

Create a comprehensive TOML-based meta-structure that defines:

- Field specifications with types and validation rules
- Normalization rules for each field
- Dependencies between fields
- Optional vs required field classifications

**Location**: `/config/hestia/config/meta/adr.toml`

### 2. Modular Field Processors

Individual Python scripts for each frontmatter field:

- `frontmatter-id.py` - ADR identifier validation and generation
- `frontmatter-title.py` - Title normalization and validation
- `frontmatter-slug.py` - Slug generation from titles
- `frontmatter-status.py` - Status lifecycle validation
- `frontmatter-related.py` - Cross-reference validation
- `frontmatter-supersedes.py` - Supersession relationship management
- `frontmatter-last_updated.py` - Date management and updates
- `frontmatter-date.py` - Creation date validation
- `frontmatter-decision.py` - Decision summary extraction

### 3. Orchestration Wrapper

A master `frontmatter-update.py` script that:

- Coordinates individual field processors
- Manages execution order and dependencies
- Provides unified CLI interface
- Handles backup and dry-run modes

## Implementation Requirements

### Phase 1: Meta-Structure Definition

#### TOML Schema Structure

```toml
[metadata]
version = "1.0"
description = "ADR Frontmatter Canonical Schema"
last_updated = "2025-10-15"

[fields.id]
type = "string"
required = true
pattern = "^ADR-\\d{4}$"
description = "Unique ADR identifier with zero-padded numbering"
validation = "regex"
normalization = "uppercase"
generation = "filename_based"

[fields.title]
type = "string"
required = true
min_length = 10
max_length = 200
description = "Full descriptive title including ADR-XXXX prefix"
validation = "length_and_format"
normalization = "trim_whitespace"
format = "ADR-XXXX: Descriptive Title"

[fields.slug]
type = "string"
required = true
pattern = "^[a-z0-9-]+$"
description = "Kebab-case slug derived from title"
validation = "regex"
normalization = "kebab_case"
generation = "title_derived"
dependencies = ["title"]

[fields.status]
type = "enum"
required = true
allowed_values = ["Draft", "Proposed", "Accepted", "Implemented", "Deprecated", "Superseded", "Rejected", "Withdrawn"]
description = "Lifecycle status of the ADR"
validation = "enum_check"
normalization = "capitalize_first"

[fields.related]
type = "array"
required = true
item_type = "string"
item_pattern = "^ADR-\\d{4}$"
description = "Array of related ADR references"
validation = "array_of_adr_refs"
normalization = "sort_and_dedupe"
default = []

[fields.supersedes]
type = "array"
required = true
item_type = "string"
item_pattern = "^ADR-\\d{4}$"
description = "Array of superseded ADR references"
validation = "array_of_adr_refs"
normalization = "sort_and_dedupe"
default = []

[fields.last_updated]
type = "date"
required = true
format = "YYYY-MM-DD"
description = "Last modification date in ISO-8601 format"
validation = "iso_date"
normalization = "iso_format"
auto_update = true

[fields.date]
type = "date"
required = true
format = "YYYY-MM-DD"
description = "Original creation/decision date in ISO-8601 format"
validation = "iso_date"
normalization = "iso_format"
immutable = true

[fields.decision]
type = "string"
required = true
min_length = 20
max_length = 300
description = "Brief summary of the architectural decision"
validation = "length_check"
normalization = "trim_and_sentence_case"
generation = "content_extraction"
dependencies = ["content"]

[processing]
field_order = ["id", "title", "slug", "status", "related", "supersedes", "last_updated", "date", "decision"]
backup_pattern = ".bk.{timestamp}"
dry_run_default = true
```

### Phase 2: Individual Field Processors

#### Common Interface Specification

Each `frontmatter-{field}.py` script must implement:

```python
#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - {FIELD}

Validates, normalizes, and updates the {field} field in ADR frontmatter.
"""

import argparse
import sys
from pathlib import Path

def validate_field(field_value, metadata, content=None):
    """Validate field according to meta-structure rules"""
    pass

def normalize_field(field_value, metadata):
    """Normalize field value according to rules"""
    pass

def generate_field(metadata, content, existing_frontmatter):
    """Generate field value if missing"""
    pass

def process_adr_file(file_path, dry_run=False, backup=False):
    """Process single ADR file for this field"""
    pass

def main():
    parser = argparse.ArgumentParser(description=f'Process {FIELD} field in ADR frontmatter')
    parser.add_argument('files', nargs='*', help='ADR files to process (default: all)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--backup', action='store_true', help='Create backup before changes')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, no changes')
    return process_files(args.files, args.dry_run, args.backup, args.validate_only)

if __name__ == '__main__':
    sys.exit(main())
```

#### Field-Specific Implementation Details

**frontmatter-id.py**:

- Extract ADR number from filename
- Validate format (ADR-XXXX)
- Ensure uniqueness across workspace
- Handle zero-padding normalization

**frontmatter-title.py**:

- Validate length constraints
- Check for ADR-XXXX prefix consistency
- Normalize whitespace and punctuation
- Validate descriptive content quality

**frontmatter-slug.py**:

- Generate from title automatically
- Validate kebab-case format
- Check for uniqueness
- Handle special character conversion

**frontmatter-status.py**:

- Validate against allowed lifecycle values
- Check status transition validity
- Normalize capitalization
- Warn on deprecated statuses

**frontmatter-related.py**:

- Validate ADR-XXXX reference format
- Check referenced ADRs exist
- Remove duplicates and sort
- Validate bidirectional relationships

**frontmatter-supersedes.py**:

- Validate supersession relationships
- Check for circular dependencies
- Update superseded ADRs with back-references
- Validate timeline consistency

**frontmatter-last_updated.py**:

- Auto-update to current date when content changes
- Validate ISO-8601 format
- Handle timezone normalization
- Track modification history

**frontmatter-date.py**:

- Validate creation date format
- Ensure immutability after first set
- Check chronological consistency
- Handle missing date inference

**frontmatter-decision.py**:

- Extract decision summary from content
- Validate length constraints
- Generate from ## Decision sections
- Handle decision evolution tracking

### Phase 3: Master Orchestrator

#### Enhanced `frontmatter-update.py` Wrapper

```python
#!/usr/bin/env python3
"""
ADR Frontmatter Update Orchestrator

Coordinates individual field processors for comprehensive ADR frontmatter management.
"""

import argparse
import concurrent.futures
import subprocess
import sys
from pathlib import Path
import toml

class FrontmatterOrchestrator:
    def __init__(self, meta_config_path):
        self.meta_config = toml.load(meta_config_path)
        self.field_order = self.meta_config['processing']['field_order']
        self.processors = {field: f"frontmatter-{field}.py" for field in self.field_order}

    def process_field(self, field, files, dry_run, backup):
        """Process single field across all files"""
        pass

    def process_files(self, files, dry_run, backup, parallel=False):
        """Coordinate processing across all fields"""
        pass

    def validate_dependencies(self):
        """Ensure all field processors are available"""
        pass

    def generate_report(self, results):
        """Generate comprehensive processing report"""
        pass

def main():
    parser = argparse.ArgumentParser(description='ADR Frontmatter Update Orchestrator')
    parser.add_argument('files', nargs='*', help='ADR files to process (default: all)')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--backup', action='store_true', help='Create backups before changes')
    parser.add_argument('--field', choices=FIELD_NAMES, help='Process only specific field')
    parser.add_argument('--parallel', action='store_true', help='Process fields in parallel')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, no changes')
    parser.add_argument('--report', action='store_true', help='Generate detailed processing report')

    orchestrator = FrontmatterOrchestrator('/config/hestia/config/meta/adr.toml')
    return orchestrator.run(args)
```

### Phase 4: Migration and Testing

#### Current Script Migration

1. **Backup Current Implementation**:

   ```bash
   timestamp=$(date +%Y%m%d-%H%M%S)
   mv /config/hestia/tools/adr/frontmatter_update.py \
      /config/hestia/tools/adr/frontmatter_update.py.back-$timestamp
   ```

2. **Validation Testing**:

   - Test each field processor independently
   - Validate against existing ADR corpus
   - Compare results with original implementation
   - Performance benchmarking

3. **Integration Testing**:
   - End-to-end workflow validation
   - Dependency resolution testing
   - Error handling and recovery
   - Backup and restore procedures

## Benefits of Modular Architecture

### Maintainability

- **Single Responsibility**: Each processor handles one field concern
- **Easier Debugging**: Isolate issues to specific field logic
- **Independent Updates**: Modify field logic without affecting others
- **Code Reusability**: Share common validation patterns

### Extensibility

- **New Fields**: Add processors without modifying core system
- **Custom Validation**: Field-specific business rules
- **Integration Points**: Easy connection with external systems
- **Plugin Architecture**: Support for custom field processors

### Reliability

- **Granular Testing**: Test individual field processors thoroughly
- **Fault Isolation**: Field processor failures don't affect others
- **Rollback Capability**: Restore individual field changes
- **Validation Pipeline**: Multi-stage validation reduces errors

### Performance

- **Parallel Processing**: Process independent fields concurrently
- **Selective Updates**: Update only changed fields
- **Caching**: Cache field validation results
- **Incremental Processing**: Skip unchanged files

## Quality Assurance

### Validation Requirements

1. **Schema Compliance**: All fields must conform to meta-structure
2. **Cross-Reference Integrity**: Related/supersedes fields must be valid
3. **Content Consistency**: Decision summaries must match content
4. **Format Standardization**: Consistent date, slug, and reference formats

### Testing Strategy

1. **Unit Tests**: Each field processor with comprehensive test cases
2. **Integration Tests**: Full workflow with realistic ADR corpus
3. **Regression Tests**: Ensure compatibility with existing ADRs
4. **Performance Tests**: Validate processing speed and memory usage

### Documentation Requirements

1. **Field Specifications**: Document each field's validation rules
2. **Processor APIs**: Interface documentation for each processor
3. **Usage Examples**: Common use cases and command patterns
4. **Troubleshooting Guide**: Common issues and solutions

## Success Criteria

1. **✅ Meta-Structure**: Complete TOML schema with all field specifications
2. **✅ Field Processors**: 9 individual field processors with common interface
3. **✅ Orchestrator**: Master wrapper with dependency management
4. **✅ Migration**: Current script backed up and new system operational
5. **✅ Validation**: 100% compatibility with existing ADR corpus
6. **✅ Performance**: Processing time comparable or better than monolithic approach
7. **✅ Documentation**: Complete usage and maintenance documentation

## Implementation Order

1. **Create canonical meta-structure** (`adr.toml`)
2. **Implement core field processors** (id, title, slug, status)
3. **Add relationship processors** (related, supersedes)
4. **Complete data processors** (dates, decision)
5. **Build orchestration wrapper**
6. **Migrate and test existing system**
7. **Generate comprehensive documentation**

Execute this systematically to create a robust, maintainable ADR frontmatter management system that leverages the standardized structure while providing granular control and validation capabilities.
