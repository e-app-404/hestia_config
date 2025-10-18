#!/usr/bin/env python3
"""
Simple consistency checker: compares IPv4s in tailscale_machines.topology.json with
network.conf.yaml `tailscale.ips` list.
Usage: python3 tools/check_tailscale_consistency.py
Note: moved from hestia/config/network/tools to hestia/tools/utils/audit to align with repo shape.
"""
import json
from pathlib import Path

import yaml

# update needed: JSON is now a TOML file tailscale.toml, but keep this script for now

BASE = Path(__file__).resolve().parents[1]
TOPO = BASE / 'tailscale_machines.topology.json'
NETCONF = BASE / 'network.conf.yaml'

if not TOPO.exists():
    print('Missing topology file:', TOPO)
    raise SystemExit(2)
if not NETCONF.exists():
    print('Missing network.conf.yaml:', NETCONF)
    raise SystemExit(2)

with open(TOPO) as f:
    topo = json.load(f)

with open(NETCONF) as f:
    net = yaml.safe_load(f)

# network.conf.yaml is an array at top-level per current file
# find tailscale.ips inside any top-level mapping
tailscale_ips_net = set()
if isinstance(net, list):
    for doc in net:
        if isinstance(doc, dict) and 'tailscale' in doc:
            ips = doc['tailscale'].get('ips') or []
            for ip in ips:
                tailscale_ips_net.add(ip)
else:
    if 'tailscale' in net:
        ips = net['tailscale'].get('ips') or []
        for ip in ips:
            tailscale_ips_net.add(ip)

# get ipv4 addresses from topology
topo_ips = set()
for d in topo:
    for ip in d.get('ipv4', []):
        topo_ips.add(ip)

print(f'Found {len(topo_ips)} ipv4 addresses in topology.json')
print(f'Found {len(tailscale_ips_net)} tailscale ips in network.conf.yaml')

only_in_topo = topo_ips - tailscale_ips_net
only_in_net = tailscale_ips_net - topo_ips

if not only_in_topo and not only_in_net:
    print('OK: no drift detected')
    raise SystemExit(0)

if only_in_topo:
    print('\nIPs present in tailscale_machines.topology.json but missing from network.conf.yaml:')
    for ip in sorted(only_in_topo):
        print('  -', ip)

if only_in_net:
    print('\nIPs present in network.conf.yaml but missing from tailscale_machines.topology.json:')
    for ip in sorted(only_in_net):
        print('  -', ip)

raise SystemExit(1)
