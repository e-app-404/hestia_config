# Enhanced Governance Index System

The enhanced governance index system provides comprehensive, intelligent cataloging of Architecture Decision Records (ADRs) with improved metadata extraction, decision summaries, and dynamic hot rules generation.

## Key Improvements Over Previous Version

### 🔍 **Enhanced Title Extraction**

- **Multi-pattern matching**: Tries YAML frontmatter, ADR-prefixed headers, and smart filename parsing
- **Quality filtering**: Avoids poor titles like "1. Context" or path fragments
- **Consistent formatting**: Normalizes ADR numbering and spacing

### 📊 **Rich Statistics & Metadata**

- **Status breakdown**: Counts by Accepted, Proposed, Draft, Pending, Superseded
- **Temporal analysis**: ADRs by year with recency indicators
- **Deprecated tracking**: Separate count and identification of deprecated ADRs
- **Priority scoring**: Algorithm-based ranking by status, recency, and importance

### 🚨 **Dynamic Hot Rules Generation**

- **Smart selection**: Automatically identifies most critical governance rules
- **Context-aware**: Prioritizes recent ADRs affecting paths, mounts, and file writing
- **Relevance scoring**: Uses keyword analysis and ADR interconnections

### 🎯 **Improved Decision Extraction**

- **Multi-pattern search**: Finds decision content in various markdown formats
- **Content quality**: Extracts meaningful summaries instead of "(see file)" placeholders
- **Length optimization**: Truncates long decisions with ellipsis for readability

### 🔗 **Supersession Tracking**

- **Relationship mapping**: Tracks which ADRs supersede others
- **Dependency analysis**: Identifies deprecated ADRs and their replacements
- **Cross-references**: Enhanced tag extraction and ADR interconnection analysis

## Generated Outputs

### Enhanced JSON Structure (`/config/.workspace/governance_index.json`)

```json
{
  "governance_index": {
    "version": 2,
    "generated_at": "2025-10-15T12:16:09",
    "total_adrs": 28,
    "statistics": {
      "by_status": {"Accepted": 21, "Proposed": 2, "Draft": 1, "Pending": 1, "Superseded": 3},
      "by_year": {"2025": 28},
      "deprecated_count": 3
    },
    "hot_rules": [
      "ADR-0024: Single canonical config mount → `/config` only; no dual SMB mounts.",
      "ADR-0022: Mount management via LaunchAgent; preflight before writes.",
      "ADR-0018: Workspace lifecycle policies with backup patterns and hygiene.",
      "Path contracts: prefer container paths over host aliases; avoid `/Volumes/...` in tooling."
    ],
    "adrs": [...]
  }
}
```

### Enhanced Markdown Format (`/config/.workspace/governance_index.md`)

**New structure includes:**

- **Index Statistics**: Total ADRs, active count, deprecated count, status breakdown
- **Critical Governance Rules**: Dynamically generated hot rules for AI agents
- **Organized ADR Catalog**: Grouped by status (Active, Proposed, Draft, Superseded)
- **Rich Metadata**: Dates, decisions, references, supersession relationships

## Current Statistics (October 2025)

- **Total ADRs**: 28
- **Active ADRs**: 25 (Accepted/Implemented)
- **Deprecated ADRs**: 3 (in deprecated/ folder or superseded)
- **Status Distribution**:
  - Accepted: 21 ADRs
  - Proposed: 2 ADRs
  - Draft: 1 ADR
  - Pending: 1 ADR
  - Superseded: 3 ADRs

## Enhanced Features

### 🎯 **Priority Algorithm**

```python
priority = base_priority + recency_bonus
- Accepted/Implemented: +3 points
- Proposed: +2 points
- Superseded: -1 points
- Recent (2025-10+): +1 bonus
```

### 🔥 **Hot Rules Generation**

The system automatically identifies critical rules by:

1. **Keyword analysis**: "mount", "path", "config", "governance", "file writing"
2. **Status importance**: Prioritizes Accepted/Implemented ADRs
3. **Recency weighting**: Recent ADRs get higher visibility
4. **Cross-reference density**: ADRs referenced by many others get priority

### 📋 **Enhanced ADR Entry Format**

Each ADR now includes:

- **Title**: Cleaned and normalized from multiple sources
- **Status**: Normalized (e.g., "Proposed (Ready to adopt)" → "Proposed")
- **Date**: Extracted from frontmatter or content
- **Decision**: Meaningful 200-char summary when available
- **References**: All ADR cross-references found in content
- **Supersession**: What it supersedes and what supersedes it
- **Priority**: Algorithmic ranking for importance

## Usage Examples

### Command Line

```bash
# Generate enhanced index
python3 /config/bin/adr-index.py

# Quick statistics
jq '.governance_index.statistics' /config/.workspace/governance_index.json

# Hot rules for AI context
jq -r '.governance_index.hot_rules[]' /config/.workspace/governance_index.json
```

### Programmatic Access

```python
import json

with open('/config/.workspace/governance_index.json') as f:
    index = json.load(f)

# Get all active ADRs
active_adrs = [adr for adr in index['governance_index']['adrs']
               if not adr['is_deprecated'] and adr['status'] == 'Accepted']

# Find high-priority recent ADRs
recent_critical = [adr for adr in index['governance_index']['adrs']
                   if adr['priority'] >= 3 and adr['date'] >= '2025-10']
```

### AI Agent Integration

The hot rules are specifically designed for AI agents and tools:

```markdown
**AI agents and tools must honor these hot rules:**

- ADR-0024: Single canonical config mount → `/config` only; no dual SMB mounts.
- ADR-0022: Mount management via LaunchAgent; preflight before writes.
- ADR-0018: Workspace lifecycle policies with backup patterns and hygiene.
- Path contracts: prefer container paths over host aliases; avoid `/Volumes/...` in tooling.
```

## Maintenance & Integration

### Automatic Updates

- **File watching**: VS Code tasks monitor ADR directory changes
- **Smart regeneration**: Only rebuilds when `.md` files in ADR directory change
- **Backup preservation**: Previous indexes available via git history

### Quality Assurance

- **Title validation**: Rejects poor auto-generated titles
- **Content verification**: Ensures decision summaries add value
- **Relationship validation**: Verifies supersession claims are bidirectional
- **Statistics consistency**: Cross-checks counts and classifications

### Cross-System Integration

- **Knowledge Base Index**: References governance documentation
- **Configuration Index**: Governance rules inform config validation
- **VS Code Tasks**: Integrated with workspace automation workflows

## Future Enhancements

### Planned Improvements

- **Semantic clustering**: Group related ADRs by topic/domain
- **Impact analysis**: Track which ADRs affect specific systems
- **Validation rules**: Automated checks for ADR formatting compliance
- **Visual timeline**: Generate chronological ADR adoption charts
- **Dependency graphs**: Visual representation of ADR supersession chains

### Integration Opportunities

- **CI/CD hooks**: Validate ADR references in pull requests
- **Documentation links**: Auto-link ADR references in other documentation
- **Change impact**: Alert when modifications affect referenced ADRs
- **Compliance reporting**: Track governance rule adherence across codebase

This enhanced system transforms the governance index from a simple catalog into an intelligent, dynamic knowledge management system that actively supports development workflows and AI-assisted operations.
