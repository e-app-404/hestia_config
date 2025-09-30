VENV=.venv_ha_governance
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: venv install lint validate autofix ci hygiene bundle reports-latest hooks

venv:
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip

install: venv
	@$(PIP) install -r requirements-dev.txt

lint:
	@$(VENV)/bin/yamllint -f colored -s .

validate:
	@$(VENV)/bin/python hestia/tools/validate_metadata.py

autofix:
	@$(VENV)/bin/python hestia/tools/autofix_metadata.py --apply || true

ci: install lint validate

hygiene:
	bash scripts/hygiene.sh

bundle:
	bash scripts/make_bundle.sh dist/bundle.tar.gz

reports-latest:
	python3 hestia/tools/utils/reportkit/link_latest.py

hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit
