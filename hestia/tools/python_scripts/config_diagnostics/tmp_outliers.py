#!/usr/bin/env python3
import os,sys,re,json

patterns = [
    (re.compile(r'\.egg-info(/|$)'), 'egg_info', '/config/hestia/workspace/cache/python/'),
    (re.compile(r'\.bak'), 'backup', '/config/hestia/workspace/archive/backups/<ISO_WEEK>/'),
    (re.compile(r'\.tar\.gz$'), 'tarball', '/config/hestia/workspace/archive/tarballs/<ISO_WEEK>/'),
    (re.compile(r'^/config/tools/'), 'legacy_tools', '/config/hestia/tools/'),
    (re.compile(r'^/config/(build\.yaml|mypy\.ini)$'), 'bb8_bleed', '/config/hestia/workspace/archive/bleedthrough/<TS>/'),
    (re.compile(r'/bb8|beep_boop|mqtt_dispatcher|bridge_controller'), 'bb8_ref', 'review_for_relocation'),
    (re.compile(r'^/config/tmp/'), 'tmp', '(managed by utility)'),
    (re.compile(r'^/config/\.trash/'), 'trash', '(managed by utility)')
]

def classify(p):
    for rx, why, target in patterns:
        if rx.search(p): 
            return why, target
    return None, None

out = 'reports/checkpoints/CONFIG_DIAGNOSTICS/config_outliers.ndjson'
count = 0

with open(out, 'w') as f:
    for dp, _, fn in os.walk('/config'):
        for n in fn:
            p = os.path.join(dp, n)
            why, target = classify(p)
            if why:
                f.write(json.dumps({
                    'path': p,
                    'pattern_hit': why,
                    'why_suspect': why,
                    'suggested_canonical_target': target
                }) + '\n')
                count += 1

print(f"Wrote {out} ({count} outliers)")