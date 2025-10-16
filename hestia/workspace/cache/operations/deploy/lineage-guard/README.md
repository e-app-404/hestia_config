Awesome—here's a **single cut-and-paste bootstrap script** that creates a complete, conflict-free **Copilot bundle** you can drop into your VSCode workspace. It includes:

- a ready-to-run modular tool skeleton (`lineage_guardian/`)
- VSCode tasks
- a Copilot coaching prompt
- a TOML patch for `/config/hestia/config/system/hestia.toml`
- lightweight, idempotent pipeline you can expand with Copilot

> **How to use**
>
> 1. Create a new empty folder in your repo/workspace root (or run this from root).
> 2. Run the bootstrap script: `chmod +x bootstrap_lineage_guardian.sh && ./bootstrap_lineage_guardian.sh`
> 3. Navigate to the created bundle directory (will be named `lineage_guardian_bundle_YYYYMMDD_HHMMSS`)
> 4. Open the bundle folder in VSCode → **Terminal → Run Task → Lineage: Full Pipeline (dry-run)**
> 5. Paste `prompts/COPILOT_GUIDE.md` into Copilot Chat to guide implementation & hardening.

---

## What you’ll see after running the script

- `lineage_guardian/` with **working, minimal** modules (scanner → validator → corrector-plan → integrity → report)
- `prompts/COPILOT_GUIDE.md` (paste into Copilot chat)
- `config/snippets/hestia.toml.patch` (merge into your central `/config/hestia/config/system/hestia.toml`)
- VSCode tasks/launch
- `./.artifacts/` (pipeline outputs)

## Next steps I recommend

1. Merge the TOML patch into your real `hestia.toml`.
2. Point the pipeline at your actual templates path (defaults to `/config/domain/templates/`).
3. Run **“Lineage: Full Pipeline (dry-run)”** from VSCode tasks.
4. Open **`prompts/COPILOT_GUIDE.md`** in Copilot Chat and say: _“Use this guide to harden `graph_scanner.py` (regex edge cases), implement ruamel-based merges in `lineage_corrector.py`, and add unit tests.”_
5. Once Copilot finishes merges, flip from plan-only to safe in-place edits by adding an `--apply` mode (backups + atomic writes).

If you want me to tailor the script to a different project layout or add a one-click zip export, say the word and I’ll drop in a variant.

::contentReference[oaicite:0]{index=0}
