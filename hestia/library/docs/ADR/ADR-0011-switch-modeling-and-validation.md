---
id: ADR-0011
title: "Switch Modeling & Validation (Netgear GS724T v3 and Similar)"
date: 2025-09-12
status: Approved
tags:
  [
    "networking",
    "switch",
    "modeling",
    "validation",
    "netgear",
    "vlan",
    "lag",
    "stp",
    "acl",
    "snmp",
  ]
author:
  - "Platform / Home-Ops"
  - "GitHub Copilot (assisted)"
related: []
supersedes: []
last_updated: 2025-09-12
decision: "Adopt a canonical **Switch Model** with deterministic artifacts and strict validation. Treat the Netgear backup as the source of truth, transformed into normalized outputs."
---

# ADR-0011: Switch Modeling & Validation (Netgear GS724T v3 and Similar)

## Context

We intake Netgear managed switch configs (XML/CFG) and must emit a canonical, human-readable model plus machine-verifiable artifacts. Risks include management lockout during VLAN migration, inconsistent PVIDs, and orphan VLANs.

## Decision

Adopt a canonical **Switch Model** with deterministic artifacts and strict validation. Treat the Netgear backup as the source of truth, transformed into normalized outputs:

1. `switch.conf` — human-readable summary (sections: management, vlans, ports, lags, stp, acls).
2. `vlans.conf` — VLAN table:
   ```yaml
   vlans:
     - vlan_id: 1
       name: default
       role: default
       subnet: null # optional
       notes: ""
   ```
3. `ports.csv` — per-port mapping with columns:

```pgsql
port,mode,pvid,tagged,untagged,lag,description
1,trunk,1,"[10,20]","[]",,Uplink to Router
2,access,10,"[]","[10]",,Office PC
```

4. `acls.conf` — normalized ACLs (if present), one rule per line:

```
rule_id,action,src_network,dst_network,proto,src_port,dst_port,notes
```

5. `stp.conf` — (optional) STP parameters if backed up.

6. Relationship graph enrichment (outside `switch/`):

Extend `graph/relationships.graph.json` with node types `vlan`, `port` and edges `tagged_on`, `untagged_on`, `members`, `connected_to`.

### Transform Rules (Backup → Model)

- Parse XML/CFG; ignore volatile attributes (timestamps, sessions).
- Normalize names (trim, collapse spaces), VLAN names lowercased except acronyms.
- Ports use numeric indices as canonical keys; descriptions preserved.
- LAGs: create a lag ID and map member ports under members.

## Validation Gates

### VLANs

- `vlan_id` integer 1–4094; IDs unique
- Name non-empty; default VLAN must exist and be identified
- No orphan VLANs (referenced by ports/LAGs but undefined)

### Ports

- **Common**: mode ∈ {access,trunk,lag}; `pvid` defined (1–4094)
- **Access**: exactly one untagged VLAN; tagged must be empty; `pvid` equals the untagged VLAN
- **Trunk**: at most one untagged VLAN; tagged set `non-empty`; if untagged present, it must equal pvid; otherwise `pvid ∈ tagged`
- **LAG members**: inherit `mode=lag`; individual tagging defined at the LAG level, not members

### LAGs

- Member ports share identical tagging/PVID once grouped
- No port belongs to more than one LAG

### STP

Consistent STP mode across the chassis; LAG/STP states coherent

### Management Reachability

- Exactly one management VLAN effective for the management interface
- Ensure at least one connected trunk/access path from HA host subnet to the management VLAN before applying changes (preflight)

### ACLs (if present)

- No shadowed/duplicate rules
- Default policy explicitly documented

### Cross-File Coherence

- `ports.csv` + `vlans.conf` agree on all VLAN IDs
- Relationship graph edges reference valid node IDs

### Preflight & Lockout Prevention

Before emitting a migration plan (e.g., introducing a mgmt VLAN):

- Confirm current mgmt IP and VLAN; record as management.current
- Compute proposed `management.next` and ensure path exists from HA host to next mgmt VLAN via at least one port/LAG
- Require two-step apply in `REPORT.md`:

  - **Phase A**: Create VLANs and trunk tagging without changing mgmt VLAN
  - **Phase B**: Move mgmt VLAN, confirm reachability, then save configuration

Home Assistant Integration (non-blocking)
Expose ports.csv to HA via sensors/REST helpers if desired

SNMP entities use ifName mapping to confirm indices

Keep SNMPv2c initially; plan SNMPv3 (authPriv) upgrade

### Examples

`vlans.conf`

```yaml
vlans:
  - { vlan_id: 1, name: default, role: default }
  - { vlan_id: 10, name: office, role: user }
  - { vlan_id: 20, name: iot, role: iot }
```

`ports.csv`

```pgsql
port,mode,pvid,tagged,untagged,lag,description
1,trunk,1,"[10,20]","[]",,Uplink to Router
2,access,10,"[]","[10]",,Office PC
3,access,20,"[]","[20]",,IoT AP
```

`switch.conf` (excerpt)

```ini
[management]
ip = 192.168.0.254/24
gateway = 192.168.0.1
dns = 192.168.0.1,8.8.8.8,1.1.1.1
ntp = 192.168.0.1,129.6.15.28,216.239.35.4
snmp = v2c(ro, community=public, src=192.168.0.129)

[vlans]
1 = default
10 = office
20 = iot

[ports]
1 = trunk pvid=1 tagged=[10,20]
2 = access pvid=10 untagged=[10]
3 = access pvid=20 untagged=[20]
```

### Determinism & Evidence

- Outputs normalized per ADR-0008
- `ports.csv`, `vlans.conf`, `switch.conf` included in `manifest.sha256`
- Deterministic tarball per reproducible flags
- `REPORT.md` must include:
  - Port/VLAN table
  - Validation results (pass/fail with reasons)
  - Management reachability preflight
  - Determinism property-hash

### Consequences

- Safer VLAN/LAG rollouts with clear preflight
- Machine-verifiable switch state for CI/audit
- Slightly more transformation logic required (worth it)

### Rollback

- Keep last three release tarballs; to revert, restore prior tar and re-apply on the switch (using its config import) after confirming mgmt reachability.

### Acceptance Criteria

- All validation gates pass
- `ports.csv`, `vlans.conf`, `switch.conf` mutually consistent
- Relationship graph extended with `vlan` and `port` nodes and edges (`tagged_on`, `untagged_on`)
- Reproducible tarball SHA256 recorded; manifest verification passes 100%
