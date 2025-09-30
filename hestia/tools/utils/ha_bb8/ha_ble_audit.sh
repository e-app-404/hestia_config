#!/bin/bash
# Home Assistant BLE/DBus/log audit - run on HA host (SSH/Terminal)
# Run with: evertappels@macbook config % bash hestia/workspace/utils/ha_ble_audit.sh

# Ensure SSH access to HA host using password from secrets.yaml
SSH_HOST="babylon-babes@192.168.0.129"
SSH_PASS=$(grep '^ha_ssh_pass:' ./secrets.yaml | awk '{print $2}')
if ! command -v sshpass >/dev/null 2>&1; then
  echo "sshpass is required but not installed. Exiting."
  exit 1
fi

OUT="hestia/config/diagnostics/logs/ble_audit_$(date +%Y%m%d_%H%M%S).log"
mkdir -p hestia/config/diagnostics/logs/
touch "$OUT"
echo "=== BB-8/HA BLE & DBus Audit $(date) ===" | tee "$OUT"

run_remote() {
  local desc="$1"
  local cmd="$2"
  echo -e "\n## $desc" | tee -a "$OUT"
  sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 $SSH_HOST "$cmd" 2>&1 | tee -a "$OUT"
}

run_remote "1. BLE Device Presence" "ls -l /dev | grep hci"
run_remote "2. USB Device List" "lsusb"
run_remote "3. lsof (Processes using /dev/hci0/hci1)" "sudo lsof /dev/hci0; sudo lsof /dev/hci1"
run_remote "4. Bluetooth/DBus Service Status" "sudo systemctl status bluetooth; sudo systemctl status dbus"
run_remote "5. DBus Socket Info" "ls -l /run/dbus/system_bus_socket"
run_remote "6. bluetoothctl Adapters/List" "bluetoothctl list; bluetoothctl show"
run_remote "7. BLE Scan Test" "echo 'Starting bluetoothctl scan for 10 seconds...'; bluetoothctl scan on & SCAN_PID=\$!; sleep 10; kill \$SCAN_PID; bluetoothctl devices"
run_remote "8. Log File Check" "ls -l /config/hestia/config/diagnostics/logs/; tail -20 /config/hestia/config/diagnostics/logs/ha_bb8_addon.log"
run_remote "9. Add-on Docker BLE Mapping" "CONTAINER_ID=\$(docker ps | grep beep_boop_bb8 | awk '{print \$1}'); if [ -n \"\$CONTAINER_ID\" ]; then echo 'Container ID: '\$CONTAINER_ID; docker exec -it \$CONTAINER_ID ls -l /dev | grep hci; else echo 'No running beep_boop_bb8 container found.'; fi"

echo -e "\n=== AUDIT COMPLETE: Log written to $OUT ===" | tee -a "$OUT"
