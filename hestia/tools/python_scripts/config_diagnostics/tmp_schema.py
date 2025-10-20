#!/usr/bin/env python3
import os,sys,json,re

cfg = '/config/configuration.yaml'
data = {
    'configuration_exists': os.path.exists(cfg), 
    'includes': [], 
    'packages': [],
    'shell_commands': []
}

def norm(p): 
    if not p: return p
    return p if p.startswith('/config') else os.path.join('/config', p).replace('//', '/')

if os.path.exists(cfg):
    try:
        txt = open(cfg).read()
        # Find include patterns
        inc = re.findall(r'!include(?:_dir(?:_merge_(?:named|list)|_list|_named))?\s+([^\n#]+)', txt)
        data['includes'] = [norm(i.strip()) for i in inc]
        
        # Look for packages dir
        if 'packages:' in txt and '!include_dir_named packages' in txt:
            data['packages'] = ['packages directory (auto-loaded)']
            
        # Find shell_command references
        shell_refs = re.findall(r'shell_command\.(\w+)', txt)
        data['shell_commands'] = shell_refs
        
    except Exception as e:
        data['error'] = str(e)

# Check for non-canonical includes
violations = [p for p in data.get('includes', []) if p and not p.startswith('/config')]
data['non_canonical_includes'] = violations

out = 'reports/checkpoints/CONFIG_DIAGNOSTICS/ha_schema_map.json'
with open(out, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Wrote {out}")