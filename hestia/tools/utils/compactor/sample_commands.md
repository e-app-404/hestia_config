See README.md for quick recipes. Example: Validate & sanitize

python3 -m hestia.tools.utils.compactor.cli validate registry/core.entity_registry.precompact.json --out registry/core.entity_registry.canonical.json 2> validation.txt

python3 -m hestia.tools.utils.compactor.cli sanitize registry/core.entity_registry.canonical.json --keep-last 0 --out registry/core.entity_registry.nodel.json 2> sanitize_report.json
