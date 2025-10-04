🧱 Prompt 1: Vendor-Aware Placeholder Stub Generation
Purpose: Build out logically correct but safely incomplete function stubs that match vendor SDKs (like spherov2), adapted for Home Assistant (HA) integration later.

/generate_vendor_stubs_for_ha

Scan the vendor module (e.g. spherov2.py) and generate minimal placeholder stubs for any functions, classes, or constants not yet implemented in ha_sphero_bb8.

Use this format:

```python
def rainbow_cycle():
    """Cycle through colors in rainbow pattern.
    Intended for Home Assistant light animation integration."""
    raise NotImplementedError("To be implemented for HA runtime")
For each stub:

Inherit correct name and doc from vendor

Append an HA-aware comment

Raise NotImplementedError to ensure runtime traceability

Tag each with: # STUB_VENDOR_PORT_HA


---

## 🩺 Prompt 2: **Project-Wide Diagnostic Audit (Copilot Agent Mode)**

**Purpose:** Instruct Copilot to run a multi-pass scan across the project tree and emit a report + fix candidates.

```plaintext
/run_project_diagnostic_audit

Perform a structured diagnostic scan across the entire project tree.
For each file or module, emit:

- ❌ Missing imports or unresolved symbols
- ⚠️ Type mismatches, unsafe fallbacks, or Optional[str] usage
- 🧱 Structural drift from vendor SDK
- 🚫 Dead logic (unreachable, duplicate class defs, etc.)
- 🪪 Home Assistant integration gaps (e.g., no sensor export)

Emit results in this format:

```yaml
module: controller.py
diagnostics:
  - ⚠️ Unknown attribute 'connect' used on BB8Controller
  - ⚠️ ControllerMode type hint is broken — fallback required
  - 🧱 BB8Like protocol does not mirror spherov2.Sphero interface
Then suggest:

Fixes with tag # PATCH_AUDIT_CLEANUP

Stubs with tag # STUB_VENDOR_PORT_HA

Any Phase marker if relevant (e.g., # PHASE_1_READY)
