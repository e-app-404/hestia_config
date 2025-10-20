# ADR System Architecture

**Document Version**: 1.0  
**Last Updated**: 2025-10-15  
**Status**: Active

## Overview

The ADR (Architecture Decision Record) System is a comprehensive, configuration-driven framework for managing architectural decisions within the Hestia workspace. The system implements clean architectural principles with clear separation of concerns between content processing, configuration management, and index rendering.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADR Management System                       │
├─────────────────────────────────────────────────────────────────┤
│ Content Processing Layer                                        │
│ ├─ frontmatter_update.py (Orchestrator)                        │
│ ├─ frontmatter-id.py (ID validation & generation)              │
│ ├─ frontmatter-title.py (Title normalization)                  │
│ ├─ frontmatter-slug.py (URL-safe slug generation)              │
│ ├─ frontmatter-status.py (Status validation)                   │
│ ├─ frontmatter-date.py (Date validation & formatting)          │
│ ├─ frontmatter-decision.py (Decision summary extraction)       │
│ ├─ frontmatter-related.py (Cross-reference management)         │
│ ├─ frontmatter-supersedes.py (Supersession tracking)           │
│ └─ frontmatter-last_updated.py (Timestamp management)          │
├─────────────────────────────────────────────────────────────────┤
│ Configuration Layer                                             │
│ └─ adr.toml (Meta-configuration & rendering specifications)    │
├─────────────────────────────────────────────────────────────────┤
│ Rendering Layer                                                 │
│ └─ adr-index.py (Configuration-driven governance index)        │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Content Processing Layer

#### Orchestrator (`frontmatter_update.py`)

- **Purpose**: Coordinates all field processors with dependency resolution
- **Responsibilities**:
  - Load meta-configuration from `adr.toml`
  - Execute field processors in dependency order
  - Handle field interdependencies and validation conflicts
  - Provide unified CLI interface for frontmatter operations
- **Key Features**:
  - Field dependency graph resolution
  - Batch processing across multiple ADR files
  - Rollback support for failed operations
  - Configuration-driven field validation

#### Field Processors (9 Individual Modules)

Each processor handles a specific frontmatter field with standardized interfaces:

**Common Interface Pattern**:

```python
def main():
    parser = argparse.ArgumentParser(description="Process {field_name} field")
    parser.add_argument("file_path", help="Path to ADR file")
    parser.add_argument("--value", help="New value for field")
    parser.add_argument("--validate-only", action="store_true")
    # Field-specific arguments...
```

**Individual Processors**:

| Processor                     | Purpose                        | Key Validation Rules                            |
| ----------------------------- | ------------------------------ | ----------------------------------------------- |
| `frontmatter-id.py`           | ADR ID validation & generation | Format: `ADR-NNNN`, uniqueness checks           |
| `frontmatter-title.py`        | Title normalization            | Length limits, format consistency               |
| `frontmatter-slug.py`         | URL-safe slug generation       | Lowercase, hyphen-separated, uniqueness         |
| `frontmatter-status.py`       | Status lifecycle validation    | Valid transitions, governance compliance        |
| `frontmatter-date.py`         | Date formatting & validation   | ISO 8601 format, chronological validation       |
| `frontmatter-decision.py`     | Decision summary extraction    | Content analysis, length limits                 |
| `frontmatter-related.py`      | Cross-reference management     | ADR ID validation, circular reference detection |
| `frontmatter-supersedes.py`   | Supersession tracking          | Lifecycle validation, bidirectional links       |
| `frontmatter-last_updated.py` | Timestamp management           | Automatic updates, change tracking              |

### 2. Configuration Layer (`adr.toml`)

The meta-configuration file defines all system behavior through structured sections:

#### Field Specifications

```toml
[fields.{field_name}]
type = "string|array|date"
required = true|false
validation_rules = [...]
dependencies = [...]
```

#### Rendering Configuration

```toml
[rendering.record.fields.{field_name}]
required = true|false
display_name = "Human-readable name"
max_length = 150
format = "array|date"
separator = ", "
```

#### Output Format Templates

```toml
[rendering.record.json]
sort_keys = false
indent_spaces = 2
preserve_field_order = true

[rendering.record.md]
title_format = "#### {id}: {title_clean}"
metadata_format = "**Status**: {status} | **Date**: {date}"
```

### 3. Rendering Layer (`adr-index.py`)

A pure, configuration-driven rendering engine that generates governance indexes.

#### Key Classes & Methods

**ADRIndexRenderer Class**:

```python
class ADRIndexRenderer:
    def __init__(self):
        self.config = self.load_config()
        self.rendering_config = self.config.get("rendering", {})
        self.field_configs = self.config.get("fields", {})

    def collect_adr_records(self) -> List[Dict]
    def render_json(self, records) -> str
    def render_markdown(self, records) -> str
```

#### Rendering Capabilities

- **JSON Output**: Structured metadata with configurable formatting
- **Markdown Output**: Human-readable governance index with:
  - Statistics section (ADR counts by status, year)
  - Critical governance rules (hot rules)
  - Categorized ADR catalog with metadata
- **Template-Based**: All formatting driven by configuration, no hardcoded presentation logic

## Data Flow

### 1. Content Processing Flow

```
ADR Files → Field Processors → Validated Frontmatter → Updated ADR Files
     ↑            ↑                    ↑                      ↓
Meta Config → Validation Rules → Dependency Resolution → File Updates
```

### 2. Index Generation Flow

```
ADR Files → Frontmatter Extraction → Record Building → Template Rendering → Output Files
     ↑              ↑                      ↑                ↑                ↓
Meta Config → Field Configs → Display Rules → Format Templates → JSON/MD
```

## Configuration-Driven Design

### Benefits

1. **Separation of Concerns**: Content processing completely separated from rendering
2. **Extensibility**: New fields added via configuration + processor implementation
3. **Consistency**: All display formatting controlled by single configuration source
4. **Maintainability**: Changes to presentation require only configuration updates
5. **Testability**: Each component can be tested independently

### Configuration Sections

#### Field Definitions (`[fields]`)

- Field types, validation rules, and requirements
- Cross-field dependencies and relationships
- Default values and transformation rules

#### Rendering Specifications (`[rendering]`)

- Display formatting for each field
- Output template definitions
- Layout and presentation rules

#### Integration Points (`[integration]`)

- Git hooks and automation triggers
- External system integration settings
- Validation and compliance checks

## File Locations

### Core System Files

```
/config/bin/adr-index.py                          # Rendering engine
/config/hestia/tools/adr/frontmatter_update.py    # Main orchestrator
/config/hestia/tools/adr/frontmatter-*.py         # Field processors (9 files)
/config/hestia/config/meta/adr.toml               # Meta-configuration
```

### Input/Output Locations

```
/config/hestia/library/docs/ADR/                  # ADR source files
/config/.workspace/governance_index.md            # Generated markdown index
/config/.workspace/governance_index.json          # Generated JSON index
```

## Usage Patterns

### Field Processing

```bash
# Process all fields for a single ADR
python /config/hestia/tools/adr/frontmatter_update.py ADR-0001-example.md

# Process specific field
python /config/hestia/tools/adr/frontmatter-title.py ADR-0001-example.md --value "New Title"

# Batch processing
python /config/hestia/tools/adr/frontmatter_update.py --all
```

### Index Generation

```bash
# Generate markdown governance index
python /config/bin/adr-index.py --format markdown

# Generate JSON output
python /config/bin/adr-index.py --format json --output custom_path.json
```

## Extension Points

### Adding New Fields

1. **Create Field Processor**: Implement `frontmatter-{field}.py` with standard interface
2. **Update Configuration**: Add field specification to `adr.toml`
3. **Define Display Rules**: Add rendering configuration for the field
4. **Update Dependencies**: Modify orchestrator if field dependencies exist

### Custom Rendering Formats

1. **Add Format Configuration**: Extend `[rendering.record.{format}]` in `adr.toml`
2. **Implement Renderer Method**: Add `render_{format}()` method to `ADRIndexRenderer`
3. **Update CLI**: Add format option to argument parser

### Integration Hooks

1. **Git Hooks**: Configure in `[integration]` section
2. **Validation Triggers**: Set up pre-commit validation
3. **External APIs**: Add integration points for external systems

## Quality Assurance

### Validation Layers

1. **Field-Level**: Each processor validates its specific field format and constraints
2. **Cross-Field**: Orchestrator validates dependencies and relationships
3. **System-Level**: Integration validation ensures consistency across ADRs

### Error Handling

- **Graceful Degradation**: System continues processing when individual validations fail
- **Rollback Support**: Failed operations can be reverted
- **Detailed Logging**: Comprehensive error reporting for debugging

### Testing Strategy

- **Unit Tests**: Each field processor tested independently
- **Integration Tests**: End-to-end workflow validation
- **Configuration Tests**: Meta-configuration parsing and validation

## Performance Considerations

### Optimization Features

- **Lazy Loading**: Configuration loaded once per session
- **Batch Processing**: Efficient handling of multiple ADR files
- **Template Caching**: Rendering templates parsed once and reused
- **Incremental Updates**: Only modified fields processed when possible

### Scalability

- **File System Efficiency**: Direct file I/O without intermediate databases
- **Memory Management**: Stream processing for large ADR collections
- **Parallel Processing**: Field processors can run independently where dependencies allow

## Governance Integration

### ADR Compliance

- **ADR-0009**: Follows ADR governance and formatting policies
- **ADR-0024**: Uses canonical `/config` paths throughout
- **ADR-0027**: Implements file writing governance with path enforcement

### Quality Gates

- **Frontmatter Validation**: All ADRs must have valid, complete frontmatter
- **Cross-Reference Integrity**: Related/supersedes fields must reference valid ADRs
- **Status Lifecycle**: Status transitions follow governance rules
- **Template Compliance**: Generated indexes follow standardized templates

## Future Enhancements

### Planned Features

- **Git Integration**: Automatic processing on commit hooks
- **API Endpoints**: REST API for external system integration
- **Visual Dashboard**: Web-based ADR governance dashboard
- **Analytics**: ADR metrics and governance health reporting

### Extension Opportunities

- **Custom Validators**: Plugin architecture for domain-specific validation
- **Export Formats**: Additional output formats (PDF, DocX, etc.)
- **Notification System**: Alerts for governance violations or status changes
- **Template Engine**: Advanced templating with conditional logic

---

**Maintainers**: Hestia Development Team  
**Review Cycle**: Quarterly  
**Next Review**: 2025-01-15
