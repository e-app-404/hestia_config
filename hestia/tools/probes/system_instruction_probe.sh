#!/usr/bin/env bash
set -euo pipefail

# System Instruction Probe — writes diagnostics to /config/hestia/reports/<YYYY-MM-DD>/system_instruction_probe/
# ADR refs: ADR-0024 (canonical /config), ADR-0027 (write governance logs), ADR-0009 (reporting)

UTC_TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT_DAY=$(date +%F)
OUTDIR="/config/hestia/reports/${OUT_DAY}/system_instruction_probe"
mkdir -p "${OUTDIR}"

SUMMARY_JSON="${OUTDIR}/${UTC_TS}__summary.json"
ENV_LOG="${OUTDIR}/${UTC_TS}__env.log"
MODE_LOG="${OUTDIR}/${UTC_TS}__workspace_mode.json"
HEALTH_LOG="${OUTDIR}/${UTC_TS}__config-health.log"
YAML_LOG="${OUTDIR}/${UTC_TS}__config-validate.log"
GIT_LOG="${OUTDIR}/${UTC_TS}__git-status.log"

probe_status() {
  local name=$1 code=$2
  printf '  %-28s : %s\n' "$name" "$([ "$code" -eq 0 ] && echo PASS || echo FAIL)"
}

# Collect environment details
{
  echo "UTC_TS=${UTC_TS}"
  echo "DATE_LOCAL=$(date)"
  echo "UNAME=$(uname -a)"
  echo "ID=$(id)"
  command -v python3 >/dev/null 2>&1 && python3 --version || true
  command -v node >/dev/null 2>&1 && node --version || true
  echo "PWD=$(pwd)"
} >"${ENV_LOG}" 2>&1 || true

# Capture workspace mode info if present
if [ -f "/config/.vscode/workspace_mode.json" ]; then
  cp -f "/config/.vscode/workspace_mode.json" "${MODE_LOG}" || true
fi

# Run health checks
HEALTH_RC=0
if [ -x "/config/bin/config-health" ]; then
  "/config/bin/config-health" "/config" >"${HEALTH_LOG}" 2>&1 || HEALTH_RC=$?
else
  echo "config-health not found" >"${HEALTH_LOG}"
fi

YAML_RC=0
if [ -x "/config/bin/config-validate" ]; then
  "/config/bin/config-validate" "/config" >"${YAML_LOG}" 2>&1 || YAML_RC=$?
else
  echo "config-validate not found" >"${YAML_LOG}"
fi

# Git snapshot (non-destructive)
{
  git rev-parse --abbrev-ref HEAD || true
  git rev-parse HEAD || true
  git status -sb || true
} >"${GIT_LOG}" 2>&1 || true

# Summary JSON
cat >"${SUMMARY_JSON}" <<EOF
{
  "timestamp_utc": "${UTC_TS}",
  "outdir": "${OUTDIR}",
  "logs": {
    "env": "$(basename "$ENV_LOG")",
    "workspace_mode": "$(basename "$MODE_LOG")",
    "config_health": "$(basename "$HEALTH_LOG")",
    "config_validate": "$(basename "$YAML_LOG")",
    "git_status": "$(basename "$GIT_LOG")"
  },
  "results": {
    "config_health": ${HEALTH_RC},
    "config_validate": ${YAML_RC}
  }
}
EOF

echo "Probe complete: OUTDIR=${OUTDIR} TS=${UTC_TS}"
echo "Health: $( [ "$HEALTH_RC" -eq 0 ] && echo PASS || echo FAIL ), YAML: $( [ "$YAML_RC" -eq 0 ] && echo PASS || echo FAIL )"
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
