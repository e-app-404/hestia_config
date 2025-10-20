#!/usr/bin/env bash
set -euo pipefail
ROOT="/config"

# Core HA runtime files and directories
ALLOWED_DIRS="blueprints custom_components domain packages python_scripts themes www tts hestia includes entities appdaemon zigbee2mqtt ps5-mqtt glances bin scripts image custom_templates tmp"

# Runtime/build directories that are OK
ALLOWED_RUNTIME=".storage .ssh .venv .venv_ha_governance .mypy_cache .cloud .trash .quarantine artifacts deps .git .github .githooks .vscode .ci-config .devcontainer"

# Core files and patterns
ALLOWED_FILES="configuration.yaml scenes.yaml scripts.yaml automations.yaml customize.yaml secrets.yaml secrets.example.yaml"
ALLOWED_FILES="$ALLOWED_FILES .HA_VERSION .uuid .allow_runtime_tools .hygiene_smoke .ha_run.lock .gitignore .yamllint.yml .env .env.adr0024"
ALLOWED_FILES="$ALLOWED_FILES Makefile home-assistant_v2.db home-assistant_v2.db-shm home-assistant_v2.db-wal"
ALLOWED_FILES="$ALLOWED_FILES icloud3.log influx.cookie ruff.toml __init__.py worker-portal-no-store.js"
ALLOWED_FILES="$ALLOWED_FILES requirements.txt requirements.in requirements-dev.txt requirements-dev.in"

violations=0
shopt -s dotglob
for p in "$ROOT"/*; do
  [ -e "$p" ] || continue
  name="${p##*/}"
  
  # Check directories
  if [ -d "$p" ]; then
    case " $ALLOWED_DIRS $ALLOWED_RUNTIME " in
      *" $name "*) continue ;;
    esac
  fi
  
  # Check files
  case " $ALLOWED_FILES " in
    *" $name "*) continue ;;
  esac
  
  # Pattern matches for dynamic files
  if [[ "$name" == .ps4-games.* ]] || [[ "$name" == home-assistant.log* ]] || [[ "$name" == *.bak ]] || [[ "$name" == *.tmp ]] || [[ "$name" == PR_BODY_*.md ]]; then
    continue
  fi
  
  # Only flag as violation if it's clearly out of place (not dev/build artifacts that should be quarantined)
  if [[ "$name" =~ ^(.*\.egg-info|node_modules|build|dist|\.pytest_cache)$ ]]; then
    echo "QUARANTINE: dev artifact should be moved -> $p"
    violations=$((violations+1))
  elif [[ "$name" =~ ^(config|archive|reports|staging)$ ]] && [ -d "$p" ]; then
    echo "QUARANTINE: misplaced directory -> $p"  
    violations=$((violations+1))
  else
    echo "INFO: non-standard item (review) -> $p"
  fi
done
shopt -u dotglob

if [ $violations -gt 0 ]; then
  echo "Root hygiene check: $violations items need attention"
  exit 1
else
  echo "Root hygiene check: OK (all items are acceptable)"
fi
