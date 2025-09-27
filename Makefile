VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: venv install lint validate autofix ci

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
