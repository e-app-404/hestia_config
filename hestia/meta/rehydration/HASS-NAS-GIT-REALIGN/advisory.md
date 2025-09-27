## 📄 Final Advisory

**Token usage advisory (for next session):**

* Keep answers compact; prefer checklists + shell blocks.
* Default to **no browsing**; only look up if user explicitly asks or if facts are time-sensitive.
* Never emit secrets; only show path/hostnames/commands.

**Recommended startup configuration:**

```yaml
startup:
  personas: [Strategos, Promachos, Meta-Architect, Kybernetes]
  modes: [meta_capture_mode, governance_overlay_mode]
  defaults:
    path_policy: "parameterize code; docs may reference canonical"
    remote_policy: "origin=push; tailnet=fetch-only"
  guards:
    run_local_validator: true
    require_ack_tokens_for_destructive_ops: true
```

**Assumptions / risks to validate on resume:**

* NAS Git package may still gate SSH `git-shell-commands`; keep `tailnet` fetch-only and prefer LAN for push.
* Add-on repos (BB-8) use container paths (`/config`, `/data`)—do **not** parameterize those.

**Guardrails to enforce:**

* Hard-coded `/n/ha` in code → **block** (validator + CI).
* PRs must include acceptance checklist + “why/what/outcome” summary.
* Scripts must enforce ACK tokens (`: "${ACK_*:?}"`).

**Patch etiquette (lock-in):**

* Small, readable commits; one concern each.
* Include runnable reproduction commands and acceptance tests.
* Never force-push `main`; backup branches/tags for merges from divergent histories.
* Prefer environment parameterization over absolute host paths.
* Keep `.env` untracked; ship `.env.sample`.

---