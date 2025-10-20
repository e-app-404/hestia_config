#!/usr/bin/env python3
import os,sys,json,time,stat,pwd,grp

def categorize(p):
    if '/hestia/workspace/archive' in p: return 'workspace_archive'
    if '/hestia/workspace/cache' in p: return 'workspace_cache'  
    if '/hestia/tools' in p: return 'tools'
    if '/hestia/' in p: return 'hestia'
    if '/blueprints/' in p: return 'blueprints'
    if '/packages/' in p: return 'packages'
    if '/.storage' in p: return 'ha_core'
    if '/www' in p or '/tts' in p: return 'logs'
    if 'bb8' in p or 'beep_boop' in p: return 'bb8_bleed'
    if '/tmp' in p: return 'tmp'
    if '/.trash' in p: return 'trash'
    if p.endswith('.yaml') and p.count('/') <= 2: return 'ha_core'
    return 'unknown'

items = []
root = '/config'
max_depth = 5

print('Scanning /config directory...')
for dp, dn, fn in os.walk(root):
    if '/.storage' in dp: 
        dn[:] = []  # Don't descend into .storage
        continue
    depth = dp[len(root):].count(os.sep)
    if depth > max_depth: 
        dn[:] = []
        continue
    
    for name in dn + fn:
        p = os.path.join(dp, name)
        try:
            st = os.lstat(p)
            t = 'dir' if stat.S_ISDIR(st.st_mode) else 'file' if stat.S_ISREG(st.st_mode) else 'link'
            try: 
                owner = pwd.getpwuid(st.st_uid).pw_name
            except: 
                owner = str(st.st_uid)
            
            rec = {
                'path': p, 
                'type': t, 
                'size_bytes': st.st_size,
                'mtime_iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(st.st_mtime)),
                'owner': owner, 
                'mode_oct': oct(st.st_mode & 0o777), 
                'category': categorize(p),
                'reason': ''
            }
            items.append(rec)
        except OSError:
            continue

out = 'reports/checkpoints/CONFIG_DIAGNOSTICS/config_inventory.json'
with open(out, 'w') as f:
    json.dump(items, f, indent=2)

print(f"Wrote {out} ({len(items)} items)")