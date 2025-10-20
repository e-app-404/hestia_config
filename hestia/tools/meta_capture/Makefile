# Meta-Capture Makefile — governed helpers
PY := /config/.venv/bin/python
TOOL := /config/hestia/tools/meta_capture/meta_capture.py
REPORT_DIR := /config/hestia/workspace/reports/meta_capture
STAGING := /config/hestia/workspace/staging
INDEX := /config/hestia/workspace/.hestia/index/meta_capture__index.jsonl
NOWZ := $(shell date -u +%Y%m%dT%H%M%SZ)

.PHONY: dry-run apply-green verify-zero-red verify-policy prune-reports prune-ledger health

dry-run:
	$(PY) $(TOOL) dry-run --inputs $(STAGING)/*.yaml \
	    --report $(REPORT_DIR)/$(NOWZ)__dry_run.json

apply-green:
	$(PY) $(TOOL) apply --inputs $(STAGING)/*.yaml \
	    --report $(REPORT_DIR)/$(NOWZ)__apply.json

verify-zero-red:
	jq -e '.severity_counts.red==0' $$(ls -1t $(REPORT_DIR)/*__dry_run.json | head -1)

verify-policy:
	@J=$$(ls -1t $(REPORT_DIR)/*__dry_run.json | head -1); \
	RED=$$(jq -r '.severity_counts.red' $$J); \
	ORANGE=$$(jq -r '.severity_counts.orange' $$J); \
	FL=$$(jq -r '.limits.fail_level' /config/hestia/config/system/hestia.toml | tr A-Z a-z); \
	test "$$RED" = "0"; \
	if [ "$$FL" = "orange" ]; then test "$$ORANGE" = "0"; fi

prune-reports:
	find $(REPORT_DIR) -type f -mtime +14 -delete

prune-ledger:
	python3 - <<'PY'
p="/config/hestia/workspace/.hestia/index/meta_capture__index.jsonl"; maxl=20000
try:
    L=open(p).read().splitlines()
    open(p,"w").write("\n".join(L[-maxl:])+"\n")
except FileNotFoundError:
    pass
PY

health:
	python3 - <<'PY'
import tomllib,json,sys
C=tomllib.load(open("/config/hestia/config/system/hestia.toml","rb"))["automation"]["meta_capture"]
print(json.dumps({k:C.get(k) for k in ["repo_root","config_root","allowed_root"]}, indent=2))
PY
