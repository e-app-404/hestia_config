#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - SUPERSEDES

Validates, normalizes, and updates the 'supersedes' field in ADR frontmatter.
Manages array of ADR references this decision supersedes with circular dependency checks.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def extract_supersession_info(content):
    """Extract supersession information from content"""
    supersedes = []

    # Look for supersession mentions
    patterns = [
        r"supersedes?\s+(ADR-\d{3,4})",
        r"replaces?\s+(ADR-\d{3,4})",
        r"amend[a-z]*\s+by\s+(ADR-\d{3,4})",
        r"obsoletes?\s+(ADR-\d{3,4})",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            supersedes.append(f"ADR-{match.zfill(4)}")

    return sorted(set(supersedes))


def validate_field(field_value, existing_adrs=None, current_adr_id=None):
    """Validate supersedes field according to meta-structure rules"""
    if field_value is None:
        return True, "Supersedes field can be empty (optional)"

    if not isinstance(field_value, list):
        return False, "Supersedes field must be an array"

    # Validate each item in the array
    for item in field_value:
        if not isinstance(item, str):
            return False, "Supersedes array items must be strings"

        if not re.match(r"^ADR-\d{4}$", item):
            return False, f"Supersedes item '{item}' must follow ADR-XXXX format"

        # Check self-reference
        if current_adr_id and item == current_adr_id:
            return False, f"ADR cannot supersede itself: {item}"

        # Check if referenced ADR exists (if existing_adrs provided)
        if existing_adrs and item not in existing_adrs:
            return False, f"Superseded ADR '{item}' does not exist in workspace"

    return True, "Valid"


def normalize_field(field_value):
    """Normalize supersedes field value"""
    if field_value is None:
        return []

    if not isinstance(field_value, list):
        return []

    # Normalize each ADR reference
    normalized = []
    for item in field_value:
        if isinstance(item, str):
            # Ensure proper ADR-XXXX format
            match = re.match(r"(?i)adr-?(\d+)", item.strip())
            if match:
                normalized.append(f"ADR-{match.group(1).zfill(4)}")

    # Sort and deduplicate
    return sorted(set(normalized))


def collect_existing_adrs():
    """Collect all existing ADR IDs for validation"""
    existing_adrs = set()

    for adr_file in ADR_DIR.glob("ADR-*.md"):
        # Extract ADR ID from filename
        match = re.search(r"ADR-(\d+)", adr_file.name)
        if match:
            existing_adrs.add(f"ADR-{match.group(1).zfill(4)}")

    return existing_adrs


def check_circular_dependencies(current_adr_id, supersedes_list, all_supersessions):
    """Check for circular supersession dependencies"""
    visited = set()

    def has_cycle(adr_id, path):
        if adr_id in path:
            return True, path + [adr_id]
        if adr_id in visited:
            return False, []

        visited.add(adr_id)
        path.append(adr_id)

        # Check what this ADR supersedes
        for superseded in all_supersessions.get(adr_id, []):
            has_cycle_result, cycle_path = has_cycle(superseded, path.copy())
            if has_cycle_result:
                return True, cycle_path

        return False, []

    # Check each item we want to supersede
    for superseded_adr in supersedes_list:
        cycle_detected, cycle_path = has_cycle(superseded_adr, [current_adr_id])
        if cycle_detected:
            return False, f"Circular supersession detected: {' -> '.join(cycle_path)}"

    return True, "No circular dependencies"


def collect_all_supersessions():
    """Collect all supersession relationships for circular dependency checking"""
    all_supersessions = {}

    for adr_file in ADR_DIR.glob("ADR-*.md"):
        try:
            content = adr_file.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    supersedes = frontmatter.get("supersedes", [])
                    if supersedes:
                        # Extract ADR ID from filename
                        match = re.search(r"ADR-(\d+)", adr_file.name)
                        if match:
                            adr_id = f"ADR-{match.group(1).zfill(4)}"
                            all_supersessions[adr_id] = supersedes
        except Exception:
            continue  # Skip files that can't be parsed

    return all_supersessions


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for supersedes field"""
    print(f"Processing SUPERSEDES field in {file_path.name}")

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: Could not read file: {e}")
        return False

    if not content.startswith("---"):
        print("  SKIP: No YAML frontmatter found")
        return True

    try:
        # Split content into frontmatter and body
        parts = content.split("---", 2)
        if len(parts) < 3:
            print("  ERROR: Invalid YAML frontmatter structure")
            return False

        yaml_content = parts[1]
        body_content = parts[2]
        frontmatter = yaml.safe_load(yaml_content) or {}

    except Exception as e:
        print(f"  ERROR: Could not parse YAML frontmatter: {e}")
        return False

    # Get current ADR ID
    current_adr_id = None
    match = re.search(r"ADR-(\d+)", file_path.name)
    if match:
        current_adr_id = f"ADR-{match.group(1).zfill(4)}"

    # Get existing ADRs for validation
    existing_adrs = collect_existing_adrs()

    # Check current supersedes value
    current_supersedes = frontmatter.get("supersedes")

    # Validate current value
    is_valid, validation_msg = validate_field(current_supersedes, existing_adrs, current_adr_id)

    if current_supersedes is not None:
        print(f"  Current SUPERSEDES: {current_supersedes}")
        if is_valid:
            normalized_current = normalize_field(current_supersedes)
            if normalized_current == current_supersedes:
                print("  OK: Supersedes field is valid and normalized")
                return True
            else:
                print(f"  INFO: Supersedes field can be normalized: {normalized_current}")
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Supersedes field not found")

    # Generate/fix the supersedes field
    if current_supersedes is not None and is_valid:
        normalized_supersedes = normalize_field(current_supersedes)
    else:
        # Extract potential supersession info from content
        content_supersedes = extract_supersession_info(body_content)
        # Filter to only existing ADRs and remove self-reference
        normalized_supersedes = [
            ref for ref in content_supersedes if ref in existing_adrs and ref != current_adr_id
        ]

    # Check for circular dependencies if we have changes
    if normalized_supersedes:
        all_supersessions = collect_all_supersessions()
        is_acyclic, cycle_msg = check_circular_dependencies(
            current_adr_id, normalized_supersedes, all_supersessions
        )
        if not is_acyclic:
            print(f"  ERROR: {cycle_msg}")
            return False

    print(f"  PROPOSED: Set supersedes to {normalized_supersedes}")

    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid

    if dry_run:
        print("  DRY-RUN: Would update supersedes field")
        return True

    # Update the frontmatter
    frontmatter["supersedes"] = normalized_supersedes

    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.supersedes")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")

    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Supersedes field updated")
        return True
    except Exception as e:
        print(f"  ERROR: Could not write updated file: {e}")
        return False


def process_files(file_paths, dry_run, backup, validate_only):
    """Process multiple ADR files"""
    if not file_paths:
        file_paths = sorted(ADR_DIR.glob("ADR-*.md"))
    else:
        file_paths = [Path(p) for p in file_paths]

    if not file_paths:
        print("No ADR files found to process")
        return 0

    print(f"Processing {len(file_paths)} files for SUPERSEDES field validation/updates")

    success_count = 0
    error_count = 0

    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1

    print("\nSUMMARY - SUPERSEDES Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")

    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process SUPERSEDES field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")

    args = parser.parse_args()

    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())
