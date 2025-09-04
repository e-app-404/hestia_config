#!/usr/bin/env python3
import json, time, sys

# Usage: emit_qa_contract.py <qa_path> <snap_path> <metrics_path>
qa = sys.argv[1] if len(sys.argv) > 1 else "qa_contract_telemetry_STP5.json"
snap = sys.argv[2] if len(sys.argv) > 2 else "telemetry_snapshot.jsonl"
metrics = sys.argv[3] if len(sys.argv) > 3 else "metrics_summary.json"

qa_doc = {
    "contract_id": "QA-TELEMETRY-STP5-001",
    "phase": "P5-TELEMETRY-STP5",
    "objective": "Echo/telemetry attestation >=10s",
    "acceptance_criteria": [
        "Window duration >= 10s",
        "At least 3 echo ping/pong cycles observed",
        "p95 echo RTT <= 250ms",
        "Artifacts: telemetry_snapshot.jsonl, metrics_summary.json"
    ],
    "artifacts": {
        "telemetry_snapshot": snap,
        "metrics_summary": metrics
    },
    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "verdict": "FAIL",
    "diagnostics": [
        "No telemetry received",
        "Check MQTT broker, device status, credentials, and network."
    ]
}

with open(qa, "w") as f:
    f.write(json.dumps(qa_doc, indent=2))
print(f"WROTE QA contract file to: {qa} (full path: {qa})")
