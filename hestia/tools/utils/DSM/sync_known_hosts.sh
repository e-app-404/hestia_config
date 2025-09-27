#!/bin/bash

# Synchronize and sanitize known_hosts for DSM Tailscale node
echo "[INFO] Cleaning known_hosts entries for DSM..."
ssh-keygen -R 100.71.87.40 2>/dev/null
ssh-keygen -R 100.93.61.53 2>/dev/null

# Auto-retrieve and add fresh key for Tailscale DSM
ssh -o StrictHostKeyChecking=accept-new \
    -o ConnectTimeout=5 \
    -p 22 \
    babylonrobot@100.93.61.53 "echo '[OK] SSH fingerprint confirmed.'" || {
  echo "[ERROR] SSH connection to DSM failed." >&2
  exit 1
}

echo "[DONE] known_hosts entry refreshed."
exit 0
