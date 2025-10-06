---
title: "0003 - Normalize HACS network_scanner mac_mapping format"
date: 2025-10-05
author: copilot
status: open
human_owner: __REPLACE_ME__
---

Summary
-------
This todo defers normalizing the `packages/hacs/hacs_network_scanner.yaml` mac mapping format to a consistent 3-column shape:

  MAC_ADDRESS ; DEVICE_OR_ENTITY_ID_OR_NAME ; PLATFORM_OR_INTEGRATION

We will park the work here to be executed later.

Acceptance criteria
-------------------
- All `mac_mapping_N` entries in `packages/hacs/hacs_network_scanner.yaml` use the 3-column format.
- Add a Tailnet ip_range placeholder in the file.
- Add a linked TODO placeholder in `hestia/workspace/operations/diagnostics/network/ha_network_analysis_20250930.md` referencing this task.
- Produce a short change log entry and backup before applying changes.

Planned steps
-------------
1. Create a branch and back up current `packages/hacs/hacs_network_scanner.yaml`.
2. Parse existing `mac_mapping_N` entries and normalize to 3 fields. For entries with 4 fields, drop any duplicate token and set platform to the 3rd column. Empty platforms become `Unknown`.
3. Add `ip_range_tailnet` with the user's Tailnet prefix (placeholder if unknown).
4. Add a linked TODO in `ha_network_analysis_20250930.md` describing the change and why.
5. Run a YAML lint/parse check and commit changes with a clear commit message.

Notes
-----
- This todo intentionally does NOT edit `custom_components/network_scanner` — the mapping format is backward-compatible with the current parser that expects at least 2–3 fields. A follow-up patch to the custom component may be required to expose the new platform/device fields.
- If you want automated replacements for placeholder tokens (e.g., `router_device_list`), provide the router/fing CSVs and inventory files.

References
----------
- `packages/hacs/hacs_network_scanner.yaml`
- `custom_components/network_scanner/sensor.py` (read-only)
- `hestia/workspace/operations/diagnostics/network/ha_network_analysis_20250930.md`

Reviewer checklist
------------------
- [ ] Confirm human_owner
- [ ] Provide Tailnet prefix
- [ ] Approve backup and commit
