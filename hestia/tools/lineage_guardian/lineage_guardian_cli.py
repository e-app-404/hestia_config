#!/usr/bin/env python3
"""
Lineage Guardian CLI - Hestia Integration
Validates and corrects entity lineage metadata across Home Assistant template YAML files.

Usage:
    python lineage_guardian_cli.py [--verbose] [--output-dir /path/to/output]

Conforms to ADR-0024 (canonical paths) and ADR-0018 (workspace lifecycle).
"""

import argparse
import datetime
import os
import sys
from pathlib import Path

# Ensure we can import from the lineage_guardian package
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description="Hestia Lineage Guardian Pipeline")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--template-dir",
        default="/config/domain/templates/",
        help="Directory containing YAML templates (default: /config/domain/templates/)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: /config/hestia/workspace/operations/logs/lineage/TIMESTAMP)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry run mode (default: true)"
    )

    args = parser.parse_args()

    # Set up output directory following ADR-0018 conventions
    if args.output_dir is None:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        args.output_dir = f"/config/hestia/workspace/operations/logs/lineage/{timestamp}__lineage_guardian__validation"

    os.makedirs(args.output_dir, exist_ok=True)

    # File paths
    graph_file = os.path.join(args.output_dir, "graph.json")
    violations_file = os.path.join(args.output_dir, "violations.json")
    integrity_file = os.path.join(args.output_dir, "integrity.json")
    report_dir = os.path.join(args.output_dir, "report")
    plan_dir = os.path.join(args.output_dir, "_plan")

    print(f"[INFO] Lineage Guardian Pipeline - Output: {args.output_dir}")
    print(f"[INFO] Template directory: {args.template_dir}")
    print(f"[INFO] Mode: {'DRY-RUN' if args.dry_run else 'APPLY'}")

    # Execute pipeline components
    verbose_flag = "--verbose" if args.verbose else ""

    # 1. Graph Scanner
    cmd = f"python lineage_guardian/graph_scanner.py --template-dir {args.template_dir} --output {graph_file} {verbose_flag}"
    print(f"[EXEC] {cmd}")
    if os.system(cmd) != 0:
        sys.exit(1)

    # 2. Lineage Validator
    cmd = f"python lineage_guardian/lineage_validator.py --graph-file {graph_file} --output {violations_file}"
    print(f"[EXEC] {cmd}")
    if os.system(cmd) != 0:
        sys.exit(1)

    # 3. Lineage Corrector (plan-only in dry-run)
    cmd = f"python lineage_guardian/lineage_corrector.py --violations-file {violations_file} --plan-dir {plan_dir}"
    print(f"[EXEC] {cmd}")
    if os.system(cmd) != 0:
        sys.exit(1)

    # 4. Graph Integrity Checker
    cmd = f"python lineage_guardian/graph_integrity_checker.py --graph-file {graph_file} --output {integrity_file}"
    print(f"[EXEC] {cmd}")
    if os.system(cmd) != 0:
        sys.exit(1)

    # 5. Report Generator
    cmd = (
        f"python lineage_guardian/lineage_report.py "
        f"--graph {graph_file} "
        f"--violations {violations_file} "
        f"--integrity {integrity_file} "
        f"--outdir {report_dir}"
    )
    print(f"[EXEC] {cmd}")
    if os.system(cmd) != 0:
        sys.exit(1)

    print(f"[INFO] Pipeline complete. Results in: {args.output_dir}")
    print(f"[INFO] Report available at: {report_dir}/REPORT.md")


if __name__ == "__main__":
    main()
