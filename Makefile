VENV=.venv_ha_governance
ACTIVATE=. $(VENV)/bin/activate
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: activate venv shell install lint validate autofix ci hygiene bundle reports-latest hooks

activate:
	@echo "Run this command to activate the virtual environment:"
	@echo "source $(VENV)/bin/activate"

venv:
	@if [ ! -d $(VENV) ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV); \
	fi
	@if [ -f $(PIP) ]; then \
		$(PIP) install --upgrade pip; \
	fi
	@echo "✅ Virtual environment ready at $(VENV)"
	@$(MAKE) activate

shell: venv
	@echo "Starting shell with virtual environment activated..."
	@$(ACTIVATE) && exec $(SHELL)

install: venv
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements-dev.txt

lint: venv
	@$(VENV)/bin/yamllint -f colored -s .

validate: venv
	@$(PY) hestia/tools/validate_metadata.py

autofix: venv
	@$(PY) hestia/tools/autofix_metadata.py --apply || true

ci: install lint validate

hygiene:
	bash scripts/hygiene.sh

bundle:
	bash scripts/make_bundle.sh dist/bundle.tar.gz

reports-latest:
	@test -f $(PY) && $(PY) hestia/tools/utils/reportkit/link_latest.py || python3 hestia/tools/utils/reportkit/link_latest.py

hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit
