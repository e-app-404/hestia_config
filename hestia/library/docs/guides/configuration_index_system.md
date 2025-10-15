# Configuration Index System

This system automatically indexes configuration files across the Hestia configuration workspace to provide searchable catalogs of devices, network, system, and other configuration artifacts.

## Overview

The configuration indexer scans `/config/hestia/config/` recursively for configuration files, excluding the `/config/hestia/config/index/` directory itself to avoid circular references.

**Supported file formats:**

- `.conf` - Configuration files (various formats)
- `.yaml`/`.yml` - YAML configuration files
- `.toml` - TOML configuration files
- `.ini` - INI configuration files

## Directory Structure & Categories

Configuration files are automatically categorized based on their directory location:

- **`devices/`** - Hardware device integrations and configurations
- **`diagnostics/`** - Monitoring, health checks, and diagnostic configurations
- **`network/`** - Network infrastructure and connectivity configs
- **`preferences/`** - User interface and system preference configurations
- **`preview/`** - Generated configuration previews (non-runtime)
- **`registry/`** - Index files and entity registries
- **`storage/`** - Storage backend and data persistence configurations
- **`system/`** - System-level and cross-component configurations

## Generated Outputs

### JSON Index (`/config/.workspace/config_index.json`)

Machine-readable index with complete metadata:

- File paths and categorization
- Content analysis (format detection, size, line count)
- Metadata extraction (titles, descriptions, tags)
- Statistics by category and format
- Generated timestamp

### YAML Index (`/config/.workspace/config_index.yaml`)

YAML format of the same data (only generated if PyYAML is available)

### Markdown Index (`/config/.workspace/config_index.md`)

Human-readable catalog organized by category with:

- Configuration file titles and descriptions
- File paths for easy navigation
- Format identification (YAML, CONF, TOML, etc.)
- Tag summaries
- Category and format statistics

## Usage

### Command Line

```bash
# Run indexer directly
/config/bin/config-index

# Or use the full indexer script
python3 /config/bin/config-index.py
```

### VS Code Tasks

The indexer integrates with VS Code tasks (see `.vscode/tasks.json`):

- **Config Index: Refresh** - Manual index regeneration
- **Config Index: Watch and Refresh** - Automatic background monitoring
- **Config Index: Full Setup & Watch** - Combined setup task

### Automatic Updates

The watch task monitors `/config/hestia/config/` for changes to:

- `.conf` files
- `.yaml`/`.yml` files
- `.toml` files
- `.ini` files

When changes are detected (excluding `/index/` subdirectory), the index is automatically regenerated.

## Content Analysis

The indexer performs sophisticated content analysis:

### Format Detection

- **YAML**: Detects YAML content with proper parsing when PyYAML available
- **TOML**: Identifies TOML structure markers `[section]`
- **INI**: Detects key=value configuration patterns
- **Text**: Fallback for unrecognized formats

### Metadata Extraction

- **Titles**: From YAML frontmatter, comment headers, or filenames
- **Descriptions**: From purpose comments, YAML metadata, or content analysis
- **Tags**: From explicit tag fields, comments, categories, and formats
- **Statistics**: File size, word count, line count, modification dates

### Example Metadata Processing

For a file like `/config/hestia/config/devices/netgear.conf`:

- **Category**: `devices` (from directory)
- **Format**: `yaml` (detected from content)
- **Title**: Extracted from `# Netgear` comment or filename
- **Description**: From `# Purpose: Network switch management` comment
- **Tags**: `['devices', 'yaml', 'network']` (auto-generated)

## Integration with Other Systems

This configuration indexing system complements:

- **ADR Governance Index** (`/config/bin/adr-index.py`) - Architecture decisions
- **Knowledge Base Index** (`/config/bin/kb-index`) - Documentation and guides
- **VS Code Prompt Files** - Agent mode templates can reference indexed configs
- **Manifest System** - Provides data source for updating manifest.yaml

## File Structure

```
/config/
├── bin/
│   ├── config-index.py          # Main indexer script
│   └── config-index             # Quick wrapper script
├── .workspace/
│   ├── config_index.json        # JSON output
│   ├── config_index.yaml        # YAML output (if PyYAML available)
│   └── config_index.md          # Markdown output
├── hestia/config/               # Source directory (scanned)
│   ├── devices/                 # Device configurations
│   ├── diagnostics/             # Monitoring and health checks
│   ├── network/                 # Network infrastructure
│   ├── system/                  # System-level configs
│   └── ...                      # Other categories
└── .vscode/
    └── tasks.json               # VS Code task definitions
```

## Maintenance & Troubleshooting

### Dependencies

- **Python 3.x** - Required
- **PyYAML** - Optional (enables full YAML parsing and YAML output)

### Error Handling

- Graceful handling of unreadable files
- Format detection fallbacks for unknown content types
- Warning messages for parsing failures
- Continues processing even if individual files fail

### Manual Maintenance

```bash
# Refresh index manually
/config/bin/config-index

# Check generated files
ls -la /config/.workspace/config_index.*

# Validate JSON output
jq . /config/.workspace/config_index.json

# Monitor file changes (if needed)
find /config/hestia/config -name "*.conf" -o -name "*.yaml" -o -name "*.toml" | grep -v '/index/' | wc -l
```

## Current Statistics

As of the last generation:

- **Total Files**: 46 configuration files
- **Categories**: 8 categories (devices, diagnostics, network, preferences, preview, registry, storage, system)
- **Formats**: YAML (37), Unknown (8), TOML (1)
- **Largest Category**: Devices (13 files), Diagnostics (12 files)

## Examples

### Searching the Index

```bash
# Find device configurations
grep -i "devices" /config/.workspace/config_index.md

# Find network-related configs
jq '.hestia_config_index.artifacts.network[]' /config/.workspace/config_index.json

# Count files by category
jq '.hestia_config_index.statistics.by_category' /config/.workspace/config_index.json
```

### Using in Automation

```bash
# Get all YAML files in diagnostics category
jq -r '.hestia_config_index.artifacts.diagnostics[] | select(.file_format == "yaml") | .path' /config/.workspace/config_index.json

# Find files modified in last day
jq -r --arg date "$(date -d '1 day ago' -Iseconds)" '.hestia_config_index.artifacts[][] | select(.last_modified > $date) | .path' /config/.workspace/config_index.json
```

This system provides comprehensive, automatically-maintained indexing of the entire Hestia configuration space, enabling improved discoverability and systematic configuration management alongside the ADR governance and knowledge base indexing systems.
