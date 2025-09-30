VENV=.venv_ha_governance
ACTIVATE=. $(VENV)/bin/activate
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: activate venv shell install lint format format-apply validate autofix ci hygiene bundle reports-latest hooks \
	hades-validate adr-validate adr-0016-validate vault-index vault-index-dry backup-create backup-rename backup-rename-dry \
	template-fix template-fix-dry template-validate config-validate

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

format: venv
	@echo "Formatting Python code with isort (Hestia files only)..."
	@$(VENV)/bin/isort hestia/ --check-only --diff || true
	@$(VENV)/bin/isort hestia/

format-apply: venv
	@echo "Applying isort formatting to Hestia files..."
	@$(VENV)/bin/isort hestia/

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

# Validation Tools
hades-validate: venv
	@echo "Running Hades config index validation..."
	@$(PY) hestia/tools/utils/validators/hades_index_validator.py

adr-validate: venv
	@echo "Validating ADR files..."
	@for adr in $$(find hestia/library/docs/ADR -name "*.md" -not -name "*template*" 2>/dev/null || true); do \
		if [ -f "$$adr" ]; then \
			echo "Validating $$adr..."; \
			$(PY) hestia/tools/utils/validators/adr_validator.py "$$adr" || exit 1; \
		fi; \
	done

adr-0016-validate:
	@echo "Validating ADR-0016 path expansion compliance..."
	@bash hestia/tools/utils/validators/adr_0016_path_expansion.sh

# Vault Management
vault-index: venv
	@echo "Running vault indexer and policy enforcement..."
	@$(PY) hestia/tools/utils/vault_manager/vault_indexer.py --no-dry

vault-index-dry: venv
	@echo "Running vault indexer (dry run)..."
	@$(PY) hestia/tools/utils/vault_manager/vault_indexer.py

# Backup Tools
backup-create: venv
	@echo "Creating Hestia workspace backup..."
	@bash hestia/tools/utils/backup/hestia_tarball.sh

tarball: venv
	@echo "Creating Hestia workspace backup..."
	@bash hestia/tools/utils/backup/hestia_tarball.sh

backup-rename: venv
	@echo "Normalizing legacy backup file names..."
	@$(PY) hestia/tools/utils/legacy_backup_renamer.py --apply

backup-rename-dry: venv
	@echo "Checking legacy backup file names (dry run)..."
	@$(PY) hestia/tools/utils/legacy_backup_renamer.py

# Template Tools (ADR-0020)
template-fix: venv
	@echo "Fixing Jinja template whitespace control issues..."
	@bash hestia/tools/template_patcher/fix_jinja_whitespace.sh

template-fix-dry: venv
	@echo "Checking for Jinja template whitespace issues (dry run)..."
	@bash hestia/tools/template_patcher/fix_jinja_whitespace.sh --dry-run

template-validate: venv
	@echo "Validating Jinja templates..."
	@bash hestia/tools/template_patcher/fix_jinja_whitespace.sh --dry-run
	@if [ $$? -eq 0 ]; then echo "✅ Template validation passed"; else echo "❌ Template validation failed"; exit 1; fi

# Configuration Validation (ADR-0020)
config-validate: adr-0016-validate template-validate hades-validate
	@echo "Running comprehensive configuration validation..."
	@echo "✅ All configuration validation checks passed"
