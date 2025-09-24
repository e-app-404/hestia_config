# 📄 Final Advisory

**Token usage advisory**

* Keep responses artifact-centric; avoid restating large files. Prefer short deltas and checklists.
* For hashes and file counts, compute in-runner and append to the index rather than in-chat.

**Recommended next GPT startup configuration**

* Persona: *Strategos + Promachos (dual-mode)*
* Mode: *quiet* signoff for routine steps; keep **confidence scoring on**.
* Tools: allow minimal shell/DSM UI step lists; avoid code generation unless requested.

**Assumptions / risks to validate on resume**

* DSM hostname `nas.xplab.io` is already certificate-bound (either DSM cert or Cloudflare Tunnel).
* Reverse Proxy prefix strip supported for `/ha` and `/grafana` targets in your environment.
* File placement uses sibling directories `/volume1/web/public` and `/volume1/web/portal` as required by assets.

**Guardrails to keep the session lightweight, fast & accurate**

* No new services; only Web Station + Reverse Proxy configuration.
* Enforce “least privilege”: public root is anonymous; `/portal` always behind DSM auth and/or Tailnet allowlist.
* Validate tile links in `_assets/portal.config.json` before exposing publicly.

**Patch etiquette & session guidelines (single-document)**

```yaml
patch_etiquette:
  principles:
    - "Prefer UI steps over template edits for Web Station"
    - "One change per checkpoint; verify before proceeding"
    - "Never weaken /portal protections to fix convenience issues"
  change_control:
    - "Record: phase id, step, outcome, evidence (URL/screenshot)"
    - "Rollback: delete/recreate Web Portal or Reverse Proxy rule — do not mutate hidden templates"
  acceptance_gates:
    - "All criteria in xplab_portal_manifest.yaml must be true"
    - "Public tiles show only visibility: public; private remain hidden"
  evidence_pack:
    - urls:
        - "https://nas.xplab.io/"
        - "https://nas.xplab.io/portal/"
    - screenshots:
        - "Web Service list"
        - "Web Portal binding"
        - "Reverse Proxy rules table"
```

---

```yaml
confidence_metrics:
  structural:
    score: 0.93
    rationale: "All requested sections provided in machine-ingestible YAML/MD blocks; seed matches bootloader style used previously."
  operational:
    score: 0.88
    rationale: "Steps align with DSM 7.2 Web Station + Reverse Proxy behavior and uploaded assets/manifest; ready for immediate application."
  semantic:
    score: 0.91
    rationale: "Directly supports STRATEGOS merge: recap, artifact index, phase registry, memory vars, seed prompt, and advisory."
  adoption_recommendation: "Proceed; compute file hashes out-of-band and attach to index for final merge."
```

**Handoff tag:** `HANDOFF/STRATEGOS/DSM-PORTAL/2025-09-19`