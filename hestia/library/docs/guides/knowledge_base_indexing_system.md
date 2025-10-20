# Knowledge Base Indexing System

This system automatically indexes documentation across the Hestia workspace to provide searchable catalogs of guides, playbooks, and Home Assistant implementation documentation.

## Overview

The knowledge base indexer scans the following directory structures:

- **Guides** (`/config/hestia/library/docs/guides`) - User-facing guides and tutorials
- **Playbooks** (`/config/hestia/library/docs/playbooks`) - Operational procedures and runbooks
- **HA Implementation** (`/config/hestia/library/ha_implementation/`) - Home Assistant technical documentation:
  - `addon/` - Add-on documentation
  - `automation/` - Automation guides and patterns
  - `hacs/` - Home Assistant Community Store documentation
  - `homeassistant/` - Core Home Assistant documentation
  - `integration/` - Integration-specific documentation
  - `vscode/` - VS Code and development tooling

## Generated Outputs

### JSON Index (`/config/.workspace/knowledge_base_index.json`)

Machine-readable index with complete metadata:

- Full document metadata (title, author, tags, etc.)
- File paths and relative paths
- Content analysis (word count, content type classification)
- Category statistics
- Generated timestamp

### Markdown Index (`/config/.workspace/knowledge_base_index.md`)

Human-readable catalog organized by category with:

- Document titles and descriptions
- File paths for easy navigation
- Content type classification
- Tag summaries
- Category statistics

## Usage

### Command Line

```bash
# Run indexer directly
/config/bin/kb-index

# Or use the full indexer script
python3 /config/bin/knowledge-base-index.py
```

### VS Code Tasks

The indexer integrates with VS Code tasks (see `.vscode/tasks.json`):

- **Knowledge Base: Refresh Index** - Manual index regeneration
- **Knowledge Base: Watch and Refresh Index** - Automatic background monitoring
- **Knowledge Base: Full Index & Watch** - Combined setup task

### Automatic Updates

The watch task monitors all knowledge base directories for changes to:

- `.md` files (Markdown)
- `.rst` files (reStructuredText)
- `.txt` files (Plain text)

When changes are detected, the index is automatically regenerated.

## Content Classification

Documents are automatically classified by content type:

- **Guide** - Tutorials and how-to documentation
- **Playbook** - Operational procedures
- **Blueprint** - Configuration templates
- **Integration** - Home Assistant integration docs
- **Automation** - Automation patterns and examples
- **Addon** - Add-on documentation
- **Documentation** - General documentation

## Metadata Extraction

The indexer extracts:

- **YAML Frontmatter** - Standard metadata fields
- **Titles** - From headers or filenames
- **Tags** - From frontmatter and hashtags in content
- **Summaries** - First meaningful paragraph
- **File Statistics** - Size, word count, modification dates

## Integration with Other Systems

This indexing system complements:

- **ADR Governance Index** (`/config/bin/adr-index.py`) - Architecture decision records
- **VS Code Prompt Files** - Agent mode templates can reference indexed content
- **Search Tools** - Provides structured data for semantic search

## File Structure

```
/config/
├── bin/
│   ├── knowledge-base-index.py    # Main indexer script
│   └── kb-index                   # Quick wrapper script
├── .workspace/
│   ├── knowledge_base_index.json  # JSON output
│   └── knowledge_base_index.md    # Markdown output
└── .vscode/
    └── tasks.json                 # VS Code task definitions
```

## Maintenance

The system is designed to be self-maintaining:

- Automatic file watching detects content changes
- Robust error handling for missing files or directories
- UTF-8 encoding support for international content
- Graceful handling of malformed frontmatter

For manual maintenance:

- Run `/config/bin/kb-index` to refresh indexes
- Check `/config/.workspace/knowledge_base_index.md` for completeness
- Monitor VS Code task output for any errors

## Examples

### Searching the Index

```bash
# Find integration docs
grep -i "integration" /config/.workspace/knowledge_base_index.md

# Find all MQTT-related content
grep -i "mqtt" /config/.workspace/knowledge_base_index.json
```

### Using in Prompt Files

Reference indexed content in VS Code prompt files:

```markdown
Analyze the Home Assistant integration documentation found in the knowledge base index at `/config/.workspace/knowledge_base_index.json` to identify relevant patterns.
```

This system provides a comprehensive, automatically-maintained catalog of the entire Hestia knowledge base for improved discoverability and systematic documentation management.
