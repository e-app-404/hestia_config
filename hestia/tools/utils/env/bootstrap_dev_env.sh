#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt || {
  pip install jsonschema yamllint ruamel.yaml pandas click pre-commit
  pip freeze > requirements-dev.txt
}
pre-commit install
echo "Dev env ready. Use: '. .venv/bin/activate'"
