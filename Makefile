VENV=.venv_ha_governance
ACTIVATE=. $(VENV)/bin/activate
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: activate venv shell install lint format format-apply validate autofix ci hygiene bundle reports-latest hooks \
	hades-validate adr-validate adr-0016-validate vault-index vault-index-dry backup-create backup-rename backup-rename-dry \
	template-fix template-fix-dry template-validate config-validate adr-tarball

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
	@$(PIP) install -r requirements.txt

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

# ADR collection artifact (artifacts/ with MANIFEST and SHA256SUMS; includes deprecated/, excludes ADR-000x-template.md)
adr-tarball:
	@echo "Creating ADR artifact (including deprecated/, excluding ADR-000x-template.md)..."
	@TS=$$(date -u +"%Y%m%dT%H%M%SZ"); \
	  ART_DIR="artifacts"; \
	  LABEL="adr-collection"; \
	  BASE="$${LABEL}__$$TS"; \
	  TARBALL="$$ART_DIR/$${BASE}__bundle.tgz"; \
	  MANIFEST="$$ART_DIR/$${BASE}__MANIFEST.json"; \
	  SUMS="$$ART_DIR/$${BASE}__SHA256SUMS"; \
	  mkdir -p "$$ART_DIR"; \
	  echo "Running: tar czf \"$$TARBALL\" -C hestia/library/docs --exclude 'ADR/ADR-000x-template.md' ADR"; \
	  tar czf "$$TARBALL" -C "hestia/library/docs" --exclude 'ADR/ADR-000x-template.md' ADR; \
	  if command -v sha256sum >/dev/null 2>&1; then \
	    SUM=$$(sha256sum "$$TARBALL" | awk '{print $$1}'); \
	  else \
	    SUM=$$(openssl dgst -sha256 "$$TARBALL" | awk '{print $$2}'); \
	  fi; \
	  echo "$$SUM  $$(basename "$$TARBALL")" > "$$SUMS"; \
	  cat > "$$MANIFEST" << EOF
{
  "label": "$$LABEL",
  "created_at": "$$TS",
  "path": "$$TARBALL",
  "source": "hestia/library/docs/ADR",
  "exclude": ["ADR-000x-template.md"],
  "includes_deprecated": true,
  "sha256": "$$SUM"
}
EOF
	@echo "ADR artifact created: $$TARBALL"
	@echo "MANIFEST: $$MANIFEST"
	@echo "SHA256SUMS: $$SUMS"

reports-latest:
	@test -f $(PY) && $(PY) hestia/tools/utils/reportkit/link_latest.py || python3 hestia/tools/utils/reportkit/link_latest.py

hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit

# Validation Tools
hades-validate: venv
	@echo "Running Hades config index validation..."
	@$(PY) hestia/tools/utils/validators/hades_index_validator.py

# Entity registry validator
validate-entities: venv
	@echo "Validating Home Assistant entities using validator_registry_entities.py"
	@$(PY) hestia/tools/utils/validators/validator_registry_entities.py -i packages/motion_lighting/helpers.yaml || true

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
	@echo "Creating Hestia workspace backup (excluding .storage)..."
	@INCLUDE_STORAGE=false bash hestia/tools/utils/backup/hestia_tarball.sh

storage-tarball: venv
	@echo "Creating Hestia workspace backup with .storage included..."
	@INCLUDE_STORAGE=true bash hestia/tools/utils/backup/hestia_tarball.sh

backup-rename: venv
	@echo "Normalizing backup file names to ADR-0018 standard..."
	@$(PY) hestia/tools/utils/normalize_backup_names.py --apply

backup-rename-dry: venv
	@echo "Checking backup file names for ADR-0018 compliance (dry run)..."
	@$(PY) hestia/tools/utils/normalize_backup_names.py --dry-run

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
