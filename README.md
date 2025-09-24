Hestia ADR Linter

Install (outside HA share):

```bash
python -m venv ~/.venv/hestia-adr
source ~/.venv/hestia-adr/bin/activate
pip install -e .[test]
```

Run:

```bash
hestia-adr-lint hestia/docs/ADR --format human
```

Note: do not create venvs or caches under /n/ha or /config. The workflow and README instruct to create the venv under the user home.
