#!/usr/bin/env bash
set -Eeuo pipefail
STAGE="init"
SINK="/config/reports"; OUT="$SINK/stp5"; GUARD="$SINK/stp5_probe_guard.json"
mkdir -p "$OUT"

emit_guard () {
  local status="$1"; local msg="$2"
  jq -n --arg status "$status" --arg stage "$STAGE" --arg msg "$msg" \
    --arg host "${HOST:-}" --arg port "${PORT:-}" --arg base "${BASE:-}" \
    --arg user "${USER:-}" \
    '{probe:{status:$status,stage:$stage,msg:$msg,ts:(now|tojson)},
      params:{host:$host,port:$port,base:$base,user:$user}}' > "$GUARD" || true
  echo "[GUARD][$status][$STAGE] $msg -> $GUARD"
}
trap 'emit_guard "ERROR" "last command: $BASH_COMMAND (exit $?)"' ERR

CFG="/addons/local/beep_boop_bb8/config.yaml"
BASE="${BASE:-bb8}"

# Prefer yq if present; fallback to awk. No secrets in guard.
if command -v yq >/dev/null 2>&1; then
  HOST="${HOST:-$(yq -r '.mqtt_broker // "127.0.0.1"' "$CFG")}"
  PORT="${PORT:-$(yq -r '.mqtt_port // 1883' "$CFG")}"
  USER="${USER:-$(yq -r '.mqtt_username // ""' "$CFG")}"
  PASS="${PASS:-$(yq -r '.mqtt_password // ""' "$CFG")}"
else
  k(){ awk -v k="$1" '$1~"^"k":"{ $1=""; sub(/^ *: */,""); gsub(/^"|"$/,""); gsub(/#.*/,""); print; exit }' "$CFG" ;}
  HOST="${HOST:-$(k mqtt_broker   || echo 127.0.0.1)}"
  PORT="${PORT:-$(k mqtt_port     || echo 1883)}"
  USER="${USER:-$(k mqtt_username || echo "")}"
  PASS="${PASS:-$(k mqtt_password || echo "")}"
fi

AUTH=(); [[ -n "${USER:-}" ]] && AUTH+=(-u "$USER"); [[ -n "${PASS:-}" ]] && AUTH+=(-P "$PASS")

# 1) AUTH+PUB/SUB handshake on neutral topic
STAGE="auth_handshake"
NONCE="selftest.$(date +%s%N)"
mosquitto_sub -h "$HOST" -p "$PORT" "${AUTH[@]}" -t "bb8/selftest/$NONCE" -C 1 -W 3 -v > /dev/null &
SPID=$!; sleep 0.2
mosquitto_pub -h "$HOST" -p "$PORT" "${AUTH[@]}" -t "bb8/selftest/$NONCE" -m "ok" -q 1
if ! wait $SPID; then emit_guard "FAIL" "auth or ACL issue on neutral topic"; exit 10; fi

# 2) Topic discovery (broad sample)
STAGE="discovery"
DISC="$OUT/probe_discovery.log"
mosquitto_sub -h "$HOST" -p "$PORT" "${AUTH[@]}" -t "#" -W 5 -v > "$DISC" || true

# 3) Echo nudge + listen on BASE
STAGE="echo_probe"
mosquitto_sub -h "$HOST" -p "$PORT" "${AUTH[@]}" -t "$BASE/#" -C 1 -W 5 -v > "$OUT/probe_first_hit.log" &
SPID=$!; sleep 0.2
mosquitto_pub -h "$HOST" -p "$PORT" "${AUTH[@]}" -t "$BASE/echo/cmd" -m '{"value":1}' -q 0 || true
if wait $SPID; then
  emit_guard "PASS" "saw at least one message on $BASE/# (see probe_first_hit.log)"
  exit 0
else
  emit_guard "FAIL" "no messages observed on $BASE/#; see discovery log"
  exit 20
fi
