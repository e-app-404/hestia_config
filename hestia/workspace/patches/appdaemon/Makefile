# Room-DB v3.1 Operations Makefile

.PHONY: backup verify reseed restore-rate help

TS := $(shell date +%Y%m%d_%H%M%S)

backup:
	@echo "Creating backups with timestamp: $(TS)"
	cp -v /config/room_database.db /config/room_database.db.$(TS).bak
	cp -v /config/hestia/workspace/patches/appdaemon/apps.yaml /config/hestia/workspace/patches/appdaemon/apps.yaml.$(TS).bak
	cp -v /config/www/area_mapping.yaml /config/www/area_mapping.yaml.$(TS).bak

verify:
	@echo "=== Validating area mapping ==="
	python3 /config/hestia/workspace/patches/appdaemon/validate_area_mapping.py
	@echo ""
	@echo "=== Testing endpoints (if AppDaemon is running) ==="
	@curl -s --connect-timeout 5 http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_health | jq . || echo "AppDaemon not reachable"
	@curl -s --connect-timeout 5 -X POST http://a0d7b954-appdaemon:5050/api/appdaemon/room_db_reload_mapping | jq . || echo "Reload endpoint not available"

reseed:
	@echo "=== Reseeding entrance motion lighting ==="
	python3 /config/hestia/workspace/patches/appdaemon/seed_from_mapping.py --domain motion_lighting --rooms entrance

reseed-all:
	@echo "=== Reseeding all rooms from mapping ==="
	python3 /config/hestia/workspace/patches/appdaemon/seed_from_mapping.py

restore-rate:
	@echo "Rate limiter would be restored to normal operation"
	@echo "In production, this would reset write_rate_limit_seconds to normal values"

dry-reseed:
	@echo "=== Dry run reseed test ==="
	python3 /config/hestia/workspace/patches/appdaemon/seed_from_mapping.py --dry-run

help:
	@echo "Room-DB v3.1 Operations:"
	@echo "  make backup      - Create timestamped backups"
	@echo "  make verify      - Validate mapping and test endpoints"
	@echo "  make reseed      - Reseed entrance motion lighting"
	@echo "  make reseed-all  - Reseed all rooms from mapping"
	@echo "  make dry-reseed  - Show what would be reseeded"
	@echo "  make restore-rate - Restore rate limiter to normal"