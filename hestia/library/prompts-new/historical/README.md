# Historical Archive

Immutable time-series archive organized by ISO week.

## Directory Structure

```
historical/
├── 2025/
│   ├── Q1/                    # January-March
│   │   ├── isoweek01/         # First week of year
│   │   ├── isoweek02/
│   │   └── ...
│   ├── Q2/                    # April-June
│   │   ├── isoweek14/
│   │   ├── isoweek15/
│   │   └── ...
│   ├── Q3/                    # July-September
│   │   ├── isoweek27/
│   │   └── ...
│   └── Q4/                    # October-December
│       ├── isoweek40/
│       └── ...
└── legacy/                    # Pre-normalization artifacts
    ├── raw_imports/
    └── conversion_logs/
```

## Purpose

- **Immutable snapshots**: Preserve original files with timestamp context
- **Audit trail**: Track evolution and changes over time
- **Recovery**: Enable rollback to previous states if needed
- **Compliance**: Meet retention and governance requirements

## File Naming

Original filenames preserved with ISO week context:
- `isoweek{NN}-{original_name}.{ext}`
- Example: `isoweek42-batch1-audit_20250502_001.md`

## Archive Workflow

1. **Process files** through normalization pipeline
2. **Validate** normalized outputs in `catalog/`
3. **Move originals** to appropriate ISO week directory
4. **Maintain immutability** - no modifications to archived files

## ISO Week Reference

- Week 01: Early January (contains Jan 4th)
- Week 14: Early April (Q2 start)
- Week 27: Early July (Q3 start)  
- Week 40: Early October (Q4 start)
- Week 52/53: Late December

## Tools

Archive management handled by normalization pipeline tools in `/config/hestia/tools/prompt_prep/`