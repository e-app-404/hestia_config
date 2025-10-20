#!/usr/bin/env python3
import json,sys,collections,os,datetime

outdir = 'reports/checkpoints/CONFIG_DIAGNOSTICS'
md_file = os.path.join(outdir, 'CONFIG_DIAGNOSTICS_SUMMARY.md')

# Load inventory
inv = json.load(open(os.path.join(outdir, 'config_inventory.json')))
by_category = collections.Counter([i['category'] for i in inv])

# Load outliers
outliers = []
try:
    with open(os.path.join(outdir, 'config_outliers.ndjson')) as f:
        outliers = [json.loads(line) for line in f]
except:
    pass

# Generate summary
lines = [
    "# CONFIG DIAGNOSTICS SUMMARY",
    f"_Generated: {datetime.datetime.utcnow().isoformat()}Z_",
    f"_Total items scanned: {len(inv)}_",
    f"_Outliers detected: {len(outliers)}_",
    "",
    "## Counts by category"
]

for k, v in by_category.most_common():
    lines.append(f"- **{k}**: {v}")

lines.extend([
    "",
    "## Top 20 candidate misplacements"
])

for o in outliers[:20]:
    lines.append(f"- `{o['path']}` → `{o['suggested_canonical_target']}` _{o['pattern_hit']}_")

lines.extend([
    "",
    "## ADR-0024 Policy Analysis",
    "- **Config cleanliness**: Checking for build artifacts, backups, and non-HA files",
    "- **Canonical paths**: All includes should reference `/config/` prefixed paths", 
    "- **Workspace organization**: Tools, cache, and archives should be in proper hestia/ subdirectories",
    "",
    f"**Files requiring attention**: {len([o for o in outliers if o['pattern_hit'] in ['egg_info', 'backup', 'bb8_bleed']])}"
])

with open(md_file, 'w') as f:
    f.write('\n'.join(lines))

print(f"Wrote {md_file}")