Hestia ADR Linter

Install (outside HA share):

```bash
python -m venv ~/.venv/hestia-adr
source ~/.venv/hestia-adr/bin/activate
pip install -e .[test]
```

Run:

```bash
hestia-adr-lint hestia/library/docs/ADR --format human
```

Note: do not create venvs or caches under ${HA_MOUNT} or /config. The workflow and README instruct to create the venv under the user home.

**Operational topology:** see `./workspace_ops_export.yaml`


------------------ 
# TODO / future work
------------------

- Make `~/hass` detection context-aware to avoid false positives on prose (currently we flag literal occurrences in code blocks and prose). Consider an AST approach or require explicit code-block context for path checks.
- Improve line-number precision for violations (some checks report the fence start line instead of the exact line). Add tests that assert exact line numbers for representative cases.
- Add additional ADR edge-case tests: multi-line frontmatter variants, more TOKEN_BLOCK shapes, and localized file-encoding edge cases.

If you want me to open the PR for this branch, I will create a dedicated feature branch, commit these files, and push to origin; if your repo requires a fork or a protected branch workflow I can instead provide the exact git commands and the prepared commit message for you to run.

