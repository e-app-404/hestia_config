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
