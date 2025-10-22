#!/usr/bin/env bash
set -euo pipefail

# System Instruction Probe
# Writes outputs under /config/hestia/reports/<YYYY-MM-DD>/system_instruction_probe/<UTC_TS>/
# Captures environment, git status, and local validation results.

ROOT="/config"
DATE_UTC="$(date -u +%F)"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUTBASE="$ROOT/hestia/reports/$DATE_UTC/system_instruction_probe"
OUTDIR="$OUTBASE/$TS_UTC"
mkdir -p "$OUTDIR"

ts_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

capture_cmd() {
  local outfile="$1"; shift
  local statusfile="${outfile%.log}.status"
  if "$@" >"$outfile" 2>&1; then
    echo 0 >"$statusfile"
  else
    echo $? >"$statusfile"
  fi
}

write_header() {
  local f="$1"
  {
    echo "# Probe: system_instruction_probe"
    echo "# Timestamp (UTC): $(ts_iso)"
    echo "# Host: $(uname -n)"
  } >>"$f"
}

# 1) Environment snapshot
ENV_LOG="$OUTDIR/env_info.log"
{
  echo "== System =="
  uname -a || true
  echo
  echo "== OS Release =="
  (cat /etc/os-release || true) | sed 's/^/  /'
  echo
  echo "== User =="
  id || true
  echo "SHELL=${SHELL:-unknown}"
  echo
  echo "== Tooling Versions =="
  for cmd in bash zsh python3 python node npm git; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "- $cmd: $($cmd --version 2>&1 | head -n1)"
    else
      echo "- $cmd: not found"
    fi
  done
} >"$ENV_LOG"
write_header "$ENV_LOG"

# 2) Git snapshot
GIT_LOG="$OUTDIR/git_info.log"
{
  echo "== Repo =="
  printf "CWD: %s\n" "$(pwd)"
  echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  echo
  echo "== Remotes =="
  git remote -v 2>&1 || true
  echo
  echo "== HEAD =="
  git show -s --format='%H %ai %an <%ae> %s' HEAD 2>&1 || true
  echo
  echo "== Status (porcelain) =="
  git status --porcelain 2>&1 || true
} >"$GIT_LOG"
write_header "$GIT_LOG"

# 3) Validations (path/mount health and YAML syntax)
PH_LOG="$OUTDIR/path_health.log"
YAML_LOG="$OUTDIR/yaml_validate.log"

PH_EXIT=0
YAML_EXIT=0

set +e
if [ -x "$ROOT/bin/config-health" ]; then
  "$ROOT/bin/config-health" "$ROOT" >"$PH_LOG" 2>&1
  PH_EXIT=$?
else
  echo "config-health not found at $ROOT/bin/config-health" >"$PH_LOG"; PH_EXIT=127
fi

if [ -x "$ROOT/bin/config-validate" ]; then
  "$ROOT/bin/config-validate" "$ROOT" >"$YAML_LOG" 2>&1
  YAML_EXIT=$?
else
  echo "config-validate not found at $ROOT/bin/config-validate" >"$YAML_LOG"; YAML_EXIT=127
fi
set -e

echo "$PH_EXIT" >"${PH_LOG%.log}.status"
echo "$YAML_EXIT" >"${YAML_LOG%.log}.status"

# 4) Summary JSON
SUMMARY_JSON="$OUTDIR/summary.json"
cat >"$SUMMARY_JSON" <<JSON
{
  "timestamp_utc": "$(ts_iso)",
  "outdir": "$OUTDIR",
  "checks": {
    "path_health": { "status": "$( [ "$PH_EXIT" -eq 0 ] && echo PASS || echo FAIL )", "exit_code": $PH_EXIT },
    "yaml_validate": { "status": "$( [ "$YAML_EXIT" -eq 0 ] && echo PASS || echo FAIL )", "exit_code": $YAML_EXIT }
  }
}
JSON

# 5) Metadata
cat >"$OUTDIR/_metadata.yaml" <<YAML
created_at_utc: "$(ts_iso)"
tool: system_instruction_probe
version: "1"
outdir: "$OUTDIR"
compliance:
  adr:
    - ADR-0024  # canonical /config paths
    - ADR-0008  # report determinism (basic structure)
YAML

echo "Probe complete: $OUTDIR"
