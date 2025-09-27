# meta_system_instruction_PR.md
version_id: "patch_20250819_01"
artifact_name: "meta_system_instruction_PR.md"
patch_type: "cleaned_full_replacement"
target_file: "system_instruction.yaml"
submitted_by: "Kybernetes"
role: "GPT Output Auditor"
runtime: "governance_patch"
status: "proposed"
ref: https://chatgpt.com/g/g-684595acfeb08191afc50003f2a0be9f-kybernetes/c/68a4519d-26e0-8326-9cc0-faf268998709
---

## Title
Enforce Prompt-Level Metadata Headers for All Emitted Prompts

## Summary
This patch adds a **prompt metadata protocol** that *requires* every GPT-emitted prompt block to include a `_meta:` header preceding `_prompt:`. The header captures standardized archival/trace metadata (UTC timestamp, prompt_id, version, persona, domain, coverage, objective, provenance, etc.). It also introduces a **minimal-meta fallback**, explicit **validation rules**, and **linting hooks** to guarantee machine-parseable and human-readable prompts across sessions and GPT instances.

---

## Rationale
- Prompts are frequently reused across sessions and tools; without a stable metadata header they are hard to archive, search, diff, or attribute.
- The system already tracks execution metadata (trace/tokens) but lacks a guaranteed *per-prompt* header contract.
- The proposed protocol integrates cleanly with `protocol_prompt_optimization_first_v2`, `protocol_confidence_scoring_v2`, and the existing metadata layer; it adds enforcement (reject on missing header) and graceful degradation (auto-minimal `_meta`).

---

## Diff (apply to `system_instruction.yaml`)
```diff
--- a/system_instruction.yaml
+++ b/system_instruction.yaml
@@
   metadata:
     execution_tracking:
       id: "protocol_metadata_tracking_v2"
       version: "2.0"
       priority: 50
       description: "Comprehensive execution metadata"
       enabled: true
       granularity: "protocol_level"
@@
     debug_diagnostics:
       id: "protocol_debug_diagnostics_v2"
       version: "2.0"
       priority: 45
       description: "Unified diagnostic behavior"
@@
+    prompt_metadata_contract:
+      id: "protocol_prompt_metadata_v1"
+      version: "1.0"
+      priority: 55
+      description: >
+        Enforce that every GPT-emitted prompt includes a `_meta` section preceding `_prompt`.
+        Ensures archival, parsing, and reproducibility across sessions and personas.
+      enforcement:
+        required_order: ["_meta", "_prompt"]
+        required_fields:
+          - generated_utc
+          - prompt_id
+          - version
+          - objective
+        recommended_fields:
+          - variant
+          - subsystem
+          - domain
+          - persona
+          - session_id
+          - session_url
+          - coverage
+          - provenance_notes
+        field_rules:
+          generated_utc:
+            format: "ISO8601"
+          prompt_id:
+            format: "^[0-9T:-]{15,}_([A-Za-z0-9_-]+)?_([A-Za-z0-9_-]+)$"
+            guidance: "Use `<timestamp>_<persona|role>_<topic>`; e.g., `20250819T154355Z_Kybernetes_cloudflare-seed`"
+          version:
+            format: "^\\d+\\.\\d+(\\.\\d+)?$"
+          coverage:
+            type: "map<string,bool>"
+          provenance_notes:
+            type: "multiline_text"
+      validation:
+        lint_checks:
+          - name: "order_check"
+            rule: "_meta must appear before _prompt"
+          - name: "required_present"
+            rule: "generated_utc, prompt_id, version, objective present"
+          - name: "id_format"
+            rule: "prompt_id matches pattern"
+          - name: "time_format"
+            rule: "generated_utc parses as ISO8601"
+        on_fail:
+          action: "reject_output"
+          fallback: "generate_minimal_meta"
+          minimal_meta:
+            generated_utc: "<auto:now_iso8601>"
+            prompt_id: "<auto:timestamp>_<auto:role>_<auto:topic>"
+            version: "1.0"
+            objective: "Prompt emitted without full metadata; auto-filled by protocol_prompt_metadata_v1."
+      integration:
+        with:
+          - "protocol_prompt_optimization_first_v2"
+          - "protocol_confidence_scoring_v2"
+          - "protocol_phase_memory_v2"
+      examples:
+        - label: "Minimal valid"
+          content: |
+            _meta:
+              generated_utc: "2025-08-19T16:42:05Z"
+              prompt_id: "20250819T164205Z_Kybernetes_metadata"
+              version: "1.0"
+              objective: >
+                "Attach metadata headers to emitted prompts for archival."
+            _prompt: >
+              You are the Integration Strategist...
+        - label: "Full featured"
+          content: |
+            _meta:
+              generated_utc: "2025-08-19T16:42:05Z"
+              prompt_id: "20250819T164205Z_Promachos_cloudflare-context"
+              version: "1.2"
+              variant: "draftA"
+              subsystem: "hades"
+              domain: "network/cloudflare"
+              persona: "Promachos"
+              session_id: "sess-abc123"
+              session_url: "https://apollo/sessions/sess-abc123"
+              coverage:
+                cloudflare: true
+                tunnels: true
+                rules: true
+              objective: >
+                "Export session knowledge into a Cloudflare context seed (YAML)."
+              provenance_notes: |
+                Sourced from cloudflared logs and session guidance; secrets redacted.
+            _prompt: >
+              You are the Integration Strategist...
```

META SCHEMA:
All keys are lower_snake_case. Unknown keys MUST be ignored (forward-compatible).

```yaml
_meta: 
  generated_utc: "ISO8601 string, required"
  prompt_id: "string, required; pattern: <timestamp>_<role-or-persona>_<topic>"
  version: "semver string, required"
  variant: "string, optional"
  subsystem: "string, optional"
  domain: "string, optional"
  persona: "string, optional"
  session_id: "string, optional"
  session_url: "string (URL), optional"
  coverage:            # optional map of boolean flags
    <topic>: true|false
  objective: >         # required, 1–2 lines
    "short description"
  provenance_notes: |  # optional, multiline
    "notes about where the prompt content came from (files, logs, etc.)"
```