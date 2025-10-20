#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - RELATED

Validates, normalizes, and updates the 'related' field in ADR frontmatter.
Manages array of ADR cross-references for linking related decisions.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def extract_adr_references(content):
    """Extract ADR references from content"""
    # Find all ADR references in various formats
    patterns = [
        r"ADR-(\d{3,4})",  # ADR-XXXX format
        r"`ADR-(\d{3,4})`",  # Backtick wrapped
        r"\[ADR-(\d{3,4})\]",  # Bracket wrapped
    ]

    references = set()
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            references.add(f"ADR-{match.zfill(4)}")

    return sorted(references)


def validate_field(field_value, existing_adrs=None):
    """Validate related field according to meta-structure rules"""
    if field_value is None:
        return True, "Related field can be empty (optional)"

    if not isinstance(field_value, list):
        return False, "Related field must be an array"

    # Validate each item in the array
    for item in field_value:
        if not isinstance(item, str):
            return False, "Related array items must be strings"

        if not re.match(r"^ADR-\d{4}$", item):
            return False, f"Related item '{item}' must follow ADR-XXXX format"

        # Check if referenced ADR exists (if existing_adrs provided)
        if existing_adrs and item not in existing_adrs:
            return False, f"Related ADR '{item}' does not exist in workspace"

    return True, "Valid"


def normalize_field(field_value):
    """Normalize related field value"""
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


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for related field"""
    print(f"Processing RELATED field in {file_path.name}")

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

    # Get existing ADRs for validation
    existing_adrs = collect_existing_adrs()
    current_adr_id = None
    match = re.search(r"ADR-(\d+)", file_path.name)
    if match:
        current_adr_id = f"ADR-{match.group(1).zfill(4)}"

    # Check current related value
    current_related = frontmatter.get("related")

    # Validate current value
    is_valid, validation_msg = validate_field(current_related, existing_adrs)

    if current_related is not None:
        print(f"  Current RELATED: {current_related}")
        if is_valid:
            normalized_current = normalize_field(current_related)
            if normalized_current == current_related:
                print("  OK: Related field is valid and normalized")
                return True
            else:
                print(f"  INFO: Related field can be normalized: {normalized_current}")
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: Related field not found")

    # Generate/fix the related field
    if current_related is not None and is_valid:
        normalized_related = normalize_field(current_related)
    else:
        # Extract potential references from content
        content_refs = extract_adr_references(body_content)
        # Remove self-reference
        if current_adr_id and current_adr_id in content_refs:
            content_refs.remove(current_adr_id)
        # Filter to only existing ADRs
        normalized_related = [ref for ref in content_refs if ref in existing_adrs]

    print(f"  PROPOSED: Set related to {normalized_related}")

    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid

    if dry_run:
        print("  DRY-RUN: Would update related field")
        return True

    # Update the frontmatter
    frontmatter["related"] = normalized_related

    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(".md.bk.related")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")

    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: Related field updated")
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

    print(f"Processing {len(file_paths)} files for RELATED field validation/updates")

    success_count = 0
    error_count = 0

    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1

    print("\nSUMMARY - RELATED Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")

    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process RELATED field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")

    args = parser.parse_args()

    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())
