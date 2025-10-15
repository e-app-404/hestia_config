#!/usr/bin/env python3
"""
ADR Frontmatter Field Processor - ID

Validates, normalizes, and updates the 'id' field in ADR frontmatter.
Ensures ADR-XXXX format and consistency with filename.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

# Try to import toml, fallback if not available
try:
    import toml
except ImportError:
    toml = None

SCRIPT_DIR = Path(__file__).parent
META_CONFIG_PATH = Path("/config/hestia/config/meta/adr.toml")
ADR_DIR = Path("/config/hestia/library/docs/ADR")


def load_meta_config():
    """Load the canonical meta-structure configuration"""
    try:
        return toml.load(META_CONFIG_PATH)
    except Exception as e:
        print(f"ERROR: Could not load meta-configuration: {e}")
        sys.exit(1)


def extract_id_from_filename(filename):
    """Extract ADR ID from filename"""
    match = re.search(r"ADR-(\d+)", filename)
    if match:
        return f"ADR-{match.group(1).zfill(4)}"
    return None


def validate_field(field_value, meta_config):
    """Validate ID field according to meta-structure rules"""
    field_spec = meta_config["fields"]["id"]

    if not field_value:
        return False, "ID field is missing"

    if not isinstance(field_value, str):
        return False, "ID must be a string"

    if not re.match(field_spec["pattern"], field_value):
        return False, f"ID must match pattern: {field_spec['pattern']}"

    return True, "Valid"


def normalize_field(field_value):
    """Normalize ID field value"""
    if isinstance(field_value, str):
        # Ensure uppercase and proper zero-padding
        match = re.match(r"adr-(\d+)", field_value.lower())
        if match:
            return f"ADR-{match.group(1).zfill(4)}"
    return field_value


def generate_field(filename):
    """Generate ID field from filename"""
    return extract_id_from_filename(filename)


def process_adr_file(file_path, dry_run=False, backup=False, validate_only=False):
    """Process single ADR file for ID field"""
    print(f"Processing ID field in {file_path.name}")

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

    meta_config = load_meta_config()

    # Check current ID value
    current_id = frontmatter.get("id")
    expected_id = generate_field(file_path.name)

    if not expected_id:
        print("  ERROR: Could not extract ADR number from filename")
        return False

    # Validate current value
    is_valid, validation_msg = validate_field(current_id, meta_config)

    if current_id:
        print(f"  Current ID: {current_id}")
        if is_valid and current_id == expected_id:
            print("  OK: ID is valid and matches filename")
            return True
        elif current_id != expected_id:
            print(f"  WARNING: ID '{current_id}' doesn't match filename '{expected_id}'")
        else:
            print(f"  WARNING: {validation_msg}")
    else:
        print("  MISSING: ID field not found")

    # Generate/fix the ID
    normalized_id = normalize_field(expected_id)
    print(f"  PROPOSED: Set ID to '{normalized_id}'")

    if validate_only:
        print("  VALIDATE-ONLY: No changes made")
        return not is_valid

    if dry_run:
        print("  DRY-RUN: Would update ID field")
        return True

    # Update the frontmatter
    frontmatter["id"] = normalized_id

    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(f".md.bk.id.{Path(__file__).stem}")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  BACKUP: Created {backup_path.name}")

    # Write updated content
    try:
        new_yaml = yaml.dump(
            frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{new_yaml}---{body_content}"
        file_path.write_text(new_content, encoding="utf-8")
        print("  SUCCESS: ID field updated")
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

    print(f"Processing {len(file_paths)} files for ID field validation/updates")

    success_count = 0
    error_count = 0

    for file_path in file_paths:
        if process_adr_file(file_path, dry_run, backup, validate_only):
            success_count += 1
        else:
            error_count += 1

    print("\nSUMMARY - ID Field Processing:")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(file_paths)}")

    return error_count


def main():
    parser = argparse.ArgumentParser(description="Process ID field in ADR frontmatter")
    parser.add_argument("files", nargs="*", help="ADR files to process (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--backup", action="store_true", help="Create backup before changes")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, no changes")

    args = parser.parse_args()

    return process_files(args.files, args.dry_run, args.backup, args.validate_only)


if __name__ == "__main__":
    sys.exit(main())
