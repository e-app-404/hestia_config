#!/bin/sh
# BusyBox-friendly step runner with 180s timeout (uses python fallback if no timeout binary)
TAG="$1"
shift || true
LOGDIR="logs"
mkdir -p "$LOGDIR"
OUT="$LOGDIR/step_${TAG}.log.out"
ERR="$LOGDIR/step_${TAG}.log.err"

run_with_timeout() {
    # Try `timeout` if present
    if command -v timeout >/dev/null 2>&1; then
        timeout 180 "$@" 1>"$OUT" 2>"$ERR"
        return $?
    fi
    # Python fallback
    python3 - <<'PY' 1>"$OUT" 2>"$ERR" &
import sys, subprocess, threading, time, os
args = sys.argv[1:]
proc = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr)
def killer():
    time.sleep(180)
    try:
        proc.kill()
    except Exception:
        pass
thr = threading.Thread(target=killer)
thr.daemon = True
thr.start()
proc.wait()
sys.exit(proc.returncode)
PY
    return $?
}

run_with_timeout "$@"
RC=$?
if [ -s "$ERR" ]; then
    cp -f "$ERR" "report_${TAG}.json" || true
fi
exit $RC
