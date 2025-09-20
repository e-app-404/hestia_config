# ADR-0010 — Workspace Shape & Neutral Autofs Mount (/n/ha)
## Status
Accepted

## Context
Frequent path divergence (/Volumes/HA vs /Volumes/ha), fragile SMB mounts, and mixed tooling cause non-deterministic edits and outages. We need a single, neutral, reboot-resilient mount and enforceable repo shape.

## Decision
1) **Neutral path:** macOS mounts the HA `config` SMB share at **/n/ha** via **autofs** (direct map in /etc/auto_master → /etc/auto_smb).  
2) **Canonical repo root:** The Home Assistant working tree is accessed at **/n/ha** only.  
3) **Programmatic enforcement:** A repo script **hestia_workspace_enforcer.sh** fails CI/pre-commit if:
   - Any tracked file contains `/Volumes/HA` or `/Volumes/ha`.
   - `/n/ha/configuration.yaml` is missing.
4) **No home-dir droppings:** All project artifacts live inside the repo; only system autofs files exist outside.

## Consequences
- Stable editing regardless of drive case or Finder behavior.
- Reduced operator error, simpler debugging, predictable CI.

## Implementation
- /etc/auto_master: ensure `/-    auto_smb   -nosuid`
- /etc/auto_smb: one active mapping to `://homeassistant/config`; commented fallbacks for `.local` and Tailscale.
- Script: `hestia/tools/system/hestia_workspace_enforcer.sh`.
- Optional pre-commit hook or Make target to run the enforcer.
- All docs/scripts must reference **/n/ha**.

## Verification
- `ls -ld /n/ha` works after `sudo automount -cv`.
- `test -f /n/ha/configuration.yaml`
- `git grep -nE '/Volumes/(HA|ha)'` returns empty in tracked files.

## Rollback
- Comment out the direct map in /etc/auto_master; `sudo automount -cv`.
- Remove `/etc/auto_smb` entry.
