#!/usr/bin/env bash
set -euo pipefail

# ha_influx_diag.sh
# Single script to run on Home Assistant host to validate InfluxDB v2 forwarding.

OUT_DIR=/config/hestia/diag
mkdir -p "$OUT_DIR"
TIME_PREFIX="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "RESULT: Started diagnostics at $TIME_PREFIX"

# 1) health check
echo "${TIME_PREFIX} - Checking InfluxDB health..." > "$OUT_DIR/influx_health.txt"
wget -qO- http://192.168.0.104:8086/health 2>&1 | tee -a "$OUT_DIR/influx_health.txt" || echo "health_check_failed" >> "$OUT_DIR/influx_health.txt"
head -n 3 "$OUT_DIR/influx_health.txt" | sed -n '1,40p' | sed -n '1,40p'

# 2) write roundtrip (requires INFLUX_TOKEN env)
if [ -z "${INFLUX_TOKEN:-}" ]; then
  echo "RESULT: MISSING_INFLUX_TOKEN"
  echo "Please run: INFLUX_TOKEN='<token>' bash ha_influx_diag.sh"
  exit 2
fi

NOW=$(date +%s%N)
# perform a write; capture HTTP status line
curl -s -i -X POST "http://192.168.0.104:8086/api/v2/write?org=Hestia&bucket=homeassistant&precision=ns" \
  -H "Authorization: Token ${INFLUX_TOKEN}" \
  --data-binary "ha_smoketest,host=ha value=1i $NOW" > "$OUT_DIR/influx_write_head.txt" || true
head -n 1 "$OUT_DIR/influx_write_head.txt" | sed -n '1,200p'

# query for the test measurement
cat > /tmp/ha_influx_query.json <<'JSON'
{"query":"from(bucket:\"homeassistant\") |> range(start:-5m) |> filter(fn:(r)=>r._measurement==\"ha_smoketest\") |> last()"}
JSON
curl -s "http://192.168.0.104:8086/api/v2/query?org=Hestia" \
  -H "Authorization: Token ${INFLUX_TOKEN}" -H "Content-Type: application/json" \
  -d @/tmp/ha_influx_query.json > "$OUT_DIR/influx_query.txt" || true
sed -n '1,60p' "$OUT_DIR/influx_query.txt"

# 3) restart HA core and collect logs
echo "${TIME_PREFIX} - Restarting HA core..."
# capture ha core check output (best-effort; may not be available outside HA host)
if command -v ha >/dev/null 2>&1; then
  echo "${TIME_PREFIX} - Running 'ha core check'..." > "$OUT_DIR/ha_core_check.txt"
  ha core check >> "$OUT_DIR/ha_core_check.txt" 2>&1 || true
else
  echo "ha CLI not available in this environment; run 'ha core check' on the HA host" > "$OUT_DIR/ha_core_check.txt"
fi

ha core restart
sleep 12
ha core logs --no-color | tee "$OUT_DIR/ha_core_full.log" >/dev/null || true
# tail relevant lines
grep -iE 'influx|write|error|retry' "$OUT_DIR/ha_core_full.log" | tail -n 200 > "$OUT_DIR/ha_influx_tail.log" || true

# summary
echo "RESULT: WROTE $OUT_DIR/influx_health.txt"
echo "RESULT: WROTE $OUT_DIR/influx_write_head.txt"
echo "RESULT: WROTE $OUT_DIR/influx_query.txt"
echo "RESULT: WROTE $OUT_DIR/ha_core_full.log"
echo "RESULT: WROTE $OUT_DIR/ha_influx_tail.log"

echo "RESULT: Completed diagnostics at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit 0
