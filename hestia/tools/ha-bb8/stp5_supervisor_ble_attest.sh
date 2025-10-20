#!/usr/bin/env bash
set -euo pipefail

# -------- Config (env overrides allowed) --------
HOST="${HOST:-192.168.0.129}"
PORT="${PORT:-1883}"
USER="${USER:-mqtt_bb8}"
PASS="${PASS:-mqtt_bb8}"
BASE="${BASE:-bb8}"
DURATION="${DURATION:-15}"        # seconds to listen
BURST_COUNT="${BURST_COUNT:-5}"   # number of echo triggers
BURST_GAP_MS="${BURST_GAP_MS:-250}"  # >= echo_min_interval_ms (default 50)
REQUIRE_BLE="${REQUIRE_BLE:-false}"  # true to enforce device-originated evidence

# -------- Paths (host filesystem) --------------
SINK="/config/reports"
OUT="$SINK/stp5"
SNAP="$OUT/telemetry_snapshot.jsonl"
ROUND="$OUT/echo_roundtrip.jsonl"
MET="$OUT/metrics_summary.json"
QA="$SINK/qa_contract_telemetry_STP5.json"
RCPT="$SINK/deploy_receipt.txt"
GUARD="$SINK/stp5_guard_report.json"
mkdir -p "$OUT"

say() { printf '%s\n' "$*"; }
fail() { say "ERROR: $*"; exit 2; }

# -------- Tooling sanity -----------------------
command -v jq >/dev/null || fail "jq missing (apk add jq in SSH add-on)"
command -v mosquitto_sub >/dev/null || fail "mosquitto_sub missing (install Mosquitto client)"
command -v mosquitto_pub >/dev/null || fail "mosquitto_pub missing (install Mosquitto client)"

# -------- Start raw snapshot collector ----------
# Capture all bb8/# for the window into JSONL
mosquitto_sub -h "$HOST" -p "$PORT" -u "$USER" -P "$PASS" -v -t "$BASE/#" -W "$((DURATION+2))" \
| awk '{
    topic=$1; $1=""; sub(/^ /,"");
    payload=$0;
    print "{\"topic\":\""topic"\",\"payload\":" payload "}"
}' > "$SNAP" &
SNAP_PID=$!

# -------- Start focused echo_roundtrip collector -
mosquitto_sub -h "$HOST" -p "$PORT" -u "$USER" -P "$PASS" -t "$BASE/telemetry/echo_roundtrip" -W "$((DURATION+2))" \
| tee "$ROUND" >/dev/null &
RT_PID=$!

# -------- Nudge: send a burst of echo cmds -------
sleep 0.25
for i in $(seq 1 "$BURST_COUNT"); do
  mosquitto_pub -h "$HOST" -p "$PORT" -u "$USER" -P "$PASS" \
    -t "$BASE/echo/cmd" -m '{"value":1}'
  usleep $((BURST_GAP_MS * 1000))
done

# -------- Wait & stop collectors -----------------
sleep "$DURATION"
kill "$SNAP_PID" "$RT_PID" 2>/dev/null || true
wait "$SNAP_PID" 2>/dev/null || true
wait "$RT_PID" 2>/dev/null || true

# -------- Guard: artifacts existence -------------
[ -s "$SNAP" ] || fail "telemetry_snapshot.jsonl is empty"
# $ROUND may be empty if no echo_roundtrip was produced; handle below.

# -------- Compute metrics (jq-only) --------------
# Make sure $ROUND is valid JSONL even if empty
touch "$ROUND"

# Calculate metrics from echo_roundtrip lines
# - window: max(ts) - min(ts)
# - echo_count: total; ble_true_count: only ble_ok==true
# - p95 of rtt_ms
jq -s -c '
  def p95(xs):
    (xs|sort) as $s
    | ( ($s|length)-1 ) as $n
    | if $n < 0 then 0
      else $s[ ( ($n*0.95)|floor ) ] // 0
      end;

  . as $all
  | {
      window_duration_sec:
        (if ($all|length)==0 then 0
         else ( ($all|map(.ts)|max) - ($all|map(.ts)|min) )
         end),
      echo_count: ($all|length),
      ble_true_count: ($all|map(select(.ble_ok==true))|length),
      echo_rtt_ms_mean:
        (if ($all|length)==0 then 0
         else (($all|map(.rtt_ms)|add) / ($all|length))
         end),
      echo_rtt_ms_p95: p95($all|map(.rtt_ms))
    }
' "$ROUND" > "$MET"

# Decide which count to enforce
ECHO_COUNT=$(jq -r '.echo_count' "$MET")
BLE_TRUE_COUNT=$(jq -r '.ble_true_count' "$MET")
WIN=$(jq -r '.window_duration_sec' "$MET")
P95=$(jq -r '.echo_rtt_ms_p95' "$MET")

if [ "$REQUIRE_BLE" = "true" ]; then
  ENFORCED_COUNT="$BLE_TRUE_COUNT"
else
  ENFORCED_COUNT="$ECHO_COUNT"
fi

CRIT_WIN=$([ "${WIN%.*}" -ge 10 ] && echo true || echo false)
CRIT_ECHO=$([ "$ENFORCED_COUNT" -ge 3 ] && echo true || echo false)
CRIT_P95=$([ "${P95%.*}" -le 250 ] && echo true || echo false)

VERDICT=false
if [ "$CRIT_WIN" = "true" ] && [ "$CRIT_ECHO" = "true" ] && [ "$CRIT_P95" = "true" ]; then
  VERDICT=true
fi

# -------- Write QA contract ----------------------
jq -n \
  --arg base "$BASE" \
  --arg sink "$SINK" \
  --arg snap "$SNAP" \
  --arg metrics "$MET" \
  --arg require_ble "$REQUIRE_BLE" \
  --argjson win "$WIN" \
  --argjson total "$ECHO_COUNT" \
  --argjson ble_true "$BLE_TRUE_COUNT" \
  --argjson p95 "$P95" \
  --argjson crit_win "$CRIT_WIN" \
  --argjson crit_echo "$CRIT_ECHO" \
  --argjson crit_p95 "$CRIT_P95" \
  --argjson verdict "$VERDICT" '
{
  contract_id: "QA-TELEMETRY-STP5-001",
  phase: "P5-TELEMETRY",
  base_topic: $base,
  enforced_ble: ($require_ble == "true"),
  artifacts: { telemetry_snapshot: $snap, metrics_summary: $metrics },
  metrics: {
    window_duration_sec: $win,
    echo_count_total: $total,
    ble_true_count: $ble_true,
    echo_rtt_ms_p95: $p95
  },
  criteria: {
    window_ge_10s: $crit_win,
    min_echoes_ge_3: $crit_echo,
    rtt_p95_le_250ms: $crit_p95
  },
  verdict: (if $verdict then "PASS" else "FAIL" end),
  timestamp_utc: (now | todate)
}' > "$QA"

# -------- Guard report (sizes) -------------------
jq -n --arg snap "$SNAP" --arg metrics "$MET" --arg qa "$QA" \
  --argjson snap_size "$(stat -c%s "$SNAP" 2>/dev/null || stat -f%z "$SNAP")" \
  --argjson metrics_size "$(stat -c%s "$MET" 2>/dev/null || stat -f%z "$MET")" \
  --argjson qa_size "$(stat -c%s "$QA" 2>/dev/null || stat -f%z "$QA")" \
  '{artifacts:{snap:$snap,metrics:$metrics,qa:$qa,sizes:{snap:$snap_size,metrics:$metrics_size,qa:$qa_size}}}' \
  > "$GUARD"

# -------- Tokenize on PASS -----------------------
if jq -e '.verdict=="PASS"' "$QA" >/dev/null; then
  {
    echo "TOKEN: TELEMETRY_ATTEST_OK"
    echo "TOKEN: ECHO_WINDOW_10S_OK"
    echo "TOKEN: TELEMETRY_ARTIFACTS_EMITTED"
  } | tee -a "$RCPT" >/dev/null
  say "STP5 PASS (binary criteria met)"
else
  say "STP5 FAIL — inspect $OUT and $QA"
  exit 1
fi
