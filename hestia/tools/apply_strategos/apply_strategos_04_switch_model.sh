#!/usr/bin/env bash
set -euo pipefail
source /Volumes/HA/config/hestia/tools/apply_strategos_00_env.sh >/dev/null

OUT_SWITCH="${OUT_DIR}/merged/switch"
mkdir -p "${OUT_SWITCH}"

/Volumes/HA/config/.venv/bin/python3 - <<'PY'
import os, csv, yaml, json
from pathlib import Path

env={}
with open(os.environ["OUT_DIR"]+"/.env.meta") as f:
 for line in f:
  if "=" in line:
   k,v=line.strip().split("=",1); env[k]=v

OUT_SWITCH = Path(env["OUT_DIR"])/"merged"/"switch"
OUT_SWITCH.mkdir(parents=True, exist_ok=True)

switch_conf = {
"management": {"vlan":1,"ip":"192.168.0.254/24","gateway":"192.168.0.1"},
"system": {"device":"netgear_gs724t_v3","lacp":"disabled"},
"vlans": [{"vlan_id":1,"name":"default","role":"mgmt","ip_subnet":"192.168.0.0/24"}],
"ports":[]
}
for i in range(1,25):
 switch_conf["ports"].append({
  "port": i, "mode":"access", "pvid":1, "tagged":[], "untagged":[1],
  "lacp_group": None,
  "description": "Uplink to Router (TP-Link AX53)" if i==1 else "Unassigned"
 })

(OUT_SWITCH/"switch.conf").write_text(yaml.safe_dump(switch_conf, sort_keys=True, allow_unicode=True), encoding="utf-8")
(OUT_SWITCH/"vlans.conf").write_text(yaml.safe_dump([{"vlan_id":1,"name":"default","ip_subnet":"192.168.0.0/24","role":"mgmt"}], sort_keys=True, allow_unicode=True), encoding="utf-8")
with open(OUT_SWITCH/"ports.csv","w", newline="", encoding="utf-8") as f:
 w=csv.writer(f); w.writerow(["port","mode","pvid","tagged","untagged","lag","description"])
 for p in switch_conf["ports"]:
  w.writerow([p["port"],p["mode"],p["pvid"],"|".join(map(str,p["tagged"])), "|".join(map(str,p["untagged"])), p["lacp_group"] or "", p["description"]])
(OUT_SWITCH/"acls.conf").write_text("# nonen", encoding="utf-8")

# Validation gates

errors=[]
for p in switch_conf["ports"]:
 if p["mode"]=="access":
  if p["untagged"]!=[1] or p["pvid"]!=1: errors.append(f"port {p['port']}: access must be untagged [1], pvid=1")
if errors:
 raise SystemExit("BLOCKED: VALIDATION -> switch_model: " + "; ".join(errors))
PY