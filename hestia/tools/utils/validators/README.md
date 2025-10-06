# Validator: validator_registry_entities.py

Purpose
-------
Scan a YAML file for Home Assistant entity IDs and validate them against the Home Assistant `core.entity_registry`. The tool emits a structured report (JSON/YAML) and provides fuzzy-match suggestions for unmatched entities.

Quick start
-----------
1. Install dependencies:

```bash
python3 -m pip install pyyaml
```

2. Run interactively:

```bash
python hestia/tools/utils/validators/validator_registry_entities.py
```

3. Or run with flags:

```bash
python hestia/tools/utils/validators/validator_registry_entities.py -i packages/motion_lighting/helpers.yaml
```

Output
------
Reports are written by default to:
```
${VALIDATOR_OUTPUT_DIR:-$HOME/hass/hestia/workspace/operations/reports/validator_registry_entities}
```
A temporary JSON file is also written to `${VALIDATOR_TEMP_DIR}` for quick debugging.

Configuration
-------------
Add a `.env` at repository root to override defaults (sample in `.env.sample`).

Contribution
------------
Open a PR against `hestia/tools/utils/validators` with tests and fixtures. Follow project linting and formatting guidelines.
